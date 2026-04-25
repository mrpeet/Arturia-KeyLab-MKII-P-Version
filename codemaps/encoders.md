# Encoders — Codemap

**Port:** DAW Port  
**Message Type:** CC  
**Relative Mode:** Rechts=1, Links=65

---

| Encoder | CC Nummer | Constant |
| :--- | :--- | :--- |
| Encoder 1 | 16 | `Encoder.ENC_1` |
| Encoder 2 | 17 | `Encoder.ENC_2` |
| Encoder 3 | 18 | `Encoder.ENC_3` |
| Encoder 4 | 19 | `Encoder.ENC_4` |
| Encoder 5 | 20 | `Encoder.ENC_5` |
| Encoder 6 | 21 | `Encoder.ENC_6` |
| Encoder 7 | 22 | `Encoder.ENC_7` |
| Encoder 8 | 23 | `Encoder.ENC_8` |
| Encoder 9 (Master) | 24 | `Encoder.ENC_9` |

---

## Relative Encoder Detection

| Richtung | Wertebereich | Konstanten |
| :--- | :--- | :--- |
| Increment (Rechts) | 0–63 | `INCREMENT_MIN = 1`, `INCREMENT_MAX = 63` |
| Decrement (Links) | 64–127 | `DECREMENT_MIN = 64`, `DECREMENT_MAX = 127` |
| Legacy Rechts | 1 | `INCREMENT = 1` |
| Legacy Links | 65 | `DECREMENT = 65` |

---

## Python Constants

```python
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

ALL_CCS = [16, 17, 18, 19, 20, 21, 22, 23, 24]

# Relative encoder direction detection
INCREMENT_MIN = 1
INCREMENT_MAX = 63
DECREMENT_MIN = 64
DECREMENT_MAX = 127

# Legacy constants
INCREMENT = 1
DECREMENT = 65
```
