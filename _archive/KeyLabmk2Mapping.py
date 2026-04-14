
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
        COLOR_YELLOW_DIM = (3, 3, 0) # ~10%
        COLOR_PURPLE_DIM = (3, 0, 3) # ~10%

    # Group 3: DAW Commands
    class DAW:
        class Track:
            CONTROL_1_1 = 8
            CONTROL_2_1 = 16
            CONTROL_3_1 = 0
            CONTROL_4_1 = 56
            CONTROL_5_1 = 57
            ALL = [8, 16, 0, 56, 57]

        class Global:
            CONTROL_1_2 = 74
            CONTROL_2_2 = 87
            CONTROL_3_2 = 88
            CONTROL_4_2 = 89
            CONTROL_5_2 = 81
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
            # Based on log: Knob 1 = 16 (0x10). 
            # Assuming sequential CCs for Knobs in DAW mode (MCU relative?)
            # MCU V-Pots usually: Ch 1 CC 16, Ch 2 CC 17...
            # Let's assume standard MCU V-Pot mapping.
            KNOB_1 = 16
            KNOB_2 = 17
            KNOB_3 = 18
            KNOB_4 = 19
            KNOB_5 = 20
            KNOB_6 = 21
            KNOB_7 = 22
            KNOB_8 = 23
            KNOB_9 = 24 # Possible conflict with Button 1 Note 24 if we mix CC/Note? No, distinct types.
            ALL = [16, 17, 18, 19, 20, 21, 22, 23, 24]

        class Faders:
            # Faders use Pitch Bend (Statuses 224-232)
            # We map them by Index (0-8) corresponding to Channels 0-8
            # Just placeholders here, logic will use Status
            FADER_1 = 0
            ALL = range(9)

        class TrackButtons:
            # Mapped to Notes (Group 6 buttons send Note On/Off in DAW mode)
            BUTTON_1 = 24 # C2
            BUTTON_2 = 25 # C#2
            BUTTON_3 = 26 # D2
            BUTTON_4 = 27 # D#2
            BUTTON_5 = 28 # E2
            BUTTON_6 = 29 # F2
            BUTTON_7 = 30 # F#2
            BUTTON_8 = 31 # G2
            BUTTON_9 = 51 # D#4
            ALL = [24, 25, 26, 27, 28, 29, 30, 31, 51]

