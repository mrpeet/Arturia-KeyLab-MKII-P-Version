# Performance Pads — Codemap

**Port:** Keys Port  
**Channel:** 10 (0-indexed: 9)  
**Messages:** Note On + Poly Aftertouch

---

## Physical Layout (4x4 Grid)

| | Spalte 1 | Spalte 2 | Spalte 3 | Spalte 4 |
| :--- | :--- | :--- | :--- | :--- |
| **Reihe 1 (oben)** | Pad 1: 48 | Pad 2: 49 | Pad 3: 50 | Pad 4: 51 |
| **Reihe 2** | Pad 5: 44 | Pad 6: 45 | Pad 7: 46 | Pad 8: 47 |
| **Reihe 3** | Pad 9: 40 | Pad 10: 41 | Pad 11: 42 | Pad 12: 43 |
| **Reihe 4 (unten)** | Pad 13: 36 | Pad 14: 37 | Pad 15: 38 | Pad 16: 39 |

---

## Python Constants

```python
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
```
