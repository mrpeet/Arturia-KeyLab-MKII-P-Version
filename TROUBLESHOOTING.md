# Troubleshooting

## KeyLab stops sending to FL Studio (USB MIDI hang)

### Symptoms
- The keyboard is on, lit and its own UI works (DAW/User/Analog Lab buttons, pad LEDs, octave LEDs, the display shows pad/wheel values), but **no notes or controls reach FL Studio**.
- "Refresh device list" in FL, or closing FL, can **freeze FL** until the keyboard is switched off.
- It typically shows up after the keyboard has not been played for a while (observed after ~20–30 min idle), but not after every pause.

### What is actually happening
Measured on Windows 11 (Windows MIDI Services / `midisrv`), KeyLab mkII 61, with `tools/` watchdogs running in parallel to FL:

| Check | Result during the hang |
|:------|:-----------------------|
| USB enumeration (`tools/usb_watch.ps1`) | Device stays fully present, all ports "OK" — no USB drop, no power loss |
| MIDI from the keyboard (`tools/midi_activity_watch.py`, listens next to FL) | **Nothing arrives at Windows at all** — so FL and the script never see it |
| Sending to the keyboard | `midiOutLongMsg` fails, closing the port **hangs inside the driver** |
| Windows MIDI service | Once something hung on the KeyLab port, **every** MIDI device (even other interfaces) hangs on open; `Restart-Service midisrv` stays in STOP_PENDING until the keyboard is switched off |
| USB selective suspend disabled | Hang still happens → not the trigger |
| Script SysEx traffic | The scripts send almost nothing while idle; the hang is independent of the script |

**Conclusion:** the keyboard's USB MIDI endpoints stop working while the rest of the firmware keeps running. It is not caused by FL Studio or this script. The FL freeze is a consequence: FL waits on the blocked Windows MIDI service.

Whether this affects every KeyLab mkII / firmware version, or only some units, USB controllers or hubs, is unknown. Reports welcome.

### Recover without power-cycling
In an **administrator** terminal:
```
pnputil /enum-devices /connected | findstr VID_1C75
pnputil /restart-device "USB\VID_1C75&PID_xxxx\<serial>"
```
Use the line **without** `&MI_` (the USB composite device). Then press **Options → MIDI Settings → Refresh device list** in FL. The keyboard works again immediately.

### Automatic recovery: `tools/keylab_guard.py`
Runs in the background (Windows, standard library only):
- Every 60 s it sends a 6-byte Universal Identity Request (`F0 7E 7F 06 01 F7`) and waits for the reply (a healthy KeyLab answers in ~5 ms). The main script swallows the reply, so FL is not affected.
- Each probe runs in a short-lived child process, because a MIDI call on a dead port can hang in the driver. The guard holds no MIDI handles and keeps no growing state.
- Two failed probes in a row → disable the device for 3 s, enable it again (like a short unplug), beep and log to `tools/keylab_guard.log`. Then press "Refresh device list" in FL if needed.
- Without admin rights it only detects, beeps and logs the command to run.

```
py tools\keylab_guard.py              (from an administrator terminal)
py tools\keylab_guard.py --once       (single probe: is the keyboard answering?)
py tools\keylab_guard.py --no-reset   (detect + log only)
```

Side question the log will answer: if the periodic probe alone keeps the keyboard from hanging (no `HANG` lines over many sessions), a tiny keep-alive could move into the FL script itself. Recovery (USB reset) cannot — FL scripts have no admin rights and no device-reset API.

### Other things worth trying
- Connect the keyboard **directly to a rear mainboard USB port** (not through a hub/front panel), with a short cable.
- Check the firmware version in Arturia MIDI Control Center and make sure the last released version is installed.
- Try a different USB controller (e.g. USB 2.0 port) if available.
