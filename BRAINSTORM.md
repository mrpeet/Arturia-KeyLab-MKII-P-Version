# KeyLab mkII — Brainstorm & Feature-Ideen

> Sammelstelle für Implementierungsideen mit **API-Reality-Check**.
> Ideen werden bei Übernahme in die [`IMPLEMENTATION_MAP.md`](IMPLEMENTATION_MAP.md) verschoben
> und dort mit konkreten MIDI-Daten + API-Calls versehen.
>
> **Legende (API-Reality-Check):**
> * � **Möglich** — mit der Standard FL Studio API umsetzbar
> * � **Workaround nötig** — machbar, erfordert aber clevere Logik oder Umwege
> * 🔴 **Unmöglich** — harte Limitierung durch FL Studio
> * ⬜ **Offen** — noch nicht bewertet
> * ✅ **Erledigt** — in die `IMPLEMENTATION_MAP.md` übernommen

---

## 1. Mixer & Fader Sektion (Der "Triple-Threat" Mixer)

**Idee:** Die rechte Fader- und Encoder-Sektion soll nicht statisch sein, sondern über die Hardware-Tasten zwischen verschiedenen Modi umgeschaltet werden können.

### Modus 1: Intelligenter FL Mixer Fokus
Wenn der Mixer fokussiert ist, repräsentiert die Hardware exakt den Zustand in FL Studio.

* **Master-Fader (Fader 9):** Bleibt immer auf dem FL-Master-Kanal gelockt.
  * *API-Check 🟢:* Das interne KeyLab-Signal (0–16383) muss auf maximal 0.8 im FL Studio Mixer skaliert werden, damit 100% am Hardware-Fader exakt 0 dB in der Software entsprechen (`mixer.setTrackVolume`).
* **Dynamisches Banking (Fader 1–8):** Fader verschieben sich je nach in FL angewähltem Track (z.B. Track 12 angewählt → Fader steuern Track 12–19).
  * *API-Check 🟢:* Standard-Logik über Offset-Berechnung. `mixer.trackNumber()` für Selektion, `mixer.setTrackVolume(index + offset, value)` für Zugriff.
* **Soft Pickup:** Fader-Wert wird erst übernommen, wenn der physische Fader die Software-Position erreicht/kreuzt.
  * *API-Check 🟢:* Reines Script-Feature. Pro Fader den letzten FL-Wert (`mixer.getTrackVolume`) mit dem eingehenden PitchBend-Wert vergleichen. State-Tracking in `keylab_state.py`.
* **Touch-Sensor → Display:** Bei Berührung eines Faders (Note On 104–112) den Tracknamen auf dem Display anzeigen.
  * *API-Check 🟢:* `mixer.getTrackName(index + offset)` + Display-SysEx.
* **RGB Track-Colors:** Die Track-Buttons übernehmen die Farbe des Mixertracks aus FL Studio.
  * *API-Check 🟡:* `mixer.getTrackColor(index)` liefert den Farbwert. Da das KeyLab SysEx für Farben braucht, muss zwingend ein **Throttling** in den Code, um das MIDI-Signal bei schnellem Scrollen nicht zu überlasten.
* **Visuelle Orientierung:** Alle Track-Buttons leuchten standardmäßig auf 30 %. Der aktuell fokussierte Track leuchtet auf 100 %.
  * *API-Check 🟢:* Einfache IF/ELSE Logik im SysEx-Farb-Befehl.
* **Bank-Wechsel LED-Feedback:** Display zeigt temporär welche Bank aktiv ist (z.B. "Bank 2: Tracks 9–16").
  * *API-Check 🟢:* Reine Display-Logik mit ephemeral line (`KeyLabDisplay`).

### Fader Jitter-Filter (Hardware-Kompensation)
Alternde Fader können in Ruhepositionen minimale Wertschwankungen (±1–2 LSB) senden, die als Dauerfeuer von MIDI-Events ankommen.
* *API-Check 🟢:* Reines Script-Feature. Pro Fader den letzten gesendeten 14-Bit-Wert tracken (`keylab_state.fader_last_sent_value`). Neuer Wert wird nur akzeptiert wenn `abs(new - old) >= FADER_JITTER_THRESHOLD` (25 ≈ 0.15% der Range). Schützt auch Soft Pickup vor falschen Trigger-Events.

### Modus 2: Free Mode (Custom Mapping)
Ein Modus für maximale Freiheit, um die Bedienelemente pro Projekt individuell zuzuweisen.
* *API-Check 🟢:* Script setzt `event.handled = False`. FL Studio empfängt rohe MIDI-Daten und erlaubt manuelles "Link to controller".

