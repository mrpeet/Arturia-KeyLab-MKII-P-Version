# KeyLab mkII — LED & Pad Feedback
# Handles: Transport LEDs, Beat indicator, Track button colors, Pad colors
# Phase 5: Transport LEDs — Phase 8+: Track/Pad colors (see ROADMAP.md)

import transport
import ui

from keylab_dispatch import send_to_device


# ---------------------------------------------------------------------------
#  SysEx LED IDs — Transport buttons
#  Format: send_to_device(bytes([0x02, 0x00, 0x10, <LED_ID>, <VALUE>]))
#  VALUE: 0x7F = full on, 0x14 = dim, 0x00 = off, 0x09 = very dim
# ---------------------------------------------------------------------------
_LED_REWIND  = 0x6A
_LED_FFWD    = 0x6B
_LED_STOP    = 0x6C
_LED_PLAY    = 0x6D
_LED_RECORD  = 0x6E
_LED_LOOP    = 0x6F

_VAL_ON  = 0x7F
_VAL_DIM = 0x14
_VAL_OFF = 0x09

# Cache to avoid redundant SysEx sends
_led_cache = {}


# ---------------------------------------------------------------------------
#  Transport LED sync
# ---------------------------------------------------------------------------

def update_transport_leds(beat_value=None):
    """Sync transport button LEDs to current FL Studio state.

    Args:
        beat_value: If provided (from OnUpdateBeatIndicator), blink play/record
                    LEDs on beat. 0=off, 1=beat, 2=bar.
    """
    is_playing = transport.isPlaying()
    is_recording = transport.isRecording()
    is_loop = ui.isLoopRecEnabled()

    # --- Play LED ---
    if beat_value is not None and is_playing:
        # Blink: on for beat/bar, off between
        _set_led(_LED_PLAY, _VAL_ON if beat_value > 0 else _VAL_DIM)
    else:
        _set_led(_LED_PLAY, _VAL_ON if is_playing else _VAL_DIM)

    # --- Stop LED ---
    _set_led(_LED_STOP, _VAL_ON if not is_playing else _VAL_DIM)

    # --- Record LED ---
    if beat_value is not None and is_recording:
        # Blink record LED on beat
        _set_led(_LED_RECORD, _VAL_ON if beat_value > 0 else _VAL_OFF)
    else:
        _set_led(_LED_RECORD, _VAL_ON if is_recording else _VAL_OFF)

    # --- Loop LED ---
    _set_led(_LED_LOOP, _VAL_ON if is_loop else _VAL_OFF)

    # --- Rewind / FastForward: always dim (no state to reflect) ---
    _set_led(_LED_REWIND, _VAL_DIM)
    _set_led(_LED_FFWD, _VAL_DIM)


# ---------------------------------------------------------------------------
#  Low-level LED control (cached)
# ---------------------------------------------------------------------------

def _set_led(led_id, value):
    """Send a single-LED SysEx command, skipping if value unchanged."""
    if _led_cache.get(led_id) == value:
        return
    _led_cache[led_id] = value
    send_to_device(bytes([0x02, 0x00, 0x10, led_id, value]))


def clear_all_leds():
    """Turn off all LEDs (used in OnDeInit)."""
    _led_cache.clear()
    send_to_device(bytes([0x02, 0x7D, 0x7D, 0x0B, 0x00]))
