# Arturia KeyLab mkII — FL Studio MIDI Script (P Version)

Custom FL Studio user MIDI script for the **Arturia KeyLab mkII** keyboard controller. Provides transport control, mixer integration (faders, encoders, track buttons), pad modes, navigation, display feedback, and more.

> **Status:** 🚧 Neustrukturierung in Arbeit — das Script wird aktuell modular neu aufgebaut. Das alte Script ist voll funktionsfähig, wird aber schrittweise durch eine saubere, modulare Version ersetzt.

---

## Credits & Lizenz

Dieses Projekt basiert auf Arbeit mehrerer Entwickler:

### Farès MEZDOUR — Original-Script
- **Dateien:** `device_KeyLabmkII.py`, `device_Forward CCs Port 10 KEYLAB MKII.py`, `KeyLabmk2Process.py`, `KeyLabmk2Return.py`, `KeyLabmk2Navigation.py`, `KeyLabmk2Mapping.py`, `KeyLabmk2Plugin.py`, `KeyLabmk2SeqParam.py`, `ArturiaCrossKeyboardKLmk2.py`, `ArturiaVCOL.py`
- Haupt-Logik für MIDI-Processing, LED-Feedback, Step Sequencer, Plugin-Steuerung und Hardware-Mapping

### Ray Juang — Dispatcher & Display (MIT License, 2020)
- **Dateien:** `KeyLabmk2Dispatch.py`, `KeyLabmk2Display.py`, `KeyLabmk2Pages.py`
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

3. Unter **Input** den KeyLab mkII DAW-Port auswählen → als Controller Type **"KeyLab mkII P Version (user)"** zuweisen

4. Falls der Companion-Script für V-Collection/Analog Lab genutzt wird: den Keys-Port separat zuweisen

---

## Dateistruktur

### Python-Scripts

| Datei | Rolle |
|:------|:------|
| `device_KeyLabmkII.py` | Primäres FL MIDI Script (Entry Point) |
| `device_Forward CCs Port 10 KEYLAB MKII.py` | Companion: CC-Forwarding an Port 10 für V-Collection |
| `device_logger.py` | Optionales Logging-/Diagnose-Script |
| `KeyLabmk2Process.py` | Kern-Logik: MIDI-Events → FL Studio Aktionen |
| `KeyLabmk2Return.py` | LED- und Pad-Feedback an die Hardware |
| `KeyLabmk2Display.py` | LCD SysEx-Builder mit Scrolling |
| `KeyLabmk2Pages.py` | Timed-Page-Manager für das Display |
| `KeyLabmk2Dispatch.py` | Event-Dispatcher + `send_to_device` (SysEx) |
| `KeyLabmk2Navigation.py` | Kontext-Hints für Benutzeraktionen |
| `KeyLabmk2Mapping.py` | Hardware-Konstanten (Note/CC/PB-Nummern) |
| `KeyLabmk2Plugin.py` | Plugin-Parameter-Steuerung bei Fokus |
| `KeyLabmk2SeqParam.py` | Step-Sequencer Parameter-Editing |
| `ArturiaCrossKeyboardKLmk2.py` | Bank-Offsets für Mixer/Channel-Ansichten |
| `ArturiaVCOL.py` | V-Collection Plugin-Namensliste |

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
