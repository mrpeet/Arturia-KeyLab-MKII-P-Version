# KeyLab mkII — Plugin Parameter Database
#
# Standardized macro parameter mappings for 300+ plugins.
# Data sourced from:
#   1. Community Plugin Spreadsheet (CPS) — CC0-1.0 License
#      https://github.com/rd3d2/FLKey-External-Plugins
#      Maintainer: Ian Walker (rd3d2/gadgeteerONE) + Community
#   2. user_defined_plugin_mappings.py (FLKey community, updated 2024)
#
# Standard 8-Macro-Slot Schema (inspired by Roland Zenology):
#   Slot 0: Cutoff / Filter       Slot 4: Modulation
#   Slot 1: Resonance             Slot 5: FX1 Level
#   Slot 2: Attack                Slot 6: FX2 Level
#   Slot 3: Release               Slot 7: Plugin Level / Volume
#
# Each entry: "PluginName": { "params": [(index, "name"), ...] }
#   - index: FL Studio parameter index (plugins.setParamValue)
#   - name:  Display name shown on KeyLab LCD
#   - index 999 = slot not mapped (plugin has no suitable parameter)
#
# Optional: "special" dict for plugin-specific hardware bindings
#   e.g. "special": {"jog_wheel": "preset_navigation"}
#
# -----------------------------------------------------------------------
# HOW TO ADD A NEW PLUGIN:
#   1. Open the plugin in FL Studio
#   2. Use fl_param_checker (https://github.com/MaddyGuthridge/fl_param_checker)
#      or the debug_plugin_params() function below to list all parameters
#   3. Pick the 8 most useful parameters following the slot schema above
#   4. Add a new entry to PLUGIN_DB below
#   5. Restart the script (or reload via FL Studio MIDI settings)
# -----------------------------------------------------------------------

NOT_MAPPED = 999


# ---------------------------------------------------------------------------
#  Plugin Database
# ---------------------------------------------------------------------------

