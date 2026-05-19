# KeyLab mkII — Pad RGB LEDs (Keys port; press/release + mode idle)
# See CONTROLLER_RULES.md — LED slot = Pad.NOTES index (keylab_config)

import keylab_shared_state as pad_state
from keylab_config import Pad
from keylab_dispatch import send_to_device

_COLOR_CHROMATIC = (127, 127, 127)
_COLOR_DRUM_MAP = (127, 0, 127)

_BRIGHT_IDLE = 0.5

_pad_rgb_cache = {}


def pad_index_from_note(note):
    """Physical RGB LED slot for native pad MIDI note."""
    pad_slot = Pad.NOTE_TO_SLOT.get(note)
    if pad_slot is None:
        return None
    return Pad.NOTE_TO_LED_SLOT.get(note, Pad.slot_to_led_slot(pad_slot))


def _mode_colors():
    if pad_state.get_pad_mode() == pad_state.PAD_MODE_CHROMATIC:
        return _COLOR_CHROMATIC
    return _COLOR_DRUM_MAP


def _rgb_for_velocity(velocity):
    """Idle 50%; pressed scales linearly to 100% at velocity 127."""
    full_r, full_g, full_b = _mode_colors()
    dim_r = int(full_r * _BRIGHT_IDLE)
    dim_g = int(full_g * _BRIGHT_IDLE)
    dim_b = int(full_b * _BRIGHT_IDLE)
    if velocity <= 0:
        return dim_r, dim_g, dim_b
    ratio = min(127, max(1, int(velocity))) / 127.0
    return (
        max(0, min(127, int(dim_r + (full_r - dim_r) * ratio))),
        max(0, min(127, int(dim_g + (full_g - dim_g) * ratio))),
        max(0, min(127, int(dim_b + (full_b - dim_b) * ratio))),
    )


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


def set_pad_color(pad_index, velocity):
    """Set one pad LED; velocity 0 = idle (50%), else 50%–100% by velocity."""
    if pad_index is None:
        return
    r, g, b = _rgb_for_velocity(velocity)
    _send_pad_rgb(pad_index, r, g, b)


def refresh_all_pads_idle():
    """All pads at idle brightness for current pad mode."""
    for i in range(Pad.COUNT):
        set_pad_color(i, 0)


def clear_pad_leds():
    """Turn off all pad RGB LEDs."""
    _pad_rgb_cache.clear()
    for pad_id in Pad.LED_IDS:
        send_to_device(bytes([0x02, 0x00, 0x16, pad_id, 0, 0, 0, 0x7F]))
