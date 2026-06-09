# KeyLab mkII — Pad RGB LEDs (Keys port)
#
# Design:
#   - Pads are always colored by the active pad mode (Chromatic=cyan, Drum=magenta).
#   - Idle brightness: ~50% (0x0F of 0x1F max).
#   - Note On:      brightness = velocity-proportional (0 → 0x1F).
#   - Aftertouch:   brightness = pressure-proportional (0 → 0x1F).
#   - Note Off:     immediately restore idle brightness (overrides MCC reset).
#   - Mode change / Init: all 16 pads set to mode color at idle brightness.
#   - Animation:    C/D letter fade-out on mode switch; only pattern pads are
#                   written; non-pattern pads keep their idle mode color.
#
# MCC-proof strategy:
#   The hardware resets a pad's LED to MCC color on every Note Off.
#   We intercept Note Off in OnMidiIn (before FL Studio processes it) and
#   immediately re-send the script color, overwriting the MCC state.
#   Same trick is applied on Aftertouch to prevent mid-pressure flickering.

import time

import keylab_shared_state as pad_state
from keylab_config import Pad
from keylab_dispatch import send_to_device

# ---------------------------------------------------------------------------
#  Mode colors (0x00-0x1F range, 5-bit per channel for Arturia LED SysEx)
# ---------------------------------------------------------------------------
_COLOR_CHROMATIC = (0, 20, 20)   # Dim cyan  (full = 0x1F each)
_COLOR_DRUM_MAP  = (20, 0, 20)   # Dim magenta

# Maximum brightness (0x1F = 31 = max for Arturia RGB SysEx)
_MAX = 0x1F

# Idle brightness fraction (applied to _COLOR_* for resting state)
_IDLE_FRACTION = 0.5

# ---------------------------------------------------------------------------
#  LED cache — keyed by physical LED slot index (0-15)
# ---------------------------------------------------------------------------
_pad_rgb_cache = {}


# ---------------------------------------------------------------------------
#  Animation state
# ---------------------------------------------------------------------------
_ANIMATION_DURATION_MS = 1500.0
_animation_start_ms    = 0.0
_animation_active      = False
_animation_pattern     = []
_animation_color       = (0, 0, 0)

# 4x4 matrix indices (0-15, left-to-right, top-to-bottom)
_PATTERN_C = [1, 2, 4, 8, 13, 14]    # 'C' for Chromatic
_PATTERN_D = [0, 1, 4, 6, 8, 10, 12, 13]  # 'D' for Drum


# ---------------------------------------------------------------------------
#  Internal: low-level send (cached)
# ---------------------------------------------------------------------------

def _send_pad_rgb(led_slot, r, g, b):
    """Send RGB SysEx to one pad (by physical LED slot 0-15). Cached."""
    if led_slot < 0 or led_slot > 15:
        return
    pad_id = Pad.LED_IDS[led_slot]
    payload = bytes([0x02, 0x00, 0x16, pad_id, r, g, b, 0x7F])
    if _pad_rgb_cache.get(led_slot) == payload:
        return
    _pad_rgb_cache[led_slot] = payload
    send_to_device(payload)


def _mode_color_at(fraction):
    """Return (r, g, b) for current pad mode scaled by fraction (0.0-1.0)."""
    mode = pad_state.get_pad_mode()
    base = _COLOR_CHROMATIC if mode == pad_state.PAD_MODE_CHROMATIC else _COLOR_DRUM_MAP
    r = int(base[0] * fraction * (_MAX / 20))
    g = int(base[1] * fraction * (_MAX / 20))
    b = int(base[2] * fraction * (_MAX / 20))
    return (
        max(0, min(_MAX, r)),
        max(0, min(_MAX, g)),
        max(0, min(_MAX, b)),
    )


# ---------------------------------------------------------------------------
#  Public: full-board idle color
# ---------------------------------------------------------------------------

def set_all_pads_idle():
    """Set all 16 pads to mode color at idle brightness.

    Called on script init, lazy init, and after a mode change animation ends.
    Clears cache first so every pad is unconditionally written.
    """
    _pad_rgb_cache.clear()
    r, g, b = _mode_color_at(_IDLE_FRACTION)
    for led_slot in range(16):
        _send_pad_rgb(led_slot, r, g, b)


