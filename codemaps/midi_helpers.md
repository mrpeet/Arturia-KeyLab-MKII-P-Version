# MIDI Helpers — Codemap

## Status Bytes

| Message | Hex | Dezimal | Konstante |
| :--- | :--- | :--- | :--- |
| Note On | 0x90 | 144 | `NOTE_ON_STATUS` |
| Note Off | 0x80 | 128 | `NOTE_OFF_STATUS` |
| Control Change | 0xB0 | 176 | `CC_STATUS` |
| Pitch Bend | 0xE0 | 224 | `PITCH_BEND_STATUS` |

## Velocity Values

| Zustand | Wert | Konstante |
| :--- | :--- | :--- |
| Gedrückt | 127 | `PRESSED` |
| Losgelassen | 0 | `RELEASED` |

## SysEx Header

| Segment | Bytes |
| :--- | :--- |
| Header | `0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42` |
| Footer | `0xF7` |

---

## Python Constants

```python
NOTE_ON_STATUS  = 0x90  # 144
NOTE_OFF_STATUS = 0x80  # 128
CC_STATUS       = 0xB0  # 176
PITCH_BEND_STATUS = 0xE0  # 224

PRESSED  = 127
RELEASED = 0

SYSEX_HEADER = bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42])
SYSEX_FOOTER = bytes([0xF7])
```
