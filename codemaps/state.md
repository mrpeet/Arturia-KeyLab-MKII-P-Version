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
| `pad_mode` | str | `'fpc'`, `'chromatic'` | Pad-Spielmodus (LCD: Drum Map / Chromatic) — **delegiert** zu `keylab_shared_state` |
| `pad_bank_offset` | int | 0–5 | Pad-Bank — delegiert zu `keylab_shared_state` |
| `pad_velocity_enabled` | bool | `True` / `False` | Pad-Velocity; Off → feste Note-On-Velocity 95 (75%) im Forward-Script |
| `focus_mode` | str | `FocusMode.*` | **Reserviert** — aktuell ungenutzt; Mixer/CR-Umschaltung via `ui.getFocused()` |
| `track_button_mode` | str | `TrackButtonMode.*` | **Reserviert** — Track-Buttons nutzen festes Short/Long-Verhalten in `keylab_mixer.py` |

### Banking

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `bank_offset` | int | Offset für Fader/Encoder-Bank (Schritte à 8). 0 = Tracks 1-8, 8 = Tracks 9-16, etc. |

### Free Mode

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `free_mode` | bool | `True` = Fader 1-8, Encoder 1-8, Track Buttons 1-8 werden durchgereicht (kein Handling). Slot 9 (Master) immer aktiv. |

**Activation**: Long Press (≥0,75 s) auf "Bank Prev" Button (Note 48). Aktion + LCD bei Schwelle via `keylab_long_press.poll()`. Siehe `keylab_mixer.py:_toggle_free_mode()`

**Deactivation**: Erneuter Long Press auf "Bank Prev"

### Fader-Management

| Attribut | Typ | Bereich | Beschreibung |
|----------|-----|---------|--------------|
| `FADER_JITTER_THRESHOLD` | int | 0-16383 | Min. Delta (14-bit) bevor Fader-Wert akzeptiert wird |
| `fader_last_sent_value` | list[int] | 8 Elemente | Letzter tatsächlich gesendeter 14-bit Wert pro Fader |
| `fader_pickup_active` | list[bool] | 9 Elemente (inkl. Master) | `True` = Physikalischer Fader hat Software-Wert gekreuzt |
| `fader_last_fl_value` | list[float] | 9 Elemente | **Nicht aktiv genutzt** — Pickup vergleicht live mit `_get_current_fl_volume()` |
| `fader_touch_pressed` | list[bool] | 9 Elemente | Debounce: letzter Touch-Sensor-Zustand pro Fader |
| `fader_last_touch_ms` | list[float] | 9 Elemente | Zeitstempel für Touch-Debounce |
| `fader_display_last_index` | int | — | LCD-Throttle: zuletzt angezeigter Fader |
| `fader_display_last_ms` | float | — | LCD-Throttle: Zeitstempel |

**Soft Pickup Logik**: Siehe `keylab_mixer.py:_do_fader()`
1. Fader wird berührt → Touch-Note empfangen
2. Erster PB-Wert → Vergleich mit aktuellem FL-Volume (`mixer`/`channels`)
3. Wenn gekreuzt → `fader_pickup_active = True`, Werte werden gesendet
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
