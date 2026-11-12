"""KeyLab mkII MIDI activity watchdog (Windows, no extra packages).

Listens read-only on the KeyLab MIDI inputs in parallel to FL Studio (Windows MIDI
Services allows several apps per port) and logs when the keyboard sends something.
When the keyboard "stops responding", play some keys and check the log:
  - messages still logged  -> keyboard + Windows are fine, problem is in FL/script
  - nothing logged         -> keyboard firmware or Windows MIDI stack stopped sending

Usage:  py tools\\midi_activity_watch.py
Stop with Ctrl+C. Log: tools\\midi_activity.log
"""
import ctypes
import ctypes.wintypes as wt
import os
import threading
import time

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "midi_activity.log")
POLL_S = 2.0        # how often the port list is checked (reconnects)
SUMMARY_S = 30.0    # interval of the per-port message count while active
PAUSE_S = 5.0       # silence after which a new message is logged as "signal again"

winmm = ctypes.WinDLL("winmm")
MIM_DATA = 0x3C3
MIM_LONGDATA = 0x3C4
CALLBACK_FUNCTION = 0x30000


class MIDIINCAPSW(ctypes.Structure):
    _fields_ = [("wMid", wt.WORD), ("wPid", wt.WORD), ("vDriverVersion", wt.UINT),
                ("szPname", wt.WCHAR * 32), ("dwSupport", wt.DWORD)]


MidiInProc = ctypes.WINFUNCTYPE(None, wt.HANDLE, wt.UINT, ctypes.c_size_t,
                                ctypes.c_size_t, ctypes.c_size_t)

_lock = threading.Lock()
_stats = {}  # port -> {'count': n, 'last': t, 'kinds': {...}}

_KIND = {0x80: "NoteOff", 0x90: "NoteOn", 0xA0: "PolyAT", 0xB0: "CC",
         0xC0: "Prog", 0xD0: "ChanAT", 0xE0: "PB"}


def log(text):
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), text)
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _make_callback(port):
    def cb(handle, msg, instance, param1, param2):
        if msg != MIM_DATA:
            return
        status = param1 & 0xF0
        now = time.monotonic()
        with _lock:
            s = _stats.setdefault(port, {"count": 0, "last": 0.0, "kinds": {}, "announced": False})
            if now - s["last"] > PAUSE_S:
                s["announced"] = False
            s["count"] += 1
            s["last"] = now
            k = _KIND.get(status, "Other")
            s["kinds"][k] = s["kinds"].get(k, 0) + 1
    return MidiInProc(cb)


def _keylab_inputs():
    ports = {}
    for i in range(winmm.midiInGetNumDevs()):
        caps = MIDIINCAPSW()
        if winmm.midiInGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
            if "KeyLab" in caps.szPname:
                ports[caps.szPname] = i
    return ports


def _open_all(ports):
    opened = []
    for name, idx in sorted(ports.items()):
        handle = wt.HANDLE()
        cb = _make_callback(name)
        res = winmm.midiInOpen(ctypes.byref(handle), idx, cb, 0, CALLBACK_FUNCTION)
        if res == 0:
            winmm.midiInStart(handle)
            opened.append((name, handle, cb))
            log("OPEN   %s" % name)
        else:
            log("FAILED to open %s (error %d)" % (name, res))
    return opened


def _close_all(opened):
    for name, handle, _cb in opened:
        winmm.midiInStop(handle)
        winmm.midiInClose(handle)


def main():
    log("--- midi_activity_watch started ---")
    opened, known = [], None
    last_summary = time.monotonic()
    try:
        while True:
            ports = _keylab_inputs()
            if set(ports) != known:
                _close_all(opened)
                opened = []
                if ports:
                    log("PORTS  %s" % ", ".join(sorted(ports)))
                    opened = _open_all(ports)
                else:
                    log("PORTS  no KeyLab MIDI input present")
                known = set(ports)

            now = time.monotonic()
            with _lock:
                for port, s in _stats.items():
                    if not s["announced"] and s["count"]:
                        log("SIGNAL %s  (keyboard is sending)" % port)
                        s["announced"] = True
                if now - last_summary >= SUMMARY_S:
                    for port, s in sorted(_stats.items()):
                        if s["count"]:
                            kinds = ", ".join("%s %d" % kv for kv in sorted(s["kinds"].items()))
                            log("COUNT  %s: %d msgs in %ds (%s)" % (port, s["count"], SUMMARY_S, kinds))
                        s["count"] = 0
                        s["kinds"] = {}
                    last_summary = now
            time.sleep(POLL_S)
    except KeyboardInterrupt:
        pass
    finally:
        _close_all(opened)
        log("--- midi_activity_watch stopped ---")


if __name__ == "__main__":
    main()
