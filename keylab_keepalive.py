# KeyLab mkII — USB keep-alive + health check (DAW port script)
#
# Background (see TROUBLESHOOTING.md): after some idle time the KeyLab can stop
# sending/receiving USB MIDI while it stays connected. This module sends a tiny
# Universal Identity Request (F0 7E 7F 06 01 F7, 6 bytes) every _INTERVAL_S:
#   - keep-alive: regular two-way traffic, in case the hang is idle-related
#   - health check: a healthy KeyLab replies within a few ms; the reply is
#     swallowed in OnSysEx (SysEx is never recorded by FL).
# If no reply arrives within _REPLY_TIMEOUT_S, a hint is shown once and probing
# pauses (sending to a dead port is what can block the Windows MIDI service)
# until the keyboard sends anything again.
#
# Cost: one timestamp compare per OnIdle, 6 bytes every 30 s, no allocations.

import time

import device
import ui

_INTERVAL_S = 30.0
_REPLY_TIMEOUT_S = 3.0

_IDENTITY_REQUEST = bytes([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
# Identity Reply: F0 7E <dev> 06 02 00 20 6B ... (00 20 6B = Arturia)
_REPLY_SUB_ID = b"\x06\x02\x00\x20\x6B"

_next_probe = 0.0
_pending_since = None   # time the unanswered request was sent, or None
_suspended = False      # True after a missing reply, until the keyboard talks again


def reset():
    """Call from OnInit: first probe after one interval."""
    global _next_probe, _pending_since, _suspended
    _next_probe = time.monotonic() + _INTERVAL_S
    _pending_since = None
    _suspended = False


def note_input():
    """Call on any incoming MIDI from the keyboard — it is alive."""
    global _pending_since, _suspended
    if _suspended:
        _suspended = False
        print("KeyLab: keyboard is responding again (%s)" % time.strftime("%H:%M:%S"))
    _pending_since = None


def on_sysex(data):
    """Call from OnSysEx. Returns True if this was our identity reply (swallow it)."""
    if data and len(data) >= 8 and data[0] == 0xF0 and data[1] == 0x7E and data[3:8] == _REPLY_SUB_ID:
        note_input()
        return True
    return False


def tick():
    """Call from OnIdle."""
    global _next_probe, _pending_since, _suspended
    if _suspended:
        return
    now = time.monotonic()
    if _pending_since is not None:
        if now - _pending_since >= _REPLY_TIMEOUT_S:
            _pending_since = None
            _suspended = True
            print("KeyLab WARNING: keyboard does not answer (%s) - USB MIDI hang? "
                  "Switch the KeyLab off and on, see TROUBLESHOOTING.md" % time.strftime("%H:%M:%S"))
            ui.setHintMsg("KeyLab not responding - switch the keyboard off and on")
        return
    if now >= _next_probe:
        _next_probe = now + _INTERVAL_S
        _pending_since = now
        device.midiOutSysex(_IDENTITY_REQUEST)
