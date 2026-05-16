# name= KeyLab mkII Forward (KeyLab mkII 61 · Port 0)

"""
[[
	Surface:	KeyLab mkII
	Original:	Farès MEZDOUR
	P Version:	Forward-Script (Pad-Transposition + V-Collection CC-Forwarding)
]]
"""

# This script runs on the Keys Port (KeyLab mkII 61) and:
#   1. Transposes pad events (Channel 10, native notes 36-51) based on shared state
#      from the DAW script:
#        - Chromatic: semitones from C3 (MIDI 48), output on MIDI channel 1
#        - Drum Map (fpc): GM Drum layout via _FPC_MAP, output stays on MIDI channel 10
#      Both support pad_bank_offset (0-5, +16 semitones per bank).
#   2. Forwards CCs and Pitch Bend to Port 10 for Arturia V-Collection plugins.
#
# Setup in FL Studio → Options → MIDI Settings:
#   Input:  "KeyLab mkII 61"
#   Script: "KeyLab mkII Forward (KeyLab mkII 61 · Port 0)"
#   Port:   0
#
# Shares state with device_KeyLabmkII.py via keylab_shared_state (sys + file).

import ui
import midi
import device

import keylab_shared_state as pad_state

from keylab_config import Pad

# Debug pad transposition in FL Script Output (set False when stable)
_DEBUG_PADS = False

# Chromatic layout starts at C3 (user spec); Drum Map uses GM drums on channel 10
_CHROMATIC_BASE = 48  # MIDI note C3
_PAD_VELOCITY_FIXED = 95  # 75% of MIDI 127 when velocity is disabled

# Status bytes
_NOTE_ON_CH10 = 0x90 + Pad.PAD_CHANNEL   # 0x99
_NOTE_OFF_CH10 = 0x80 + Pad.PAD_CHANNEL  # 0x89
_NOTE_ON_CH1 = 0x90
_NOTE_OFF_CH1 = 0x80

# CHROMATIC_MAP: native pad note -> sequential index (0-15), top-left = lowest
_CHROMATIC_MAP = {
    48: 0,  49: 1,  50: 2,  51: 3,
    44: 4,  45: 5,  46: 6,  47: 7,
    40: 8,  41: 9,  42: 10, 43: 11,
    36: 12, 37: 13, 38: 14, 39: 15,
}

# FPC_MAP: native pad note -> GM Drum note (channel 10)
_FPC_MAP = {
    36: 49, 37: 55, 38: 51, 39: 53,
    40: 48, 41: 47, 42: 45, 43: 43,
    44: 40, 45: 38, 46: 46, 47: 44,
    48: 37, 49: 36, 50: 42, 51: 54,
}

V_COLLECTION = {
    'Analog Lab V',
    'Analog Lab 4',
    'ARP 2600 V3',
    'B-3 V2',
    'Buchla Easel V',
    'Clavinet V',
    'CMI V',
    'CS-80 V3',
    'CZ V',
    'DX7 V',
    'Emulator II V',
    'Farfisa V',
    'Jun-6 V',
    'Jup-8 V4',
    'Matrix-12 V2',
    'Mellotron V',
    'Mini V3',
    'Modular V3',
    'OB-Xa V',
    'PatchWorks',
    'Piano V2',
    'Prophet V3',
    'SEM V2',
    'Solina V2',
    'Stage-73 V2',
    'SQ80 V',
    'Synclavier V',
    'Synthi V',
    'Synthopedia',
    'Vocoder V',
    'Vox Continental V2',
    'Wurli V2',
}


def _is_pad_note_event(event):
    """True if this is a pad Note On/Off on the hardware drum channel."""
    if event.status not in (_NOTE_ON_CH10, _NOTE_OFF_CH10):
        return False
    return Pad.FIRST <= event.data1 <= Pad.LAST


def _set_melodic_channel(event, note_on):
    """Rewrite event to MIDI channel 1 (melodic, not GM drum channel 10)."""
    event.status = _NOTE_ON_CH1 if note_on else _NOTE_OFF_CH1
    event.midiChan = 0
    try:
        event.note = event.data1
    except Exception:
        pass


def _transpose_pad(event):
    """Modify event.data1 (and channel in chromatic mode) in place."""
    note = event.data1
    bank = pad_state.get_pad_bank_offset()
    mode = pad_state.get_pad_mode()
    note_on = event.status == _NOTE_ON_CH10 and event.data2 > 0

    if mode == pad_state.PAD_MODE_CHROMATIC:
        idx = _CHROMATIC_MAP.get(note)
        if idx is None:
            return
        new_note = _CHROMATIC_BASE + idx + bank * 16
        event.data1 = max(0, min(127, new_note))
        _set_melodic_channel(event, note_on)
    else:
        mapped = _FPC_MAP.get(note)
        if mapped is None:
            return
        event.data1 = max(0, min(127, mapped + bank * 16))
        # Stay on channel 10 for GM drums


def _apply_pad_velocity(event, note_on_before_transpose):
    """When velocity is off, pad Note-On uses fixed 75% strength."""
    if not note_on_before_transpose or event.data2 <= 0:
        return
    if not pad_state.get_pad_velocity_enabled():
        event.data2 = _PAD_VELOCITY_FIXED


def OnInit():
    print("### INIT KeyLab mkII Forward (Port 0) ###")
    print("### Pad mode: %s (file+sys sync) ###" % pad_state.get_pad_mode())


def OnDeInit():
    return


def OnMidiIn(event):
    """Intercept before FL processing."""
    if _is_pad_note_event(event):
        old_note = event.data1
        old_status = event.status
        note_on = event.status == _NOTE_ON_CH10 and event.data2 > 0
        _transpose_pad(event)
        _apply_pad_velocity(event, note_on)
        if _DEBUG_PADS:
            print("Pad: mode=%s bank=%d vel=%s ch=%d note %d->%d vel=%d status %d->%d" % (
                pad_state.get_pad_mode(),
                pad_state.get_pad_bank_offset(),
                "on" if pad_state.get_pad_velocity_enabled() else "off",
                event.midiChan,
                old_note, event.data1,
                event.data2,
                old_status, event.status))

    focused_plugin = ui.getFocusedPluginName()
    is_vcol = focused_plugin in V_COLLECTION

    if (event.status == midi.MIDI_CONTROLCHANGE and is_vcol) or event.status == 0xE0:
        msg = event.status + (event.data1 << 8) + (event.data2 << 16) + (10 << 24)
        device.forwardMIDICC(msg, 2)

    event.handled = False


def OnMidiMsg(event):
    event.handled = False