### Modus 3: Macro / Plugin Mode
Ein Modus zur direkten Steuerung von Plugin-Parametern (besonders für FL-interne und Arturia-Plugins).
* *API-Check 🟡:* `plugins.setParamValue(paramIndex, value, slotIndex)` existiert. Erfordert jedoch Mapping-Tabellen pro Plugin. Alternative: `device.linkToLastTweaked` für dynamisches Mapping.

### Track Buttons: Modi (Select / Solo / Mute)
Umschalten der Track-Button-Funktion über Modifier-Button.
* *API-Check �:* `mixer.setTrackNumber` (Select), `mixer.soloTrack` (Solo), `mixer.muteTrack` (Mute) — alle vorhanden. Modifier-Logik ist reines Script-Feature.
* **Offene Frage:** Welcher Hardware-Button dient als Modifier? Kandidaten: Part 1/Part 2, oder ein DAW-Command-Button.

---

## 2. Transport & Playback

* **Rewind/FF: Short Press vs. Long Press**
  Short Press = Bar-Navigation, Long Press = kontinuierliches Spulen.
  * *API-Check 🟢:* `transport.rewind` / `transport.fastForward` für Spulen. Bar-Navigation via `transport.markerJumpJog`. Long-Press-Erkennung ist reines Script-Feature (Timer zwischen Note On / Note Off).

* **Tap Tempo**
  Tap Tempo über den "Read"-Button (Note 74) in der DAW-Command-Reihe.
  * *API-Check 🟢:* `transport.globalTransport(midi.FPT_TapTempo, value)` — direkt vorhanden.

* **Song-Position auf Display**
  Während Playback die aktuelle Position (Bar:Beat) auf dem Display anzeigen.
  * *API-Check �:* `transport.getSongPosHint()` liefert formatierten String. Anzeige via `OnIdle` + Display-Update.

---

## 3. Navigation Sektion (Jogwheel & Pfeile)

* **Kontextabhängiges Jogwheel**
  Browser → Scroll, Mixer → Track Select, Channel Rack → Channel Select, Plugin → Parameter-Scroll.
  * *API-Check 🟢:* `ui.getFocused(widMixer)` etc. für Kontext-Erkennung. `ui.jog(value)` für Browser, `mixer.setTrackNumber` für Mixer, `channels.selectOneChannel` für Channel Rack.

* **Doppelklick auf Jog = Enter/Bestätigen**
  * *API-Check 🟢:* `device.isDoubleClick` existiert. Bei Doppelklick → `ui.enter()`.

* **Links/Rechts kontextabhängig**
  Browser → Tab wechseln, Plugin → Preset wechseln, sonst → Pattern wechseln.
  * *API-Check �:* `ui.navigateBrowserTabs(direction)` für Browser. `plugins.nextPreset` / `plugins.prevPreset` für Plugins. `patterns.jumpToPattern` für Patterns.

### Edison Scrubbing & Editing
Wenn Edison fokussiert ist, soll das Jogwheel zum Scrobbeln durch die Audiodatei genutzt werden.
* *API-Check 🔴/🟡:* Echtes Scrubbing (Playhead-Position auslesen) ist per API **unmöglich**.
* *Workaround:* `ui.left()` / `ui.right()` für Navigation. Stark eingeschränkte Funktionalität.

---

## 4. Pads

* **Pad-Farben per SysEx an Channel/Pattern anpassen**
  * *API-Check 🟢:* `channels.getChannelColor(index)` + SysEx-Protokoll aus altem Script. Farb-Konvertierung (FL RGB → KeyLab 5-Bit RGB) nötig.

* **Step Sequencer auf Pads: aktive Steps leuchten**
  * *API-Check 🟢:* `channels.getGridBit(index, step)` liefert Step-Status. SysEx-Feedback für Pad-Farben. Braucht `OnRefresh` mit `HW_Dirty_LEDs` Flag.

* **Velocity-Kurve umschalten (Full/Soft/Hard)**
  Per Long Press auf TogglePadMode (Note 87).
  * *API-Check 🟢:* Rein internes Script-Feature. Velocity-Wert vor Weiterleiten skalieren.

* **Pad Velocity Visualisierung**
  Die Pads sollen die Anschlagstärke durch ihre Leuchtkraft widerspiegeln.
  * *API-Check 🟢:* Feste Basishelligkeit (20–30 %) + eingehender Velocity-Wert (0–127) wird in die Helligkeits-Variable des SysEx-RGB-Befehls umgerechnet.

* **Pad-Aftertouch für Expression-Mapping**
  Poly Aftertouch der Pads für z.B. Filter Cutoff nutzen.
  * *API-Check �:* Hardware sendet Poly Aftertouch (Kanal 10). FL empfängt via `OnKeyPressure`. Routing auf Plugin-Parameter erfordert `channels.setChannelPitch` oder manuelles CC-Mapping — kein direktes "Aftertouch → Filter" in der API.

---

## 5. Display (LCD)

