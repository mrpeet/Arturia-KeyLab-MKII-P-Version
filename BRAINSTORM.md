# KeyLab mkII — Brainstorm & Feature-Ideen

> Sammelstelle für Implementierungsideen, die noch auf **Machbarkeit geprüft** werden müssen.
> Nichts hier ist beschlossen — alles ist Diskussionsgrundlage.
>
> **Legende:**
> - 💡 Idee — noch nicht geprüft
> - 🔍 In Prüfung — Machbarkeit wird untersucht
> - ✅ Übernommen → nach `IMPLEMENTATION_MAP.md` verschoben
> - ❌ Verworfen — mit Begründung

---

## Transport & Playback

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| T1 | Rewind/FF: Short Press = Bar-Navigation, Long Press = kontinuierliches Spulen | 💡 | War im alten Script so; Long-Press-Erkennung nötig |
| T2 | Tap Tempo über mehrfaches Drücken eines DAW-Buttons | 💡 | `FPT_TapTempo` via `globalTransport` |
| T3 | Song-Position auf Display anzeigen während Transport | 💡 | Braucht `OnIdle` + Display-Logik |

---

## Mixer & Fader

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| M1 | Soft Pickup für Fader (Wert erst übernehmen wenn Fader physische Position erreicht) | 💡 | Verhindert Sprünge; braucht State-Tracking pro Fader |
| M2 | Fader Touch-Sensor: bei Berührung Trackname auf Display zeigen | 💡 | Touch = Note On 104–112 |
| M3 | Track Buttons: Modi umschalten (Select / Solo / Mute) über Modifier-Button | 💡 | Welcher Button als Modifier? |
| M4 | Bank-Wechsel: LED-Feedback welche Bank aktiv ist | 💡 | SysEx an Pads oder Display nötig |

---

## Pads

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| P1 | Pad-Farben per SysEx an aktiven Channel/Pattern anpassen | 💡 | SysEx-Protokoll aus altem Script übernehmen |
| P2 | Step Sequencer auf Pads: aktive Steps leuchten | 💡 | `channels.getGridBit` + SysEx-Feedback |
| P3 | Velocity-Kurve umschalten (Full/Soft/Hard) über Long Press | 💡 | Nur interner State; kein FL-API nötig |
| P4 | Pad-Aftertouch für Expression-Mapping (z.B. Filter Cutoff) | 💡 | Hardware sendet Poly Aftertouch; FL-Routing prüfen |

---

## Display (LCD)

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| D1 | Zweizeilig: Zeile 1 = Kontext (Mixer/Channel/Plugin), Zeile 2 = Wert/Name | 💡 | Display-SysEx aus altem Script vorhanden |
| D2 | Temporäre Hinweise (z.B. "Bank 2" für 2 Sekunden) mit Auto-Rückkehr | 💡 | Timer-Logik aus `KeyLabmk2Pages.py` |
| D3 | Pattern-Name + Nummer dauerhaft auf Display | 💡 | `patterns.getPatternName` |
| D4 | Bei Plugin-Fokus: Plugin-Name + Parameter auf Display | 💡 | `ui.getFocusedPluginName` + `plugins.getParamName` |

---

## Navigation & UI

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| N1 | Jog Wheel kontextabhängig: Browser → Scroll, Mixer → Track Select, Channel → Channel Select | 💡 | Braucht Window-Focus-Erkennung |
| N2 | Doppelklick auf Jog = "Enter" / Bestätigen | 💡 | `device.isDoubleClick` vorhanden |
| N3 | Links/Rechts-Pfeile: im Browser → Tab wechseln, sonst → Pattern wechseln | 💡 | War im alten Script kontextabhängig |

---

## Plugin-Steuerung

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| PL1 | Encoder → Plugin-Parameter wenn Plugin-Fenster fokussiert | 💡 | `plugins.setParamValue`; Parameter-Mapping pro Plugin? |
| PL2 | Preset-Wechsel über Links/Rechts wenn Plugin fokussiert | 💡 | `plugins.nextPreset` / `plugins.prevPreset` |
| PL3 | Analog Lab / V-Collection: CCs an Port 10 weiterleiten | 💡 | `device.forwardMIDICC`; Companion-Script nötig |

---

## LED Feedback

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| L1 | Transport-LEDs: Play/Record/Loop Status widerspiegeln | 💡 | `transport.isPlaying` / `isRecording` / `getLoopMode` |
| L2 | Beat-Indikator: LED blinkt im Takt | 💡 | `OnUpdateBeatIndicator` Callback |
| L3 | Metronom-LED: leuchtet wenn aktiv | 💡 | `general.getUseMetronome` |

---

## Architektur & Code-Qualität

| # | Idee | Status | Notizen |
|:--|:-----|:-------|:--------|
| A1 | Klare Modul-Trennung: Dispatch → Process → Return (kein zirkulärer Import) | 💡 | Altes Script hat problematische Kopplungen (siehe `architecture.md`) |
| A2 | State als zentrale Klasse statt Module-Level Globals | 💡 | Testbarkeit und Übersichtlichkeit |
| A3 | Event-Dispatcher Pattern mit registrierbaren Handlern | 💡 | Statt monolithischer if/elif Ketten |
| A4 | Logging-Modul für Debug-Ausgaben (an/aus schaltbar) | 💡 | `device_logger.py` als Basis |

---

## Offene Fragen

- [ ] Soll das Companion-Script (Port 10 Forwarding) im neuen Script integriert oder separat bleiben?
- [ ] Welche Funktionen haben Priorität für die erste lauffähige Version (MVP)?
- [ ] Soll die Channel-Rack-Steuerung (Fader/Encoder → Channel Vol/Pan) von Anfang an dabei sein oder erst nach Mixer?
- [ ] Display-SysEx: Protokoll aus altem Script 1:1 übernehmen oder neu aufsetzen?

---

*Ideen werden bei Übernahme in die [`IMPLEMENTATION_MAP.md`](IMPLEMENTATION_MAP.md) verschoben und dort mit konkreten MIDI-Daten + API-Calls versehen.*
