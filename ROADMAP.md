# KeyLab mkII P Version — Roadmap

> Übersicht aller Entwicklungsphasen. Jede Phase ist in sich abgeschlossen und testbar.
>
> **Prinzipien:**
> - Keine Magic Numbers — alle MIDI-Werte über `keylab_config.py`
> - State nur über `keylab_state.py` — kein Module-Level-Mutable-State
> - Jede Phase wird in `IMPLEMENTATION_MAP.md` als ✅ markiert
> - Archiv-Code (`_archive/`) dient als Referenz, wird nie importiert

---

## Phase 1 — Bestandsaufnahme & Analyse ✅

**Ziel:** Altes Script vollständig verstehen, dokumentieren, Bugs und Dead Code identifizieren.

| Ergebnis | Datei |
|:---------|:------|
| Architektur-Analyse (Import-Graph, Coupling, Dead Code, Bugs) | `architecture.md` |
| Hardware MIDI Map (alle Ports, Kanäle, Note/CC/PB) | `hardware_map.md` |
| Altes Script archiviert (14 Dateien) | `_archive/` |

---

## Phase 2 — Dokumentation ✅

**Ziel:** Referenzdokumente für die Neuentwicklung erstellen.

| Ergebnis | Datei |
|:---------|:------|
| FL Studio MIDI Scripting API — lokale Referenz | `FL_Studio_API_Reference.md` |
| Implementierungsplan: Hardware ↔ Funktionen | `IMPLEMENTATION_MAP.md` |
| Feature-Ideen & Design-Entscheidungen | `BRAINSTORM.md` |
| Projekt-README mit Setup, Credits, Dateistruktur | `README.md` |
| AI-Agent Crosscheck Rules | `.cursorrules` |

---

## Phase 3 — Skeleton & Infrastruktur ✅

**Ziel:** Modulare Basis, die in FL Studio lädt und das LCD ansteuert.

| Ergebnis | Datei | Herkunft |
|:---------|:------|:---------|
| Hardware-Konstanten (Transport, Encoder, Fader, Pads, Pedals) | `keylab_config.py` | Neu |
| Zentraler State (Modes, Banking, Fader-Pickup, Plugin-State) | `keylab_state.py` | Neu |
| Event-Dispatcher (transform → lookup → callback) | `keylab_dispatch.py` | Portiert (Ray Juang, MIT) |
| LCD SysEx-Builder mit Scrolling | `keylab_display.py` | Portiert (Ray Juang, MIT) |
| Timed-Page-Manager | `keylab_pages.py` | Portiert (Ray Juang, MIT) |
| FL Callbacks Entry Point (DAW Port) | `device_KeyLabmkII.py` | Neu (Skeleton) |
| V-Collection CC-Forwarding (Keys Port) | `device_KeyLabmkII_Forward.py` | Fertig |

**Testbar:** Script lädt in FL Studio, LCD zeigt Channel + Pattern.

---

## Phase 4 — Plugin-Datenbank ✅

**Ziel:** 300+ Plugin-Parameter-Mappings für Encoder-Steuerung.

| Ergebnis | Datei |
|:---------|:------|
| 309 Plugins mit 8-Macro-Slot-Schema, Lookup-API | `plugin_database.py` |
| Plugin-Encoder-Handler (Logik fertig, noch nicht eingehängt) | `keylab_plugin.py` |
| User-Defined Mappings (Datenquelle für Merge) | `user_defined_plugin_mappings.py` |

**Datenquellen:** CPS Community Spreadsheet + user_defined_plugin_mappings.py (FLKey Community)

---

## Phase 5 — Transport ✅

**Ziel:** Play/Stop/Record/Loop/Rewind/FastForward funktionieren. Dispatcher-Kette aufbauen.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Transport-Handler (6 Buttons → FL API) | `keylab_transport.py` | ✅ |
| Dispatcher-Kette in OnMidiMsg aufbauen | `device_KeyLabmkII.py` | ✅ |
| Transport LED-Feedback (Play/Record/Loop) | `keylab_feedback.py` | ✅ |
| Beat-Indicator LED (OnUpdateBeatIndicator) | `keylab_feedback.py` | ✅ |

---

## Phase 6 — DAW Commands ✅

**Ziel:** Utility-Buttons für Workflow-Beschleunigung.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Snap Toggle, NewPattern, FocusMixer | `keylab_daw_commands.py` | ✅ |
| Undo (Short Press) / Cut (Long Press) | `keylab_daw_commands.py` | ✅ |
| Metronome Toggle, Overdub Toggle | `keylab_daw_commands.py` | ✅ |
| Tap Tempo, Redo | `keylab_daw_commands.py` | ✅ |

**Testbar:** Alle 10 DAW Buttons haben definierte Aktionen, LCD zeigt Feedback.

---

## Phase 7 — Navigation ✅

