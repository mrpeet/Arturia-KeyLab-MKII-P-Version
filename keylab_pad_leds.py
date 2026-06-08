# KeyLab mkII — Pad RGB LEDs (Keys port; press/release + mode idle)
# See CONTROLLER_RULES.md — LED slot = Pad.NOTES index (keylab_config)

import keylab_shared_state as pad_state
from keylab_config import Pad
from keylab_dispatch import send_to_device

import time
import keylab_shared_state as pad_state
from keylab_config import Pad
from keylab_dispatch import send_to_device

_COLOR_CHROMATIC = (0, 127, 127)  # Cyan for Chromatic
_COLOR_DRUM_MAP = (127, 0, 127)   # Magenta for Drum

_pad_rgb_cache = {}

# Animation state
_ANIMATION_DURATION_MS = 1500.0
_animation_start_ms = 0.0
_animation_active = False
_animation_pattern = []
_animation_color = (0, 0, 0)

# 4x4 matrix indices (0-15, left-to-right, top-to-bottom)
# Pattern for 'C' (Chromatic)
_PATTERN_C = [1, 2, 4, 8, 13, 14]
# Pattern for 'D' (Drum)
_PATTERN_D = [0, 1, 4, 6, 8, 10, 12, 13]


def _send_pad_rgb(pad_index, r, g, b):
    if pad_index is None or pad_index < 0 or pad_index > 15:
        return
    pad_id = Pad.LED_IDS[pad_index]
    payload = bytes([0x02, 0x00, 0x16, pad_id, r, g, b, 0x7F])
    key = pad_index
    if _pad_rgb_cache.get(key) == payload:
        return
    _pad_rgb_cache[key] = payload
    send_to_device(payload)


def clear_pad_leds():
    """Turn off all pad RGB LEDs."""
    _pad_rgb_cache.clear()
    for pad_id in Pad.LED_IDS:
        send_to_device(bytes([0x02, 0x00, 0x16, pad_id, 0, 0, 0, 0x7F]))


def restore_mcc_pads():
    """Restore pads to their default MCC color at idle brightness."""
    _pad_rgb_cache.clear()
    for pad_id in Pad.LED_IDS:
        # Sending the monochrome command (0x10) to a pad restores its 
        # MCC-defined color. 0x2A is ~33% brightness (idle state).
        send_to_device(bytes([0x02, 0x00, 0x10, pad_id, 0x2A]))


def trigger_mode_animation(mode):
    """Start a C/D shape fade-out animation on the pads."""
    global _animation_start_ms, _animation_active, _animation_pattern, _animation_color
    
    _animation_start_ms = time.monotonic() * 1000.0
    _animation_active = True
    
    if mode == pad_state.PAD_MODE_CHROMATIC:
        _animation_pattern = _PATTERN_C
        _animation_color = _COLOR_CHROMATIC
    else:
        _animation_pattern = _PATTERN_D
        _animation_color = _COLOR_DRUM_MAP
        
    # Clear any existing state
    clear_pad_leds()
    tick_animation()  # Initial draw


def tick_animation():
    """Called in OnIdle to update the animation fade-out."""
    global _animation_active
    
    if not _animation_active:
        return
        
    now_ms = time.monotonic() * 1000.0
    elapsed = now_ms - _animation_start_ms
    
    if elapsed >= _ANIMATION_DURATION_MS:
        _animation_active = False
        restore_mcc_pads()
        return
        
    # Calculate fade ratio (1.0 to 0.0)
    ratio = 1.0 - (elapsed / _ANIMATION_DURATION_MS)
    
    r = int(_animation_color[0] * ratio)
    g = int(_animation_color[1] * ratio)
    b = int(_animation_color[2] * ratio)
    
    for i in range(16):
        if i in _animation_pattern:
            # We must map the logical index (0-15) to the physical LED slot
            # Pad indices are 0-15 left to right, top to bottom.
            # slot_to_led_slot handles the vertical flip
            led_slot = Pad.slot_to_led_slot(i)
            _send_pad_rgb(led_slot, r, g, b)
        else:
            led_slot = Pad.slot_to_led_slot(i)
            _send_pad_rgb(led_slot, 0, 0, 0)
