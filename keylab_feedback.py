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

# Track row (mono) - Hardware labels: Record, Solo, Mute, Read, Write
_LED_TRACK_RECORD = 0x62
_LED_TRACK_SOLO = 0x60
_LED_TRACK_MUTE = 0x61
_LED_TRACK_READ = 0x63
_LED_TRACK_WRITE = 0x64

# Navigation
_LED_NAV_LEFT = 0x1A
_LED_NAV_RIGHT = 0x1B
_LED_JOG_CLICK = 0x54

# Part Prev/Next
_LED_PART_PREV = 0x1F
_LED_PART_NEXT = 0x20

# ---------------------------------------------------------------------------
#  RGB: track buttons (SysEx 0x02 0x00 0x16, id, R, G, B, 0x7F)
# ---------------------------------------------------------------------------
_TRACK_BTN_IDS = [0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]

_BRIGHT_FOCUSED   = 1.0
_BRIGHT_UNFOCUSED = 0.25
_BRIGHT_MUTED     = 0.1

_TRACK_LED_IDLE_MS = 60
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
    """Send RGB SysEx. Hardware range: 0x00-0x1F (32 steps) per channel."""
    r = max(0, min(0x1F, int(r)))
    g = max(0, min(0x1F, int(g)))
    b = max(0, min(0x1F, int(b)))
    key = ('rgb', btn_id)
    payload = bytes([0x02, 0x00, 0x16, btn_id, r, g, b, 0x7F])
    if _rgb_cache.get(key) == payload:
        return
    _rgb_cache[key] = payload
    send_to_device(payload)


def _fl_color_to_rgb(color_int, brightness):
    """FL color int (0xRRGGBB) → RGB 0–0x1F (32 steps) for RGB LED SysEx.
    
    Hardware spec: R/G/B values MUST be 0x00-0x1F (not 0-127!).
    Uncolored tracks (unsaturated greys) are rendered as white.
    """
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF

    # Detect FL's default "no custom color": very low saturation + dark.
    # max(rgb) < 150 and all channels within 25 of each other = grey-ish.
    max_ch = max(r, g, b)
    min_ch = min(r, g, b)
    is_grey = (max_ch - min_ch) < 25 and max_ch < 160
    if is_grey or max_ch == 0:
        r, g, b = 220, 220, 220  # render as white

    # Scale 0-255 -> 0-31 and apply brightness
    dim_r = int((r / 255.0) * 31 * brightness)
    dim_g = int((g / 255.0) * 31 * brightness)
    dim_b = int((b / 255.0) * 31 * brightness)

    # Unfocused tracks: guarantee a minimum floor of 2 (just visible)
    if brightness < 1.0:
        if dim_r < 2 and dim_g < 2 and dim_b < 2:
            if r >= g and r >= b:   dim_r = 2
            elif g >= r and g >= b: dim_g = 2
            else:                   dim_b = 2

    return (
        max(0, min(0x1F, dim_r)),
        max(0, min(0x1F, dim_g)),
        max(0, min(0x1F, dim_b)),
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
    _set_mono(_LED_REWIND, _VAL_ON)
    _set_mono(_LED_FFWD, _VAL_ON)


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
    
    try:
        import general
        if general.getUndoHistoryPos() > 0:
            _mono_always_on(_LED_UNDO)
        else:
            _mono_toggle(_LED_UNDO, False)
    except Exception:
        _mono_always_on(_LED_UNDO)

    _mono_always_on(_LED_TRACK_RECORD)
    _mono_toggle(_LED_TRACK_SOLO, ui.getFocused(midi.widMixer))
    _mono_toggle(_LED_TRACK_MUTE, snap_on)
    _mono_always_on(_LED_TRACK_READ)
    _mono_always_on(_LED_TRACK_WRITE)


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
    """RGB track buttons: muted=10%, unfocused=dim, focused=full FL color.
    
    Bank 0 => Mixer tracks 1-8 (track 0 = Master, not on these 8 buttons).
    Bank 0 => Channels 0-7.
    Uncolored tracks show white.
    """
    try:
        if ui.getFocused(midi.widMixer):
            count = mixer.getTrackCount()
            base_track = state.bank_offset * 8
            selected = mixer.trackNumber()
            for i in range(8):
                btn_id = _TRACK_BTN_IDS[i]
                # Mixer tracks are 1-indexed for the 8 faders (Master is 0, on fader 9)
                track_idx = base_track + i + 1
                if track_idx >= count:
                    _send_rgb(btn_id, 0, 0, 0)
                    continue
                if mixer.isTrackMuted(track_idx):
                    bright = _BRIGHT_MUTED
                else:
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
                # Channels are 0-indexed
                ch_idx = base_ch + i
                if ch_idx >= ch_count:
                    _send_rgb(btn_id, 0, 0, 0)
                    continue
                if channels.isChannelMuted(ch_idx):
                    bright = _BRIGHT_MUTED
                else:
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
                return True
        else:
            ch = channels.channelNumber()
            if (ch != state.last_led_channel
                    or bank != state.last_led_bank_offset):
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


def update_refresh_feedback(state, flags=0):
    """Lighter OnRefresh: transport + DAW toggles; always schedule track RGB update."""
    update_transport_leds()
    update_daw_command_leds()
    if state is None:
        return
    # Always schedule a track LED update — jog scrolling triggers OnRefresh
    # without specific dirty flags, so we can't filter by flags here.
    state.force_track_led_update = True


def tick_feedback_idle(state):
    """Refresh track-button RGB only when selection or bank changes."""
    global _last_track_led_ms
    if state is None:
        return
        
    needs_update = _selection_changed(state) or getattr(state, 'force_track_led_update', False)
    if not needs_update:
        return
        
    now_ms = time.monotonic() * 1000.0
    if now_ms - _last_track_led_ms < _TRACK_LED_IDLE_MS:
        return
        
    _last_track_led_ms = now_ms
    state.force_track_led_update = False
    update_track_button_leds(state)


def flush_track_leds_if_ready(state):
    """Called explicitly by fast actions (e.g. jog wheel) to bypass OnIdle GUI lag."""
    global _last_track_led_ms
    now_ms = time.monotonic() * 1000.0
    if now_ms - _last_track_led_ms >= _TRACK_LED_IDLE_MS:
        _last_track_led_ms = now_ms
        if getattr(state, 'force_track_led_update', False):
            state.force_track_led_update = False
        update_track_button_leds(state)


def clear_all_leds():
    """Turn off all LEDs (used in OnDeInit)."""
    global _static_mono_inited
    _mono_cache.clear()
    _rgb_cache.clear()
    _static_mono_inited = False
    send_to_device(bytes([0x02, 0x7D, 0x7D, 0x0B, 0x00]))