PLUGIN_DB = {

    # =====================================================================
    #  FL STUDIO INTERNAL PLUGINS — Instruments
    # =====================================================================

    "3x Osc": {
        "params": [
            (1, "Osc 1 Shape"),
            (8, "Osc 2 Shape"),
            (15, "Osc 3 Shape"),
            (9, "Osc 2 Coarse"),
            (16, "Osc 3 Coarse"),
            (2, "Filter Cutoff"),
            (3, "Filter Res"),
            (5, "Filter Type"),
        ],
    },

    "Autogun": {
        "params": [
            (0, "Master Level"),
        ],
    },

    "BASSDRUM": {
        "params": [
            (6, "Base"),
            (7, "Peak"),
            (8, "Slide Time"),
            (4, "Drive"),
            (15, "Click Amount"),
            (21, "Noise Mix"),
            (17, "Noise Decay"),
            (2, "Duration"),
        ],
    },

    "BeepMap": {
        "params": [
            (0, "Freq Range"),
            (1, "Pixel Length"),
            (2, "Scale Type"),
            (3, "Use Blue"),
            (4, "Grainy"),
            (5, "Loop"),
            (6, "Widen"),
        ],
    },

    "BooBass": {
        "params": [
            (0, "Bass"),
            (1, "Mid"),
            (2, "Treble"),
        ],
    },

    "DirectWave": {
        "params": [
            (32, "Amp Env Atk"),
            (33, "Amp Env Decay"),
            (34, "Amp Env Sus"),
            (35, "Amp Env Rel"),
            (83, "Delay Send"),
            (84, "Chorus Send"),
            (85, "Reverb Send"),
            (1, "Glide"),
        ],
    },

    "Drumaxx": {
        "params": [
            (0, "Ch.1 Vol"),
            (44, "Ch.2 Vol"),
            (88, "Ch.3 Vol"),
            (132, "Ch.4 Vol"),
            (176, "Ch.5 Vol"),
            (220, "Ch.6 Vol"),
            (264, "Ch.7 Vol"),
            (308, "Ch.8 Vol"),
        ],
    },

    "Drumpad": {
        "params": [
            (3, "Mallet Decay"),
            (5, "Mallet Noise"),
            (6, "Membrane Decay"),
            (8, "Membrane Tens"),
            (12, "Membrane Shape"),
            (13, "Low Freq"),
            (23, "Mid Decay"),
            (29, "Pitch"),
        ],
    },

    "FL Keys": {
        "params": [
            (1, "Release"),
            (7, "Stereo"),
            (14, "Overdrive"),
            (11, "Treble"),
            (5, "Vel > Muffle"),
            (4, "Muffle"),
            (3, "Vel > Hardness"),
            (2, "Hardness"),
        ],
    },

    "FLEX": {
        "params": [
            (10, "Macro 1"),
            (11, "Macro 2"),
            (12, "Macro 3"),
            (13, "Macro 4"),
            (14, "Macro 5"),
            (15, "Macro 6"),
            (16, "Macro 7"),
            (17, "Macro 8"),
        ],
    },

    "FPC": {
        "params": [
            (256, "Pad 1 Tune"),
            (257, "Pad 2 Tune"),
            (258, "Pad 3 Tune"),
            (259, "Pad 4 Tune"),
            (260, "Pad 5 Tune"),
            (261, "Pad 6 Tune"),
            (262, "Pad 7 Tune"),
            (263, "Pad 8 Tune"),
        ],
        "special": {
            "pads": "drum_mapping",
        },
    },

    "Fruit kick": {
        "params": [
            (0, "Max Freq"),
            (1, "Min Freq"),
            (2, "Freq Decay"),
            (3, "Amp Decay"),
            (4, "Click"),
            (5, "Distortion"),
        ],
    },

    "Fruity DX10": {
        "params": [
            (11, "Waveform"),
            (21, "Coarse"),
            (5, "Mod 1 Init"),
            (6, "Mod 1 Decay"),
            (3, "Mod 1 Coarse"),
            (16, "Mod 2 Init"),
            (17, "Mod 2 Decay"),
            (14, "Mod 2 Coarse"),
        ],
    },

    "Fruity Dance": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (NOT_MAPPED, ""),
        ],
    },

    "Fruity DrumSynth Live": {
        "params": [
            (460, "Osc1 Freq"),
            (461, "Osc1 Sweep Start"),
            (462, "Osc1 Sweep Time"),
            (463, "Osc1 Env Decay"),
            (466, "Osc2 Freq"),
            (467, "Osc2 Bandwidth"),
            (489, "O1>O2 Ring Mod"),
            (469, "Osc2 Env Decay"),
        ],
    },

    "Fruity granulizer": {
        "params": [
            (0, "Grain Attack"),
            (1, "Grain Hold"),
            (2, "Grain Spacing"),
            (3, "Wave Spacing"),
            (7, "Pan"),
            (6, "Randomness"),
            (10, "Sample Start"),
            (9, "Hold Sound"),
        ],
    },

    "GMS": {
        "params": [
            (32, "Filter Cutoff"),
            (33, "Filter Res"),
            (40, "Env Attack"),
            (41, "Env Decay"),
            (42, "Env Amount"),
            (45, "LFO Rate"),
            (46, "LFO Amount"),
            (65, "Modulation"),
        ],
    },

    "Harmless": {
        "params": [
            (31, "Pluck"),
            (79, "Harmonizer Mix"),
            (54, "Filter Freq"),
            (59, "Filter Res"),
            (49, "Filter Decay"),
            (52, "Env > Filter"),
            (71, "Phaser Mix"),
            (65, "Unison"),
        ],
    },

    "Harmor": {
        "params": [
            (772, "Mod X"),
            (773, "Mod Y"),
            (774, "Mod Z"),
            (75, "Pluck Decay"),
            (76, "Phaser Mix"),
            (27, "Harmonizer Mix"),
            (23, "Harmonic Blur"),
            (52, "Filter Cutoff"),
        ],
    },

    "Kepler": {
        "params": [
            (19, "Param 19"),
            (20, "Param 20"),
            (26, "Param 26"),
            (29, "Param 29"),
            (5, "Param 5"),
            (30, "Param 30"),
            (31, "Param 31"),
            (33, "Param 33"),
        ],
    },

    "MIDI Out": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
        ],
    },

    "MiniSynth": {
        "params": [
            (8, "Filter Freq"),
            (9, "Filter Peak"),
            (5, "Osc Waveform"),
            (6, "Osc Modifier"),
            (20, "LFO Amount"),
            (19, "LFO Rate"),
            (18, "LFO Dest"),
            (2, "Slide Time"),
        ],
    },

    "Morphine": {
        "params": [
            (30, "Master Atk"),
            (31, "Master Decay"),
            (32, "Master Sus"),
            (33, "Master Rel"),
            (17, "Reverb Decay"),
            (19, "Reverb Mix"),
            (52, "Gen A: Pan Rng"),
            (6, "Overdrive"),
        ],
    },

    "Ogun": {
        "params": [
            (3, "Mod X"),
            (4, "Mod Y"),
            (5, "Timbre Pre-Decay"),
            (6, "Timbre Decay"),
            (7, "Timbre Release"),
            (8, "Timbre Fullness"),
            (15, "Unison Pitch"),
            (40, "EQ Band 1"),
        ],
    },

    "PLUCKED!": {
        "params": [
            (0, "Decay"),
            (1, "Color"),
            (2, "Normalize Decay"),
            (3, "Gate"),
            (4, "Widen"),
        ],
    },

    "PoiZone": {
        "params": [
            (18, "Filter Cutoff"),
            (19, "Filter Res"),
            (23, "Amp Decay"),
            (12, "Env Decay"),
            (10, "Env Amount"),
            (8, "Osc Balance"),
            (38, "Delay Wet"),
            (42, "Chorus Wet"),
        ],
    },

    "Sakura": {
        "params": [
            (2, "Amp Attack"),
            (3, "Amp Decay"),
            (4, "Amp Sustain"),
            (5, "Amp Release"),
            (6, "String 1 Decay"),
            (9, "String 1 Damp"),
            (11, "String 2 Decay"),
            (14, "String 2 Damp"),
        ],
    },

    "Sampler": {
        "params": [
            (2, "Filter Cutoff"),
            (3, "Filter Res"),
            (5, "Filter Type"),
            (13, "Sample Start"),
            (9, "Gate Time"),
            (11, "Time Shift"),
            (12, "Swing Mix"),
        ],
    },

    "Sawer": {
        "params": [
            (27, "Filter Cutoff"),
            (28, "Filter Res"),
            (31, "Filter Mode"),
            (45, "LFO Amount"),
            (39, "LFO Speed"),
            (19, "Sub-Saw Level"),
            (18, "Sub-Saw Harm"),
            (11, "Glide Time"),
        ],
    },

    "SimSynth Live": {
        "params": [
            (11, "Filter Cutoff"),
            (12, "Filter Emph"),
            (15, "Filter HP"),
            (16, "Filter BP"),
            (13, "Env > Filter"),
            (22, "Filter Attack"),
            (23, "Filter Decay"),
            (18, "Amp Decay"),
        ],
    },

    "Slicex": {
        "params": [
            (6, "Mod X"),
            (7, "Mod Y"),
            (5, "Master Pitch"),
            (8, "Filter Env"),
            (9, "Filter Cutoff"),
            (10, "Filter Res"),
            (20, "Vol Env Decay"),
            (28, "Filt Env Decay"),
        ],
    },

    "SoundFont Player": {
        "params": [
            (5, "Env 2 Attack"),
            (6, "Env 2 Decay"),
            (7, "Env 2 Sustain"),
            (8, "Env 2 Release"),
            (12, "Filter Cutoff"),
            (4, "Modulation"),
            (2, "Reverb Send"),
            (3, "Chorus Send"),
        ],
    },

    "Sytrus": {
        "params": [
            (18, "Mod X"),
            (19, "Mod Y"),
            (4, "Vol Decay"),
            (8, "Filter Decay"),
            (11, "Unison Order"),
            (14, "Unison Pitch"),
            (15, "Unison Sub"),
            (1, "Master LFO"),
        ],
    },

    "Toxic Biohazard": {
        "params": [
            (15, "Param 15"),
            (16, "Param 16"),
            (43, "Param 43"),
            (44, "Param 44"),
            (45, "Param 45"),
            (46, "Param 46"),
            (47, "Param 47"),
            (48, "Param 48"),
        ],
    },

    "ToxicBiohazard": {
        "params": [
            (110, "Osc 2>1 FM"),
            (44, "Osc 2 Shift"),
            (117, "Osc 3>2 FM"),
            (45, "Osc 3 Shift"),
            (15, "Filter Cutoff"),
            (16, "Filter Res"),
            (3, "Master Attack"),
            (1, "Distortion"),
        ],
    },

    "Transistor Bass": {
        "params": [
            (0, "Tuning"),
            (41, "303 Pulse"),
            (1, "Waveform"),
            (2, "Filter Cutoff"),
            (4, "Filter Res"),
            (5, "Envelope Mod"),
            (6, "Decay"),
            (7, "Accent"),
        ],
    },


    # =====================================================================
    #  FL STUDIO INTERNAL PLUGINS — Effects
    # =====================================================================

    "Distructor": {
        "params": [
            (37, "Param 37"),
            (86, "Param 86"),
            (135, "Param 135"),
            (184, "Param 184"),
            (2, "Param 2"),
            (88, "Param 88"),
            (144, "Param 144"),
            (189, "Param 189"),
        ],
    },

    "EQUO": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (815, "Param 815"),
            (830, "Param 830"),
            (845, "Param 845"),
        ],
    },

    "Edison": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
        ],
    },

    "Effector": {
        "params": [
            (0, "Param 0"),
            (3, "Param 3"),
            (4, "Param 4"),
            (2, "Param 2"),
            (5, "Param 5"),
            (7, "Param 7"),
            (9, "Param 9"),
            (8, "Param 8"),
        ],
    },

    "Frequency Shifter": {
        "params": [
            (4, "Param 4"),
            (2, "Param 2"),
            (5, "Param 5"),
            (9, "Param 9"),
            (5, "Param 5"),
            (6, "Param 6"),
            (0, "Param 0"),
            (7, "Param 7"),
        ],
    },

    "Frequency Splitter": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "Fruity 7 Band EQ": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
        ],
    },

    "Fruity Balance": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "Fruity Bass Boost": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "Fruity Blood Overdrive": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
        ],
    },

    "Fruity Center": {
        "params": [
            (0, "Param 0"),
        ],
    },

    "Fruity Chorus": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Compressor": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
        ],
    },

    "Fruity Convolver": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
        ],
    },

    "Fruity Delay": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
        ],
    },

    "Fruity Delay 2": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (6, "Param 6"),
            (3, "Param 3"),
            (7, "Param 7"),
            (4, "Param 4"),
            (5, "Param 5"),
            (3, "Param 3"),
        ],
    },

    "Fruity Delay 3": {
        "params": [
            (0, "Param 0"),
            (4, "Param 4"),
            (1, "Param 1"),
            (7, "Param 7"),
            (15, "Param 15"),
            (8, "Param 8"),
            (18, "Param 18"),
            (23, "Param 23"),
        ],
    },

    "Fruity Delay Bank": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (5, "Param 5"),
            (19, "Param 19"),
            (17, "Param 17"),
            (18, "Param 18"),
        ],
    },

    "Fruity Fast Dist": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
        ],
    },

    "Fruity Fast LP": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "Fruity Filter": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
        ],
    },

    "Fruity Flanger": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Flangus": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Free Filter": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
        ],
    },

    "Fruity LSD": {
        "params": [
            (0, "Param 0"),
        ],
    },

    "Fruity Limiter": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Love Philter": {
        "params": [
            (18, "Param 18"),
            (52, "Param 52"),
            (9, "Param 9"),
            (10, "Param 10"),
            (6, "Param 6"),
            (7, "Param 7"),
            (3, "Param 3"),
            (4, "Param 4"),
        ],
    },

    "Fruity Multiband Compressor": {
        "params": [
            (21, "Param 21"),
            (13, "Param 13"),
            (12, "Param 12"),
            (4, "Param 4"),
            (20, "Param 20"),
            (11, "Param 11"),
            (3, "Param 3"),
            (0, "Param 0"),
        ],
    },

    "Fruity Mute 2": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "Fruity NoteBook": {
        "params": [
            (0, "Param 0"),
        ],
    },

    "Fruity PanOMatic": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
        ],
    },

    "Fruity Parametric EQ": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Parametric EQ2": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Phase Inverter": {
        "params": [
            (0, "Param 0"),
        ],
    },

    "Fruity Phaser": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Reeverb": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (9, "Param 9"),
        ],
    },

    "Fruity Reeverb 2": {
        "params": [
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (12, "Param 12"),
        ],
    },

    "Fruity Scratcher": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (8, "Param 8"),
        ],
    },

    "Fruity Send": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
        ],
    },

    "Fruity Soft Clipper": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "Fruity Spectroman": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
        ],
    },

    "Fruity Squeeze": {
        "params": [
            (2, "Param 2"),
            (10, "Param 10"),
            (9, "Param 9"),
            (8, "Param 8"),
            (11, "Param 11"),
            (3, "Param 3"),
            (1, "Param 1"),
            (0, "Param 0"),
        ],
    },

    "Fruity Stereo Enhancer": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
        ],
    },

    "Fruity Stereo Shaper": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
        ],
    },

    "Fruity Vocoder": {
        "params": [
            (4, "Param 4"),
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (6, "Param 6"),
            (7, "Param 7"),
            (9, "Param 9"),
            (11, "Param 11"),
        ],
    },

    "Fruity WaveShaper": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
        ],
    },

    "Gross Beat": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Hardcore": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
            (16, "Param 16"),
            (17, "Param 17"),
            (18, "Param 18"),
            (19, "Param 19"),
            (20, "Param 20"),
        ],
    },

    "Hyper Chorus": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (9, "Param 9"),
        ],
    },

    "LuxeVerb": {
        "params": [
            (0, "Param 0"),
            (4, "Param 4"),
            (7, "Param 7"),
            (9, "Param 9"),
            (16, "Param 16"),
            (19, "Param 19"),
            (32, "Param 32"),
            (33, "Param 33"),
        ],
    },

    "Maximus Multiband Maximizer": {
        "params": [
            (46, "Param 46"),
            (47, "Param 47"),
            (48, "Param 48"),
            (49, "Param 49"),
            (50, "Param 50"),
            (51, "Param 51"),
            (52, "Param 52"),
            (53, "Param 53"),
        ],
    },

    "Multiband Delay": {
        "params": [
            (388, "Param 388"),
            (384, "Param 384"),
            (392, "Param 392"),
            (386, "Param 386"),
            (387, "Param 387"),
            (398, "Param 398"),
            (394, "Param 394"),
            (391, "Param 391"),
        ],
    },

    "Pitch Shifter": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (4, "Param 4"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
            (3, "Param 3"),
        ],
    },

    "Pitcher": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Transient Processor": {
        "params": [
            (6, "Param 6"),
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (7, "Param 7"),
            (5, "Param 5"),
        ],
    },

    "Tuner": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
        ],
    },

    "Vintage Chorus": {
        "params": [
            (0, "Param 0"),
            (5, "Param 5"),
            (6, "Param 6"),
            (10, "Param 10"),
            (11, "Param 11"),
            (16, "Param 16"),
            (4, "Param 4"),
            (7, "Param 7"),
        ],
    },

    "Vintage Phaser": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (6, "Param 6"),
            (12, "Param 12"),
            (23, "Param 23"),
            (23, "Param 23"),
            (21, "Param 21"),
        ],
    },

    "Vocodex": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },


    # =====================================================================
    #  ARTURIA V-COLLECTION
    # =====================================================================

    "ARP 2600 V3": {
        "params": [
            (27, "Param 27"),
            (26, "Param 26"),
            (40, "Param 40"),
            (41, "Param 41"),
            (83, "Param 83"),
            (341, "Param 341"),
            (342, "Param 342"),
            (114, "Param 114"),
        ],
    },

    "Analog Lab 4": {
        "params": [
            (2, "Param 2"),
            (4, "Param 4"),
            (6, "Param 6"),
            (8, "Param 8"),
            (102, "Param 102"),
            (341, "Param 341"),
            (342, "Param 342"),
            (0, "Param 0"),
        ],
    },

    "Analog Lab V": {
        "params": [
            (2, "Param 2"),
            (4, "Param 4"),
            (6, "Param 6"),
            (8, "Param 8"),
            (102, "Param 102"),
            (341, "Param 341"),
            (342, "Param 342"),
            (233, "Param 233"),
        ],
    },

    "Augmented GRAND PIANO": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
        ],
    },

    "Augmented STRINGS": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
        ],
    },

    "Augmented VOICES": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
        ],
    },

    "Buchla Easel V": {
        "params": [
            (256, "Param 256"),
            (257, "Param 257"),
            (50, "Param 50"),
            (258, "Param 258"),
            (259, "Param 259"),
            (341, "Param 341"),
            (342, "Param 342"),
            (36, "Param 36"),
        ],
    },

    "CMI V": {
        "params": [
            (1593, "Param 1593"),
            (1594, "Param 1594"),
            (5, "Param 5"),
            (3, "Param 3"),
            (4, "Param 4"),
            (1596, "Param 1596"),
            (1596, "Param 1596"),
            (7, "Param 7"),
        ],
    },

    "CS-80 V3": {
        "params": [
            (1004, "Param 1004"),
            (1005, "Param 1005"),
            (15, "Param 15"),
            (18, "Param 18"),
            (0, "Param 0"),
            (1006, "Param 1006"),
            (1007, "Param 1007"),
            (8, "Param 8"),
        ],
    },

    "CS-80 V4": {
        "params": [
            (213, "Param 213"),
            (214, "Param 214"),
            (54, "Param 54"),
            (57, "Param 57"),
            (70, "Param 70"),
            (215, "Param 215"),
            (216, "Param 216"),
            (46, "Param 46"),
        ],
    },

    "CZ V": {
        "params": [
            (614, "Param 614"),
            (615, "Param 615"),
            (108, "Param 108"),
            (112, "Param 112"),
            (7, "Param 7"),
            (616, "Param 616"),
            (617, "Param 617"),
            (0, "Param 0"),
        ],
    },

    "Clavinet V": {
        "params": [
            (92, "Param 92"),
            (93, "Param 93"),
            (36, "Param 36"),
            (3, "Param 3"),
            (94, "Param 94"),
            (94, "Param 94"),
            (95, "Param 95"),
            (15, "Param 15"),
        ],
    },

    "DX7 V": {
        "params": [
            (946, "Param 946"),
            (932, "Param 932"),
            (933, "Param 933"),
            (934, "Param 934"),
            (935, "Param 935"),
            (948, "Param 948"),
            (949, "Param 949"),
            (0, "Param 0"),
        ],
    },

    "Emulator II V": {
        "params": [
            (3, "Param 3"),
            (4, "Param 4"),
            (16, "Param 16"),
            (15, "Param 15"),
            (21, "Param 21"),
            (526, "Param 526"),
            (528, "Param 528"),
            (0, "Param 0"),
        ],
    },

    "Jun-6 V": {
        "params": [
            (66, "Param 66"),
            (67, "Param 67"),
            (45, "Param 45"),
            (48, "Param 48"),
            (6, "Param 6"),
            (68, "Param 68"),
            (69, "Param 69"),
            (13, "Param 13"),
        ],
    },

    "Jup 8 V4": {
        "params": [
            (21, "Param 21"),
            (22, "Param 22"),
            (38, "Param 38"),
            (33, "Param 33"),
            (86, "Param 86"),
            (341, "Param 341"),
            (342, "Param 342"),
            (204, "Param 204"),
        ],
    },

    "Jup-8 V3": {
        "params": [
            (12, "Param 12"),
            (13, "Param 13"),
            (25, "Param 25"),
            (28, "Param 28"),
            (121, "Param 121"),
            (209, "Param 209"),
            (214, "Param 214"),
            (204, "Param 204"),
        ],
    },

    "Jup-8 V4": {
        "params": [
            (21, "Param 21"),
            (22, "Param 22"),
            (19, "Param 19"),
            (3, "Param 3"),
            (10, "Param 10"),
            (341, "Param 341"),
            (342, "Param 342"),
            (18, "Param 18"),
        ],
    },

    "KORG MS-20 V": {
        "params": [
            (15, "Param 15"),
            (16, "Param 16"),
            (27, "Param 27"),
            (28, "Param 28"),
            (20, "Param 20"),
            (149, "Param 149"),
            (282, "Param 282"),
            (0, "Param 0"),
        ],
    },

    "Matrix-12 V2": {
        "params": [
            (144, "Param 144"),
            (145, "Param 145"),
            (146, "Param 146"),
            (114, "Param 114"),
            (126, "Param 126"),
            (341, "Param 341"),
            (342, "Param 342"),
            (0, "Param 0"),
        ],
    },

    "Mini V3": {
        "params": [
            (143, "Param 143"),
            (144, "Param 144"),
            (26, "Param 26"),
            (27, "Param 27"),
            (146, "Param 146"),
            (145, "Param 145"),
            (146, "Param 146"),
            (0, "Param 0"),
        ],
    },

    "MiniFreak V": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (10, "Param 10"),
        ],
    },

    "Modular V3": {
        "params": [
            (564, "Param 564"),
            (565, "Param 565"),
            (133, "Param 133"),
            (135, "Param 135"),
            (25, "Param 25"),
            (566, "Param 566"),
            (567, "Param 567"),
            (0, "Param 0"),
        ],
    },

    "OP-Xa V": {
        "params": [
            (283, "Param 283"),
            (284, "Param 284"),
            (12, "Param 12"),
            (2, "Param 2"),
            (6, "Param 6"),
            (285, "Param 285"),
            (286, "Param 286"),
            (286, "Param 286"),
        ],
    },

    "Piano V2": {
        "params": [
            (50, "Param 50"),
            (51, "Param 51"),
            (76, "Param 76"),
            (12, "Param 12"),
            (78, "Param 78"),
            (53, "Param 53"),
            (54, "Param 54"),
            (0, "Param 0"),
        ],
    },

    "Pigments": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (205, "Param 205"),
            (85, "Param 85"),
            (125, "Param 125"),
            (439, "Param 439"),
        ],
    },

    "Prophet V3": {
        "params": [
            (175, "Param 175"),
            (176, "Param 176"),
            (24, "Param 24"),
            (27, "Param 27"),
            (178, "Param 178"),
            (177, "Param 177"),
            (178, "Param 178"),
            (105, "Param 105"),
        ],
    },

    "Prophet-5 V": {
        "params": [
            (96, "Param 96"),
            (97, "Param 97"),
            (24, "Param 24"),
            (0, "Param 0"),
            (5, "Param 5"),
            (98, "Param 98"),
            (99, "Param 99"),
            (15, "Param 15"),
        ],
    },

    "Prophet-VS V": {
        "params": [
            (96, "Param 96"),
            (97, "Param 97"),
            (29, "Param 29"),
            (32, "Param 32"),
            (48, "Param 48"),
            (98, "Param 98"),
            (99, "Param 99"),
            (9, "Param 9"),
        ],
    },

    "SEM V2": {
        "params": [
            (168, "Param 168"),
            (169, "Param 169"),
            (170, "Param 170"),
            (3, "Param 3"),
            (7, "Param 7"),
            (170, "Param 170"),
            (171, "Param 171"),
            (0, "Param 0"),
        ],
    },

    "SQ80 V": {
        "params": [
            (825, "Param 825"),
            (826, "Param 826"),
            (60, "Param 60"),
            (63, "Param 63"),
            (831, "Param 831"),
            (827, "Param 827"),
            (828, "Param 828"),
            (0, "Param 0"),
        ],
    },

    "Stage-73 V": {
        "params": [
            (0, "Param 1"),
            (0, "Param 2"),
            (0, "Param 3"),
            (0, "Param 4"),
            (0, "Param 5"),
            (0, "Param 6"),
            (0, "Param 7"),
            (0, "Param 8"),
        ],
    },

    "Stage-73 V2": {
        "params": [
            (343, "Param 343"),
            (344, "Param 344"),
            (41, "Param 41"),
            (42, "Param 42"),
            (17, "Param 17"),
            (345, "Param 345"),
            (346, "Param 346"),
            (0, "Param 0"),
        ],
    },

    "Synclavier V": {
        "params": [
            (826, "Param 826"),
            (827, "Param 827"),
            (39, "Param 39"),
            (41, "Param 41"),
            (2, "Param 2"),
            (828, "Param 828"),
            (829, "Param 829"),
            (0, "Param 0"),
        ],
    },

    "Synthi V": {
        "params": [
            (368, "Param 368"),
            (369, "Param 369"),
            (36, "Param 36"),
            (39, "Param 39"),
            (4, "Param 4"),
            (370, "Param 370"),
            (371, "Param 371"),
            (0, "Param 0"),
        ],
    },

    "Vocoder V": {
        "params": [
            (310, "Param 310"),
            (311, "Param 311"),
            (4, "Param 4"),
            (5, "Param 5"),
            (3, "Param 3"),
            (312, "Param 312"),
            (313, "Param 313"),
            (0, "Param 0"),
        ],
    },


    # =====================================================================
    #  ROLAND
    # =====================================================================

    "Corona": {
        "params": [
            (22, "Param 22"),
            (23, "Param 23"),
            (17, "Param 17"),
            (20, "Param 20"),
            (27, "Param 27"),
            (58, "Param 58"),
            (106, "Param 106"),
            (12, "Param 12"),
        ],
    },

    "D-50": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (22, "Param 22"),
            (23, "Param 23"),
            (11, "Param 11"),
            (NOT_MAPPED, ""),
            (NOT_MAPPED, ""),
            (306, "Param 306"),
        ],
    },

    "DCO-106": {
        "params": [
            (15, "Param 15"),
            (16, "Param 16"),
            (23, "Param 23"),
            (26, "Param 26"),
            (0, "Param 0"),
            (68, "Param 68"),
            (70, "Param 70"),
            (29, "Param 29"),
        ],
    },

    "JD-800": {
        "params": [
            (29, "Param 29"),
            (33, "Param 33"),
            (45, "Param 45"),
            (47, "Param 47"),
            (37, "Param 37"),
            (74, "Param 74"),
            (75, "Param 75"),
            (0, "Param 0"),
        ],
    },

    "JUNO-106": {
        "params": [
            (12, "Param 12"),
            (13, "Param 13"),
            (16, "Param 16"),
            (19, "Param 19"),
            (46, "Param 46"),
            (27, "Param 27"),
            (28, "Param 28"),
            (35, "Param 35"),
        ],
    },

    "JUPITER-4": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (22, "Param 22"),
            (25, "Param 25"),
            (2, "Param 2"),
            (51, "Param 51"),
            (27, "Param 27"),
            (37, "Param 37"),
        ],
    },

    "JUPITER-8": {
        "params": [
            (21, "Cutoff"),
            (22, "Resonance"),
            (30, "Attack"),
            (33, "Release"),
            (57, "Modulation"),
        ],
    },

    "JUPITER-8.": {
        "params": [
            (21, "Param 21"),
            (22, "Param 22"),
            (25, "Param 25"),
            (28, "Param 28"),
            (57, "Param 57"),
            (69, "Param 69"),
            (70, "Param 70"),
            (54, "Param 54"),
        ],
    },

    "JX-3P": {
        "params": [
            (19, "Param 19"),
            (20, "Param 20"),
            (25, "Param 25"),
            (28, "Param 28"),
            (61, "Param 61"),
            (37, "Param 37"),
            (38, "Param 38"),
            (39, "Param 39"),
        ],
    },

    "Juno-60": {
        "params": [
            (12, "Param 12"),
            (13, "Param 13"),
            (16, "Param 16"),
            (19, "Param 19"),
            (2, "Param 2"),
            (26, "Param 26"),
            (27, "Param 27"),
            (35, "Param 35"),
        ],
    },

    "Jura": {
        "params": [
            (19, "Param 19"),
            (20, "Param 20"),
            (29, "Param 29"),
            (32, "Param 32"),
            (45, "Param 45"),
            (54, "Param 54"),
            (75, "Param 75"),
            (0, "Param 0"),
        ],
    },

    "Mercury-4": {
        "params": [
            (16, "Param 16"),
            (18, "Param 18"),
            (24, "Param 24"),
            (30, "Param 30"),
            (64, "Param 64"),
            (55, "Param 55"),
            (58, "Param 58"),
            (32, "Param 32"),
        ],
    },

    "Mercury-6": {
        "params": [
            (20, "Param 20"),
            (22, "Param 22"),
            (34, "Param 34"),
            (40, "Param 40"),
            (26, "Param 26"),
            (225, "Param 225"),
            (294, "Param 294"),
            (67, "Param 67"),
        ],
    },

    "Model 84 Polyphonic Synthesizer": {
        "params": [
            (10, "Param 10"),
            (11, "Param 11"),
            (18, "Param 18"),
            (21, "Param 21"),
            (28, "Param 28"),
            (23, "Param 23"),
            (22, "Param 22"),
            (31, "Param 31"),
        ],
    },

    "PG-8X": {
        "params": [
            (20, "Param 20"),
            (21, "Param 21"),
            (35, "Param 35"),
            (38, "Param 38"),
            (45, "Param 45"),
            (1, "Param 1"),
            (30, "Param 30"),
            (27, "Param 27"),
        ],
    },

    "PROMARS": {
        "params": [
            (21, "Param 21"),
            (20, "Param 20"),
            (28, "Param 28"),
            (31, "Param 31"),
            (3, "Param 3"),
            (32, "Param 32"),
            (33, "Param 33"),
            (42, "Param 42"),
        ],
    },

    "SH-101": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (16, "Param 16"),
            (19, "Param 19"),
            (1, "Param 1"),
            (26, "Param 26"),
            (27, "Param 27"),
            (35, "Param 35"),
        ],
    },

    "SOUND Canvas VA": {
        "params": [
            (128, "Param 128"),
            (144, "Param 144"),
            (160, "Param 160"),
            (192, "Param 192"),
            (208, "Param 208"),
            (1811, "Param 1811"),
            (1827, "Param 1827"),
            (272, "Param 272"),
        ],
    },

    "SYSTEM-1": {
        "params": [
            (27, "Param 27"),
            (31, "Param 31"),
            (39, "Param 39"),
            (42, "Param 42"),
            (9, "Param 9"),
            (45, "Param 45"),
            (46, "Param 46"),
            (47, "Param 47"),
        ],
    },

    "TAL BassLine 101": {
        "params": [
            (26, "Param 26"),
            (27, "Param 27"),
            (35, "Param 35"),
            (38, "Param 38"),
            (10, "Param 10"),
            (NOT_MAPPED, ""),
            (NOT_MAPPED, ""),
            (1, "Param 1"),
        ],
    },

    "TAL U-No-LX-V2": {
        "params": [
            (10, "Param 10"),
            (11, "Param 11"),
            (24, "Param 24"),
            (1, "Param 1"),
            (25, "Param 25"),
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
        ],
    },

    "TAL-J-8": {
        "params": [
            (105, "Param 105"),
            (107, "Param 107"),
            (65, "Param 65"),
            (71, "Param 71"),
            (43, "Param 43"),
            (NOT_MAPPED, ""),
            (NOT_MAPPED, ""),
            (0, "Param 0"),
        ],
    },

    "U-NO-62 - TAL": {
        "params": [
            (12, "Param 12"),
            (13, "Param 13"),
            (20, "Param 20"),
            (23, "Param 23"),
            (24, "Param 24"),
            (NOT_MAPPED, ""),
            (NOT_MAPPED, ""),
            (1, "Param 1"),
        ],
    },

    "XV-5080": {
        "params": [
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (16, "Param 16"),
            (13, "Param 13"),
            (14, "Param 14"),
            (0, "Param 0"),
        ],
    },

    "ZENOLOGY": {
        "params": [
            (90, "Param 90"),
            (91, "Param 91"),
            (92, "Param 92"),
            (93, "Param 93"),
            (94, "Param 94"),
            (168, "Param 168"),
            (169, "Param 169"),
            (89, "Param 89"),
        ],
    },


    # =====================================================================
    #  KORG
    # =====================================================================

    "ARP_ODYSSEY": {
        "params": [
            (41, "Param 41"),
            (42, "Param 42"),
            (55, "Param 55"),
            (58, "Param 58"),
            (10, "Param 10"),
            (246, "Param 246"),
            (260, "Param 260"),
            (271, "Param 271"),
        ],
    },

    "ELECTRIBE-R": {
        "params": [
            (7, "Param 7"),
            (9, "Param 9"),
            (10, "Param 10"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
            (0, "Param 0"),
        ],
    },

    "M1": {
        "params": [
            (7, "Param 7"),
            (8, "Param 8"),
            (10, "Param 10"),
            (12, "Param 12"),
            (6, "Param 6"),
            (13, "Param 13"),
            (28, "Param 28"),
            (13, "Param 13"),
        ],
    },

    "MS-20": {
        "params": [
            (15, "Param 15"),
            (16, "Param 16"),
            (23, "Param 23"),
            (24, "Param 24"),
            (8, "Param 8"),
            (149, "Param 149"),
            (282, "Param 282"),
            (35, "Param 35"),
        ],
    },

    "MonoPoly": {
        "params": [
            (24, "Param 24"),
            (25, "Param 25"),
            (26, "Param 26"),
            (31, "Param 31"),
            (45, "Param 45"),
            (97, "Param 97"),
            (143, "Param 143"),
            (95, "Param 95"),
        ],
    },

    "Polysix": {
        "params": [
            (7, "Param 7"),
            (8, "Param 8"),
            (23, "Param 23"),
            (26, "Param 26"),
            (44, "Param 44"),
            (46, "Param 46"),
            (92, "Param 92"),
            (0, "Param 0"),
        ],
    },

    "Prophecy": {
        "params": [
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
            (16, "Param 16"),
            (845, "Param 845"),
            (857, "Param 857"),
            (1013, "Param 1013"),
        ],
    },

    "TRITON": {
        "params": [
            (60, "Param 60"),
            (61, "Param 61"),
            (62, "Param 62"),
            (63, "Param 63"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (0, "Param 0"),
        ],
    },

    "TRITON Extreme": {
        "params": [
            (60, "Param 60"),
            (61, "Param 61"),
            (62, "Param 62"),
            (63, "Param 63"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (0, "Param 0"),
        ],
    },

    "WAVESTATION": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (0, "Param 0"),
        ],
    },

    "microKORG": {
        "params": [
            (53, "Param 53"),
            (54, "Param 54"),
            (126, "Param 126"),
            (129, "Param 129"),
            (26, "Param 26"),
            (27, "Param 27"),
            (28, "Param 28"),
            (214, "Param 214"),
        ],
    },

    "miniKORG": {
        "params": [
            (18, "Param 18"),
            (19, "Param 19"),
            (93, "Param 93"),
            (96, "Param 96"),
            (12, "Param 12"),
            (105, "Param 105"),
            (106, "Param 106"),
            (165, "Param 165"),
        ],
    },


    # =====================================================================
    #  CHERRY AUDIO
    # =====================================================================

    "Dreamsynth": {
        "params": [
            (100, "Param 100"),
            (101, "Param 101"),
            (115, "Param 115"),
            (118, "Param 118"),
            (24, "Param 24"),
            (168, "Param 168"),
            (191, "Param 191"),
            (135, "Param 135"),
        ],
    },

    "Elka-X": {
        "params": [
            (73, "Param 73"),
            (74, "Param 74"),
            (82, "Param 82"),
            (85, "Param 85"),
            (147, "Param 147"),
            (123, "Param 123"),
            (130, "Param 130"),
            (134, "Param 134"),
        ],
    },

    "Lowdown": {
        "params": [
            (15, "Param 15"),
            (11, "Param 11"),
            (7, "Param 7"),
            (9, "Param 9"),
            (6, "Param 6"),
            (16, "Param 16"),
            (20, "Param 20"),
            (0, "Param 0"),
        ],
    },

    "Minimode": {
        "params": [
            (16, "Param 16"),
            (17, "Param 17"),
            (22, "Param 22"),
            (23, "Param 23"),
            (4, "Param 4"),
            (1, "Param 1"),
            (3, "Param 3"),
            (25, "Param 25"),
        ],
    },

    "Octave Cat": {
        "params": [
            (60, "Param 60"),
            (61, "Param 61"),
            (0, "Param 0"),
            (3, "Param 3"),
            (59, "Param 59"),
            (121, "Param 121"),
            (27, "Param 27"),
            (61, "Param 61"),
        ],
    },

    "Quadra": {
        "params": [
            (53, "Param 53"),
            (54, "Param 54"),
            (55, "Param 55"),
            (58, "Param 58"),
            (47, "Param 47"),
            (114, "Param 114"),
            (123, "Param 123"),
            (143, "Param 143"),
        ],
    },

    "Surrealistic MG-1 Plus": {
        "params": [
            (19, "Param 19"),
            (20, "Param 20"),
            (22, "Param 22"),
            (23, "Param 23"),
            (24, "Param 24"),
            (25, "Param 25"),
            (26, "Param 26"),
            (27, "Param 27"),
        ],
    },


    # =====================================================================
    #  TAL
    # =====================================================================

    "TAL Mod": {
        "params": [
            (10, "Param 10"),
            (11, "Param 11"),
            (74, "Param 74"),
            (77, "Param 77"),
            (101, "Param 101"),
            (NOT_MAPPED, ""),
            (NOT_MAPPED, ""),
            (0, "Param 0"),
        ],
    },

    "Tal-Drum": {
        "params": [
            (73, "Param 73"),
            (407, "Param 407"),
            (741, "Param 741"),
            (1075, "Param 1075"),
            (1409, "Param 1409"),
            (1743, "Param 1743"),
            (2077, "Param 2077"),
            (2411, "Param 2411"),
        ],
    },


    # =====================================================================
    #  NATIVE INSTRUMENTS
    # =====================================================================

    "Komplete Kontrol": {
        "params": [
            (21, "Param 21"),
            (22, "Param 22"),
            (23, "Param 23"),
            (24, "Param 24"),
            (25, "Param 25"),
            (26, "Param 26"),
            (27, "Param 27"),
            (28, "Param 28"),
        ],
        "special": {
            "jog_wheel": "preset_navigation",
        },
    },

    "Kontakt": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
        "special": {
            "jog_wheel": "preset_navigation",
        },
    },

    "Kontakt 7": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
        "special": {
            "jog_wheel": "preset_navigation",
        },
    },

    "Massive": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Massive X": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Native Instruments Absynth 5": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Native Instruments FM8": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (5, "Param 5"),
            (15, "Param 15"),
            (17, "Param 17"),
            (18, "Param 18"),
            (19, "Param 19"),
            (20, "Param 20"),
        ],
    },

    "Reaktor 6": {
        "params": [
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
        ],
    },


    # =====================================================================
    #  SPITFIRE AUDIO
    # =====================================================================

    "BBC Symphony Orchestra": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "LABS": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (20, "Param 20"),
            (21, "Param 21"),
            (12, "Param 12"),
        ],
    },

    "Originals - Epic Choir": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
            (4, "Param 4"),
            (3, "Param 3"),
        ],
    },

    "Spitfire Originals - Cinematic Pads": {
        "params": [
            (0, "Param 0"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
        ],
    },


    # =====================================================================
    #  UJAM
    # =====================================================================

    "UJAM Berserk": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (127, "Param 127"),
            (126, "Param 126"),
            (90, "Param 90"),
            (8, "Param 8"),
            (2, "Param 2"),
            (3, "Param 3"),
        ],
    },

    "UJAM IRON": {
        "params": [
            (0, "Param 0"),
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (16, "Param 16"),
        ],
    },

    "UJAM IRON2": {
        "params": [
            (0, "Param 0"),
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (16, "Param 16"),
        ],
    },


    # =====================================================================
    #  U-HE
    # =====================================================================

    "BazilleCM": {
        "params": [
            (109, "Param 109"),
            (115, "Param 115"),
            (12, "Param 12"),
            (16, "Param 16"),
            (45, "Param 45"),
            (140, "Param 140"),
            (139, "Param 139"),
            (141, "Param 141"),
        ],
    },

    "Diva": {
        "params": [
            (140, "Param 140"),
            (148, "Param 148"),
            (149, "Param 149"),
            (104, "Param 104"),
            (106, "Param 106"),
            (136, "Param 136"),
            (155, "Param 155"),
            (168, "Param 168"),
        ],
    },

    "Hive": {
        "params": [
            (35, "Param 35"),
            (36, "Param 36"),
            (34, "Param 34"),
            (38, "Param 38"),
            (40, "Param 40"),
            (11, "Param 11"),
            (275, "Param 275"),
            (0, "Param 0"),
        ],
    },

    "U-HE Tyrell N6": {
        "params": [
            (62, "Param 62"),
            (68, "Param 68"),
            (69, "Param 69"),
            (18, "Param 18"),
            (19, "Param 19"),
            (20, "Param 20"),
            (22, "Param 22"),
            (25, "Param 25"),
        ],
    },

    "Zebra2": {
        "params": [
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "ZebraCM": {
        "params": [
            (98, "Param 98"),
            (99, "Param 99"),
            (15, "Param 15"),
            (20, "Param 20"),
            (66, "Param 66"),
            (110, "Param 110"),
            (117, "Param 117"),
            (0, "Param 0"),
        ],
    },

    "ZebraHZ": {
        "params": [
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },


    # =====================================================================
    #  APPLIED ACOUSTICS
    # =====================================================================

    "Lounge Lizard Session 4": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (22, "Param 22"),
            (4, "Param 4"),
            (5, "Param 5"),
            (20, "Param 20"),
        ],
    },

    "Strum GS-2": {
        "params": [
            (0, "Param 0"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (2, "Param 2"),
            (3, "Param 3"),
        ],
    },

    "Strum Session 2": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (5, "Param 5"),
            (6, "Param 6"),
            (53, "Param 53"),
            (55, "Param 55"),
        ],
    },

    "Ultra Analog Session 2": {
        "params": [
            (7, "Param 7"),
            (6, "Param 6"),
            (10, "Param 10"),
            (13, "Param 13"),
            (2, "Param 2"),
            (39, "Param 39"),
            (40, "Param 40"),
            (37, "Param 37"),
        ],
    },

    "Ultra Analog VA-3": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },


    # =====================================================================
    #  AMPLE SOUND
    # =====================================================================

    "Ample Bass P Lite II": {
        "params": [
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (30, "Param 30"),
            (31, "Param 31"),
            (12, "Param 12"),
            (0, "Param 0"),
        ],
    },

    "Ample Bass U": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "Ample Ethno U": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "Ample Guitar LP": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "Ample Guitar M": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "Ample Guitar M II Lite": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (18, "Param 18"),
            (19, "Param 19"),
            (20, "Param 20"),
            (24, "Param 24"),
            (28, "Param 28"),
            (2, "Param 2"),
        ],
    },

    "Ample Percussion Cloudrum": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },


    # =====================================================================
    #  SOFTUBE
    # =====================================================================

    "Model 72 Synthesizer System": {
        "params": [
            (29, "Param 29"),
            (30, "Param 30"),
            (38, "Param 38"),
            (39, "Param 39"),
            (6, "Param 6"),
            (10, "Param 10"),
            (12, "Param 12"),
            (41, "Param 41"),
        ],
    },

    "Model 80 Five Voice Synthesizer": {
        "params": [
            (34, "Param 34"),
            (35, "Param 35"),
            (42, "Param 42"),
            (45, "Param 45"),
            (56, "Param 56"),
            (17, "Param 17"),
            (22, "Param 22"),
            (54, "Param 54"),
        ],
    },


    # =====================================================================
    #  DSP (discodsp)
    # =====================================================================

    "Discovery": {
        "params": [
            (40, "Param 40"),
            (42, "Param 42"),
            (22, "Param 22"),
            (28, "Param 28"),
            (2, "Param 2"),
            (55, "Param 55"),
            (60, "Param 60"),
            (264, "Param 264"),
        ],
    },

    "Discovery Pro": {
        "params": [
            (40, "Param 40"),
            (42, "Param 42"),
            (22, "Param 22"),
            (28, "Param 28"),
            (2, "Param 2"),
            (55, "Param 55"),
            (60, "Param 60"),
            (264, "Param 264"),
        ],
    },

    "OB-Xd": {
        "params": [
            (44, "Param 44"),
            (45, "Param 45"),
            (46, "Param 46"),
            (21, "Param 21"),
            (40, "Param 40"),
            (41, "Param 41"),
            (29, "Param 29"),
            (2, "Param 2"),
        ],
    },

    "OPL": {
        "params": [
            (20, "Param 20"),
            (21, "Param 21"),
            (22, "Param 22"),
            (23, "Param 23"),
            (13, "Param 13"),
            (6, "Param 6"),
            (7, "Param 7"),
            (4, "Param 4"),
        ],
    },

    "Phantom": {
        "params": [
            (30, "Param 30"),
            (32, "Param 32"),
            (144, "Param 144"),
            (152, "Param 152"),
            (7, "Param 7"),
            (70, "Param 70"),
            (75, "Param 75"),
            (0, "Param 0"),
        ],
    },

    "Vertigo": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (12, "Param 12"),
            (20, "Param 20"),
            (35, "Param 35"),
            (31, "Param 31"),
            (40, "Param 40"),
            (84, "Param 84"),
        ],
    },


    # =====================================================================
    #  BLEASS
    # =====================================================================

    "BLEASS Alpha": {
        "params": [
            (49, "Param 49"),
            (50, "Param 50"),
            (61, "Param 61"),
            (64, "Param 64"),
            (6, "Param 6"),
            (109, "Param 109"),
            (118, "Param 118"),
            (0, "Param 0"),
        ],
    },

    "BLEASS Monolit": {
        "params": [
            (62, "Param 62"),
            (63, "Param 63"),
            (47, "Param 47"),
            (50, "Param 50"),
            (6, "Param 6"),
            (39, "Param 39"),
            (43, "Param 43"),
            (0, "Param 0"),
        ],
    },

    "BLEASS Omega": {
        "params": [
            (89, "Param 89"),
            (90, "Param 90"),
            (116, "Param 116"),
            (119, "Param 119"),
            (9, "Param 9"),
            (168, "Param 168"),
            (177, "Param 177"),
            (0, "Param 0"),
        ],
    },


    # =====================================================================
    #  W.A. PRODUCTION
    # =====================================================================

    "W.A Production Ascension": {
        "params": [
            (96, "Param 96"),
            (97, "Param 97"),
            (71, "Param 71"),
            (72, "Param 72"),
            (73, "Param 73"),
            (74, "Param 74"),
            (89, "Param 89"),
            (90, "Param 90"),
        ],
    },

    "W.A Production Babylon": {
        "params": [
            (76, "Param 76"),
            (77, "Param 77"),
            (69, "Param 69"),
            (70, "Param 70"),
            (71, "Param 71"),
            (72, "Param 72"),
            (80, "Param 80"),
            (81, "Param 81"),
        ],
    },

    "W.A Production Instachord": {
        "params": [
            (0, "Param 0"),
            (2, "Param 2"),
            (3, "Param 3"),
            (10, "Param 10"),
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
        ],
    },


    # =====================================================================
    #  TOONTRACK
    # =====================================================================

    "EZDrummer": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "EZKeys": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "EZbass": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },


    # =====================================================================
    #  THIRD PARTY / OTHER
    # =====================================================================

    "ADM_CM": {
        "params": [
            (33, "Param 33"),
            (34, "Param 34"),
            (29, "Param 29"),
            (30, "Param 30"),
            (35, "Param 35"),
            (27, "Param 27"),
            (5, "Param 5"),
            (32, "Param 32"),
        ],
    },

    "ALPHA_RAY": {
        "params": [
            (26, "Param 26"),
            (85, "Param 85"),
            (30, "Param 30"),
            (106, "Param 106"),
            (107, "Param 107"),
            (109, "Param 109"),
            (110, "Param 110"),
            (119, "Param 119"),
        ],
    },

    "Addictive Keys": {
        "params": [
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
        ],
    },

    "Air LoomII": {
        "params": [
            (15, "Param 15"),
            (2, "Param 2"),
            (22, "Param 22"),
            (25, "Param 25"),
            (5, "Param 5"),
            (4, "Param 4"),
            (52, "Param 52"),
            (53, "Param 53"),
        ],
    },

    "BA-1": {
        "params": [
            (22, "Param 22"),
            (23, "Param 23"),
            (30, "Param 30"),
            (8, "Param 8"),
            (4, "Param 4"),
            (5, "Param 5"),
            (40, "Param 40"),
            (20, "Param 20"),
        ],
    },

    "Bells": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (8, "Param 8"),
            (9, "Param 9"),
            (14, "Param 14"),
            (15, "Param 15"),
            (16, "Param 16"),
            (10, "Param 10"),
        ],
    },

    "Black": {
        "params": [
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (9, "Param 9"),
            (15, "Param 15"),
            (16, "Param 16"),
            (10, "Param 10"),
        ],
    },

    "BlueARP": {
        "params": [
            (278, "Param 278"),
            (279, "Param 279"),
            (280, "Param 280"),
            (281, "Param 281"),
            (282, "Param 282"),
            (283, "Param 283"),
            (284, "Param 284"),
            (285, "Param 285"),
        ],
    },

    "Brass": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (8, "Param 8"),
            (9, "Param 9"),
            (14, "Param 14"),
            (15, "Param 15"),
            (16, "Param 16"),
            (10, "Param 10"),
        ],
    },

    "Clean Electric Guitar": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Crystal": {
        "params": [
            (44, "Param 44"),
            (39, "Param 39"),
            (45, "Param 45"),
            (145, "Param 145"),
            (50, "Param 50"),
            (475, "Param 475"),
            (476, "Param 476"),
            (526, "Param 526"),
        ],
    },

    "Curve2CM": {
        "params": [
            (89, "Param 89"),
            (90, "Param 90"),
            (32, "Param 32"),
            (36, "Param 36"),
            (59, "Param 59"),
            (0, "Param 0"),
            (2, "Param 2"),
            (4, "Param 4"),
        ],
    },

    "DJX10": {
        "params": [
            (6, "Param 6"),
            (7, "Param 7"),
            (15, "Param 15"),
            (18, "Param 18"),
            (9, "Param 9"),
            (3, "Param 3"),
            (4, "Param 4"),
            (24, "Param 24"),
        ],
    },

    "DPiano-A": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (10, "Param 10"),
            (11, "Param 11"),
            (5, "Param 5"),
            (12, "Param 12"),
        ],
    },

    "DPiano-E": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "DS Thorn": {
        "params": [
            (93, "Param 93"),
            (94, "Param 94"),
            (95, "Param 95"),
            (104, "Param 104"),
            (105, "Param 105"),
            (106, "Param 106"),
            (107, "Param 107"),
            (14, "Param 14"),
        ],
    },

    "DUNE 3": {
        "params": [
            (75, "Param 75"),
            (76, "Param 76"),
            (79, "Param 79"),
            (87, "Param 87"),
            (88, "Param 88"),
            (89, "Param 89"),
            (90, "Param 90"),
            (0, "Param 0"),
        ],
    },

    "Decent Sampler": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Dexed": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (4, "Param 4"),
            (5, "Param 5"),
            (31, "Param 31"),
            (53, "Param 53"),
            (75, "Param 75"),
            (97, "Param 97"),
        ],
    },

    "Dune": {
        "params": [
            (28, "Param 28"),
            (29, "Param 29"),
            (18, "Param 18"),
            (21, "Param 21"),
            (57, "Param 57"),
            (0, "Param 0"),
            (5, "Param 5"),
            (12, "Param 12"),
        ],
    },

    "EON-Arp": {
        "params": [
            (24, "Param 24"),
            (25, "Param 25"),
            (19, "Param 19"),
            (22, "Param 22"),
            (10, "Param 10"),
            (32, "Param 32"),
            (30, "Param 30"),
            (8, "Param 8"),
        ],
    },

    "Efx MOTIONS": {
        "params": [
            (66, "Param 66"),
            (67, "Param 67"),
            (69, "Param 69"),
            (65, "Param 65"),
            (60, "Param 60"),
            (412, "Param 412"),
            (413, "Param 413"),
            (1, "Param 1"),
        ],
    },

    "Einklang - CM": {
        "params": [
            (7, "Param 7"),
            (6, "Param 6"),
            (0, "Param 0"),
            (1, "Param 1"),
            (4, "Param 4"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
        ],
    },

    "ElectraX64": {
        "params": [
            (97, "Param 97"),
            (99, "Param 99"),
            (924, "Param 924"),
            (925, "Param 925"),
            (926, "Param 926"),
            (1020, "Param 1020"),
            (1022, "Param 1022"),
            (0, "Param 0"),
        ],
    },

    "EvaBeats Melody Sauce 2": {
        "params": [
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
        ],
    },

    "Fathom": {
        "params": [
            (25, "Param 25"),
            (26, "Param 26"),
            (27, "Param 27"),
            (28, "Param 28"),
            (29, "Param 29"),
            (30, "Param 30"),
            (31, "Param 31"),
            (32, "Param 32"),
        ],
    },

    "Feelyoursound RandARP": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (4, "Param 4"),
            (5, "Param 5"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
        ],
    },

    "Forager Mini": {
        "params": [
            (0, "Param 0"),
            (2, "Param 2"),
            (8, "Param 8"),
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
        ],
    },

    "Frozen Pain Obelisk": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Fruity Envelope Controller": {
        "params": [
            (88, "Mod X"),
            (89, "Mod Y"),
            (0, "Base Level"),
            (1, "Env Level"),
            (3, "Atk Scale"),
            (4, "Decay Scale"),
            (5, "Sustain Offset"),
            (6, "Release Scale"),
        ],
    },

    "Fruity Keyboard Controller": {
        "params": [
            (0, "Atk Smooth"),
            (1, "Rel Smooth"),
        ],
    },

    "Fruity Slicer": {
        "params": [
            (2, "Filter Cutoff"),
            (3, "Filter Res"),
            (5, "Filter Type"),
        ],
    },

    "Futurephonic Rhythmizer": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (4, "Param 4"),
            (5, "Param 5"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
        ],
    },

    "Generic": {
        "params": [
            (90, "Cutoff"),
            (91, "Resonance"),
            (92, "Attack"),
            (93, "Release"),
            (94, "Modulation"),
            (89, "Volume"),
        ],
    },

    "Genesis Pro": {
        "params": [
            (263, "Param 263"),
            (278, "Param 278"),
            (262, "Param 262"),
            (267, "Param 267"),
            (20, "Param 20"),
            (0, "Param 0"),
            (28, "Param 28"),
            (7, "Param 7"),
        ],
    },

    "Gorilla Bass": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Harvest-MINI": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (15, "Param 15"),
            (16, "Param 16"),
            (17, "Param 17"),
            (18, "Param 18"),
            (19, "Param 19"),
            (20, "Param 20"),
        ],
    },

    "HatefishRhyGeneratorOne": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Helm": {
        "params": [
            (13, "Param 13"),
            (29, "Param 29"),
            (30, "Param 30"),
            (26, "Param 26"),
            (0, "Param 0"),
            (1, "Param 1"),
            (3, "Param 3"),
            (2, "Param 2"),
        ],
    },

    "Hybrid": {
        "params": [
            (159, "Param 159"),
            (160, "Param 160"),
            (161, "Param 161"),
            (117, "Param 117"),
            (132, "Param 132"),
            (144, "Param 144"),
            (193, "Param 193"),
            (668, "Param 668"),
        ],
    },

    "Hype": {
        "params": [
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
            (6, "Param 6"),
            (7, "Param 7"),
            (4, "Param 4"),
            (5, "Param 5"),
            (61, "Param 61"),
        ],
    },

    "Izotope BreakTweaker": {
        "params": [
            (1, "Param 1"),
            (3, "Param 3"),
            (5, "Param 5"),
            (7, "Param 7"),
            (9, "Param 9"),
            (11, "Param 11"),
            (2, "Param 2"),
            (4, "Param 4"),
        ],
    },

    "KV331 SynthMaster Player": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "KiloHearts Phase Plant": {
        "params": [
            (7, "Param 7"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
            (11, "Param 11"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
        ],
    },

    "MNDALA": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "MNDALA 2": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (0, "Param 0"),
            (1, "Param 1"),
        ],
    },

    "Neo Piano": {
        "params": [
            (35, "Param 35"),
            (34, "Param 34"),
            (33, "Param 33"),
            (8, "Param 8"),
            (9, "Param 9"),
            (15, "Param 15"),
            (16, "Param 16"),
            (20, "Param 20"),
        ],
    },

    "Oddity 2": {
        "params": [
            (494, "Param 494"),
            (509, "Param 509"),
            (149, "Param 149"),
            (194, "Param 194"),
            (69, "Param 69"),
            (637, "Param 637"),
            (682, "Param 682"),
            (600, "Param 600"),
        ],
    },

    "Oddity3": {
        "params": [
            (485, "Param 485"),
            (500, "Param 500"),
            (358, "Param 358"),
            (362, "Param 362"),
            (267, "Param 267"),
            (1086, "Param 1086"),
            (1087, "Param 1087"),
            (0, "Param 0"),
        ],
    },

    "One": {
        "params": [
            (5, "Param 5"),
            (6, "Param 6"),
            (3, "Param 3"),
            (7, "Param 7"),
            (10, "Param 10"),
            (22, "Param 22"),
            (3, "Param 3"),
            (24, "Param 24"),
        ],
    },

    "Pastoral Piano": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Pluginguru Unify": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Retro Cazio": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "SEM": {
        "params": [
            (12, "Param 12"),
            (13, "Param 13"),
            (18, "Param 18"),
            (19, "Param 19"),
            (66, "Param 66"),
            (89, "Param 89"),
            (90, "Param 90"),
            (87, "Param 87"),
        ],
    },

    "SSL Native Bus Compressor 2": {
        "params": [
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
            (1, "Param 1"),
        ],
    },

    "Serum": {
        "params": [
            (45, "Param 45"),
            (46, "Param 46"),
            (35, "Param 35"),
            (37, "Param 37"),
            (218, "Param 218"),
            (219, "Param 219"),
            (220, "Param 220"),
            (221, "Param 221"),
        ],
    },

    "Sonic Academy ANA2": {
        "params": [
            (265, "Param 265"),
            (266, "Param 266"),
            (403, "Param 403"),
            (404, "Param 404"),
            (405, "Param 405"),
            (406, "Param 406"),
            (199, "Param 199"),
            (201, "Param 201"),
        ],
    },

    "Sonic Academy Kick 2": {
        "params": [
            (2, "Param 2"),
            (6, "Param 6"),
            (10, "Param 10"),
            (14, "Param 14"),
            (83, "Param 83"),
            (89, "Param 89"),
            (57, "Param 57"),
            (58, "Param 58"),
        ],
    },

    "Soundspot Union": {
        "params": [
            (409, "Param 409"),
            (410, "Param 410"),
            (296, "Param 296"),
            (315, "Param 315"),
            (334, "Param 334"),
            (249, "Param 249"),
            (279, "Param 279"),
            (265, "Param 265"),
        ],
    },

    "Spire": {
        "params": [
            (103, "Param 103"),
            (104, "Param 104"),
            (43, "Param 43"),
            (33, "Param 33"),
            (34, "Param 34"),
            (248, "Param 248"),
            (287, "Param 287"),
            (9, "Param 9"),
        ],
    },

    "Spire_x64_v1.5.11": {
        "params": [
            (103, "Param 103"),
            (104, "Param 104"),
            (43, "Param 43"),
            (33, "Param 33"),
            (34, "Param 34"),
            (248, "Param 248"),
            (287, "Param 287"),
            (9, "Param 9"),
        ],
    },

    "Surge XT": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
        ],
    },

    "Sylenth1": {
        "params": [
            (42, "Param 42"),
            (45, "Param 45"),
            (0, "Param 0"),
            (2, "Param 2"),
            (61, "Param 61"),
            (69, "Param 69"),
            (70, "Param 70"),
            (68, "Param 68"),
        ],
    },

    "Synapse Audio The Legend": {
        "params": [
            (34, "Param 34"),
            (35, "Param 35"),
            (36, "Param 36"),
            (33, "Param 33"),
            (43, "Param 43"),
            (44, "Param 44"),
            (45, "Param 45"),
            (46, "Param 46"),
        ],
    },

    "Synapse Audio Zampler": {
        "params": [
            (28, "Param 28"),
            (29, "Param 29"),
            (30, "Param 30"),
            (26, "Param 26"),
            (18, "Param 18"),
            (19, "Param 19"),
            (20, "Param 20"),
            (21, "Param 21"),
        ],
    },

    "Synth1 VSTi": {
        "params": [
            (19, "Param 19"),
            (20, "Param 20"),
            (76, "Param 76"),
            (45, "Param 45"),
            (2, "Param 2"),
            (5, "Param 5"),
            (44, "Param 44"),
            (254, "Param 254"),
        ],
    },

    "Thorn CM": {
        "params": [
            (66, "Param 66"),
            (67, "Param 67"),
            (71, "Param 71"),
            (74, "Param 74"),
            (30, "Param 30"),
            (52, "Param 52"),
            (15, "Param 15"),
            (0, "Param 0"),
        ],
    },

    "Tone2 FireBird": {
        "params": [
            (17, "Param 17"),
            (18, "Param 18"),
            (20, "Param 20"),
            (19, "Param 19"),
            (28, "Param 28"),
            (29, "Param 29"),
            (30, "Param 30"),
            (31, "Param 31"),
        ],
    },

    "Traktion BioTek": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (8, "Param 8"),
            (9, "Param 9"),
            (10, "Param 10"),
            (13, "Param 13"),
        ],
    },

    "UVIWorkstation": {
        "params": [
            (0, "Param 0"),
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (7, "Param 7"),
            (8, "Param 8"),
        ],
    },

    "VPS Avenger": {
        "params": [
            (760, "Param 760"),
            (763, "Param 763"),
            (1173, "Param 1173"),
            (1174, "Param 1174"),
            (1175, "Param 1175"),
            (31, "Param 31"),
            (3, "Param 3"),
            (728, "Param 728"),
        ],
    },

    "VacuumPro": {
        "params": [
            (16, "Param 16"),
            (17, "Param 17"),
            (45, "Param 45"),
            (46, "Param 46"),
            (47, "Param 47"),
            (48, "Param 48"),
            (49, "Param 49"),
            (50, "Param 50"),
        ],
    },

    "Vanguard": {
        "params": [
            (7, "Param 7"),
            (8, "Param 8"),
            (69, "Param 69"),
            (68, "Param 68"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (124, "Param 124"),
        ],
    },

    "Velvet": {
        "params": [
            (13, "Param 13"),
            (14, "Param 14"),
            (19, "Param 19"),
            (22, "Param 22"),
            (25, "Param 25"),
            (27, "Param 27"),
            (29, "Param 29"),
            (91, "Param 91"),
        ],
    },

    "Vital": {
        "params": [
            (211, "Param 211"),
            (212, "Param 212"),
            (213, "Param 213"),
            (214, "Param 214"),
            (396, "Param 396"),
            (397, "Param 397"),
            (382, "Param 382"),
            (391, "Param 391"),
        ],
    },

    "iZotope Iris 2": {
        "params": [
            (18, "Param 18"),
            (19, "Param 19"),
            (73, "Param 73"),
            (72, "Param 72"),
            (71, "Param 71"),
            (70, "Param 70"),
            (10, "Param 10"),
            (8, "Param 8"),
        ],
    },

    "impOSCar2": {
        "params": [
            (2, "Param 2"),
            (1, "Param 1"),
            (25, "Param 25"),
            (28, "Param 28"),
            (9, "Param 9"),
            (43, "Param 43"),
            (45, "Param 45"),
            (8, "Param 8"),
        ],
    },

    "kHs ONE": {
        "params": [
            (23, "Param 23"),
            (24, "Param 24"),
            (15, "Param 15"),
            (18, "Param 18"),
            (76, "Param 76"),
            (40, "Param 40"),
            (30, "Param 30"),
            (98, "Param 98"),
        ],
    },

    "miniBitCM": {
        "params": [
            (7, "Param 7"),
            (8, "Param 8"),
            (3, "Param 3"),
            (6, "Param 6"),
            (12, "Param 12"),
            (13, "Param 13"),
            (14, "Param 14"),
            (5, "Param 5"),
        ],
    },

    "rgcAudio Square I": {
        "params": [
            (32, "Param 32"),
            (33, "Param 33"),
            (35, "Param 35"),
            (36, "Param 36"),
            (37, "Param 37"),
            (52, "Param 52"),
            (62, "Param 62"),
            (59, "Param 59"),
        ],
    },

    "theRiser": {
        "params": [
            (1, "Param 1"),
            (2, "Param 2"),
            (3, "Param 3"),
            (4, "Param 4"),
            (5, "Param 5"),
            (6, "Param 6"),
            (7, "Param 7"),
            (8, "Param 8"),
        ],
    },

}


