# KeyLab mkII — Central State
# The ONLY place where mutable global state lives.
# All handler modules read/write state through this object.

from keylab_config import Fader
import keylab_shared_state


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
        # pad_mode, pad_bank_offset, pad_bank_count are delegated to
        # keylab_shared_state via @property below (cross-port sharing with
        # device_KeyLabmkII_Forward.py which performs the actual transposition).

        # --- Track buttons ---
        self.track_button_mode = TrackButtonMode.SELECT

        # --- Free mode ---
        # Explicitly activated via Long Press Bank Prev (>1s). NOT auto-deactivated by focus.
        # When True: Fader 1-8, Encoder 1-8, Track Buttons 1-8 pass MIDI through unmodified.
        # Slot 9 (Master) always stays in normal mode.
        # Deactivated by another Long Press Bank Prev.
        self.free_mode = False

        # Free Mode: absolute encoder values (0-127, start at 64=center)
        # Only slots 0-7, slot 8 (master) is always absolute Pitch Bend
        self.free_encoder_values = [64] * 8

        # --- Fader jitter filter ---
        # Minimum delta (14-bit PB range 0–16383) before a fader value is accepted.
        # Filters electrical noise from aging faders without noticeably reducing resolution.
        # ~0.15 % of full range — enough to suppress ±1–2 LSB noise.
        self.FADER_JITTER_THRESHOLD = 1  # Minimal: filters single LSB noise only
        # Last 14-bit value that was actually forwarded to FL Studio, per fader.
        self.fader_last_sent_value = [0] * Fader.COUNT

        # --- Soft pickup ---
        # Per-fader: True once the physical fader has crossed the software value
        self.fader_pickup_active = [False] * Fader.COUNT
        # Last known FL Studio volume per fader slot (0.0–1.0)
        self.fader_last_fl_value = [0.0] * Fader.COUNT

        # --- Fader touch sensor (debounce noisy/stuck capacitive sensors) ---
        self.fader_touch_pressed = [False] * Fader.COUNT
        self.fader_last_touch_ms = [0.0] * Fader.COUNT

        # --- Fader LCD hint throttle (avoid page flicker / "Fader 1" stuck) ---
        self.fader_display_last_index = -1
        self.fader_display_last_ms = 0.0
        # Last line2 actually sent for fader hints (touch name vs %); throttle repeats only
        self.fader_display_last_value_str = None
        # Monotonic ms: last Pitch Bend that passed jitter (ghost touch after move)
        self.fader_last_move_ms = [0.0] * Fader.COUNT
        # Any fader moved (shared `fader` page — cross-slot ghost touch must not win)
        self.fader_last_any_move_ms = 0.0
        # While set, touch-name hints are blocked (value/pickup hint has priority)
        self.fader_value_hint_until_ms = 0.0
        # At physical top: stop setTrackVolume until fader drops (prevents 100% oscillation)
        self.fader_at_ceiling = [False] * Fader.COUNT
        self.fader_last_written_linear = [0.0] * Fader.COUNT

        # --- Plugin mode ---
        self.plugin_fader_hint_until_ms = 0.0

        # --- Track-button LED refresh (only when selection changes) ---
        self.last_led_mixer_track = -1
        self.last_led_channel = -1
        self.last_led_bank_offset = -1

        self.plugin_mode = False       # When True, encoders 1-8 control plugin params
        self.last_plugin_name = ""     # Cache: last detected plugin name
        self.plugin_encoder_values = [0.0] * 8  # Current values for relative encoders

    # ------------------------------------------------------------------
    #  Pad state — delegated to keylab_shared_state for cross-port sharing
    # ------------------------------------------------------------------
    @property
    def pad_mode(self):
        return keylab_shared_state.get_pad_mode()

    @pad_mode.setter
    def pad_mode(self, value):
        keylab_shared_state.set_pad_mode(value)

    @property
    def pad_bank_offset(self):
        return keylab_shared_state.get_pad_bank_offset()

    @pad_bank_offset.setter
    def pad_bank_offset(self, value):
        keylab_shared_state.set_pad_bank_offset(value)

    @property
    def pad_bank_count(self):
        return keylab_shared_state.PAD_BANK_COUNT

    @property
    def pad_velocity_enabled(self):
        return keylab_shared_state.get_pad_velocity_enabled()

    @pad_velocity_enabled.setter
    def pad_velocity_enabled(self, value):
        keylab_shared_state.set_pad_velocity_enabled(value)
