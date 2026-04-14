# Arturia KeyLab mkII — FL Studio MIDI Script (P Version)

Custom FL Studio user MIDI script for the **Arturia KeyLab mkII** keyboard controller. Provides transport control, mixer integration (faders, encoders, track buttons), pad modes, navigation, display feedback, and more.

> **Status:** 🚧 Neustrukturierung in Arbeit — das Script wird aktuell modular neu aufgebaut. Das alte Script ist voll funktionsfähig, wird aber schrittweise durch eine saubere, modulare Version ersetzt.

---

## Credits & Lizenz

Dieses Projekt basiert auf Arbeit mehrerer Entwickler:

### Farès MEZDOUR — Original-Script
- **Dateien:** siehe `_archive/` — alle Originaldateien des alten Scripts
- Haupt-Logik für MIDI-Processing, LED-Feedback, Step Sequencer, Plugin-Steuerung und Hardware-Mapping

### Ray Juang — Dispatcher & Display (MIT License, 2020)
- **Portiert nach:** `keylab_dispatch.py`, `keylab_display.py`, `keylab_pages.py`
- Event-Dispatcher-Pattern, LCD-SysEx-Ansteuerung mit Scrolling, Timed-Page-Manager
- Lizenz: MIT License — Copyright (c) 2020 Ray Juang

### P Version — Anpassungen & Neustrukturierung
- Bugfixes, Anpassungen an persönliche Workflow-Bedürfnisse
- Bestandsaufnahme und Dokumentation des gesamten Codes
- Modulare Neustrukturierung (in Arbeit)

---

## Setup

### Voraussetzungen
- **FL Studio** (mit MIDI Scripting Support)
- **Arturia KeyLab mkII** (im DAW-Modus / MCU-Modus)

### Installation
1. Diesen gesamten Ordner nach folgendem Pfad kopieren:
   ```
   [FL Studio User Data]\Settings\Hardware\Arturia KeyLab MKII P Version\
   ```
   Typischer Pfad unter Windows:
   ```
   Documents\Image-Line\FL Studio\Settings\Hardware\Arturia KeyLab MKII P Version\
   ```

2. FL Studio öffnen → **Options → MIDI Settings**

3. Zwei MIDI-Inputs zuweisen:

   | FL Studio Input | Hardware-Name | Script | Port |
   |:----------------|:--------------|:-------|:-----|
   | `MIDIIN2 (KeyLab mkII 61)` | DAW Port | **KeyLab mkII P Version (user)** | 1 |
   | `KeyLab mkII 61` | Keys Port | **Forward CCs Port 10 (user)** *(optional, für V-Collection)* | 0 |

---

## Dateistruktur

### Python-Scripts (neu — modulare Struktur)

| Datei | Rolle | Status |
|:------|:------|:-------|
| `device_KeyLabmkII.py` | FL Callbacks / Entry Point | ✅ Skeleton |
| `keylab_config.py` | Hardware-Konstanten (Note/CC/PB aus `hardware_map.md`) | ✅ Fertig |
| `keylab_state.py` | Zentraler State (Modes, Banking, Pickup) | ✅ Fertig |
| `keylab_dispatch.py` | Event-Dispatcher + `send_to_device` (SysEx) | ✅ Portiert |
| `keylab_display.py` | LCD SysEx-Builder mit Scrolling | ✅ Portiert |
| `keylab_pages.py` | Timed-Page-Manager für das Display | ✅ Portiert |
| `keylab_transport.py` | Transport-Handler (Play/Stop/Record/Loop/RW/FF) | ⬜ Stub |
| `keylab_mixer.py` | Mixer-Handler (Fader/Encoder/Buttons/Banks) | ⬜ Stub |
| `keylab_navigation.py` | Jog/Arrows/Window-Switching | ⬜ Stub |
| `keylab_daw_commands.py` | DAW Command Buttons (Snap/Undo/Metro...) | ⬜ Stub |
| `keylab_feedback.py` | LED- und Pad-Feedback | ⬜ Stub |

### Archiv (Referenz für Portierung)

| Ordner | Inhalt |
|:-------|:-------|
| `_archive/` | Alle 14 Original-`.py`-Dateien des alten Scripts (Farès MEZDOUR + Ray Juang) |

### Dokumentation

| Datei | Inhalt |
|:------|:-------|
| [`architecture.md`](architecture.md) | Modul-Abhängigkeiten, Import-Graph, Dead Code, bekannte Bugs & Risiken |
| [`hardware_map.md`](hardware_map.md) | Physische MIDI-Daten aller Controls (Ports, Kanäle, Note/CC/PB-Nummern) |
| [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md) | FL Studio MIDI Scripting API — lokale Referenz |
| [`IMPLEMENTATION_MAP.md`](IMPLEMENTATION_MAP.md) | Implementierungsplan: Hardware-MIDI ↔ gewünschte Funktionen (WIP) |
| [`BRAINSTORM.md`](BRAINSTORM.md) | Feature-Ideen mit Machbarkeits-Tracking |
| [`CONTROLLER_OVERVIEW.md`](CONTROLLER_OVERVIEW.md) | Historische Referenz (Funktionen korrekt, MIDI-Daten vom alten Mapping) |
| [`.cursorrules`](.cursorrules) | Pflicht-Crosschecks für AI-Agents |

---

## Für AI-Agents

Vor jeder Code-Änderung in diesem Workspace die folgenden Referenzen konsultieren (siehe auch `.cursorrules`):

1. **`FL_Studio_API_Reference.md`** — Jeden FL-API-Call verifizieren
2. **`hardware_map.md`** — Alle MIDI-Annahmen verifizieren
3. **`architecture.md`** — Modulstruktur und bekannte Probleme verstehen
4. **`IMPLEMENTATION_MAP.md`** — Gewünschte Funktionszuordnung prüfen
