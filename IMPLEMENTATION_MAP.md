# KeyLab mkII — Implementation Map

> **Status:** 🚧 Work in Progress — wird während der Entwicklung aktualisiert.
>
> Dieses Dokument verbindet die **physischen MIDI-Daten** (Quelle: `hardware_map.md`) mit den
> **gewünschten FL Studio Funktionen** (Quelle: eigene Planung + `BRAINSTORM.md`).
> Es dient als verbindlicher Implementierungsplan für das neue Script.
>
> **Hinweis:** Das Forward-Script (`device_KeyLabmkII_Forward.py`) ist **optional** und nur für
> Arturia V-Collection Plugins relevant. Alle anderen Features funktionieren ohne es.
>
> **Legende Status:** ⬜ offen · 🔧 in Arbeit · ✅ fertig · ❌ verworfen

---

## 1. Transport (DAW Port · Note On · Kanal 1)

| Hardware-Label | Typ     | Data1 | Funktion             | FL API / Logik                                    | Status |
|:---            |:---     |:---   |:---                  |:---                                               |:---    |
| Rewind (<<)    | Note On | 91    | RewindORprevBar      | `transport.rewind` / `transport.markerJumpJog(-1)` | ⬜     |
| Fast Fwd (>>)  | Note On | 92    | FastForwardORnextBar | `transport.fastForward` / `transport.markerJumpJog(1)` | ⬜ |
| Stop           | Note On | 93    | Stop                 | `transport.stop`                                  | ⬜     |
| Play           | Note On | 94    | Start                | `transport.start`                                 | ⬜     |
| Record         | Note On | 95    | Record               | `transport.record`                                | ⬜     |
| Loop           | Note On | 86    | Loop                 | `transport.setLoopMode`                           | ⬜     |

---

## 2. DAW Commands — Track Controls (DAW Port · Note On · Kanal 1)

| Hardware-Label | Typ     | Data1 | Funktion        | FL API / Logik                          | Status |
|:---            |:---     |:---   |:---             |:---                                     |:---    |
| Record (Reihe 1) | Note On | 0  | SnapToggle      | `ui.snapOnOff`                          | ⬜     |
| Solo           | Note On | 8     | NewPattern      | `patterns.findFirstNextEmptyPat`        | ⬜     |
| Mute           | Note On | 16    | FocusMixer      | `ui.showWindow(widMixer)`               | ⬜     |
| Read           | Note On | 74    | TapTempo        | `transport.globalTransport(FPT_TapTempo)` | ⬜   |
| Write          | Note On | 75    | Redo            | `general.undoUp`                        | ⬜     |

---

## 3. DAW Commands — Global Controls (DAW Port · Note On · Kanal 1)

| Hardware-Label | Typ     | Data1 | Funktion            | FL API / Logik                                     | Status |
|:---            |:---     |:---   |:---                 |:---                                                |:---    |
| Save           | Note On | 80    | ToggleBrowserCR     | `ui.showWindow` toggle (Channel Rack / Browser / Mixer) | ⬜ |
| In             | Note On | 87    | TogglePadMode       | Interner State-Toggle (FPC ↔ Chromatic); Long Press: Velocity | ⬜ |
| Out            | Note On | 88    | ToggleOverdub       | `transport.globalTransport(FPT_Overdub)`           | ⬜     |
| Metro          | Note On | 89    | MetronomeToggle     | `transport.globalTransport(FPT_Metronome)`         | ⬜     |
| Undo           | Note On | 81    | UndoOrCut           | Short: `general.undo` / Long: `ui.cut`             | ⬜     |

---

## 4. Navigation (DAW Port)

| Hardware-Label   | Typ     | Data1 | Funktion            | FL API / Logik                               | Status |
|:---              |:---     |:---   |:---                 |:---                                          |:---    |
| Bank Left (<)    | Note On | 98    | previousPattern     | Kontextabhängig: Pattern / Preset / Browser  | ⬜     |
| Bank Right (>)   | Note On | 99    | nextPattern         | Kontextabhängig: Pattern / Preset / Browser  | ⬜     |
| Jog Wheel Drehen | CC      | 60    | TrackSelectMainKnob | `ui.jog` / kontextabhängig                   | ⬜     |
| Jog Wheel Klick  | Note On | 84    | SwitchWindow        | `ui.nextWindow` / kontextabhängig            | ⬜     |

---

## 5. Mixer — Fader (DAW Port · Pitch Bend)

Fader senden Pitch Bend auf separaten MIDI-Kanälen. Touch-Sensor sendet zusätzlich Note On.

| Hardware-Label    | Typ        | Kanal      | Touch Note | Funktion            | FL API / Logik            | Status |
|:---               |:---        |:---        |:---        |:---                 |:---                       |:---    |
| Fader 1           | Pitch Bend | 1 (0xE0)  | 104        | Track 1 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 2           | Pitch Bend | 2 (0xE1)  | 105        | Track 2 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 3           | Pitch Bend | 3 (0xE2)  | 106        | Track 3 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 4           | Pitch Bend | 4 (0xE3)  | 107        | Track 4 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 5           | Pitch Bend | 5 (0xE4)  | 108        | Track 5 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 6           | Pitch Bend | 6 (0xE5)  | 109        | Track 6 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 7           | Pitch Bend | 7 (0xE6)  | 110        | Track 7 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 8           | Pitch Bend | 8 (0xE7)  | 111        | Track 8 Volume      | `mixer.setTrackVolume`    | ⬜     |
| Fader 9 (Master)  | Pitch Bend | 9 (0xE8)  | 112        | Master Volume       | `mixer.setTrackVolume(0)` | ⬜     |

