# Navigation — Codemap

**Port:** DAW Port

---

| Control | Type | Data1 | Constant | Bemerkung |
| :--- | :--- | :--- | :--- | :--- |
| Jog Wheel (Drehen) | CC | 60 | `Navigation.JOG_WHEEL_CC` | Endlosregler: Rechts=1, Links=65 |
| Jog Wheel (Klick) | Note On | 84 | `Navigation.JOG_WHEEL_CLICK` | |
| Bank Left (<) | Note On | 98 | `Navigation.BANK_LEFT` | |
| Bank Right (>) | Note On | 99 | `Navigation.BANK_RIGHT` | |

---

## Python Constants

```python
JOG_WHEEL_CC    = 60   # CC: right=1, left=65
JOG_WHEEL_CLICK = 84   # Note On
BANK_LEFT       = 98   # Note On
BANK_RIGHT      = 99   # Note On

ALL_NOTES = [84, 98, 99]
```
