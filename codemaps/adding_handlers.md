# Adding New Handlers — Template & Checklist

---
use_case: Neuer MIDI-Handler-Bereich (z.B. neue Button-Reihe, Pad-Modus, etc.)
prerequisite: Verständnis von handler_chain.md
---

## Checkliste

- [ ] 1. State-Attribute in `keylab_state.py` definieren (falls nötig)
- [ ] 2. MIDI-Konstanten in `keylab_config.py` hinzufügen (falls nötig)
- [ ] 3. Neues Handler-Modul `keylab_<feature>.py` erstellen
- [ ] 4. Handler in `device_KeyLabmkII.py` importieren
- [ ] 5. Handler in Chain einhängen (Reihenfolge beachten!)
- [ ] 6. `IMPLEMENTATION_MAP.md` Status aktualisieren
- [ ] 7. Test: Free Mode, Plugin Mode Interaktion

---

## Template: Neues Handler-Modul

```python
# keylab_newfeature.py
"""
KeyLab mkII — <Feature Name> Handler
Handles: <Welche MIDI-Events>
"""

from keylab_config import (
    # Importiere nur was du brauchst
    NOTE_ON_STATUS,
    NOTE_OFF_STATUS,
    CC_STATUS,
    # ...
)


def handle_newfeature(event, state, pages):
    """
    Handle <feature> events.
    
    Args:
        event: FL Studio MIDI event object
        state: KeyLabState instance
        pages: KeyLabPagedDisplay instance
    
    Returns:
        bool: True if handled, False otherwise
    """
    # --- Filter: Ist das Event für diesen Handler? ---
    if not _is_my_event(event):
        return False
    
    # --- Mode-Check: Darf dieses Feature aktuell laufen? ---
    if _is_blocked_by_mode(state):
        return False  # Passthrough
    
    # --- Event verarbeiten ---
    if event.midiId == NOTE_ON_STATUS:
        _do_button_press(event, state, pages)
    elif event.midiId == CC_STATUS:
        _do_encoder_turn(event, state)
    
    return True  # Event consumed


def _is_my_event(event):
    """Return True if this event belongs to this handler."""
    # Beispiel: Note Range prüfen
    # return NOTE_X <= event.data1 <= NOTE_Y
    pass


def _is_blocked_by_mode(state):
    """Return True if current mode blocks this handler."""
    # Beispiel: In Free Mode blockiert?
    # return state.free_mode
    pass


def _do_button_press(event, state, pages):
    """Handle Note On event."""
    # Deine Logik hier
    pass


def _do_encoder_turn(event, state):
    """Handle CC/Encoder event."""
    # Deine Logik hier
    pass
```

---

## Integration in `device_KeyLabmkII.py`

### 1. Import hinzufügen
```python
from keylab_transport import handle_transport
from keylab_daw_commands import handle_daw_commands
from keylab_navigation import handle_navigation
from keylab_plugin import handle_plugin_encoder, handle_plugin_special_jog
from keylab_mixer import handle_mixer
from keylab_newfeature import handle_newfeature  # ← HIER
```

### 2. In OnMidiMsg() einhängen

**WICHTIG**: Reihenfolge beachten! Spezifisch → Allgemein

```python
def OnMidiMsg(event):
    """Central dispatcher — routes MIDI events through the handler chain."""
    
    if handle_transport(event, _state, _pages):
        event.handled = True
        return

    if handle_daw_commands(event, _state, _pages):
        event.handled = True
        return

    if handle_newfeature(event, _state, _pages):  # ← HIER
        event.handled = True
        return

    if handle_navigation(event, _state, _pages):
        event.handled = True
        return

    if handle_plugin_encoder(event, _state, _pages):
        event.handled = True
        return

    if handle_mixer(event, _state, _pages):
        event.handled = True
        return

    # Unhandled...
```

---

## State-Änderungen

### In `keylab_state.py` hinzufügen:

```python
class KeyLabState:
    def __init__(self):
        # --- Bestehende Attribute ---
        self.focus_mode = FocusMode.MIXER
        # ...
        
        # --- Neue Feature-State ---
        self.newfeature_active = False
        self.newfeature_values = [0] * 8
```

### In `keylab_config.py` hinzufügen:

```python
class NewFeature:
    """<Feature> hardware mappings."""
    BUTTON_1 = 100  # Note number
    BUTTON_2 = 101
    # ...
    
    ALL_BUTTONS = range(BUTTON_1, BUTTON_2 + 1)
```

---

## Testing-Checklist

### Funktionalität
- [ ] Event wird korrekt erkannt
- [ ] Aktion wird ausgeführt
- [ ] `event.handled = True` wird gesetzt

### Inter-Feature-Kompatibilität
- [ ] **Free Mode**: Wenn Feature Slots 1-8 nutzt → müssen durchgereicht werden
- [ ] **Plugin Mode**: Feature deaktiviert wenn `state.plugin_mode = True`?
- [ ] **Banking**: Feature reagiert korrekt auf `state.bank_offset`?

### Performance
- [ ] Keine Loops in `OnMidiMsg` Path
- [ ] Keine Imports während Event-Handling
- [ ] Display-Updates nicht zu häufig (throttlen wenn nötig)

---

## Häufige Fehler

| Fehler | Symptom | Lösung |
|--------|---------|--------|
| `return False` vergessen | Event wird nicht an nächsten Handler weitergegeben, aber auch nicht gehandled | Explizit `return False` am Ende |
| `event.handled` nicht setzen | FL Studio verarbeitet Event zusätzlich | In `OnMidiMsg` setzen, nicht im Handler |
| Hardcoded MIDI-Werte | Inkonsistent, schwer wartbar | In `keylab_config.py` definieren |
| State direkt importieren | Zirkuläre Imports, schwer testbar | State als Parameter durchreichen |
