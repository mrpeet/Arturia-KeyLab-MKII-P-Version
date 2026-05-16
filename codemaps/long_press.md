# Long Press — Shared Detection

---
module: keylab_long_press.py
polled_from: device_KeyLabmkII.OnIdle()
threshold: 0.75 seconds
---

## Verhalten

1. **Press** → `begin(key, on_long, on_short)`
2. **OnIdle** → `poll()` feuert `on_long` einmal, sobald `elapsed >= 0.75 s` (Taste noch gedrückt)
3. **Release** → `release(key)` — `on_short` nur wenn Long **nicht** ausgelöst wurde

Long-Aktionen zeigen LCD-Hinweise **in** `on_long` (sofort bei Erreichen der Schwelle).

## Verwendende Controls

| Key | Modul | Short | Long |
|-----|-------|-------|------|
| `daw_undo` | `keylab_daw_commands.py` | Undo (Write) | Cut |
| `daw_in` | `keylab_daw_commands.py` | Pad-Modus | Pad-Velocity |
| `('track_btn', index)` | `keylab_mixer.py` | Mute | Pan Reset / Solo |
| `bank_prev` | `keylab_mixer.py` | Bank −1 | Free Mode |

## API

```python
import keylab_long_press as long_press

long_press.begin('my_key', on_long=lambda: ..., on_short=lambda: ...)
long_press.release('my_key')
long_press.poll()  # nur aus OnIdle
```