* **Zweizeiliges Kontext-Display**
  Zeile 1 = Kontext (Mixer/Channel/Plugin), Zeile 2 = Wert/Name.
  * *API-Check 🟢:* Display-SysEx aus `KeyLabmk2Display.py` ist bewährt, wird 1:1 portiert.

* **Temporäre Hinweise mit Auto-Rückkehr**
  Z.B. "Bank 2" für 2 Sekunden, dann zurück zum Hauptdisplay.
  * *API-Check 🟢:* Timer-Logik aus `KeyLabmk2Pages.py` — ephemeral lines mit `expires` Parameter.

* **Pattern-Name + Nummer dauerhaft**
  * *API-Check 🟢:* `patterns.patternNumber()` + `patterns.getPatternName(index)`.

* **Plugin-Fokus: Plugin-Name + Parameter**
  * *API-Check 🟢:* `ui.getFocusedPluginName()` + `plugins.getParamName(paramIndex, slotIndex)`.

---

## 6. LED Feedback

* **Transport-LEDs: Status widerspiegeln**
  Play/Record/Loop LEDs zeigen aktuellen Status.
  * *API-Check �:* `transport.isPlaying()`, `transport.isRecording()`, `transport.getLoopMode()`. LED-Steuerung via `device.midiOutMsg` oder SysEx.

* **Beat-Indikator: LED blinkt im Takt**
  * *API-Check 🟢:* `OnUpdateBeatIndicator(value)` Callback — `value` gibt Beat/Bar/Off an.

* **Metronom-LED: leuchtet wenn aktiv**
  * *API-Check 🟢:* `general.getUseMetronome()` vorhanden.

---

## 7. System & Feedback

### Fast Boot Animation
Die aktuelle Startup-Animation (Lauflicht) dauert zu lange und stört bei schnellen Script-Refreshes.
* *API-Check 🟢:* Ein kurzes Aufblitzen aller relevanten LEDs in `OnInit()` reicht als visuelle Bestätigung.

---

## 8. Plugin-Steuerung

Es gibt **drei unabhängige Ansätze** zur Plugin-Steuerung über Hardware. Sie schließen sich nicht gegenseitig aus.

### Ansatz A: Free Mode (Priorität: HOCH)
Der universellste Ansatz. Script setzt `event.handled = False`, FL Studio empfängt rohe MIDI-Daten.
User nutzt FL Studios eingebautes **"Link to controller"** (Rechtsklick → Link to controller) um beliebige Parameter an beliebige Hardware-Controls zu binden.
* *API-Check �:* Kein spezieller Code nötig — nur `event.handled = False` setzen.
* **Pro:** Funktioniert mit jedem Plugin, keine Mapping-Tabelle, keine Pflege.
* **Contra:** Mappings sind pro Projekt, nicht pro Plugin. Muss jedes Mal neu gemacht werden.

### Ansatz B: Plugin Database via FL API (Priorität: MITTEL)
Script erkennt automatisch das fokussierte Plugin (`ui.getFocusedPluginName()`) und steuert Parameter direkt über `plugins.setParamValue()`. Erfordert pro Plugin eine **Mapping-Tabelle** (welcher Encoder/Fader → welcher Parameter-Index).
* *API-Check 🟢:* `plugins.setParamValue(value, paramIndex, channelIndex)` + `plugins.getParamName(paramIndex, channelIndex)` — beides vorhanden, funktioniert mit FL-internen UND 3rd-Party-Plugins.

**Implementierung:** Eigene Datei `plugin_database.py` mit einfacher Dictionary-Struktur:
```python
PLUGIN_MAPS = {
    'FLEX': {
        'encoders': { 1: (21, 'Macro 1'), 2: (22, 'Macro 2'), ... },
        'faders':   { 1: (10, 'Volume'), ... },
    },
}
```
**User-Zugänglichkeit:**
- Header-Kommentar mit Schritt-für-Schritt-Anleitung zum Hinzufügen neuer Plugins
- Debug-Helper: Bei unbekanntem Plugin alle Parameter mit Index + Name in Script Output loggen
- Struktur so einfach, dass Hinzufügen per Copy-Paste oder per AI-Prompt möglich ist
- Für unbekannte Plugins: Fallback auf **generischen Modus** (erste 8 Parameter auf Encoder)

**Bereits im alten Script gemappte Plugins** (als Vorlage in `_archive/KeyLabmk2Plugin.py`):
FLEX, FPC, FL Keys, Sytrus, GMS, Harmless, Harmor, Morphine, 3x Osc, Fruity DX10, BassDrum, Fruit Kick, MiniSynth, PoiZone, Sakura

**Display-Feedback:** Beim Drehen eines Encoders/Faders wird der **Parametername + Wert** auf dem LCD angezeigt → User muss nichts auswendig lernen.

