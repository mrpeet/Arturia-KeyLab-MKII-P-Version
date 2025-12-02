
class Hardware:
    # Group 1: Basic Keyboard Controller
    class Keyboard:
        PITCH_BEND = 0xE0 # Status byte for pitch bend
        MOD_WHEEL = 1     # CC number

    # Group 2: Pads (Channel 10, Note On/Off)
    class Pads:
        CHANNEL = 10
        # Pad 1-16 Note numbers
        PAD_1 = 36
        PAD_2 = 37
        PAD_3 = 38
        PAD_4 = 39
        PAD_5 = 40
        PAD_6 = 41
        PAD_7 = 42
        PAD_8 = 43
        PAD_9 = 44
        PAD_10 = 45
        PAD_11 = 46
        PAD_12 = 47
        PAD_13 = 48
        PAD_14 = 49
        PAD_15 = 50
        PAD_16 = 51
        
        ALL_PADS = range(36, 52) # 36 to 51

        # Pad Colors (SysEx)
        PAD_LED_START_ID = 0x70 # 112
        COLOR_YELLOW = (31, 31, 0)
        COLOR_PURPLE = (31, 0, 31)
        COLOR_YELLOW_DIM = (12, 12, 0) # ~40%
        COLOR_PURPLE_DIM = (12, 0, 12) # ~40%

    # Group 3: DAW Commands
    class DAW:
        class Track:
            CONTROL_1 = 8
            CONTROL_2 = 16
            CONTROL_3 = 0
            CONTROL_4 = 56
            CONTROL_5 = 57
            ALL = [8, 16, 0, 56, 57]

        class Global:
            CONTROL_1 = 74
            CONTROL_2 = 87
            CONTROL_3 = 88
            CONTROL_4 = 89
            CONTROL_5 = 81
            ALL = [74, 87, 88, 89, 81]

    # Group 4: Transport Control
    class Transport:
        REWIND = 91
        FAST_FORWARD = 92
        STOP = 93
        PLAY = 94
        RECORD = 95
        LOOP = 86

    # Group 5: Navigation
    class Navigation:
        LEFT_ARROW = 98
        RIGHT_ARROW = 99
        KNOB_TURN = 60
        KNOB_PUSH = 84

    # Group 6: Mixer & Parameter Control
    class Mixer:
        class Knobs:
            KNOB_1 = 74
            KNOB_2 = 71
            KNOB_3 = 76
            KNOB_4 = 77
            KNOB_5 = 93
            KNOB_6 = 18
            KNOB_7 = 19
            KNOB_8 = 16
            KNOB_9 = 17
            ALL = [74, 71, 76, 77, 93, 18, 19, 16, 17]

        class Faders:
            FADER_1 = 73
            FADER_2 = 75
            FADER_3 = 79
            FADER_4 = 72
            FADER_5 = 80
            FADER_6 = 81
            FADER_7 = 82
            FADER_8 = 83
            FADER_9 = 85
            ALL = [73, 75, 79, 72, 80, 81, 82, 83, 85]

        class TrackButtons:
            BUTTON_1 = 22
            BUTTON_2 = 23
            BUTTON_3 = 24
            BUTTON_4 = 25
            BUTTON_5 = 26
            BUTTON_6 = 27
            BUTTON_7 = 28
            BUTTON_8 = 29
            BUTTON_9 = 30
            ALL = range(22, 31) # 22 to 30
