# MidiEventDispatcher Pattern

---
module: keylab_dispatch.py
class: MidiEventDispatcher
origin: Ray Juang (MIT License, 2020)
used_by: keylab_mixer.py (intern), potentiell andere Handler
---

## Zweck

Generisches Dispatcher-Pattern für MIDI-Events. Transformiert ein Event in einen Key, sucht im Dispatch-Map nach einem Handler, und führt diesen aus wenn ein Filter passt.

## API

### Konstruktion

```python
dispatcher = MidiEventDispatcher(transform_fn)
```

**`transform_fn(event)`** → Key (int, str, tuple).  
Beispiele:
- `lambda e: e.data1` → Key ist die Note-Nummer
- `lambda e: (e.midiId, e.data1)` → Key ist (Status, Data1) Tupel
- `lambda e: e.midiChan` → Key ist MIDI-Kanal

### Handler registrieren

```python
dispatcher.NewHandler(key, callback_fn, filter_fn=None)
```

- **`key`**: Ergebnis von `transform_fn(event)`
- **`callback_fn(event)`**: Wird aufgerufen wenn Key matcht und Filter True
- **`filter_fn(event)`** → bool: Optional. Default ist immer True.

**Bulk-Registration**:
```python
dispatcher.NewHandlerForKeys([16, 17, 18, 19], handle_pan_encoder)
```

### Dispatch

```python
processed = dispatcher.Dispatch(event)  # → bool
```

Returns `True` wenn ein Handler gefunden und ausgeführt wurde (auch wenn Filter False ergab).

## Verwendung im Projekt

Aktuell wird `MidiEventDispatcher` **nicht direkt in `device_KeyLabmkII.py`** verwendet — die Handler-Chain nutzt explizite if/elif Logik.

**Potentieller Einsatz** (für komplexe Sub-Routing):
```python
# In handle_mixer() für Encoder-Routing
def handle_mixer(event, state, pages):
    # Fader-Handling...
    
    # Encoder-Dispatch
    if event.midiId == CC_STATUS and 16 <= event.data1 <= 24:
        return _encoder_dispatcher.Dispatch(event)
```

## Vergleich: Dispatcher vs. If/Elif Chain

| Kriterium | If/Elif Chain (aktuell) | MidiEventDispatcher |
|-----------|---------------------------|---------------------|
| Lesbarkeit | Linear, explizit | Lookup-Table |
| Performance | Gut für <10 Checks | Bessere für >20 Checks |
| Dynamisch | Nein (Code-Änderung nötig) | Ja (Handler zur Laufzeit) |
| Debugging | Einfach (Breakpoints) | Schwieriger (Callback-Indirection) |

## Empfehlung

Für die aktuelle KeyLab-Architektur mit ~5 Haupt-Handlern ist die **If/Elif Chain in `OnMidiMsg()`** ausreichend.  
Dispatcher lohnt sich erst bei:
- Vielen (>10) ähnlichen Events (z.B. 16 Pads mit unterschiedlichen Funktionen)
- Laufzeit-konfigurierbarem Mapping

## SysEx Helper

```python
def send_to_device(data):
    """Sendet SysEx mit Arturia-Header zum KeyLab."""
    device.midiOutSysex(
        bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]) + 
        data + 
        bytes([0xF7])
    )
```

**Verwendung**: `keylab_display.py`, `keylab_feedback.py`
