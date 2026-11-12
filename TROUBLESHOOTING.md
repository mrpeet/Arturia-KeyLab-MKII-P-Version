# Troubleshooting

## KeyLab stops sending to FL Studio (USB MIDI hang)

### Symptoms
- The keyboard is on, lit and its own UI works (DAW/User/Analog Lab buttons, pad LEDs, octave LEDs, the display shows pad/wheel values), but **no notes or controls reach FL Studio**.
- "Refresh device list" in FL, or closing FL, can **freeze FL** until the keyboard is switched off.
- It typically shows up after the keyboard has not been played for a while (observed after ~20–30 min idle), but not after every pause.

### What is actually happening
Measured on Windows 11 (Windows MIDI Services / `midisrv`), KeyLab mkII 61, with the `tools/` watchdogs listening in parallel to FL:

| Check | Result during the hang |
|:------|:-----------------------|
| USB enumeration (`tools/usb_watch.ps1`) | Device stays fully present, all ports "OK" — no USB drop, no power loss |
| MIDI from the keyboard (`tools/midi_activity_watch.py`) | **Nothing arrives at Windows at all** — so FL and the script never see it |
| Sending to the keyboard | `midiOutLongMsg` fails, closing the port **hangs inside the driver** |
| Windows MIDI service | Once something hung on the KeyLab port, **every** MIDI device (even other interfaces) hangs on open; `Restart-Service midisrv` stays in STOP_PENDING until the keyboard is switched off |
| USB selective suspend disabled | Hang still happens → not the trigger |
| Script traffic while idle | Before the keep-alive the scripts sent **nothing** while idle |

**Conclusion:** the keyboard's USB MIDI endpoints stop working while the rest of the firmware keeps running. It is not caused by FL Studio or by the script's MIDI handling. The FL freeze is a consequence: FL waits on the blocked Windows MIDI service.

Whether this affects every KeyLab mkII / firmware version, or only some units, USB controllers or hubs, is unknown. Reports welcome.

### Keep-alive in the script (`keylab_keepalive.py`)
Because the hang appears after idle time, the DAW script sends a 6-byte Universal Identity Request (`F0 7E 7F 06 01 F7`) every 30 s:
- **Keep-alive:** regular two-way USB MIDI traffic even when nobody plays.
- **Health check:** a healthy KeyLab answers within a few ms. Both scripts swallow the reply in `OnSysEx`; SysEx is not recorded by FL, so nothing shows up in patterns or recordings.
- **If the keyboard does not answer** within 3 s, Script Output prints `KeyLab WARNING: keyboard does not answer` and FL's hint bar shows *"KeyLab not responding – switch the keyboard off and on"*. Probing then pauses (sending to a dead port is what can block the Windows MIDI service) until the keyboard sends anything again.
- Cost: one timestamp compare per `OnIdle`, no allocations, no growing state.

Whether the keep-alive actually *prevents* the hang is being tested — if you still get the warning with it, please report it.

### Recovering
- **Simplest:** switch the KeyLab off and on.
- **Without power-cycling** (administrator terminal):
  ```
  pnputil /enum-devices /connected | findstr VID_1C75
  pnputil /restart-device "USB\VID_1C75&PID_xxxx\<serial>"
  ```
  Use the line **without** `&MI_` (the USB composite device). Then press **Options → MIDI Settings → Refresh device list** in FL.

### Other things worth trying
- Connect the keyboard **directly to a rear mainboard USB port** (not through a hub/front panel), with a short cable.
- Check the firmware version in Arturia MIDI Control Center and make sure the last released version is installed.
- Try a different USB controller (e.g. USB 2.0 port) if available.
