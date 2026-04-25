# Global Controls — Codemap

**Port:** DAW Port  
**Message Type:** Note On  
**Channel:** 1

---

| Control | Data1 (Note) | Constant | Function |
| :--- | :--- | :--- | :--- |
| Save | 80 | `GlobalControl.SAVE` | Save project |
| In | 87 | `GlobalControl.IN` | Toggle Pad Mode |
| Out | 88 | `GlobalControl.OUT` | Toggle Overdub |
| Metro | 89 | `GlobalControl.METRO` | Toggle Metronome |
| Undo | 81 | `GlobalControl.UNDO` | Undo |

---

## Python Constants

```python
SAVE    = 80
IN      = 87   # TogglePadMode
OUT     = 88   # ToggleOverdub
METRO   = 89
UNDO    = 81

ALL_NOTES = [80, 87, 88, 89, 81]
```
