# KeyLab mkII — CodeMap Index

Zentrale Navigation für KI-Assistenz (Cursor/Antigravity). Diese Maps beschreiben Code-Architektur, Patterns und Design-Entscheidungen — nicht die Feature-Anforderungen (die in `IMPLEMENTATION_MAP.md` stehen).

## Quick Start für neue Features

1. **Handler-Chain verstehen**: `handler_chain.md` — zeigt die Entscheidungsreihenfolge in `OnMidiMsg()`
2. **State-Attribute finden**: `state.md` — alle `KeyLabState` Felder mit Semantik
3. **MIDI-Werte nachschlagen**: `hardware_constants.md` — CC/Note/PB Mappings
4. **Neuen Handler bauen**: `adding_handlers.md` — Template + Checkliste

---

## CodeMap-Übersicht

| Map | Inhalt | Wann konsultieren |
|-----|--------|-------------------|
| `handler_chain.md` | Reihenfolge: Transport → DAW → Navigation → Plugin → Mixer | Bei neuen MIDI-Events oder Handler-Integration |
| `state.md` | `KeyLabState` Attribute: `focus_mode`, `bank_offset`, `free_mode`, etc. | Wenn du State lesen/schreiben musst |
| `hardware_constants.md` | `keylab_config.py` erklärt: `Fader.ALL_CHANNELS`, `Encoder.CC_START`, etc. | Bei MIDI-Mappings oder neuen Hardware-Zuweisungen |
| `midi_dispatcher.md` | `MidiEventDispatcher` Klasse: Pattern für Event-Routing | Bei komplexem Dispatch oder neuen Dispatcher-Instanzen |
| `adding_handlers.md` | Schritt-für-Schritt: Neues Handler-Modul erstellen | Wenn du einen komplett neuen Bereich hinzufügst |
| `free_mode.md` | Free Mode Logik: Was wird durchgereicht, was blockiert | Bei Änderungen am Free Mode Verhalten |
| `long_press.md` | `keylab_long_press.py`: 0,75 s Schwelle, OnIdle-Poll, sofortiges LCD | Bei Short/Long-Press auf Buttons |
| `plugin_control.md` | Plugin-Modus: Encoder-Mapping, `plugin_database.py` Schema | Bei Plugin-Parameter-Mapping |

---

## Cross-Reference: CodeMap ↔ Implementations-Doku

| CodeMap | Feature-Doku |
|---------|--------------|
| `handler_chain.md` | `IMPLEMENTATION_MAP.md` — Handler-Chain erfüllt Feature-Reqs |
| `state.md` | `ROADMAP.md` — State-Änderungen für neue Phasen |
| `hardware_constants.md` | `hardware_map.md` — Physisches MIDI ↔ Code-Konstanten |

---

## Architektur-Dateien (Legacy)

- `architecture.md` — Enthält Mermaid-Diagramm der alten Architektur + Dead-Code-Analyse
- `BRAINSTORM.md` — Design-Entscheidungen, API-Diskussionen

---

## Hinweis für KI-Assistenz

> **WICHTIG**: `codemaps/*.md` dokumentieren **wie** der Code funktioniert.  
> `IMPLEMENTATION_MAP.md` dokumentiert **was** implementiert werden muss.  
> Beide sind Pflichtlektüre vor Code-Generierung.