### Ansatz C: Port 10 Forwarding für V-Collection (Priorität: NIEDRIG)
Separates Forward-Script (`device_KeyLabmkII_Forward.py`) leitet CCs vom Keys Port an FL Studios internen Port 10 weiter. Arturia V-Collection Plugins (Analog Lab, Mini V, Jup-8 etc.) haben **vorgefertigte CC-Mappings** und funktionieren sofort, wenn ihr MIDI-In-Port auf 10 steht.
* *API-Check 🟢:* `device.forwardMIDICC(message, port)` — direkt verfügbar.
* **Pro:** Arturia-Plugins funktionieren sofort ohne Mapping-Arbeit.
* **Contra:** Nur für Arturia-Plugins nützlich. Jede Plugin-Instanz muss manuell MIDI-In Port 10 bekommen. Alle Plugins auf Port 10 empfangen gleichzeitig — keine automatische Trennung.
* **Alternative:** Hardware "Analog Lab"-Modus (kein Script nötig, aber kein gleichzeitiger DAW-Zugriff).

### Preset-Wechsel über Links/Rechts
* *API-Check 🟢:* `plugins.nextPreset(slotIndex)` / `plugins.prevPreset(slotIndex)` — direkt verfügbar. Kontextabhängig: nur wenn Plugin fokussiert.

---

## 9. Architektur & Code-Qualität

* **Klare Modul-Trennung** (kein zirkulärer Import)
  * *API-Check �:* Reines Design-Pattern. Dispatch → Handler → State → Feedback.

* **Zentraler State** (`keylab_state.py`) statt Module-Level Globals
  * *API-Check 🟢:* Reine Python-Architektur. Löst Problem #3 aus `architecture.md`.

* **Event-Dispatcher mit registrierbaren Handlern**
  * *API-Check 🟢:* `MidiEventDispatcher` aus `KeyLabmk2Dispatch.py` als Basis. Erweitern mit `register()`-Pattern.

* **Logging-Modul für Debug-Ausgaben** (an/aus schaltbar)
  * *API-Check 🟢:* `device_logger.py` als Basis. Python `print()` geht in FL Script Output.

---

## Entschiedene Fragen

- [x] **Companion-Script (Port 10):** Bleibt **separat** — zwei unabhängige Scripts für zwei Hardware-Inputs:
  - Port 0 = `KeyLab mkII 61` → Forward-Script (V-Collection CCs)
  - Port 1 = `MIDIIN2 (KeyLab mkII 61)` → Hauptscript (DAW-Steuerung)
  - Beide Scripts sollten über `# name=` und `# supportedDevices=` klar dokumentieren, welcher Input/Port benötigt wird.
- [x] **Channel-Rack-Steuerung:** **Gleichwertiger Modus**, nicht optional. Die Fader/Encoder-Sektion wechselt **automatisch** je nach fokussiertem Fenster (Mixer → Mixer-Tracks, Channel Rack → Channel-Rack-Kanäle). Banking, Jog-Navigation und Track-Button-Feedback funktionieren identisch für beide. Architektur muss von vornherein abstrakt genug für beide Backends sein.
- [x] **Display-SysEx:** **1:1 portieren** aus `KeyLabmk2Display.py` + `KeyLabmk2Pages.py` (Ray Juang, MIT 2020). Bewährt, keine Bugs.
- [x] **Track-Button-Modi (Select/Solo/Mute):** **Long Press auf Track-Button** — Short Press = Select, Long Press = Solo, Double-Click = Mute. Kein extra Modifier-Button nötig.
- [x] **Free Mode:** **Script-Toggle über Button** (z.B. Long Press auf Save/Note 80). Man bleibt im DAW-Modus der Hardware, aber Fader/Encoder werden an FL Studio durchgereicht für manuelles "Link to controller".
- [x] **Plugin-Steuerung:** Drei getrennte Ansätze, unabhängig voneinander:
  - **Free Mode** (Prio hoch) — universell, für jeden Parameter in jedem Plugin
  - **Plugin Database** (Prio mittel) — `plugins.setParamValue()` mit curated Mappings pro Plugin, user-friendly erweiterbar über `plugin_database.py`
  - **Port 10 Forwarding** (Prio niedrig) — nur für Arturia V-Collection, optional, separates Script
- [x] **Port 10 Forwarding:** Ist **optional** und nur für Arturia V-Collection relevant. Für FL-interne und 3rd-Party-Plugins nutzt das Script die FL API direkt (`plugins.setParamValue`), kein Forwarding nötig. Das Forward-Script (`device_KeyLabmkII_Forward.py`) ist eigenständig und hat keine Abhängigkeit zum Hauptscript.

---

*Alle API-Checks basieren auf [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md). Hardware-Daten verifiziert gegen [`hardware_map.md`](hardware_map.md).*