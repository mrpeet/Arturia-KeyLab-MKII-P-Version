# Transport Controls — Codemap

**Port:** DAW Port  
**Message Type:** Note On  
**Channel:** 1

---

| Control | Data1 (Note) | Constant |
| :--- | :--- | :--- |
| Rewind (<<) | 91 | `Transport.REWIND` |
| Fast Fwd (>>) | 92 | `Transport.FAST_FWD` |
| Stop | 93 | `Transport.STOP` |
| Play | 94 | `Transport.PLAY` |
| Record | 95 | `Transport.RECORD` |
| Loop | 86 | `Transport.LOOP` |

---

## Python Constants

```python
REWIND      = 91
FAST_FWD    = 92
STOP        = 93
PLAY        = 94
RECORD      = 95
LOOP        = 86

ALL_NOTES = [91, 92, 93, 94, 95, 86]
```
