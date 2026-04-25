# Pedals — Codemap

**Port:** Keys Port  
**Channel:** 1  
**Message Type:** CC  
**Wertebereich:** 0 bis 127

---

| Anschluss | CC | Constant | Bemerkung |
| :--- | :--- | :--- | :--- |
| Sustain Pedal | 64 | `Pedal.SUSTAIN` | 0 = Losgelassen, 127 = Gedrückt |
| Expression Pedal | 11 | `Pedal.EXPRESSION` | 0–127 (Stufenlos) |
| Aux 1 Pedal | 12 | `Pedal.AUX_1` | 0–127 (Stufenlos) |
| Aux 2 Pedal | 13 | `Pedal.AUX_2` | 0–127 (Stufenlos) |
| Aux 3 Pedal | 14 | `Pedal.AUX_3` | 0–127 (Stufenlos) |

---

## Python Constants

```python
SUSTAIN    = 64
EXPRESSION = 11
AUX_1      = 12
AUX_2      = 13
AUX_3      = 14

ALL_CCS = [64, 11, 12, 13, 14]
```
