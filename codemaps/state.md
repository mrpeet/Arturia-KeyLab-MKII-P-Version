# KeyLabState — Central State Container

---
module: keylab_state.py
class: KeyLabState
created_in: device_KeyLabmkII.OnInit()
passed_to: All handler functions as `state` parameter
---

## State-Attribute nach Kategorie

### Focus & Modus

| Attribut | Typ | Werte | Beschreibung |
|----------|-----|-------|--------------|
| `focus_mode` | str | `FocusMode.MIXER`, `FocusMode.CHANNEL` | Bestimmt, ob Fader/Encoder Mixer oder Channel Rack steuern |
| `pad_mode` | str | `PadMode.FPC`, `PadMode.CHROMATIC` | Pad-Spielmodus (Drum vs. chromatisch) |
| `track_button_mode` | str | `TrackButtonMode.SELECT`, `SOLO`, `MUTE` | Was Track Buttons tun (zyklisch umschaltbar) |

### Banking

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `bank_offset` | int | Offset für Fader/Encoder-Bank (Schritte à 8). 0 = Tracks 1-8, 8 = Tracks 9-16, etc. |

### Free Mode

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `free_mode` | bool | `True` = Fader 1-8, Encoder 1-8, Track Buttons 1-8 werden durchgereicht (kein Handling). Slot 9 (Master) immer aktiv. |

**Activation**: Long Press (>1s) auf "Bank Prev" Button (Note 48). Siehe `keylab_mixer.py:_do_bank()`

**Deactivation**: Erneuter Long Press auf "Bank Prev"

### Fader-Management

| Attribut | Typ | Bereich | Beschreibung |
|----------|-----|---------|--------------|
| `FADER_JITTER_THRESHOLD` | int | 0-16383 | Min. Delta (14-bit) bevor Fader-Wert akzeptiert wird |
| `fader_last_sent_value` | list[int] | 8 Elemente | Letzter tatsächlich gesendeter 14-bit Wert pro Fader |
| `fader_pickup_active` | list[bool] | 9 Elemente (inkl. Master) | `True` = Physikalischer Fader hat Software-Wert gekreuzt |
| `fader_last_fl_value` | list[float] | 9 Elemente | Letzter bekannter FL Studio Volume-Wert (0.0-1.0) pro Slot |

**Soft Pickup Logik**: Siehe `keylab_mixer.py:_do_fader()`
1. Fader wird berührt → Touch-Note empfangen
2. Erster PB-Wert → Vergleich mit `fader_last_fl_value`
3. Wenn gekreuzt → `pickup_active = True`, Werte werden gesendet
4. Wenn nicht gekreuzt → Werte werden ignoriert

### Plugin Mode

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `plugin_mode` | bool | `True` wenn Plugin-Fenster fokussiert (außer `free_mode` override) |
| `last_plugin_name` | str | Cache: Letzter erkannter Plugin-Name |
| `plugin_encoder_values` | list[float] | Aktuelle Encoder-Werte für relative Steuerung (8 Slots) |

**Auto-Detection**: `device_KeyLabmkII._update_plugin_mode()` prüft `ui.getFocused(midi.widPlugin)`

## State-Änderungen erlauben vs. verbieten

**State darf gelesen werden von:**
- Allen Handlern (als Funktionsparameter)
- `OnRefresh`, `OnIdle` Callbacks

**State darf geschrieben werden von:**
- Handlern (z.B. `handle_mixer` setzt `bank_offset`)
- `device_KeyLabmkII._update_plugin_mode()` (setzt `plugin_mode`)

**State darf NICHT geschrieben werden von:**
- Externen Modulen (kein direkter Import von `_state` außerhalb von `device_KeyLabmkII`)

## State-Lifecycle

```
OnInit()
  └── KeyLabState() erstellt
        ├── Alle Defaults gesetzt
        └── Referenz in _state-Variable

OnMidiMsg() / OnRefresh() / OnIdle()
  └── Handler bekommen state als Parameter
        └── Lesen/Schreiben der Attribute

OnDeInit()
  └── state wird verworfen (Python GC)
```

## Pattern: State-Check in Handlern

```python
def handle_mixer(event, state, pages):
    # Plugin Mode deaktiviert Mixer (außer Master)
    if state.plugin_mode and event.midiChan < Fader.MASTER_CHANNEL:
        return False  # Passthrough
    
    # Free Mode deaktiviert Slots 1-8
    if state.free_mode and event.midiChan < Fader.MASTER_CHANNEL:
        return False  # Passthrough
    
    # ... normaler Handler-Code
```
