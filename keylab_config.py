# KeyLab mkII — Hardware Constants
# Source of truth: hardware_map.md
# All values verified against physical MIDI data in MCU/DAW mode.


# ---------------------------------------------------------------------------
#  Transport (DAW Port · Note On · Channel 1)
# ---------------------------------------------------------------------------
class Transport:
    REWIND      = 91
    FAST_FWD    = 92
    STOP        = 93
    PLAY        = 94
    RECORD      = 95
    LOOP        = 86

    ALL_NOTES = [REWIND, FAST_FWD, STOP, PLAY, RECORD, LOOP]


# ---------------------------------------------------------------------------
#  DAW Commands — Track Controls (DAW Port · Note On · Channel 1)
# ---------------------------------------------------------------------------
class TrackControl:
    RECORD  = 0
    SOLO    = 8
    MUTE    = 16
    READ    = 74
    WRITE   = 75

    ALL_NOTES = [RECORD, SOLO, MUTE, READ, WRITE]


# ---------------------------------------------------------------------------
#  DAW Commands — Global Controls (DAW Port · Note On · Channel 1)
# ---------------------------------------------------------------------------
class GlobalControl:
    SAVE    = 80
    IN      = 87   # Short: TogglePadMode; Long: TogglePadVelocity
    OUT     = 88   # ToggleOverdub
    METRO   = 89
    UNDO    = 81

    ALL_NOTES = [SAVE, IN, OUT, METRO, UNDO]


# ---------------------------------------------------------------------------
#  Navigation (DAW Port)
# ---------------------------------------------------------------------------
class Navigation:
    JOG_WHEEL_CC    = 60   # CC: right=1, left=65
    JOG_WHEEL_CLICK = 84   # Note On
    BANK_LEFT       = 98   # Note On
    BANK_RIGHT      = 99   # Note On

    ALL_NOTES = [JOG_WHEEL_CLICK, BANK_LEFT, BANK_RIGHT]


# ---------------------------------------------------------------------------
#  Mixer — Fader (DAW Port · Pitch Bend · Channels 1–9)
#  Pitch Bend status bytes: 0xE0–0xE8
# ---------------------------------------------------------------------------
class Fader:
    # Pitch Bend channels (0-indexed internally, 1-indexed in hardware_map)
    CHANNEL_1 = 0   # 0xE0
    CHANNEL_2 = 1   # 0xE1
    CHANNEL_3 = 2   # 0xE2
    CHANNEL_4 = 3   # 0xE3
    CHANNEL_5 = 4   # 0xE4
    CHANNEL_6 = 5   # 0xE5
    CHANNEL_7 = 6   # 0xE6
    CHANNEL_8 = 7   # 0xE7
    CHANNEL_9 = 8   # 0xE8 (Master)

    MASTER_CHANNEL = 8
    COUNT = 9

    ALL_CHANNELS = list(range(COUNT))

    # Touch sensor Note On values (DAW Port · Channel 1)
    TOUCH_1  = 104
    TOUCH_2  = 105
    TOUCH_3  = 106
    TOUCH_4  = 107
    TOUCH_5  = 108
    TOUCH_6  = 109
    TOUCH_7  = 110
    TOUCH_8  = 111
    TOUCH_9  = 112  # Master

    ALL_TOUCH_NOTES = list(range(TOUCH_1, TOUCH_9 + 1))


# ---------------------------------------------------------------------------
#  Mixer — Encoder (DAW Port · CC · Relative: right=1, left=65)
# ---------------------------------------------------------------------------
class Encoder:
    ENC_1 = 16
    ENC_2 = 17
    ENC_3 = 18
    ENC_4 = 19
    ENC_5 = 20
    ENC_6 = 21
    ENC_7 = 22
    ENC_8 = 23
    ENC_9 = 24  # Master

    FIRST = 16
    LAST  = 24
    COUNT = 9

    ALL_CCS = list(range(FIRST, LAST + 1))

    # Relative encoder direction detection
    # 0–63 = increment (right), 64–127 = decrement (left)
    INCREMENT_MIN = 1
    INCREMENT_MAX = 63
    DECREMENT_MIN = 64
    DECREMENT_MAX = 127
    DECREMENT_BASE = 64
    # Legacy constants for simple checks
    INCREMENT = 1
    DECREMENT = 65


