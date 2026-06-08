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
_VAL_3_PERCENT = 0x04  # ~3% of 127

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
_MASTER_BTN_ID = 0x2A

_BRIGHT_FOCUSED         = 1.0
_BRIGHT_UNFOCUSED       = 0.25
_BRIGHT_MUTED_FOCUSED   = 0.15
_BRIGHT_MUTED           = 0.01  # Hardware might treat low values as completely off, handled in _fl_color_to_rgb

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


def _boost_saturation(r, g, b, boost=0.65):
    """Boost saturation of an RGB triplet (0-255) so pale FL colors stay
    visually distinct on the hardware LEDs.

    Strategy: normalize so the brightest channel is always 255, then
    lerp between the original normalized color and a fully-saturated
    version (min channel → 0) using *boost* as the blend weight.

      boost = 0.0  → no change (pure normalized color)
      boost = 1.0  → max saturation (darkest channel forced to 0)

    The overall perceived lightness is preserved by the normalization step,
    which is then re-applied by the caller's brightness multiplier.
    """
    max_ch = max(r, g, b)
    if max_ch == 0:
        return r, g, b  # black stays black

    # Normalize so the brightest channel fills the 0-255 range.
    nr = (r / max_ch) * 255.0
    ng = (g / max_ch) * 255.0
    nb = (b / max_ch) * 255.0

    # Fully-saturated version: shift min channel to 0, keep hue.
    min_n = min(nr, ng, nb)
    sr = nr - min_n
    sg = ng - min_n
    sb = nb - min_n
    # Re-normalize saturated version so it still peaks at 255.
    sat_max = max(sr, sg, sb)
    if sat_max > 0:
        sr = (sr / sat_max) * 255.0
        sg = (sg / sat_max) * 255.0
        sb = (sb / sat_max) * 255.0

    # Blend: boosted_color = lerp(normalized, saturated, boost)
    br = nr + (sr - nr) * boost
    bg = ng + (sg - ng) * boost
    bb = nb + (sb - nb) * boost

    return br, bg, bb


def _fl_color_to_rgb(color_int, brightness):
    """FL color int (0xRRGGBB) → RGB 0–0x1F (32 steps) for RGB LED SysEx.

    Hardware spec: R/G/B values MUST be 0x00-0x1F (not 0-127!).
    Uncolored tracks (unsaturated greys) are rendered as white.
    Pale FL colors are saturation-boosted so they remain visually distinct
    on the LED hardware (see _boost_saturation).
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
    else:
        # Boost saturation so pale colors still read as distinct hues on LEDs.
        # 0.65 = strong boost without making every color look neon.
        r, g, b = _boost_saturation(r, g, b, boost=0.65)

    # Scale 0-255 -> 0-31 and apply brightness
    dim_r = int((r / 255.0) * 31 * brightness)
    dim_g = int((g / 255.0) * 31 * brightness)
    dim_b = int((b / 255.0) * 31 * brightness)

    # Unfocused tracks: guarantee a minimum floor of 2 (just visible)
    if brightness < 1.0:
        if dim_r < 2 and dim_g < 2 and dim_b < 2:
            if brightness == _BRIGHT_MUTED:
                # Muted: absolutely darkest visible state (1)
                floor = 1
            else:
                # Unfocused: dim but clearly visible (2)
                floor = 2

            if r > 0 and r >= g and r >= b: dim_r = floor
            if g > 0 and g >= r and g >= b: dim_g = floor
            if b > 0 and b >= r and b >= g: dim_b = floor

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
        _set_mono(_LED_RECORD, _VAL_ON if beat_value > 0 else _VAL_3_PERCENT)
    else:
        _set_mono(_LED_RECORD, _VAL_ON if is_recording else _VAL_3_PERCENT)

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

def update_daw_command_leds(state=None):
    """Toggle states: 30% off / 100% on; mode/action buttons: always 100%.

    state: optional KeyLabState — used to read overdub_enabled (FL has no getter).
    """
    _set_mono(_LED_METRO, _VAL_ON if ui.isMetronomeEnabled() else _VAL_3_PERCENT)
    # Overdub: On=100%, Off=~3%. We track this ourselves since FL has no getter.
    if state is not None:
        _set_mono(_LED_OUT, _VAL_ON if state.overdub_enabled else _VAL_3_PERCENT)
    # else: leave OUT LED as-is (no state available, avoid guessing)

    _mono_always_on(_LED_SAVE)
    _mono_always_on(_LED_IN)
    
    try:
        import general
        if general.getUndoHistoryPos() > 0:
            _set_mono(_LED_UNDO, 127) # 100%
        else:
            _set_mono(_LED_UNDO, 89)  # ~70%
    except Exception:
        _mono_always_on(_LED_UNDO)

    try:
        # Record button LED reflects whether Snap is enabled (not 'None'/3)
        is_snap = (ui.getSnapMode() != 3)
        _mono_toggle(_LED_TRACK_RECORD, is_snap)
        
        # Solo button represents NewPattern (one-shot, always on)
        _mono_always_on(_LED_TRACK_SOLO)
        
        # Mute button toggles Piano Roll: 100% open / 3% closed
        _set_mono(_LED_TRACK_MUTE, _VAL_ON if ui.getFocused(midi.widPianoRoll) else _VAL_3_PERCENT)
    except Exception:
        pass

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
                is_selected = (track_idx == selected)
                if mixer.isTrackMuted(track_idx):
                    bright = _BRIGHT_MUTED_FOCUSED if is_selected else _BRIGHT_MUTED
                else:
                    bright = _BRIGHT_FOCUSED if is_selected else _BRIGHT_UNFOCUSED
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
                is_selected = (ch_idx == selected)
                if channels.isChannelMuted(ch_idx):
                    bright = _BRIGHT_MUTED_FOCUSED if is_selected else _BRIGHT_MUTED
                else:
                    bright = _BRIGHT_FOCUSED if is_selected else _BRIGHT_UNFOCUSED
                col = channels.getChannelColor(ch_idx)
                r, g, b = _fl_color_to_rgb(col, bright)
                _send_rgb(btn_id, r, g, b)
                
        # Master track (Track 0) is ALWAYS on the Multi button (0x2A), regardless of window focus
        try:
            master_muted = mixer.isTrackMuted(0)
            master_selected = mixer.trackNumber() == 0 and ui.getFocused(midi.widMixer)
            if master_muted:
                bright = _BRIGHT_MUTED_FOCUSED if master_selected else _BRIGHT_MUTED
            else:
                bright = _BRIGHT_FOCUSED if master_selected else _BRIGHT_UNFOCUSED
            col = mixer.getTrackColor(0)
            r, g, b = _fl_color_to_rgb(col, bright)
            _send_rgb(_MASTER_BTN_ID, r, g, b)
        except Exception:
            pass
            
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
    update_daw_command_leds(state)
    if state is not None:
        update_track_button_leds(state)


def update_refresh_feedback(state, flags=0):
    """Lighter OnRefresh: transport + DAW toggles; always schedule track RGB update."""
    update_transport_leds()
    update_daw_command_leds(state)
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


def clear_led_caches():
    """Clear LED caches to force a full hardware update on the next feedback pass."""
    global _static_mono_inited
    _mono_cache.clear()
    _rgb_cache.clear()
    _static_mono_inited = False

def clear_all_leds():
    """Turn off all LEDs (used in OnDeInit)."""
    clear_led_caches()
    send_to_device(bytes([0x02, 0x7D, 0x7D, 0x0B, 0x00]))