# ---------------------------------------------------------------------------
#  Public: per-event pad LED updates (call from OnMidiIn before transpose)
# ---------------------------------------------------------------------------

def on_pad_note_on(note, velocity):
    """Velocity-proportional brightness on Note On.

    velocity: 0-127 from hardware.
    """
    led_slot = Pad.NOTE_TO_LED_SLOT.get(note)
    if led_slot is None:
        return
    # Velocity 0-127 → brightness 0.0-1.0
    frac = velocity / 127.0
    r, g, b = _mode_color_at(frac)
    # Force send (bypass cache) so this always reaches the hardware
    _pad_rgb_cache.pop(led_slot, None)
    _send_pad_rgb(led_slot, r, g, b)


def on_pad_note_off(note):
    """Immediately restore idle brightness on Note Off.

    This outruns the hardware's MCC-restore triggered by the Note Off event.
    """
    led_slot = Pad.NOTE_TO_LED_SLOT.get(note)
    if led_slot is None:
        return
    r, g, b = _mode_color_at(_IDLE_FRACTION)
    # Force send so we always beat the hardware MCC reset
    _pad_rgb_cache.pop(led_slot, None)
    _send_pad_rgb(led_slot, r, g, b)


def on_pad_aftertouch(note, pressure):
    """Pressure-proportional brightness on Poly Aftertouch.

    Also prevents MCC-color flicker during sustained pressure.
    pressure: 0-127.
    """
    led_slot = Pad.NOTE_TO_LED_SLOT.get(note)
    if led_slot is None:
        return
    # Keep at least idle brightness so pad never goes dark while held
    frac = max(_IDLE_FRACTION, pressure / 127.0)
    r, g, b = _mode_color_at(frac)
    _pad_rgb_cache.pop(led_slot, None)
    _send_pad_rgb(led_slot, r, g, b)


# ---------------------------------------------------------------------------
#  Public: animation (mode switch visual feedback)
# ---------------------------------------------------------------------------

def trigger_mode_animation(mode):
    """Start a C/D letter fade-out animation on the pads.

    Non-pattern pads are not touched (they keep their idle mode color).
    """
    global _animation_start_ms, _animation_active, _animation_pattern, _animation_color

    if mode == pad_state.PAD_MODE_CHROMATIC:
        _animation_pattern = list(_PATTERN_C)
        _animation_color   = (0, _MAX, _MAX)   # Full cyan
    else:
        _animation_pattern = list(_PATTERN_D)
        _animation_color   = (_MAX, 0, _MAX)   # Full magenta

    # Invalidate cache for pattern pads so first frame always fires
    for i in _animation_pattern:
        led_slot = Pad.slot_to_led_slot(i)
        _pad_rgb_cache.pop(led_slot, None)

    _animation_start_ms = time.monotonic() * 1000.0
    _animation_active   = True
    tick_animation()  # Draw first frame immediately


def tick_animation():
    """Called in OnIdle. Updates the fade-out; restores idle color when done."""
    global _animation_active

    if not _animation_active:
        return

    elapsed = (time.monotonic() * 1000.0) - _animation_start_ms

    if elapsed >= _ANIMATION_DURATION_MS:
        _animation_active = False
        # Restore only the pattern pads to idle color.
        # Non-pattern pads were never overwritten by the animation.
        r_idle, g_idle, b_idle = _mode_color_at(_IDLE_FRACTION)
        for i in _animation_pattern:
            led_slot = Pad.slot_to_led_slot(i)
            _pad_rgb_cache.pop(led_slot, None)
            _send_pad_rgb(led_slot, r_idle, g_idle, b_idle)
        return

    ratio = 1.0 - (elapsed / _ANIMATION_DURATION_MS)
    r = int(_animation_color[0] * ratio)
    g = int(_animation_color[1] * ratio)
    b = int(_animation_color[2] * ratio)

    for i in _animation_pattern:
        led_slot = Pad.slot_to_led_slot(i)
        _send_pad_rgb(led_slot, r, g, b)


# ---------------------------------------------------------------------------
#  Public: cleanup
# ---------------------------------------------------------------------------

def clear_pad_leds():
    """Turn off all pad RGB LEDs (used in OnDeInit)."""
    _pad_rgb_cache.clear()
    for pad_id in Pad.LED_IDS:
        send_to_device(bytes([0x02, 0x00, 0x16, pad_id, 0, 0, 0, 0x7F]))
