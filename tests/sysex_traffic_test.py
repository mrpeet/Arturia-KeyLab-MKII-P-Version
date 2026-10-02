"""Offline SysEx traffic test for the KeyLab mkII scripts (runs without FL Studio).

Simulates typical playing situations with stubbed FL modules and counts the SysEx
messages both scripts send to the device. Fails if a scenario exceeds its limit —
too much SysEx can hang the KeyLab firmware, and a hung device freezes FL.

Usage:  python tests/sysex_traffic_test.py [script_dir]
The script dir (default: parent of this folder) is copied to a temp folder first,
so keylab_pad_state.json in the live folder is never touched.
"""
import importlib, math, os, shutil, sys, tempfile, time, types

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = tempfile.mkdtemp(prefix="klsim_")
for f in os.listdir(SRC):
    if f.endswith(".py"):
        shutil.copy(os.path.join(SRC, f), WORK)
sys.path.insert(0, WORK)
sys.dont_write_bytecode = True

# ---------------------------------------------------------------- simulated clock
_now = [1000.0]
time.monotonic = lambda: _now[0]
time.time = lambda: _now[0]


def advance(sec):
    _now[0] += sec


# ---------------------------------------------------------------- traffic log
SYSEX = []          # (t, script_tag, bytes)
CURRENT = ["?"]
STATS = [0]
INVALID = []
_orig_getmtime = os.path.getmtime


def _counting_getmtime(p):
    STATS[0] += 1
    return _orig_getmtime(p)


os.path.getmtime = _counting_getmtime


# ---------------------------------------------------------------- FL module stubs
class Stub(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: 0


def stub(name, **attrs):
    m = Stub(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m


def _sysex_out(data):
    data = bytes(data)
    SYSEX.append((_now[0], CURRENT[0], data))
    if data[0] != 0xF0 or data[-1] != 0xF7 or any(b > 0x7F for b in data[1:-1]):
        INVALID.append((CURRENT[0], data.hex(" ")))


stub("device", midiOutSysex=_sysex_out, forwardMIDICC=lambda *a: None,
     getName=lambda: "KeyLab mkII 61", isAssigned=lambda: 1)
stub("midi", widMixer=0, widChannelRack=1, widPlaylist=2, widPianoRoll=3, widBrowser=4,
     widPlugin=5, MIDI_CONTROLCHANGE=0xB0, PITCH_BEND_STATUS=0xE0, FPT_Left=0, FPT_Right=0,
     FPT_LoopRecord=0, FPT_Metronome=0, FPT_Overdub=0, FPT_TapTempo=0, SS_Start=2, SS_Stop=0)
_vol = {}
stub("mixer", getTrackCount=lambda: 20, trackNumber=lambda: 1,
     getTrackVolume=lambda t, mode=0: (20 * math.log10(max(_vol.get(t, 0.8) / 0.8, 1e-6)) if mode else _vol.get(t, 0.8)),
     setTrackVolume=lambda t, v, *a: _vol.__setitem__(t, v),
     getTrackName=lambda t: "Insert %d" % t, getTrackColor=lambda t: 0x336699)
_chvol = {}
stub("channels", channelNumber=lambda: 0, channelCount=lambda: 12,
     getChannelName=lambda c: "Kick Groß %d" % c, getChannelColor=lambda c: 0x993366,
     getChannelVolume=lambda c, mode=0: (20 * math.log10(max(_chvol.get(c, 0.78) / 0.8, 1e-6)) if mode else _chvol.get(c, 0.78)),
     setChannelVolume=lambda c, v, *a: _chvol.__setitem__(c, v))
FOCUS = {"w": 0}
stub("ui", getFocused=lambda w: 1 if w == FOCUS["w"] else 0, getProgTitle=lambda: "FL Studio",
     getFocusedPluginName=lambda: "", getSnapMode=lambda: 3)
for m in ("patterns", "transport", "general", "plugins", "playlist", "arrangement"):
    stub(m)
sys.modules["patterns"].getPatternName = lambda n: "Pattern 1"


class Ev:
    def __init__(self, status, d1=0, d2=0, sysex=None):
        self.status = status; self.data1 = d1; self.data2 = d2
        self.midiId = status & 0xF0 if status < 0xF0 else status
        self.midiChan = status & 0x0F; self.handled = False
        self.sysex = sysex; self.port = 0; self.note = d1
        self.controlNum = d1; self.controlVal = d2


def load(modname, tag):
    CURRENT[0] = tag
    return importlib.import_module(modname)


def run(tag, mod, fn, *a):
    CURRENT[0] = tag
    return getattr(mod, fn)(*a)


def window(t0, t1):
    return [s for s in SYSEX if t0 <= s[0] < t1]


RESULTS = []


def report(name, t0, t1, max_per_sec=None):
    msgs = window(t0, t1)
    dur = max(t1 - t0, 1e-9)
    rate = len(msgs) / dur
    nbytes = sum(len(s[2]) for s in msgs)
    peak, t = 0, t0
    while t < t1:
        peak = max(peak, len(window(t, t + 0.1)))
        t += 0.05
    ok = max_per_sec is None or rate <= max_per_sec
    RESULTS.append(ok)
    limit = "" if max_per_sec is None else "(max %d/s)" % max_per_sec
    print("%-4s %-30s %5d SysEx %6.0f msg/s %7.0f B/s  peak %3d/100ms %s" % (
        "OK" if ok else "FAIL", name, len(msgs), rate, nbytes / dur, peak, limit))


IDLE_DT = 0.02  # FL calls OnIdle roughly every 20 ms


def idle(fwd, daw, seconds):
    end = _now[0] + seconds
    while _now[0] < end:
        run("fwd", fwd, "OnIdle"); run("daw", daw, "OnIdle")
        advance(IDLE_DT)


# ---------------------------------------------------------------- scenarios
# Note: FL runs both scripts in separate interpreters; here they share one, which
# is fine for counting traffic (the DAW script reloads its own keylab_* modules).
fwd = load("device_KeyLabmkII_Forward", "fwd")
run("fwd", fwd, "OnInit")
daw = load("device_KeyLabmkII", "daw")
run("daw", daw, "OnInit")

print("Script dir:", SRC)
t = _now[0]; idle(fwd, daw, 0.5)
run("daw", daw, "OnSysEx", Ev(0xF0, sysex=bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42, 0x02, 0x00, 0x00, 0x15, 0x00, 0xF7])))
idle(fwd, daw, 0.5)
report("Init + lazy init (1 s)", t, _now[0])

