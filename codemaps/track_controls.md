# Track Controls — Codemap

**Port:** DAW Port  
**Message Type:** Note On  
**Channel:** 1

---

| Control | Data1 (Note) | Constant |
| :--- | :--- | :--- |
| Record | 0 | `TrackControl.RECORD` |
| Solo | 8 | `TrackControl.SOLO` |
| Mute | 16 | `TrackControl.MUTE` |
| Read | 74 | `TrackControl.READ` |
| Write | 75 | `TrackControl.WRITE` |

---

## Python Constants

```python
RECORD  = 0
SOLO    = 8
MUTE    = 16
READ    = 74
WRITE   = 75

ALL_NOTES = [0, 8, 16, 74, 75]
```
