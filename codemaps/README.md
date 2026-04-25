# KeyLab mkII — CodeMaps

Übersicht aller MIDI-Codes und Konstanten für das Arturia KeyLab mkII FL Studio Script.

> **Source of truth:** `keylab_config.py`  
> **Hardware Referenz:** `hardware_map.md`

---

## Übersicht der CodeMaps

| Datei | Beschreibung |
| :--- | :--- |
| [transport.md](./transport.md) | Transport-Controls (Play, Stop, Record, etc.) |
| [track_controls.md](./track_controls.md) | Track-Controls (Record, Solo, Mute, Read, Write) |
| [global_controls.md](./global_controls.md) | Global-Controls (Save, Undo, Metro, etc.) |
| [navigation.md](./navigation.md) | Navigation (Jog Wheel, Bank Left/Right) |
| [faders.md](./faders.md) | 9 Fader (Pitch Bend) + Touch-Sensoren |
| [encoders.md](./encoders.md) | 9 Encoder (CC, Relative Mode) |
| [track_buttons.md](./track_buttons.md) | 9 Track-Buttons (Select/Mute/Solo) |
| [bank_buttons.md](./bank_buttons.md) | Bank/Part Buttons (Previous/Next) |
| [pads.md](./pads.md) | 16 Performance Pads (Note On, Channel 10) |
| [performance.md](./performance.md) | Performance-Sektion (Pitch Bend, Mod Wheel) |
| [pedals.md](./pedals.md) | Pedale (Sustain, Expression, Aux 1-3) |
| [midi_helpers.md](./midi_helpers.md) | MIDI Status Bytes, Velocity, SysEx |

---

## Ports

| Port | Verwendung |
| :--- | :--- |
| **Keys Port** | Klaviatur, Pads, Mod-Wheel, Pedale |
| **DAW Port** | Transport, Mixer, Navigation, DAW-Commands |

---

## Änderungen

Bei Änderungen an den Konstanten muss sowohl `keylab_config.py` als auch die entsprechende CodeMap-Datei aktualisiert werden.