t = _now[0]; idle(fwd, daw, 10)
report("Idle (10 s)", t, _now[0], max_per_sec=2)

# 4 pads held 2 s, poly aftertouch ~250 msg/s per pad, then released
STATS[0] = 0
t = _now[0]
pads = [36, 41, 46, 51]
for p in pads:
    run("fwd", fwd, "OnMidiIn", Ev(0x99, p, 100))
end = _now[0] + 2.0; k = 0
while _now[0] < end:
    for p in pads:
        run("fwd", fwd, "OnMidiIn", Ev(0xA9, p, 40 + (k * 7 + p) % 80))
    k += 1
    advance(0.004)
    if k % 5 == 0:
        run("fwd", fwd, "OnIdle"); run("daw", daw, "OnIdle")
for p in pads:
    run("fwd", fwd, "OnMidiIn", Ev(0x89, p, 0))
report("4 pads + aftertouch (2 s)", t, _now[0], max_per_sec=150)
stats = STATS[0]
print("     -> state-file stat() calls: %d %s" % (stats, "" if stats <= 100 else "(FAIL, max 100)"))
RESULTS.append(stats <= 100)

t = _now[0]
for i in range(40):
    p = 36 + (i % 16)
    run("fwd", fwd, "OnMidiIn", Ev(0x99, p, 90)); advance(0.025)
    run("fwd", fwd, "OnMidiIn", Ev(0x89, p, 0)); advance(0.025)
report("Drum roll 20 hits/s (2 s)", t, _now[0], max_per_sec=60)

FOCUS["w"] = 1  # channel rack
t = _now[0]
raw0 = int(0.78 / 0.8 * 16383)
run("daw", daw, "OnMidiMsg", Ev(0xE0, raw0 & 0x7F, raw0 >> 7))
for i in range(200):
    raw = int(raw0 * (1 - i / 200.0))
    run("daw", daw, "OnMidiMsg", Ev(0xE0, raw & 0x7F, raw >> 7))
    advance(0.005)
    if i % 4 == 0:
        run("daw", daw, "OnIdle"); run("fwd", fwd, "OnIdle")
report("Fader move, 1 fader (1 s)", t, _now[0], max_per_sec=40)

t = _now[0]
for i in range(200):
    for ch in range(3):
        raw = int(16383 * (i / 200.0))
        run("daw", daw, "OnMidiMsg", Ev(0xE0 + ch, raw & 0x7F, raw >> 7))
    advance(0.005)
    if i % 4 == 0:
        run("daw", daw, "OnIdle"); run("fwd", fwd, "OnIdle")
report("Fader move, 3 faders (1 s)", t, _now[0], max_per_sec=40)

t = _now[0]
for i in range(100):
    run("daw", daw, "OnMidiMsg", Ev(0xB0, 16 + (i % 2), 1 if i % 3 else 65)); advance(0.01)
    if i % 2 == 0:
        run("daw", daw, "OnIdle")
report("Encoder turning (1 s)", t, _now[0], max_per_sec=40)

t = _now[0]
run("daw", daw, "OnDeInit"); run("fwd", fwd, "OnDeInit")
print("     OnDeInit sends %d SysEx" % len(window(t, _now[0] + 1)))

if INVALID:
    RESULTS.append(False)
    print("FAIL invalid SysEx (data byte > 0x7F or bad framing):")
    for tag, hx in INVALID[:10]:
        print("     %s: %s" % (tag, hx))

shutil.rmtree(WORK, ignore_errors=True)
print()
print("ALL OK" if all(RESULTS) else "FAILED")
sys.exit(0 if all(RESULTS) else 1)