# ---------------------------------------------------------------------------
#  Lookup functions
# ---------------------------------------------------------------------------

def get_plugin_params(plugin_name):
    """Look up macro parameters for a plugin. Returns list of (index, name) or None."""
    entry = PLUGIN_DB.get(plugin_name)
    if entry is not None:
        return entry["params"]
    return None


def get_plugin_special(plugin_name):
    """Look up special hardware bindings for a plugin. Returns dict or None."""
    entry = PLUGIN_DB.get(plugin_name)
    if entry is not None:
        return entry.get("special")
    return None


def is_plugin_known(plugin_name):
    """Check if a plugin has a database entry."""
    return plugin_name in PLUGIN_DB


def debug_plugin_params(plugin_name):
    """Print all known params for a plugin (for Script Output debugging)."""
    entry = PLUGIN_DB.get(plugin_name)
    if entry is None:
        print("[PluginDB] '%s' NOT FOUND in database" % plugin_name)
        return
    print("[PluginDB] '%s' — %d params:" % (plugin_name, len(entry["params"])))
    for i, (idx, name) in enumerate(entry["params"]):
        if idx != NOT_MAPPED:
            print("  Slot %d: index=%d  name='%s'" % (i, idx, name))
        else:
            print("  Slot %d: (not mapped)" % i)
    special = entry.get("special")
    if special:
        print("  Special: %s" % str(special))
