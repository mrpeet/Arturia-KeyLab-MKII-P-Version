# Arturia KeyLab MKII - Controller Overview

This document provides an overview of all defined surface controllers, their groups, names, and current functions in the FL Studio script.

## Group 1: Basic Keyboard Controller
*   **Pitch Bend** (Status `0xE0`): Standard Pitch Bend.
*   **Mod Wheel** (CC `1`): Standard Modulation Wheel.

## Group 2: Pads (Channel 10)
*   **Pads 1-16** (CC `36` - `51`):
    *   **Default Mode**: Triggers notes/drums based on the selected Pad Mode.
    *   **Sequencer Mode** (`SEQ_MODE = 1`): Used for step sequencing and editing graph editor parameters.
    *   **Pad Modes** (Toggled by Global Control 2):
        *   **FPC / Drum**: Mapped to FPC standard layout.
        *   **Chromatic**: Mapped chromatically starting from C3 (Note 48) upwards.

## Group 3: DAW Commands

### Track Controls
| Control | CC | Function | Description |
| :--- | :--- | :--- | :--- |
| **Control 1** | `8` | `NewPattern` | Creates a new empty pattern. |
| **Control 2** | `16` | `FocusMixer` | Focuses the Mixer window. |
| **Control 3** | `0` | `SnapToggle` | Toggles Snap mode between Line and None. |
| **Control 4** | `56` | `TapTempo` | Tap Tempo. |
| **Control 5** | `57` | `Redo` | Redo the last undone action. |

### Global Controls
| Control | CC | Function | Description |
| :--- | :--- | :--- | :--- |
| **Control 1** | `74` | `ToggleBrowserChannelRack` | Toggles focus between Channel Rack, Browser, and Mixer. |
| **Control 2** | `87` | `TogglePadMode` | **Short Press**: Toggles Pads between FPC/Drum and Chromatic modes.<br>**Long Press**: Toggles Pad Velocity On/Off. |
| **Control 3** | `88` | `ToggleOverdub` | Toggles Overdub recording mode. |
| **Control 4** | `89` | `MetronomeToggle` | Toggles the Metronome. |
| **Control 5** | `81` | `UndoOrCut` | **Short Press**: Undo.<br>**Long Press**: Cut selected. |

## Group 4: Transport Control
| Control | CC | Function | Description |
| :--- | :--- | :--- | :--- |
| **Rewind** | `91` | `RewindORprevBar` | Rewinds playback or moves to previous bar. |
| **Fast Forward** | `92` | `FastForwardORnextBar` | Fast forwards playback or moves to next bar. |
| **Stop** | `93` | `Stop` | Stops playback. |
| **Play** | `94` | `Start` | Starts playback. |
| **Record** | `95` | `Record` | Toggles recording. |
| **Loop** | `86` | `Loop` | Toggles Loop recording mode. |

## Group 5: Navigation
| Control | CC | Function | Description |
| :--- | :--- | :--- | :--- |
| **Left Arrow** | `98` | `previousPattern` | **Browser Focused**: Previous Tab.<br>**Plugin Focused**: Previous Preset.<br>**Other**: Previous Pattern. |
| **Right Arrow** | `99` | `nextPattern` | **Browser Focused**: Next Tab.<br>**Plugin Focused**: Next Preset.<br>**Other**: Next Pattern. |
| **Knob Turn** | `60` | `TrackSelectMainKnob` | Navigates/Selects based on focused window (Browser, Mixer, Channel Rack). |
| **Knob Push** | `84` | `SwitchWindow` | Switches focus or selects item based on context. |

## Group 6: Mixer & Parameter Control

### Knobs
*   **Knobs 1-8** (CC `74, 71, 76, 77, 93, 18, 19, 16`):
    *   **Mixer Mode**: Controls Track Pan.
    *   **Plugin Mode**: Controls Plugin Parameters.
*   **Knob 9** (CC `17`):
    *   **Mixer Mode**: Controls Master Pan (or Track 9 Pan).
    *   **Plugin Mode**: Controls Plugin Parameter.

### Faders
*   **Faders 1-8** (CC `73, 75, 79, 72, 80, 81, 82, 83`):
    *   **Mixer Mode**: Controls Track Volume.
    *   **Plugin Mode**: Controls Plugin Parameters.
*   **Fader 9** (CC `85`):
    *   **Mixer Mode**: Controls Master Volume.
    *   **Plugin Mode**: Controls Plugin Parameter.

### Track Buttons (Select/Solo/Mute)
*   **Buttons 1-8** (CC `22` - `29`):
    *   **Mixer Mode**: Selects Track.
    *   **Plugin Mode**: Controls Plugin Parameters.
    *   **Note**: `SoloChannel` (CC 8-15) and `MuteChannel` (CC 16-23) are also mapped to these physical buttons in different banks/modes on the hardware itself, but handled as separate CCs in the script.
        *   **Solo**: Solos the target channel/track.
        *   **Mute**: Mutes the target channel/track.
        *   **Select**: Selects the target channel/track.

## Modes & States
*   **Mixer Mode**: Toggled by `ToggleMixerChannelRack` (CC 51). Switches Knobs/Faders to control Mixer Pan/Vol.
*   **Sequencer Mode**: Logic exists (`DrumSeqToggle`), but it is currently **not mapped** to any button. Default is Drum/Pad mode.
*   **Pad Mode**: Toggled by Global Control 2.
