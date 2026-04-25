# Handler Chain — MIDI Event Processing

---
module: device_KeyLabmkII.py
function: OnMidiMsg()
pattern: Chain of Responsibility
---

## Handler Chain (Priorität von oben nach unten)

```
┌─────────────────────────────────────────────────────────────────┐
│  MIDI Event kommt rein (event.midiId, event.data1, event.data2)  │
└─────────────────┬───────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ 1. handle_transport()               │
│    - Play/Stop/Record               │
│    - Loop, Metronome, Tap Tempo     │
│    - Rewind/Fast-Forward (mit Jog)  │
│    - Cut/Undo (kombinierte Logik)   │
└──────────────┬────────────────────────┘
               │ returns True → event.handled = True, return
               │ returns False → next handler
               ▼
┌─────────────────────────────────────┐
│ 2. handle_daw_commands()            │
│    - Track Buttons (Solo/Mute/Arm)  │
│    - DAW Control Encoder            │
│    - Preset Prev/Next               │
└──────────────┬────────────────────────┘
               │ returns True → event.handled = True, return
               │ returns False → next handler
               ▼
┌─────────────────────────────────────┐
│ 3. handle_navigation()                │
│    - Jog Wheel (Turn + Push)         │
│    - Window Switcher                 │
│    - Browser/Mixer/Channel Focus      │
│    - Pattern Prev/Next              │
└──────────────┬────────────────────────┘
               │ returns True → event.handled = True, return
               │ returns False → next handler
               ▼
┌─────────────────────────────────────┐
│ 4. handle_plugin_encoder()            │
│    - Encoders 1-8 im Plugin Mode     │
│    - Plugin-Special-Jog (falls aktiv)│
└──────────────┬────────────────────────┘
               │ returns True → event.handled = True, return
               │ returns False → next handler
               ▼
┌─────────────────────────────────────┐
│ 5. handle_mixer()                     │
│    - Fader (Pitch Bend, Ch 0-8)      │
│    - Encoder (Pan, CC 16-24)         │
│    - Track Buttons (Note 24-32)      │
│    - Bank Prev/Next (Note 48-49)     │
│    - Free Mode Check (Passthrough)    │
└──────────────┬────────────────────────┘
               │ returns True → event.handled = True, return
               │ returns False → log unhandled
               ▼
┌─────────────────────────────────────┐
│ 6. Log unhandled event              │
│    print("MIDI | id: %d  data1: %d...")
└─────────────────────────────────────┘
```

## Entscheidungsbaum (vereinfacht)

```python
# In jedem Handler:
def handle_xxx(event, state, pages):
    # 1. Filter: Ist das Event für diesen Handler?
    if not _is_my_event(event):
        return False
    
    # 2. State-Check: Modus erlaubt Handling?
    if state.some_mode_blocks_this:
        return False  # Passthrough
    
    # 3. Aktion ausführen
    _do_action(event, state)
    
    # 4. Display-Update (optional)
    pages.SetPageLines('xxx', line1='...', line2='...')
    
    return True  # Event consumed
```

## Handler-Integration (Code-Pattern)

**Neuen Handler hinzufügen:**

1. **Import** in `device_KeyLabmkII.py`:
```python
from keylab_newfeature import handle_newfeature
```

2. **In Chain einhängen** (Reihenfolge beachten!):
```python
def OnMidiMsg(event):
    if handle_transport(event, _state, _pages):
        event.handled = True
        return
    
    if handle_newfeature(event, _state, _pages):  # ← Hier einfügen
        event.handled = True
        return
    
    if handle_mixer(event, _state, _pages):
        event.handled = True
        return
```

3. **State-Attribute** in `keylab_state.py` hinzufügen (falls nötig)

## Besondere Regeln

### Plugin Mode Override
- `state.plugin_mode = True` → Mixer Fader 1-8, Encoder 1-8, Track Buttons 1-8 sind **deaktiviert**
- Master (Fader/Encoder/Button 9) bleibt **immer aktiv**
- Siehe: `keylab_mixer.py:63-66`, `keylab_mixer.py:75-78`, `keylab_mixer.py:86-89`

### Free Mode Override
- `state.free_mode = True` → Slots 1-8 werden durchgereicht (`return False`)
- Master bleibt aktiv
- Siehe: `free_mode.md`

### Event.handled Semantik
- `True` = FL Studio verarbeitet dieses Event nicht weiter
- `False` = FL Studio kann das Event verwenden (z.B. für "Link to Controller")
