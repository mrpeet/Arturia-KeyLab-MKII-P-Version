# Arturia KeyLab mkII — Benutzerhandbuch

**Script: KeyLab mkII P Version**
Letzte Aktualisierung: 2026-04-15

---

## Inhalt

1. [Modi und Kontexte](#1-modi-und-kontexte)
2. [Transport](#2-transport)
3. [DAW Commands](#3-daw-commands)
4. [Navigation (Jog Wheel + Bank)](#4-navigation-jog-wheel--bank)
5. [Mixer Fader (Volume)](#5-mixer-fader-volume)
6. [Mixer Encoder (Pan)](#6-mixer-encoder-pan)
7. [Track Buttons](#7-track-buttons)
8. [Bank Buttons](#8-bank-buttons)
9. [Plugin-Steuerung](#9-plugin-steuerung)
10. [Free Mode](#10-free-mode)
11. [LCD-Feedback](#11-lcd-feedback)
12. [Pads](#12-pads)
13. [LED-Regeln](#13-led-regeln)

---

## 1. Modi und Kontexte

Das Script wechselt automatisch zwischen Steuerungskontexten, je nachdem welches FL Studio Fenster fokussiert ist. Es gibt **keine manuelle Umschaltung** notwendig — außer für den [Free Mode](#10-free-mode).

| Fokussiertes Fenster | Encoder 1–8 | Fader 1–8 | Jog Wheel |
|:---------------------|:------------|:----------|:----------|
| **Channel Rack** | Pan (Channels) | Volume (Channels) | Channel wechseln |
| **Mixer** | Pan (Mixer Tracks) | Volume (Mixer Tracks) | Mixer Track wechseln |
| **Plugin Editor** | Plugin-Parameter | Volume (Mixer Tracks) | Preset-Navigation* |
| **Browser** | Pan (Channel Rack) | Volume (Channel Rack) | Browser-Items navigieren |
| **Free Mode** | MIDI Passthrough | MIDI Passthrough | Normal |

*Nur bei Plugins mit definierter `jog_wheel`-Funktion in `plugin_database.py`.

---

## 2. Transport

Die Transport-Buttons senden ihre Aktionen an FL Studio und zeigen LED-Feedback.

| Button | Funktion | LED |
|:-------|:---------|:----|
| **Play** | Play / Pause | Leuchtet bei Wiedergabe |
| **Stop** | Stop | — |
| **Record** | Aufnahme starten/stoppen | Leuchtet bei Aufnahme |
| **Loop** | Loop ein/aus | Leuchtet wenn Loop aktiv |
| **Rewind** | Rückspulen (schnell bei gehalten) | — |
| **Fast Forward** | Vorspulen (schnell bei gehalten) | — |

---

## 3. DAW Commands

Die Utility-Buttons oben links.

| Button | Kurz-Druck | Lang-Druck (≥0,75 s) |
|:-------|:-----------|:---------------------|
| **Save** | Browser ↔ Channel Rack | — |
| **In** | Pad-Modus (Chromatic / Drum Map) | Pad-Velocity ein/aus |
| **Out** | Overdub | — |
| **Metro** | Metronome | — |
| **Undo** (Global) | Redo | — |
| **Write** (Track) | Undo | Cut |
| **Record** (Track) | Snap | — |
| **Solo** (Track) | New Pattern | — |
| **Mute** (Track) | Mixer fokussieren | — |
| **Read** (Track) | Tap Tempo | — |

> **Long Press:** Aktion und LCD erscheinen bei **0,75 s Haltezeit** — noch bevor du loslässt. Kurzer Druck = Aktion beim Loslassen.

---

## 4. Navigation (Jog Wheel + Bank)

### Jog Wheel drehen

Kontextabhängig:

| Kontext | Aktion |
|:--------|:-------|
| **Channel Rack / Default** | Nächster/Vorheriger Channel |
| **Mixer** | Nächster/Vorheriger Mixer Track |
| **Browser** | Nächstes/Vorheriges Item |
| **Browser (Popup-Menü)** | Auf/Ab im Menü |
| **Plugin mit Jog-Mapping** | Nächstes/Vorheriges Preset |

### Jog Wheel klicken

| Kontext | Aktion |
|:--------|:-------|
| **Channel Rack** | Plugin-Editor öffnen |
| **Plugin Editor** | Plugin-Editor schließen |
| **Mixer** | Track arm/un-arm |
| **Browser (Ordner)** | Ordner auf/zuklappen |
| **Browser (Datei)** | Datei laden |
| **Anderes** | Nächstes Fenster |

### Bank Left / Right (Pfeiltasten oben)

| Kontext | Aktion |
|:--------|:-------|
| **Plugin fokussiert** | Vorheriges / Nächstes Preset |
| **Browser** | Vorheriger / Nächster Browser-Tab |
| **Mixer** | Vorheriger / Nächster Track |
| **Default** | Vorheriges / Nächstes Pattern |

---

## 5. Mixer Fader (Volume)

Die 9 Fader steuern die Lautstärke:

| Fader | Kontext: Mixer | Kontext: Channel Rack |
|:------|:--------------|:----------------------|
| **1–8** | Mixer Tracks 1–8 (+ Bank Offset) | Channels 0–7 (+ Bank Offset) |
| **9 (Master)** | Immer: Master Volume | Immer: Master Volume |

### Soft Pickup

Beim ersten Bewegen eines Faders nach dem Laden zeigt das LCD den aktuellen FL-Wert in dB (z. B. `-> -6.0 dB`). Der Fader muss erst diesen Wert **kreuzen**, bevor er aktiv wird — so entstehen keine Sprünge.

Beim Bewegen: **Zeile 1** = Track-/Channel-Name, **Zeile 2** = Lautstärke in **dB** (aus FL gelesen, nicht aus der Hardware-Position — auch bei schneller Faderbewegung korrekt).

> **Tipp:** Fader berühren zeigt Track-Name (Zeile 1) und aktuelle dB (Zeile 2).

### Banking

Mit den [Bank Buttons (Prev/Next)](#8-bank-buttons) (Part 48/49) wechselst du in Schritten von 8 Inserts/Channels — bis zum **letzten** Track des Projekts. Das LCD zeigt den echten Bereich (z. B. `Tracks 25–31`, nicht `25–32` wenn der letzte Slot leer ist). Beim Bank-Wechsel wird Soft Pickup zurückgesetzt.

---

## 6. Mixer Encoder (Pan)

Encoder 1–8 steuern Pan (Links/Rechts):

| Encoder | Kontext: Mixer | Kontext: Channel Rack |
|:--------|:--------------|:----------------------|
| **1–8** | Pan Mixer Track | Pan Channel |
| **9 (Master)** | *(reserviert)* | *(reserviert)* |

LCD zeigt: `TrackName / L 30%` oder `Center` oder `R 45%`

> **Im Plugin-Modus** steuern Encoder 1–8 stattdessen Plugin-Parameter (siehe [Plugin-Steuerung](#9-plugin-steuerung)).

---

## 7. Track Buttons

Die 9 Buttons unter den Encodern:

| Aktion | Funktion |
|:-------|:---------|
| **Kurz drücken** | Track/Channel muten / unmuten |
| **Lang drücken (≥0,75 s)** | Pan Reset (Mixer) oder Solo (Channel Rack) — LCD bei Schwelle |

> Button 9 (Master) ist reserviert.

---

## 8. Bank Buttons

Die zwei Buttons links neben den Fadern (`<` und `>`):

| Button | Kurz-Druck | Lang-Druck (≥0,75 s) |
|:-------|:-----------|:---------------------|
| **`<` (Bank Prev)** | Bank um 8 zurück (min. 0) | **Free Mode** ein/aus (LCD bei Schwelle) |
| **`>` (Bank Next)** | Bank um 8 vor | — |

LCD zeigt beim Bank-Wechsel: `Bank / Tracks 9-16` (letzte Bank nur bis zum höchsten vorhandenen Track)

---

## 9. Plugin-Steuerung

Wenn ein Plugin-Editor fokussiert ist, wechseln die **Encoder 1–8 automatisch** in den Plugin-Modus.

### Bekannte Plugins

Für über 300 Plugins sind Parameter in `plugin_database.py` definiert. Die 8 Encoder-Slots sind nach diesem Schema belegt:

| Slot | Typische Funktion |
|:-----|:-----------------|
| 1 | Filter Cutoff |
| 2 | Resonance |
| 3 | Attack |
| 4 | Release |
| 5 | Modulation |
| 6 | FX1 Level |
| 7 | FX2 Level |
| 8 | Volume / Level |

LCD zeigt: `Parametername / 67%`

### Unbekannte Plugins

Wenn ein Plugin **nicht** in `plugin_database.py` vorhanden ist:
- LCD zeigt: `PluginName / Not mapped!`
- Encoder sind **blockiert** (keine Aktion, kein versehentliches Pan-Ändern)

> **Plugin hinzufügen:** In `plugin_database.py` einen neuen Eintrag anlegen. Die Debug-Funktion `scan_plugin_params()` in `keylab_plugin.py` listet alle verfügbaren Parameter-Indizes.

### Plugin-Jog (Preset-Navigation)

Plugins mit `"special": {"jog_wheel": "preset_navigation"}` in der Datenbank nutzen das Jog Wheel für Preset-Navigation statt Channel-Wechsel.

---

## 10. Free Mode

**Free Mode** ist ein manuell aktivierter Modus, der die gesamte Mixer-Sektion (Fader 1–8, Encoder 1–8, Track Buttons 1–8) von der automatischen Steuerung befreit und als **blank MIDI-Controller** nutzbar macht.

### Aktivieren / Deaktivieren

**Long Press `<` (Bank Prev) für ≥0,75 Sekunden** → Free Mode an/aus (Feedback auf LCD bei Erreichen der Schwelle)

LCD zeigt: `FREE MODE / Active` oder `FREE MODE / Off`

### Verhalten im Free Mode

| Element | Free Mode AUS | Free Mode AN |
|:--------|:-------------|:------------|
| Fader 1–8 | Volume (Mixer/Channel) | MIDI Passthrough |
| Encoder 1–8 | Pan / Plugin-Parameter | MIDI Passthrough |
| Track Buttons 1–8 | Pan Reset / Mute | MIDI Passthrough |
| **Fader 9 (Master)** | Master Volume | **Immer Master Volume** |
| **Encoder 9** | *(reserviert)* | *(reserviert)* |
| **Track Button 9** | *(reserviert)* | *(reserviert)* |
| Plugin-Modus | Auto-detect | **Deaktiviert** |

> **MIDI Passthrough** bedeutet: FL Studio empfängt die rohen MIDI-Events (Pitch Bend / CC / Note) und kann sie frei über MIDI Learn oder andere Scripts zuweisen.

> **Wichtig:** Free Mode wird **nicht** automatisch deaktiviert wenn das Fenster wechselt. Nur ein weiterer Long Press auf `<` deaktiviert ihn.

---

## 11. LCD-Feedback

Das LCD zeigt kontextuell Informationen. Die Anzeigedauer variiert:

| Kontext | Zeile 1 | Zeile 2 | Dauer |
|:--------|:--------|:--------|:------|
| Standard | Channel-Name | Pattern-Name | dauerhaft |
| Fader | Track-Name | Lautstärke dB (FL-Readback) | 0,8s |
| Fader (Touch) | Track-Name | dB (aktuell) | 2s |
| Encoder | Track-Name | `L 30%` / `Center` / `R 45%` | 0,8s |
| Navigation | `Nav` | Beschreibung | 1s |
| Plugin | Plugin-Name | Parameter / `Not mapped!` | 1,5s |
| Bank | `Bank` | `Tracks 9-16` | 1,2s |
| Free Mode | `FREE MODE` | `Active` / `Off` | 1,5s |
| Transport | — | — | sofort via LED |

---

## 12. Pads

**Layout (Pad 1 oben links):** Reihe 1 = Noten 36–39, Reihe 4 unten = 48–51 (siehe `hardware_map.md`).

- **Drum Map:** Standard GM-Drum-Layout (intern `fpc`)
- **Chromatischer Modus:** Pad 1 = C3, Pad 2 = C#3, … (Pad 16 = höchste Note der Bank)
- **Modus-Wechsel:** In-Button (Note 87) kurz drücken
- **Pad-Velocity:** In-Button (Note 87) lang drücken (≥0,75 s) — LCD `Pad Velo: On` / `Pad Velo: Off`; aus = feste 75%-Anschlagstärke (MIDI 95)
- **Pad-LEDs:** Chromatic = **weiß**, Drum Map = **lila**; ungedrückt **50%**, beim Drücken heller bis **100%** (Anschlagstärke). In Arturia MIDI Control Center: Pad-LED = **Off** (nicht „Light when triggered“)
- **Plugin-Modus:** Encoder steuern Plugin-Parameter; Hardware-Fader 1–8 sind deaktiviert — für Fader-Passthrough **Free Mode** (Bank Prev lang)

---

## 13. LED-Regeln

Vollständige Spezifikation: [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md)

- **DAW/Navigation:** Toggle-Zustände 30%/100%; Nav + Part Prev/Next immer 100% (einmalig bei Init)
- **Track-Buttons 1–8:** FL-Farbe; muted = aus, ausgewählt = 100%, andere in der Bank = 20% (nur bei Track-/Bank-Wechsel)

---

*Für technische Details und Plugin-Mappings: siehe `plugin_database.py` und `ROADMAP.md`*
