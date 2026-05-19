# KeyLab mkII — LED & Pad Feedback
# See CONTROLLER_RULES.md for brightness and color conventions.

import time

import channels
import mixer
import midi
import transport
import ui

from keylab_dispatch import send_to_device

# ---------------------------------------------------------------------------
#  Monochrome LEDs (SysEx 0x02 0x00 0x10, id, value)
# ---------------------------------------------------------------------------
_VAL_ON = 0x7F
_VAL_DIM = 0x26   # ~30% per CONTROLLER_RULES.md
_VAL_OFF = 0x00

# Transport
_LED_REWIND = 0x6A
_LED_FFWD = 0x6B
_LED_STOP = 0x6C
_LED_PLAY = 0x6D
_LED_RECORD = 0x6E
_LED_LOOP = 0x6F

# Global / DAW (from _archive/KeyLabmk2Return.py — verify on hardware if needed)
_LED_SAVE = 0x65
_LED_IN = 0x66
_LED_OUT = 0x67
_LED_METRO = 0x68
_LED_UNDO = 0x69

# Track row (mono)
_LED_TRACK_NEW_PAT = 0x58
_LED_TRACK_MIXER = 0x59
_LED_TRACK_SNAP = 0x5A
_LED_TRACK_TAP = 0x5B
_LED_TRACK_REDO = 0x5C

# Navigation (archive: note 98/99)
_LED_NAV_LEFT = 0x62
_LED_NAV_RIGHT = 0x63
_LED_JOG_CLICK = 0x54

# Part Prev/Next (DAW notes 48/49) — archive used 0x1A/0x1B for bank/center LEDs
_LED_PART_PREV = 0x1A
_LED_PART_NEXT = 0x1B

# ---------------------------------------------------------------------------
#  RGB: track buttons (SysEx 0x02 0x00 0x16, id, R, G, B, 0x7F)
# ---------------------------------------------------------------------------
_TRACK_BTN_IDS = [24, 25, 26, 27, 28, 29, 30, 31]

_BRIGHT_FOCUSED = 1.0
_BRIGHT_UNFOCUSED = 0.2

_TRACK_LED_IDLE_MS = 80
_last_track_led_ms = 0.0

_mono_cache = {}
_rgb_cache = {}
_static_mono_inited = False

# FL OnRefresh flags (see FL_Studio_API_Reference.md)
_HW_DIRTY_LEDS = 2
_HW_DIRTY_MIXER_CONTROLS = 8


# ---------------------------------------------------------------------------
#  Low-level send (cached)
# ---------------------------------------------------------------------------

def _set_mono(led_id, value):
    if _mono_cache.get(led_id) == value:
        return
    _mono_cache[led_id] = value
    send_to_device(bytes([0x02, 0x00, 0x10, led_id, value]))


def _send_rgb(btn_id, r, g, b):
    r = max(0, min(127, int(r)))
    g = max(0, min(127, int(g)))
    b = max(0, min(127, int(b)))
    key = ('rgb', btn_id)
    payload = bytes([0x02, 0x00, 0x16, btn_id, r, g, b, 0x7F])
    if _rgb_cache.get(key) == payload:
        return
    _rgb_cache[key] = payload
    send_to_device(payload)


def _fl_color_to_rgb(color_int, brightness):
    """FL color int (BGR) → RGB 0–127 with brightness scale."""
    b = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    r = color_int & 0xFF
    return (
        max(0, min(127, int(r * brightness))),
        max(0, min(127, int(g * brightness))),
        max(0, min(127, int(b * brightness))),
    )


def _mono_toggle(led_id, is_on):
    _set_mono(led_id, _VAL_ON if is_on else _VAL_DIM)


def _mono_always_on(led_id):
    _set_mono(led_id, _VAL_ON)


# ---------------------------------------------------------------------------
#  Transport LEDs (existing behaviour + dim rewind/ff)
# ---------------------------------------------------------------------------

def update_transport_leds(beat_value=None):
    """Sync transport button LEDs to current FL Studio state."""
    is_playing = transport.isPlaying()
    is_recording = transport.isRecording()
    is_loop = ui.isLoopRecEnabled()

    if beat_value is not None and is_playing:
        _set_mono(_LED_PLAY, _VAL_ON if beat_value > 0 else _VAL_DIM)
    else:
        _set_mono(_LED_PLAY, _VAL_ON if is_playing else _VAL_DIM)

    _set_mono(_LED_STOP, _VAL_ON if not is_playing else _VAL_DIM)

    if beat_value is not None and is_recording:
        _set_mono(_LED_RECORD, _VAL_ON if beat_value > 0 else _VAL_OFF)
    else:
        _set_mono(_LED_RECORD, _VAL_ON if is_recording else _VAL_OFF)

    _set_mono(_LED_LOOP, _VAL_ON if is_loop else _VAL_DIM)
    _set_mono(_LED_REWIND, _VAL_DIM)
    _set_mono(_LED_FFWD, _VAL_DIM)


def init_static_mono_leds():
    """Nav, jog, Part Prev/Next — set once (not on every OnRefresh)."""
    global _static_mono_inited
    if _static_mono_inited:
        return
    _mono_always_on(_LED_NAV_LEFT)
    _mono_always_on(_LED_NAV_RIGHT)
    _mono_always_on(_LED_JOG_CLICK)
    _mono_always_on(_LED_PART_PREV)
    _mono_always_on(_LED_PART_NEXT)
    _static_mono_inited = True


