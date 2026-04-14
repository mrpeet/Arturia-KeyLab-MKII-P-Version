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

* **Encoder → Plugin-Parameter wenn Plugin fokussiert**
  * *API-Check 🟡:* `plugins.setParamValue(paramIndex, value, slotIndex)` existiert. Problem: Parameter-Index ist Plugin-spezifisch. Ohne Mapping-Tabelle muss man generisch die ersten 8 Parameter nehmen. Alternative: `device.linkToLastTweaked`.

* **Preset-Wechsel über Links/Rechts**
  * *API-Check 🟢:* `plugins.nextPreset(slotIndex)` / `plugins.prevPreset(slotIndex)` — direkt verfügbar.

* **Analog Lab / V-Collection: CCs an Port 10 weiterleiten**
  * *API-Check 🟢:* `device.forwardMIDICC(message, port)` — direkt verfügbar. Braucht Companion-Script oder Port-10-Logik im Hauptscript.

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

---

*Alle API-Checks basieren auf [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md). Hardware-Daten verifiziert gegen [`hardware_map.md`](hardware_map.md).*