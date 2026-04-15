# KeyLab mkII — Central State
# The ONLY place where mutable global state lives.
# All handler modules read/write state through this object.

from keylab_config import Fader


class FocusMode:
    """Which FL Studio window context drives the fader/encoder section."""
    MIXER   = 'mixer'
    CHANNEL = 'channel'


class PadMode:
    """Pad playing mode."""
    FPC       = 'fpc'
    CHROMATIC = 'chromatic'


class TrackButtonMode:
    """What happens when a track button is pressed."""
    SELECT = 'select'
    SOLO   = 'solo'
    MUTE   = 'mute'


class KeyLabState:
    """Singleton-style state container. Created once in device_KeyLabmkII.py."""

    def __init__(self):
        # --- Focus ---
        self.focus_mode = FocusMode.MIXER

        # --- Banking ---
        self.bank_offset = 0  # Offset for fader/encoder/track-button bank (steps of 8)

        # --- Pads ---
        self.pad_mode = PadMode.FPC

        # --- Track buttons ---
        self.track_button_mode = TrackButtonMode.SELECT

        # --- Free mode ---
        self.free_mode = False  # When True, fader/encoder events are not handled (pass-through)

        # --- Fader jitter filter ---
        # Minimum delta (14-bit PB range 0–16383) before a fader value is accepted.
        # Filters electrical noise from aging faders without noticeably reducing resolution.
        # ~0.15 % of full range — enough to suppress ±1–2 LSB noise.
        self.FADER_JITTER_THRESHOLD = 3
        # Last 14-bit value that was actually forwarded to FL Studio, per fader.
        self.fader_last_sent_value = [0] * Fader.COUNT

        # --- Soft pickup ---
        # Per-fader: True once the physical fader has crossed the software value
        self.fader_pickup_active = [False] * Fader.COUNT
        # Last known FL Studio volume per fader slot (0.0–1.0)
        self.fader_last_fl_value = [0.0] * Fader.COUNT

        # --- Plugin mode ---
        self.plugin_mode = False       # When True, encoders 1-8 control plugin params
        self.last_plugin_name = ""     # Cache: last detected plugin name
        self.plugin_encoder_values = [0.0] * 8  # Current values for relative encoders
