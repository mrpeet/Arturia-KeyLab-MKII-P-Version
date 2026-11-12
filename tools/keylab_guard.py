"""KeyLab Guard - detects the KeyLab mkII "USB MIDI hang" and recovers it without a power cycle.

Background (see TROUBLESHOOTING.md): after some idle time the KeyLab can stop sending and
receiving USB MIDI while it stays enumerated and its own UI keeps working. Any app that then
sends to / closes the port blocks the whole Windows MIDI service (FL freezes on refresh).
A USB-level device restart (what `pnputil /restart-device` does) brings it back.

How the guard works (Windows only, standard library only):
  * Every PROBE_INTERVAL_S a short-lived child process sends a Universal Identity Request
    (F0 7E 7F 06 01 F7, 6 bytes) and waits for the keyboard's reply. A healthy KeyLab answers
    in ~5 ms. The child process is used on purpose: if the port is dead, the MIDI call can hang
    inside the driver, and only a separate process keeps the guard itself responsive.
  * No reply twice in a row -> the guard restarts the KeyLab on USB (disable, wait, enable),
    beeps and logs it. Afterwards press "Refresh device list" in FL's MIDI settings if FL does
    not pick the keyboard up by itself.
  * The guard holds no MIDI handles, keeps no growing state and only writes event lines
    (plus one heartbeat per hour) to tools/keylab_guard.log.

Resetting a device needs administrator rights. Run from an *administrator* terminal:
    py tools\\keylab_guard.py
Without admin rights it still detects the hang, beeps and tells you the command to run.
Options:  --interval 60   --once (single probe, prints result)   --no-reset (detect only)
Stop with Ctrl+C.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "keylab_guard.log")

ARTURIA_VID = "1C75"
PROBE_INTERVAL_S = 60.0
PROBE_TIMEOUT_S = 6.0        # child process must finish within this time
REPLY_TIMEOUT_S = 1.5        # healthy reply arrives in a few ms
CONFIRM_DELAY_S = 5.0        # second probe before declaring the keyboard dead
RESET_OFF_S = 3.0            # how long the device stays disabled (like a short power-off)
AFTER_RESET_GRACE_S = 15.0   # let Windows re-enumerate before probing again
HEARTBEAT_S = 3600.0

EXIT_OK, EXIT_NO_REPLY, EXIT_NO_PORTS = 0, 2, 3


# ---------------------------------------------------------------------------
#  Child process: one identity-request probe
# ---------------------------------------------------------------------------

def _probe_child():
    w = ctypes.WinDLL("winmm")

    class INCAPS(ctypes.Structure):
        _fields_ = [("wMid", wt.WORD), ("wPid", wt.WORD), ("v", wt.UINT),
                    ("szPname", wt.WCHAR * 32), ("s", wt.DWORD)]

    class OUTCAPS(ctypes.Structure):
        _fields_ = [("wMid", wt.WORD), ("wPid", wt.WORD), ("v", wt.UINT), ("szPname", wt.WCHAR * 32),
                    ("t", wt.WORD), ("vo", wt.WORD), ("n", wt.WORD), ("c", wt.WORD), ("s", wt.DWORD)]

    class MIDIHDR(ctypes.Structure):
        _fields_ = [("lpData", ctypes.c_void_p), ("dwBufferLength", wt.DWORD),
                    ("dwBytesRecorded", wt.DWORD), ("dwUser", ctypes.c_size_t),
                    ("dwFlags", wt.DWORD), ("lpNext", ctypes.c_void_p),
                    ("reserved", ctypes.c_size_t), ("dwOffset", wt.DWORD),
                    ("dwReserved", ctypes.c_size_t * 8)]

    callback_type = ctypes.WINFUNCTYPE(None, wt.HANDLE, wt.UINT, ctypes.c_size_t,
                                       ctypes.c_size_t, ctypes.c_size_t)
    got_reply = [False]

    def on_input(handle, msg, instance, param1, param2):
        if msg == 0x3C4:  # MIM_LONGDATA
            hdr = ctypes.cast(param1, ctypes.POINTER(MIDIHDR)).contents
            data = ctypes.string_at(hdr.lpData, hdr.dwBytesRecorded) if hdr.dwBytesRecorded else b""
            # Identity Reply: F0 7E <dev> 06 02 00 20 6B ... (Arturia manufacturer ID)
            if data[:2] == b"\xF0\x7E" and data[3:8] == b"\x06\x02\x00\x20\x6B":
                got_reply[0] = True

    cb = callback_type(on_input)
    inputs = []
    for i in range(w.midiInGetNumDevs()):
        caps = INCAPS()
        if w.midiInGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) != 0:
            continue
        if "KeyLab" not in caps.szPname:
            continue
        h = wt.HANDLE()
        if w.midiInOpen(ctypes.byref(h), i, cb, 0, 0x30000) != 0:  # CALLBACK_FUNCTION
            continue
        buf = ctypes.create_string_buffer(256)
        hdr = MIDIHDR()
        hdr.lpData = ctypes.cast(buf, ctypes.c_void_p)
        hdr.dwBufferLength = 256
        w.midiInPrepareHeader(h, ctypes.byref(hdr), ctypes.sizeof(hdr))
        w.midiInAddBuffer(h, ctypes.byref(hdr), ctypes.sizeof(hdr))
        w.midiInStart(h)
        inputs.append((h, hdr, buf))

    out_index = None
    for i in range(w.midiOutGetNumDevs()):
        caps = OUTCAPS()
        if w.midiOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) != 0:
            continue
        if "KeyLab" in caps.szPname:
            # Prefer the DAW port (MIDIOUT2), fall back to any KeyLab output
            if out_index is None or "MIDIOUT2" in caps.szPname:
                out_index = i

    if not inputs or out_index is None:
        return EXIT_NO_PORTS

    request = ctypes.create_string_buffer(bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]), 6)
    out = wt.HANDLE()
    sent = False
    if w.midiOutOpen(ctypes.byref(out), out_index, 0, 0, 0) == 0:
        ohdr = MIDIHDR()
        ohdr.lpData = ctypes.cast(request, ctypes.c_void_p)
        ohdr.dwBufferLength = 6
        w.midiOutPrepareHeader(out, ctypes.byref(ohdr), ctypes.sizeof(ohdr))
        sent = w.midiOutLongMsg(out, ctypes.byref(ohdr), ctypes.sizeof(ohdr)) == 0
        deadline = time.monotonic() + REPLY_TIMEOUT_S
        while sent and not got_reply[0] and time.monotonic() < deadline:
            time.sleep(0.005)
        if got_reply[0]:
            w.midiOutUnprepareHeader(out, ctypes.byref(ohdr), ctypes.sizeof(ohdr))
            w.midiOutClose(out)
        # On failure the out handle is NOT closed: closing a dead port can hang in the driver.
        # The process exits right away and the OS cleans up (or the guard resets the device).

    if got_reply[0]:
        for h, hdr, _buf in inputs:
            w.midiInStop(h)
            w.midiInReset(h)
            w.midiInUnprepareHeader(h, ctypes.byref(hdr), ctypes.sizeof(hdr))
            w.midiInClose(h)
        return EXIT_OK
    os._exit(EXIT_NO_REPLY)  # skip any cleanup that could block on the dead device


# ---------------------------------------------------------------------------
#  Guard (parent process)
# ---------------------------------------------------------------------------

def log(text):
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), text)
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def beep():
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def find_keylab_instance_id():
    """Return the USB composite-device instance ID of the connected KeyLab, or None.

    Parses `pnputil /enum-devices /connected` language-independently (only the
    `USB\\VID_1C75&PID_xxxx\\<serial>` token is used, interface entries with &MI_ are skipped).
    """
    try:
        out = subprocess.run(["pnputil", "/enum-devices", "/connected"], capture_output=True,
                             text=True, errors="replace", timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    pattern = re.compile(r"USB\\VID_%s&PID_[0-9A-F]{4}\\[^\s&]+" % ARTURIA_VID, re.IGNORECASE)
    for match in pattern.finditer(out):
        return match.group(0)
    return None


def run_probe():
    """Run one probe in a child process. Returns 'ok', 'no_reply', 'hung' or 'no_ports'."""
    cmd = [sys.executable, "-I", os.path.abspath(__file__), "--probe-child"]
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=flags)
    try:
        code = proc.wait(timeout=PROBE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        proc.kill()
        _stuck_children.append(proc)
        return "hung"
    return {EXIT_OK: "ok", EXIT_NO_REPLY: "no_reply", EXIT_NO_PORTS: "no_ports"}.get(code, "no_reply")


_stuck_children = []


def reap_stuck_children():
    """Children stuck in the driver exit once the device is reset; drop them then."""
    for proc in list(_stuck_children):
        if proc.poll() is not None:
            _stuck_children.remove(proc)
        else:
            proc.kill()


def reset_device(instance_id):
    """Disable + enable the KeyLab on USB (like a short unplug). Falls back to restart-device."""
    def pnp(*args):
        r = subprocess.run(["pnputil"] + list(args) + [instance_id], capture_output=True,
                           text=True, errors="replace", timeout=60)
        return r.returncode == 0

    if pnp("/disable-device"):
        time.sleep(RESET_OFF_S)
        if pnp("/enable-device"):
            return True
    return pnp("/restart-device")


def guard(interval, allow_reset):
    admin = is_admin()
    log("--- keylab_guard started (interval %ds, %s) ---"
        % (interval, "admin: auto-reset on" if admin and allow_reset else "detect only"))
    if allow_reset and not admin:
        log("NOTE   not running as administrator - hangs are detected but not reset")

    was_present = None
    last_heartbeat = time.monotonic()
    probes_ok = 0
    resets = 0
    try:
        while True:
            reap_stuck_children()
            result = run_probe()

            if result == "no_ports":
                if was_present is not False:
                    log("ABSENT KeyLab MIDI ports not present (keyboard off/unplugged?)")
                was_present = False
            elif result == "ok":
                if was_present is not True:
                    log("OK     KeyLab answers")
                was_present = True
                probes_ok += 1
            else:
                time.sleep(CONFIRM_DELAY_S)
                second = run_probe()
                if second == "ok":
                    log("WARN   one probe failed (%s), second one OK - ignored" % result)
                    probes_ok += 1
                elif second == "no_ports":
                    log("ABSENT KeyLab MIDI ports disappeared during probe")
                    was_present = False
                else:
                    log("HANG   KeyLab does not answer (%s, %s) - USB MIDI is stuck" % (result, second))
                    beep()
                    instance_id = find_keylab_instance_id()
                    if not instance_id:
                        log("ERROR  KeyLab USB device not found for reset")
                    elif not (allow_reset and admin):
                        log("ACTION run as admin:  pnputil /restart-device \"%s\"" % instance_id)
                    elif reset_device(instance_id):
                        resets += 1
                        log("RESET  KeyLab restarted on USB (reset #%d) - press 'Refresh device list' "
                            "in FL if the keyboard stays silent there" % resets)
                        beep()
                        time.sleep(AFTER_RESET_GRACE_S)
                        reap_stuck_children()
                        log("CHECK  after reset: %s" % run_probe())
                    else:
                        log("ERROR  pnputil reset failed")
                    was_present = None

            now = time.monotonic()
            if now - last_heartbeat >= HEARTBEAT_S:
                log("ALIVE  %d probes OK in the last hour, %d resets so far" % (probes_ok, resets))
                probes_ok = 0
                last_heartbeat = now
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        log("--- keylab_guard stopped ---")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--interval", type=float, default=PROBE_INTERVAL_S, help="seconds between probes")
    parser.add_argument("--once", action="store_true", help="run a single probe and print the result")
    parser.add_argument("--no-reset", action="store_true", help="only detect and log, never reset")
    parser.add_argument("--probe-child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if sys.platform != "win32":
        sys.exit("keylab_guard runs on Windows only")
    if args.probe_child:
        sys.exit(_probe_child())
    if args.once:
        print("probe:", run_probe(), "| device:", find_keylab_instance_id(), "| admin:", is_admin())
        return
    guard(max(10.0, args.interval), allow_reset=not args.no_reset)


if __name__ == "__main__":
    main()