**Ziel:** Jog Wheel und Bank-Buttons für kontextabhängige Navigation.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Jog Wheel Drehen → context-sensitive | `keylab_navigation.py` | ✅ |
| Jog Wheel Klick → Plugin/Folder/Arm | `keylab_navigation.py` | ✅ |
| Bank Left/Right → Pattern/Preset/Browser | `keylab_navigation.py` | ✅ |
| LCD-Feedback Navigation | `keylab_navigation.py` | ✅ |

**Testbar:** Jog wechselt Tracks/Patterns/Browser-Items, Bank-Buttons schalten Patterns/Presets/Browser-Tabs.

---

## Phase 8 — Mixer Fader ✅

**Ziel:** 9 Fader (8 + Master) steuern Mixer-Volume mit Jitter-Filter und Soft Pickup.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Pitch Bend → mixer.setTrackVolume (+ Banking) | `keylab_mixer.py` | ✅ |
| Jitter-Filter (FADER_JITTER_THRESHOLD) | `keylab_mixer.py` | ✅ |
| Soft Pickup (Fader muss Software-Wert kreuzen) | `keylab_mixer.py` | ✅ |
| Touch-Sensor Events (Fader Touch/Release) | `keylab_mixer.py` | ✅ |

**Testbar:** Fader steuern Mixer-Volume, kein Springen bei Bank-Wechsel.

---

## Phase 9 — Mixer Encoder + Track Buttons ✅

**Ziel:** Encoder steuern Pan, Track-Buttons selektieren/solo/muten Tracks.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Relative Encoder → mixer.setTrackPan (+ Banking) | `keylab_mixer.py` | ✅ |
| Track Buttons: Short=ResetPan, Long=ToggleMute | `keylab_mixer.py` | ✅ |
| Bank Prev/Next → bank_offset ±1 | `keylab_mixer.py` | ✅ |

**Testbar:** Encoder dreht Pan, Buttons selektieren Tracks, Banking funktioniert.

---

## Phase 10 — Plugin-Steuerung ✅

**Ziel:** Encoder 1–8 steuern Plugin-Parameter wenn Plugin fokussiert.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Plugin-Mode auto-detect (OnIdle → widPlugin) | `device_KeyLabmkII.py` | ✅ |
| Encoder → Plugin-Parameter (aus plugin_database.py) | `keylab_plugin.py` | ✅ |
| Jog Wheel → Preset-Navigation (bei Plugins mit special) | `keylab_navigation.py` | ✅ |
| LCD: Parameter-Name + Wert-Anzeige | `keylab_plugin.py` | ✅ |
| Fallback: Unbekannte Plugins → Free Mode / Generic | `keylab_plugin.py` | ✅ |

**Testbar:** Plugin öffnen → Encoder steuern die richtigen Parameter, LCD zeigt Plugin-Name.


## Phase 10.1 — Foundation Sync / Stabilisierung 🔧

**Ziel:** Doku/Codemaps an die aktive `keylab_*`-Architektur anbinden, klare Basis-Bugs beheben, Pad-Mode-Toggle zum Laufen bringen.

| Aufgabe | Datei | Status |
|:--------|:------|:-------|
| Roadmap + `IMPLEMENTATION_MAP.md` auf Code-Stand | `ROADMAP.md`, `IMPLEMENTATION_MAP.md` | 🔧 |
| Codemaps + `FL_Studio_API_Reference.md` ergänzen | `codemaps/*`, `FL_Studio_API_Reference.md` | 🔧 |
| `_sync_mixer_bank`: fehlender `mixer`-Import | `device_KeyLabmkII.py` | 🔧 |
| Free-Mode-Fader-Jitter, Bank-Limit, Debug-Spam | `keylab_mixer.py` | 🔧 |
| Plugin-Focus: `midi.widPlugin`, Jog-Richtung | `keylab_plugin.py` | 🔧 |
| Pad-Mode IN ↔ Forward-Script (siehe unten) | `keylab_shared_state.py`, `device_KeyLabmkII_Forward.py` | 🔧 |
| Encoder/Fader/Track-Buttons in allen Kontexten testen | manuell in FL Studio | ⬜ |

### Bekanntes Problem: Pad-Mode-Toggle (Priorität)

**Symptom (historisch):** IN-Button (Global Control, Note 87) zeigte auf dem LCD den Wechsel zwischen **Chromatic** und **Drum Map**, aber die 16 Pads blieben hörbar im **GM-Drum-Layout**.

**Soll-Verhalten:**

| Modus | Default | Mapping |
|:------|:--------|:--------|
| **Chromatic** | ja | Halbtöne ab **C3 (MIDI 48)** auf Pads 1–16 (Lesereihenfolge oben-links → unten-rechts), inkl. Pad-Bank (+16 Halbtöne) |
| **Drum Map** (`fpc`) | nein | Native Pad-Noten → **GM Drum-Layout** (`_FPC_MAP`), Kanal 10 |