# ---------------------------------------------------------------------------
#  DAW command buttons (toggle states refresh on OnRefresh)
# ---------------------------------------------------------------------------

def update_daw_command_leds():
    """Toggle states: 30% off / 100% on; mode/action buttons: always 100%."""
    _mono_toggle(_LED_METRO, ui.isMetronomeEnabled())
    try:
        snap_on = ui.getSnapMode() != 3
    except Exception:
        snap_on = bool(ui.getSnapMode())
    _mono_toggle(_LED_TRACK_SNAP, snap_on)
    _mono_toggle(_LED_OUT, ui.isLoopRecEnabled())

    _mono_always_on(_LED_SAVE)
    _mono_always_on(_LED_IN)
    _mono_always_on(_LED_UNDO)

    _mono_always_on(_LED_TRACK_NEW_PAT)
    _mono_toggle(_LED_TRACK_MIXER, ui.getFocused(midi.widMixer))
    _mono_always_on(_LED_TRACK_TAP)
    _mono_always_on(_LED_TRACK_REDO)


# ---------------------------------------------------------------------------
#  Track buttons 1–8 — FL color, brightness by mute/focus
# ---------------------------------------------------------------------------

def _sync_led_selection_cache(state):
    """After a manual track-button LED refresh, avoid duplicate idle tick."""
    try:
        state.last_led_bank_offset = state.bank_offset
        if ui.getFocused(midi.widMixer):
            state.last_led_mixer_track = mixer.trackNumber()
            state.last_led_channel = -1
        else:
            state.last_led_channel = channels.channelNumber()
            state.last_led_mixer_track = -1
    except Exception:
        pass


def update_track_button_leds(state):
    """RGB track buttons: muted=off, unfocused=20%, focused=100% of FL color."""
    try:
        if ui.getFocused(midi.widMixer):
            count = mixer.getTrackCount()
            base_track = state.bank_offset * 8 + 1
            selected = mixer.trackNumber()
            for i in range(8):
                btn_id = _TRACK_BTN_IDS[i]
                track_idx = base_track + i
                if track_idx >= count:
                    _send_rgb(btn_id, 0, 0, 0)
                    continue
                if mixer.isTrackMuted(track_idx):
                    _send_rgb(btn_id, 0, 0, 0)
                    continue
                bright = _BRIGHT_FOCUSED if track_idx == selected else _BRIGHT_UNFOCUSED
                col = mixer.getTrackColor(track_idx)
                r, g, b = _fl_color_to_rgb(col, bright)
                _send_rgb(btn_id, r, g, b)
        else:
            ch_count = channels.channelCount()
            base_ch = state.bank_offset * 8
            selected = channels.channelNumber()
            for i in range(8):
                btn_id = _TRACK_BTN_IDS[i]
                ch_idx = base_ch + i
                if ch_idx >= ch_count:
                    _send_rgb(btn_id, 0, 0, 0)
                    continue
                if channels.isChannelMuted(ch_idx):
                    _send_rgb(btn_id, 0, 0, 0)
                    continue
                bright = _BRIGHT_FOCUSED if ch_idx == selected else _BRIGHT_UNFOCUSED
                col = channels.getChannelColor(ch_idx)
                r, g, b = _fl_color_to_rgb(col, bright)
                _send_rgb(btn_id, r, g, b)
    except Exception:
        pass
    _sync_led_selection_cache(state)


def _selection_changed(state):
    """True if track/channel selection or bank changed since last LED refresh."""
    try:
        bank = state.bank_offset
        if ui.getFocused(midi.widMixer):
            track = mixer.trackNumber()
            if (track != state.last_led_mixer_track
                    or bank != state.last_led_bank_offset):
                state.last_led_mixer_track = track
                state.last_led_bank_offset = bank
                state.last_led_channel = -1
                return True
        else:
            ch = channels.channelNumber()
            if (ch != state.last_led_channel
                    or bank != state.last_led_bank_offset):
                state.last_led_channel = ch
                state.last_led_bank_offset = bank
                state.last_led_mixer_track = -1
                return True
    except Exception:
        pass
    return False


def update_all_feedback(state, beat_value=None):
    """Full LED sync on OnInit (no pad RGB — Forward script only)."""
    update_transport_leds(beat_value)
    init_static_mono_leds()
    update_daw_command_leds()
    if state is not None:
        update_track_button_leds(state)
        _selection_changed(state)


def update_refresh_feedback(state, flags=0):
    """Lighter OnRefresh: transport + DAW toggles; track RGB if mixer dirty."""
    update_transport_leds()
    update_daw_command_leds()
    if state is None:
        return
    if flags & (_HW_DIRTY_MIXER_CONTROLS | _HW_DIRTY_LEDS):
        update_track_button_leds(state)
        _selection_changed(state)


def tick_feedback_idle(state):
    """Refresh track-button RGB only when selection or bank changes."""
    global _last_track_led_ms
    if state is None:
        return
    if not _selection_changed(state):
        return
    now_ms = time.monotonic() * 1000.0
    if now_ms - _last_track_led_ms < _TRACK_LED_IDLE_MS:
        return
    _last_track_led_ms = now_ms
    update_track_button_leds(state)


def clear_all_leds():
    """Turn off all LEDs (used in OnDeInit)."""
    global _static_mono_inited
    _mono_cache.clear()
    _rgb_cache.clear()
    _static_mono_inited = False
    send_to_device(bytes([0x02, 0x7D, 0x7D, 0x0B, 0x00]))
