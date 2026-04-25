# Faders — Codemap

**Port:** DAW Port  
**Faders:** Pitch Bend (weiche Übergänge)  
**Touch:** Note On, Channel 1

---

## Pitch Bend Channels

| Fader | Kanal (0-indexed) | Status Byte | Constant |
| :--- | :--- | :--- | :--- |
| Fader 1 | 0 | 0xE0 | `Fader.CHANNEL_1` |
| Fader 2 | 1 | 0xE1 | `Fader.CHANNEL_2` |
| Fader 3 | 2 | 0xE2 | `Fader.CHANNEL_3` |
| Fader 4 | 3 | 0xE3 | `Fader.CHANNEL_4` |
| Fader 5 | 4 | 0xE4 | `Fader.CHANNEL_5` |
| Fader 6 | 5 | 0xE5 | `Fader.CHANNEL_6` |
| Fader 7 | 6 | 0xE6 | `Fader.CHANNEL_7` |
| Fader 8 | 7 | 0xE7 | `Fader.CHANNEL_8` |
| Fader 9 (Master) | 8 | 0xE8 | `Fader.CHANNEL_9` |

---

## Touch Sensors

| Fader | Touch Note | Constant |
| :--- | :--- | :--- |
| Fader 1 | 104 | `Fader.TOUCH_1` |
| Fader 2 | 105 | `Fader.TOUCH_2` |
| Fader 3 | 106 | `Fader.TOUCH_3` |
| Fader 4 | 107 | `Fader.TOUCH_4` |
| Fader 5 | 108 | `Fader.TOUCH_5` |
| Fader 6 | 109 | `Fader.TOUCH_6` |
| Fader 7 | 110 | `Fader.TOUCH_7` |
| Fader 8 | 111 | `Fader.TOUCH_8` |
| Fader 9 (Master) | 112 | `Fader.TOUCH_9` |

---

## Python Constants

```python
# Pitch Bend channels (0-indexed internally)
CHANNEL_1 = 0   # 0xE0
CHANNEL_2 = 1   # 0xE1
CHANNEL_3 = 2   # 0xE2
CHANNEL_4 = 3   # 0xE3
CHANNEL_5 = 4   # 0xE4
CHANNEL_6 = 5   # 0xE5
CHANNEL_7 = 6   # 0xE6
CHANNEL_8 = 7   # 0xE7
CHANNEL_9 = 8   # 0xE8 (Master)

MASTER_CHANNEL = 8
COUNT = 9
ALL_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# Touch sensor Note On values
TOUCH_1  = 104
TOUCH_2  = 105
TOUCH_3  = 106
TOUCH_4  = 107
TOUCH_5  = 108
TOUCH_6  = 109
TOUCH_7  = 110
TOUCH_8  = 111
TOUCH_9  = 112  # Master

ALL_TOUCH_NOTES = [104, 105, 106, 107, 108, 109, 110, 111, 112]
```