**Umschalten:** IN kurz = Pad-Modus; IN lang (≥0,75 s, Aktion bei Schwelle) = Pad-Velocity → `keylab_shared_state` / `keylab_long_press.py`.

**Technische Ursachen (vermutet / adressiert in 10.1):**

1. **Cross-Script-State:** DAW-Script (Port 1) und Forward-Script (Port 0) teilen sich `pad_mode` über `keylab_shared_state` (`sys` + Datei-Fallback).
2. **MIDI-Kanal 10 = GM Drums:** Chromatic-Noten auf Kanal 10 klingen weiterhin wie Percussion — Chromatic muss auf **Kanal 1** ausgegeben werden; Drum Map bleibt auf **Kanal 10**.
3. **Forward-Script** muss in FL MIDI Settings auf dem **Keys Port** aktiv sein (`device_KeyLabmkII_Forward.py`).

**Noch offen nach 10.1:** Pad-LED-Farben pro Modus/Bank, Step-Sequencer. Velocity-Toggle (Long Press IN) ist implementiert.

---

## Phase 11 — Pads (Erweiterung) ⬜

**Ziel:** Pad-UX vervollständigen (LEDs, Velocity, optional Sequencer).

| Aufgabe | Datei |
|:--------|:------|
| Pad-LED-Farben / Bank-Feedback | `keylab_feedback.py` |
| Velocity-Toggle (Long Press IN) | `keylab_daw_commands.py`, Forward | fertig |
| Step-Sequencer-Modus (optional) | TBD |

**Testbar:** Chromatic = Melodie auf Kanal 1; Drum Map = GM-Drums auf Kanal 10; IN kurz = Modus; IN lang = Velocity; LCD-Hints.

---

## Phase 12 — LED Feedback (DAW Commands + Track Buttons) ⬜

**Ziel:** Buttons leuchten passend zum FL Studio State.

| Aufgabe | Datei |
|:--------|:------|
| DAW Command Buttons: aktiv=100%, inaktiv=30% | `keylab_feedback.py` |
| Track Buttons: Mute/Solo-State als LED | `keylab_feedback.py` |
| Snap/Metronome/Overdub: State-LED synchronisiert | `keylab_feedback.py` |
| OnRefresh → alle LEDs neu synchronisieren | `keylab_feedback.py` |

---

## Phase 13 — Polish & Edge Cases ⬜

**Ziel:** Feinschliff, Performance, Robustheit.

| Aufgabe | Datei |
|:--------|:------|
| Alle LEDs korrekt synchronisiert (OnRefresh) | `keylab_feedback.py` |
| Display-Feinschliff (Truncation, Sonderzeichen) | `keylab_display.py` |
| Error-Handling für alle FL API Calls | Alle Handler |
| Channel Rack Mode (Auto-Switch wenn CR fokussiert) | `keylab_mixer.py` |
| Free Mode (Long Press Bank Prev → Fader/Encoder passthrough toggle) | `keylab_mixer.py`, `keylab_state.py` |
| Performance-Check (keine Allocations in Event-Handlern) | Alle Handler |
| Dokumentation finalisieren | Alle .md Dateien |

---

## Dateiübersicht (Zielzustand)

| Datei | Rolle | Phase |
|:------|:------|:------|
| `device_KeyLabmkII.py` | Entry Point + Dispatcher-Kette | 3, 5 |
| `device_KeyLabmkII_Forward.py` | V-Collection CC-Forwarding | 3 |
| `keylab_config.py` | Hardware-Konstanten | 3 |
| `keylab_state.py` | Zentraler State | 3 |
| `keylab_dispatch.py` | Event-Dispatcher + SysEx | 3 |
| `keylab_display.py` | LCD-Treiber | 3 |
| `keylab_pages.py` | Page-Manager | 3 |
| `keylab_transport.py` | Transport-Handler | 5 |
| `keylab_feedback.py` | LED/Pad-Feedback | 5, 8, 11 |
| `keylab_daw_commands.py` | DAW Command Buttons | 6 |
| `keylab_navigation.py` | Jog/Bank/Window | 7 |
| `keylab_mixer.py` | Fader/Encoder/Buttons/Banking | 8, 9 |
| `keylab_plugin.py` | Plugin-Encoder-Steuerung | 10 |
| `keylab_shared_state.py` | Pad-Mode/Bank (cross-port) | 10.1 |
| `device_KeyLabmkII_Forward.py` | Pad-Transposition + V-Collection | 3, 10.1 |
| `plugin_database.py` | 309 Plugin-Mappings | 4 |

---

*Letzte Aktualisierung: 2026-05-15 — Phase 10 abgeschlossen; Phase 10.1 Foundation + Pad-Mode-Fix in Arbeit*