---

## 6. Mixer — Encoder (DAW Port · CC · Relativ: Rechts=1, Links=65)

| Hardware-Label | Typ | Data1 | Funktion         | FL API / Logik         | Status |
|:---            |:--- |:---   |:---              |:---                    |:---    |
| Encoder 1      | CC  | 16    | Track 1 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 2      | CC  | 17    | Track 2 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 3      | CC  | 18    | Track 3 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 4      | CC  | 19    | Track 4 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 5      | CC  | 20    | Track 5 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 6      | CC  | 21    | Track 6 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 7      | CC  | 22    | Track 7 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 8      | CC  | 23    | Track 8 Pan      | `mixer.setTrackPan`    | ⬜     |
| Encoder 9      | CC  | 24    | Master Pan       | `mixer.setTrackPan(0)` | ⬜     |

---

## 7. Mixer — Track Buttons (DAW Port · Note On)

| Hardware-Label | Typ     | Data1 | Funktion        | FL API / Logik            | Status |
|:---            |:---     |:---   |:---             |:---                       |:---    |
| Button 1       | Note On | 24    | Select Track 1  | `mixer.setTrackNumber`    | ⬜     |
| Button 2       | Note On | 25    | Select Track 2  | `mixer.setTrackNumber`    | ⬜     |
| Button 3       | Note On | 26    | Select Track 3  | `mixer.setTrackNumber`    | ⬜     |
| Button 4       | Note On | 27    | Select Track 4  | `mixer.setTrackNumber`    | ⬜     |
| Button 5       | Note On | 28    | Select Track 5  | `mixer.setTrackNumber`    | ⬜     |
| Button 6       | Note On | 29    | Select Track 6  | `mixer.setTrackNumber`    | ⬜     |
| Button 7       | Note On | 30    | Select Track 7  | `mixer.setTrackNumber`    | ⬜     |
| Button 8       | Note On | 31    | Select Track 8  | `mixer.setTrackNumber`    | ⬜     |
| Button 9       | Note On | 32    | Select Track 9  | `mixer.setTrackNumber`    | ⬜     |

---

## 8. Mixer — Bank Buttons (DAW Port · Note On)

| Hardware-Label  | Typ     | Data1 | Funktion      | Logik               | Status |
|:---             |:---     |:---   |:---           |:---                 |:---    |
| Part 2 / Prev   | Note On | 48    | Bank Previous | `bank_offset -= 8`  | ⬜     |
| Part 1 / Next   | Note On | 49    | Bank Next     | `bank_offset += 8`  | ⬜     |

---

## 9. Pads (Keys Port · Kanal 10 · Note On + Poly Aftertouch)

| Hardware-Label | Typ     | Data1 Bereich | Funktion                     | Status |
|:---            |:---     |:---           |:---                          |:---    |
| Pad 1–16       | Note On | 36–51         | FPC/Drum-Modus: FPC-Layout   | ⬜     |
| Pad 1–16       | Note On | 36–51         | Chromatic-Modus: ab C3 (48)  | ⬜     |
| Pad 1–16       | Note On | 36–51         | Sequencer-Modus: Step-Grid   | ⬜     |

---

## 10. Performance — Keys Port (Kanal 1)

| Hardware-Label   | Typ        | Data1 | Funktion           | Status |
|:---              |:---        |:---   |:---                |:---    |
| Pitch Bend Rad   | Pitch Bend | —     | Standard Pitch Bend | ⬜    |
| Mod Wheel        | CC         | 1     | Standard Modulation | ⬜    |

---

## 11. Pedale (Keys Port · Kanal 1)

| Hardware-Label    | Typ | Data1 (CC) | Funktion           | Status |
|:---               |:--- |:---        |:---                |:---    |
| Sustain Pedal     | CC  | 64         | Standard Sustain   | ⬜     |
| Expression Pedal  | CC  | 11         | Expression         | ⬜     |
| Aux 1 Pedal       | CC  | 12         | (TBD)              | ⬜     |
| Aux 2 Pedal       | CC  | 13         | (TBD)              | ⬜     |
| Aux 3 Pedal       | CC  | 14         | (TBD)              | ⬜     |

---

## Modes & States

| Modus           | Auslöser                          | Beschreibung                                |
|:---             |:---                               |:---                                         |
| Mixer Mode      | Auto (Mixer fokussiert)           | Fader/Encoder → Mixer Track Vol/Pan         |
| Channel Mode    | Auto (Channel Rack fokussiert)    | Fader/Encoder → Channel Rack Vol/Pan        |
| Free Mode       | Long Press Save (Note 80)         | Fader/Encoder → `event.handled = False` (Link to controller) |
| Pad FPC/Drum    | TogglePadMode (Note 87)           | Pads → FPC Standard-Layout                  |
| Pad Chromatic   | TogglePadMode (Note 87)           | Pads → chromatisch ab C3                    |
| Sequencer Mode  | (TBD — aktuell nicht belegt)      | Pads → Step-Sequencer Grid                  |

### Track-Button-Modi

| Aktion       | Auslöser                  | FL API                     |
|:---          |:---                       |:---                        |
| Select Track | Short Press (Track Btn)   | `mixer.setTrackNumber`     |
| Solo Track   | Long Press (Track Btn)    | `mixer.soloTrack`          |
| Mute Track   | Double-Click (Track Btn)  | `mixer.muteTrack`          |

---

*Quellen: [`hardware_map.md`](hardware_map.md) · [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md) · [`_archive/CONTROLLER_OVERVIEW.md`](_archive/CONTROLLER_OVERVIEW.md) (historisch)*