# ---------------------------------------------------------------------------
#  Mixer — Track Buttons (DAW Port · Note On)
# ---------------------------------------------------------------------------
class TrackButton:
    BTN_1 = 24
    BTN_2 = 25
    BTN_3 = 26
    BTN_4 = 27
    BTN_5 = 28
    BTN_6 = 29
    BTN_7 = 30
    BTN_8 = 31
    BTN_9 = 32

    FIRST = 24
    LAST  = 32
    COUNT = 9

    ALL_NOTES = list(range(FIRST, LAST + 1))


# ---------------------------------------------------------------------------
#  Mixer — Bank / Part Buttons (DAW Port · Note On)
# ---------------------------------------------------------------------------
class BankButton:
    PART2_PREV = 48
    PART1_NEXT = 49

    ALL_NOTES = [PART2_PREV, PART1_NEXT]


# ---------------------------------------------------------------------------
#  Mixer — Live/Bank Modifier Buttons (DAW Port · Note On)
#  When Live/Bank is held, Part 2/1 send different notes for pad bank navigation
# ---------------------------------------------------------------------------
class LiveBankButton:
    PREV = 46  # Live/Bank + Part 2
    NEXT = 47  # Live/Bank + Part 1

    ALL_NOTES = [PREV, NEXT]


# ---------------------------------------------------------------------------
#  Pads (Keys Port · Channel 10 · Note On + Poly Aftertouch)
#  Physical layout (top-left = Pad 1):
#    Pad 1 (48)  Pad 2 (49)  Pad 3 (50)  Pad 4 (51)
#    Pad 5 (44)  Pad 6 (45)  Pad 7 (46)  Pad 8 (47)
#    Pad 9 (40)  Pad 10(41)  Pad 11(42)  Pad 12(43)
#    Pad 13(36)  Pad 14(37)  Pad 15(38)  Pad 16(39)
# ---------------------------------------------------------------------------
class Pad:
    PAD_CHANNEL = 9  # 0-indexed = MIDI channel 10

    # Note numbers in physical order (Pad 1–16)
    NOTES = [
        48, 49, 50, 51,  # Row 1 (top)
        44, 45, 46, 47,  # Row 2
        40, 41, 42, 43,  # Row 3
        36, 37, 38, 39,  # Row 4 (bottom)
    ]

    FIRST = 36
    LAST  = 51
    COUNT = 16


# ---------------------------------------------------------------------------
#  Performance — Keys Port (Channel 1)
# ---------------------------------------------------------------------------
class Performance:
    PITCH_BEND_DATA1 = 80  # Pitch Bend on channel 1
    MOD_WHEEL_CC     = 1   # CC 1 on channel 1


# ---------------------------------------------------------------------------
#  Pedals (Keys Port · Channel 1 · CC)
# ---------------------------------------------------------------------------
class Pedal:
    SUSTAIN    = 64
    EXPRESSION = 11
    AUX_1      = 12
    AUX_2      = 13
    AUX_3      = 14

    ALL_CCS = [SUSTAIN, EXPRESSION, AUX_1, AUX_2, AUX_3]


# ---------------------------------------------------------------------------
#  SysEx — Arturia manufacturer prefix
# ---------------------------------------------------------------------------
SYSEX_HEADER = bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42])
SYSEX_FOOTER = bytes([0xF7])


# ---------------------------------------------------------------------------
#  MIDI helpers
# ---------------------------------------------------------------------------
NOTE_ON_STATUS  = 0x90  # 144
NOTE_OFF_STATUS = 0x80  # 128
CC_STATUS       = 0xB0  # 176
PITCH_BEND_STATUS = 0xE0  # 224

PRESSED  = 127
RELEASED = 0
