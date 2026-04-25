# Free Mode — Passthrough Logic

---
module: keylab_mixer.py
state_flag: state.free_mode
toggled_by: Long Press (>1s) auf Bank Prev (Note 48)
---

## Zweck

Free Mode erlaubt es dem User, die Fader, Encoder und Track Buttons 1-8 direkt an FL Studio durchzureichen, ohne dass das Script sie abfängt. Das ermöglicht "Link to Controller" für beliebige Plugins/Parameter.

**Wichtig**: Slot 9 (Master) ist **von Free Mode ausgenommen** — er bleibt immer unter Script-Kontrolle.

## Activation / Deactivation

```python
# In keylab_mixer.py:_do_bank()

_BANK_BUTTON_PRESS_TIME = 0
_LONG_PRESS_THRESHOLD = 1.0  # seconds

def _do_bank(event, state, pages):
    if event.data1 == BankButton.PREV_NOTE:
        if event.midiId == NOTE_ON_STATUS:
            _bank_button_press_time = time.time()
        elif event.midiId == NOTE_OFF_STATUS:
            press_duration = time.time() - _bank_button_press_time
            if press_duration >= _LONG_PRESS_THRESHOLD:
                # Toggle Free Mode
                state.free_mode = not state.free_mode
                # Display Feedback...
            else:
                # Normal: Bank Prev
                state.bank_offset = max(0, state.bank_offset - 8)
```

## Betroffene Controls

| Control | Kanal/Bereich | Verhalten in Free Mode |
|---------|---------------|------------------------|
| Fader 1-8 | PB Ch 0-7 | **Passthrough** (`return False`) |
| Fader 9 (Master) | PB Ch 8 | **Normal** — Script behandelt |
| Encoder 1-8 | CC 16-23 | **Passthrough** (`return False`) |
| Encoder 9 (Master) | CC 24 | **Normal** — Script behandelt |
| Track Button 1-8 | Note 24-31 | **Passthrough** (`return False`) |
| Track Button 9 | Note 32 | **Normal** — Script behandelt |

## Implementierungs-Pattern

### In jedem betroffenen Handler:

```python
def handle_mixer(event, state, pages):
    # --- Fader ---
    if event.midiId == PITCH_BEND_STATUS and event.midiChan in Fader.ALL_CHANNELS:
        
        # Plugin Mode check (höhere Priorität)
        if state.plugin_mode and event.midiChan < Fader.MASTER_CHANNEL:
            return False  # Plugin Mode blockiert
        
        # Free Mode check
        if state.free_mode and event.midiChan < Fader.MASTER_CHANNEL:
            return False  # ← PASSTHROUGH: Slot 1-8 durchreichen
        
        # Normal handling...
        _do_fader(event, state, pages)
        return True
```

### Critical Check: `event.midiChan < Fader.MASTER_CHANNEL`

- `Fader.MASTER_CHANNEL = 8` (Channel 9 in 1-basiert)
- Vergleich ist **strikt kleiner** — Master (8) ist ausgenommen

## Interaktion mit anderen Modi

| Kombination | Verhalten |
|-------------|-----------|
| Free Mode + Plugin Mode | Free Mode "gewinnt" für Slots 1-8 — sie werden durchgereicht statt Plugin-Params zu steuern |
| Free Mode + Banking | Banking-Buttons (Prev/Next) funktionieren normal — sie sind nicht in Free Mode |
| Free Mode + Display | Free Mode zeigt visuelles Feedback auf Display: `line1='FREE MODE', line2='Faders/Encoders pass-through'` |

## Debug-Output

Wenn Free Mode aktiviert/deaktiviert wird:
```python
print("### FREE MODE:", "ON" if state.free_mode else "OFF", "###")
```

## Edge Cases

### Fader Touch in Free Mode
- Touch-Sensoren (Note 104-112) werden auch durchgereicht
- Das kann FL Studio verwirren, da Touch normalerweise "Write Automation" triggert
- Aktuelles Verhalten: Passthrough (konsistent mit Fader-Bewegung)

### Encoder Button-Press
- KeyLab Encoder haben einen Push-Button (nicht direkt dokumentiert)
- Falls implementiert: Sollte in Free Mode auch durchgereicht werden

## Testing

1. **Aktivierung**: Bank Prev >1s halten → Display zeigt "FREE MODE"
2. **Fader Test**: Fader 1 bewegen → FL Studio Mixer Channel 1 sollte sich bewegen (nicht KeyLab Script!)
3. **Master Test**: Master Fader bewegen → Script steuert Master Volume (FL API)
4. **Deaktivierung**: Erneut Bank Prev >1s → Normal-Modus
5. **Plugin Mode Kombination**: Plugin öffnen, Free Mode aktivieren → Encoder sollten Plugin steuern (nicht Plugin-Params)
