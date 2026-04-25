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
12. [Pads](#12-pads) *(Phase 11 – in Arbeit)*

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

| Button | Kurz-Druck | Lang-Druck (>1s) |
|:-------|:-----------|:-----------------|
| **Save** | Snap Toggle | — |
| **In** | Undo | Cut |
| **Out** | Redo | — |
| **Metro** | Metronome an/aus | — |
| **Undo** | Tap Tempo | — |
| **Quantize** | Overdub an/aus | — |
| **Add Track** | New Pattern (ohne Dialog) | — |
| **Punch** | Mixer fokussieren | — |

> **Hinweis:** Long Press auf "In" führt Cut aus (nicht Undo). Kurzer Druck = Undo.

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

Beim ersten Bewegen eines Faders nach dem Laden zeigt das LCD den aktuellen FL-Wert (`-> 75%`). Der Fader muss erst diesen Wert **kreuzen**, bevor er aktiv wird — so entstehen keine Sprünge.

> **Tipp:** Fader berühren zeigt den Track-Namen auf dem LCD.

### Banking

Mit den [Bank Buttons (Prev/Next)](#8-bank-buttons) kann auf Tracks 9–16, 17–24 usw. umgeschaltet werden. Beim Bank-Wechsel wird Soft Pickup zurückgesetzt.

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
| **Kurz drücken** | Pan des Tracks/Channels auf Center (0) zurücksetzen |
| **Lang drücken (>1s)** | Track/Channel muten / unmuten |

> Button 9 (Master) ist reserviert.

---

## 8. Bank Buttons

Die zwei Buttons links neben den Fadern (`<` und `>`):

| Button | Kurz-Druck | Lang-Druck (>1s) |
|:-------|:-----------|:-----------------|
| **`<` (Bank Prev)** | Bank um 8 zurück (min. 0) | **Free Mode** ein/aus |
| **`>` (Bank Next)** | Bank um 8 vor | — |

LCD zeigt beim Bank-Wechsel: `Bank / Tracks 9-16`

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

**Long Press `<` (Bank Prev) für >1 Sekunde** → Free Mode an/aus

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
| Fader | `Fader N` / `Master` | Lautstärke % | 0,8s |
| Fader (Touch) | `Fader N` | Track-Name | 2s |
| Encoder | Track-Name | `L 30%` / `Center` / `R 45%` | 0,8s |
| Navigation | `Nav` | Beschreibung | 1s |
| Plugin | Plugin-Name | Parameter / `Not mapped!` | 1,5s |
| Bank | `Bank` | `Tracks 9-16` | 1,2s |
| Free Mode | `FREE MODE` | `Active` / `Off` | 1,5s |
| Transport | — | — | sofort via LED |

---

## 12. Pads

*(Phase 11 — noch nicht implementiert)*

Geplant:
- **FPC-Modus:** Standard Drum-Layout für FL Studio FPC
- **Chromatischer Modus:** Chromatische Noten ab C3
- **Modus-Wechsel:** In-Button (Note 87) kurz drücken

---

*Für technische Details und Plugin-Mappings: siehe `plugin_database.py` und `ROADMAP.md`*
