# Hardware Constants — MIDI Mappings

---
module: keylab_config.py
rule: NEVER hardcode MIDI values elsewhere — always import from keylab_config
---

## Fader (Pitch Bend)

| Hardware | MIDI | Konstante | Notizen |
|----------|------|-----------|---------|
| Fader 1 | PB, Channel 0 | `Fader.CHANNEL_1` (0) | 14-bit Wert (0-16383) |
| Fader 2 | PB, Channel 1 | `Fader.CHANNEL_2` (1) | |
| ... | ... | ... | |
| Fader 8 | PB, Channel 7 | `Fader.CHANNEL_8` (7) | |
| **Master** | PB, Channel 8 | `Fader.MASTER_CHANNEL` (8) | **Immer aktiv**, nie Free Mode |

**Wertebereich**: 14-bit Pitch Bend → `_pb_to_float()` gibt 0.0-1.0  
**FL Studio Mapping**: 0.8 = 100% Volume (über 100% möglich, aber nicht empfohlen)

### Fader Touch Sensoren

| Hardware | MIDI | Konstante |
|----------|------|-----------|
| Touch Fader 1 | Note 104, Ch 0 | `Fader.TOUCH_1` |
| Touch Fader 2 | Note 105, Ch 0 | `Fader.TOUCH_2` |
| ... | ... | ... |
| Touch Fader 8 | Note 111, Ch 0 | `Fader.TOUCH_8` |
| Touch Master | Note 112, Ch 0 | `Fader.TOUCH_MASTER` |

**Status**: Note On (0x90) = Finger auf Fader, Note Off (0x80) = Finger los

## Encoder (Control Change)

| Hardware | MIDI | Konstante | Funktion |
|----------|------|-----------|----------|
| Encoder 1 | CC 16, Ch 0 | `Encoder.CC_1` | Pan (Mixer Mode) / Plugin Param (Plugin Mode) |
| Encoder 2 | CC 17, Ch 0 | `Encoder.CC_2` | Pan / Plugin Param |
| ... | ... | ... | |
| Encoder 8 | CC 23, Ch 0 | `Encoder.CC_8` | Pan / Plugin Param |
| **Encoder 9 (Master)** | CC 24, Ch 0 | `Encoder.CC_MASTER` | Master Pan / Master Plugin Param |

**Wertebereich**: CC 0-127  
**Relative vs. Absolute**: Pan ist absolut (0-127 = L-C-R). Plugin-Params können relativ sein.

## Track Buttons

| Hardware | MIDI | Konstante |
|----------|------|-----------|
| Track Button 1 | Note 24, Ch 0 | `TrackButton.FIRST` (24) |
| Track Button 2 | Note 25, Ch 0 | |
| ... | ... | |
| Track Button 9 | Note 32, Ch 0 | `TrackButton.LAST` (32) |

**Funktion**: Abhängig von `state.track_button_mode`:
- `SELECT` → Track/Channel Select
- `SOLO` → Solo
- `MUTE` → Mute/Arm

## Bank Buttons

| Hardware | MIDI | Konstante | Funktion |
|----------|------|-----------|----------|
| Bank Prev | Note 48, Ch 0 | `BankButton.PREV_NOTE` | Kurz: Bank -8, Lang: Toggle Free Mode |
| Bank Next | Note 49, Ch 0 | `BankButton.NEXT_NOTE` | Kurz: Bank +8 |

## Transport Buttons

| Hardware | MIDI | Konstante | Funktion |
|----------|------|-----------|----------|
| Rewind | Note 112 | `Transport.REWIND` | Jog links / Previous Bar |
| Forward | Note 113 | `Transport.FORWARD` | Jog rechts / Next Bar |
| Stop | Note 114 | `Transport.STOP` | Stop |
| Play | Note 115 | `Transport.PLAY` | Play/Pause |
| Loop | Note 116 | `Transport.LOOP` | Pattern/Song Loop |
| Record | Note 117 | `Transport.RECORD` | Record |

## DAW Command Buttons

| Hardware | MIDI | Konstante | Funktion |
|----------|------|-----------|----------|
| Save | Note 80 | `DAWCommands.SAVE` | Save project |
| Punch In | Note 81 | `DAWCommands.PUNCH_IN` | Punch in/out |
| Punch Out | Note 82 | `DAWCommands.PUNCH_OUT` | |
| Metronome | Note 83 | `DAWCommands.METRONOME` | Toggle metronome |
| Undo | Note 84 | `DAWCommands.UNDO` | Undo |
|Redo | Note 85 | `DAWCommands.REDO` | Redo |
| QWERTY 1-6 | Note 86-91 | `DAWCommands.QWERTY_1` etc. | Custom mappings |
| Cut | Note 92 | `DAWCommands.CUT` | Cut + Undo (kombiniert) |

## MIDI Status Bytes (Hilfskonstanten)

```python
NOTE_ON_STATUS = 0x90      # 144
NOTE_OFF_STATUS = 0x80     # 128
CC_STATUS = 0xB0           # 176
PITCH_BEND_STATUS = 0xE0   # 224
```

**Pattern**: `event.midiId == PITCH_BEND_STATUS`

## SysEx Header

Alle SysEx-Messages zum KeyLab beginnen mit:
```python
SYSEX_PREFIX = [0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]
```

**Funktionen**:
- LCD Display Update
- Pad Farbsteuerung
- LED Feedback

Siehe: `keylab_dispatch.send_to_device()`

## Port-Konfiguration

| Script | Port | Zweck |
|--------|------|-------|
| `device_KeyLabmkII.py` | MIDIIN2 (Port 1) | Hauptsteuerung |
| `device_KeyLabmkII_Forward.py` | MIDIIN2 (Port 10) | V Collection Forwarding |

**Wichtig**: FL Studio MIDI Settings müssen beide Ports auf separate Input-Devices mappen, sonst Double-Handling!
