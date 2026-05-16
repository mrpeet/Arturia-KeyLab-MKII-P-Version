# Plugin Control — Encoder Mapping & Database

---
modules: [keylab_plugin.py, plugin_database.py]
entry_point: handle_plugin_encoder(), handle_plugin_special_jog()
mode_activation: ui.getFocused(midi.widPlugin) → state.plugin_mode = True
---

## Architektur-Übersicht

Plugin-Steuerung hat **3 unabhängige Ansätze** (siehe `BRAINSTORM.md`):

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. FREE MODE (höchste Priorität)                                │
│    state.free_mode = True                                       │
│    → event.handled = False für Encoder 1-8                       │
│    → FL Studio "Link to Controller" funktioniert                 │
│    → Universell, aber manuelles Mapping nötig                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (wenn free_mode = False)
┌─────────────────────────────────────────────────────────────────┐
│ 2. PLUGIN DATABASE (mittlere Priorität)                         │
│    → plugins.setParamValue() mit curated Mappings                │
│    → plugin_database.py enthält 200+ Plugin-Presets               │
│    → 8 Makro-Slots pro Plugin (Roland Zenology-Schema)           │
│    → User-erweiterbar                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (wenn Plugin nicht in Database)
┌─────────────────────────────────────────────────────────────────┐
│ 3. PORT 10 FORWARDING (niedrigste Priorität)                    │
│    → Nur für Arturia V-Collection                               │
│    → device_KeyLabmkII_Forward.py (optional, separat)           │
│    → Keine FL API, direktes MIDI Forwarding                     │
└─────────────────────────────────────────────────────────────────┘
```

## Auto-Detection

```python
# In device_KeyLabmkII.py:_update_plugin_mode()

def _update_plugin_mode():
    if state.free_mode:
        return  # Free Mode überschreibt alles
    
    focused = ui.getFocused(midi.widPlugin)
    if focused != state.plugin_mode:
        state.plugin_mode = focused
        if focused:
            # Plugin gerade fokussiert
            name = plugins.getPluginName(channels.selectedChannel())
            _pages.SetPageLines('plugin', line1=name, line2='Plugin Mode')
```

**Ablauf**:
1. `OnIdle()` ruft `_update_plugin_mode()` periodisch auf
2. Plugin-Fenster fokussiert → `state.plugin_mode = True`
3. Mixer Fader 1-8, Encoder 1-8, Track Buttons 1-8 werden **deaktiviert**
4. Master bleibt aktiv

## Plugin Database Schema

### Format in `plugin_database.py`:

```python
PLUGIN_DATABASE = {
    "FLEX": {
        "params": [0, 1, 2, 3, 4, 5, 6, 7],  # 8 FL-Parameter-Indices
        "names": ["Cutoff", "Resonance", "Attack", "Release", 
                  "Modulation", "FX1", "FX2", "Volume"],
        # Optional: "special" für Hardware-Bindings
        "special": {
            "jog_function": "preset_navigate",  # Jog Wheel steuert Presets
        }
    },
    "Sytrus": {
        "params": [10, 11, 12, 13, 14, 15, 16, 17],
        "names": ["Op1 Coarse", "Op1 Fine", "Op1 Lev", ...],
    },
    # ... 200+ Einträge
}
```

### 8-Makro-Standard (Roland Zenology-inspired):

| Slot | Standard-Funktion | FL-Parameter-Index |
|------|-------------------|-------------------|
| 1 | Cutoff | Plugin-spezifisch |
| 2 | Resonance | Plugin-spezifisch |
| 3 | Attack | Plugin-spezifisch |
| 4 | Release | Plugin-spezifisch |
| 5 | Modulation | Plugin-spezifisch |
| 6 | FX1 | Plugin-spezifisch |
| 7 | FX2 | Plugin-spezifisch |
| 8 | Volume | Plugin-spezifisch |

## Encoder-Handling

```python
# In keylab_plugin.py:handle_plugin_encoder()

def handle_plugin_encoder(event, state, pages):
    # Nur im Plugin Mode
    if not state.plugin_mode:
        return False
    
    # Free Mode check
    if state.free_mode:
        return False  # Durchreichen
    
    # Encoder CC 16-23?
    if not (Encoder.CC_START <= event.data1 <= Encoder.CC_END):
        return False
    
    # Plugin-Namen lookup
    channel = channels.selectedChannel()
    plugin_name = plugins.getPluginName(channel)
    
    # Database lookup
    mapping = PLUGIN_DATABASE.get(plugin_name)
    if not mapping:
        return False  # Kein Mapping → Free Mode fallback
    
    # Parameter setzen
    encoder_index = event.data1 - Encoder.CC_START  # 0-7
    param_index = mapping["params"][encoder_index]
    
    # Relative oder absolute?
    # Aktuell: Absolute (0-127 → 0.0-1.0)
    value = event.data2 / 127.0
    plugins.setParamValue(param_index, value, channel)
    
    return True
```

## Special Functions

Manche Plugins haben erweiterte Hardware-Bindings:

```python
# Beispiel: Kontakt mit Jog Wheel Navigation

if "special" in mapping:
    if mapping["special"].get("jog_function") == "preset_navigate":
        # Jog Wheel steuert Preset Prev/Next statt Parameter
        handle_plugin_special_jog(event, state, pages)
```

## User-Defined Mappings

`user_defined_plugin_mappings.py` enthält Community-Mappings im FLKey-JSON-Format.

**Status:** Noch **nicht** in `plugin_database.get_plugin_params()` gemerged — nur als Datenquelle dokumentiert. Bis Merge: Free Mode oder Eintrag direkt in `PLUGIN_DB`.

## Integration mit Community Plugin Spreadsheet (CPS)

- **Quelle**: Ian Walker's FLKey-External-Plugins Repo
- **Schema**: `native_pot_parameters.py` (auto-generiert aus Spreadsheet)
- **Lizenz**: CC0-1.0 (Public Domain)
- **Plugin Count**: 200+ Instruments + Effects

**WICHTIG**: Wir nutzen nur die **rohen Daten** (Plugin-Name → 8 Parameter-Indices).  
Wir nutzen **NICHT** die Novation-spezifischen Imports (`PluginPotParameterType`, etc.).

## Preset Navigation

Encoder-Druck (oder spezielle Button-Kombination) kann Preset-Wechsel triggern:

```python
# CC 28 = Preset Prev, CC 29 = Preset Next
PREV_CC = 28
NEXT_CC = 29

def _do_preset_navigate(direction, channel):
    if direction == "prev":
        plugins.prevPreset(channel)
    else:
        plugins.nextPreset(channel)
```

## Testing Checklist

- [ ] Plugin Mode auto-detection: Fenster fokussieren → Display zeigt "Plugin Mode"
- [ ] Encoder 1-8 steuern Plugin-Params (wenn in Database)
- [ ] Free Mode: Encoder durchreichen (FL "Link to Controller" möglich)
- [ ] Unbekanntes Plugin: Free Mode Fallback
- [ ] Master Encoder funktioniert immer (auch im Plugin Mode)
- [ ] Preset Prev/Next funktioniert

## Häufige Probleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| Encoder reagieren nicht | Plugin nicht in Database | Free Mode nutzen oder Mapping hinzufügen |
| Falsche Parameter | Parameter-Indices haben sich geändert | Database updaten (FL-Version-Check) |
| Delay bei Parameter-Änderung | Zu viele SysEx/Display-Updates | Throttling in Display-Modul |
| Plugin Mode bleibt aktiv | Fenster nicht erkannt | `ui.getFocused()` kann flaky sein — manuell toggle? |
