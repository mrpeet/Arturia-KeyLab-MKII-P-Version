# KeyLab mkII — Implementation Map

> **Status:** Work in Progress — aligned with modular P-version (`keylab_*` modules).
>
> Dieses Dokument verbindet die **physischen MIDI-Daten** (Quelle: `hardware_map.md`) mit den
> **gewünschten FL Studio Funktionen** (Quelle: eigene Planung + `BRAINSTORM.md`).
>
> **Hinweis:** `device_KeyLabmkII_Forward.py` läuft auf dem **Keys Port** (Pads + optional V-Collection).
> Das Hauptscript läuft auf **MIDIIN2 / DAW Port**. Beide müssen in FL MIDI Settings zugewiesen sein.
>
> **Legende Status:** offen · in Arbeit · fertig · verworfen

---

## 1. Transport (DAW Port · Note On · Kanal 1)

| Hardware-Label | Typ     | Data1 | Funktion             | FL API / Logik                                    | Status |
|:---            |:---     |:---   |:---                  |:---                                               |:---    |
| Rewind (<<)    | Note On | 91    | Continuous rewind    | `transport.continuousMove(-1, SS_Start/Stop)`      | fertig |
| Fast Fwd (>>)  | Note On | 92    | Continuous FF        | `transport.continuousMove(1, SS_Start/Stop)`       | fertig |
| Stop           | Note On | 93    | Stop                 | `transport.stop`                                  | fertig |
| Play           | Note On | 94    | Start                | `transport.start`                                 | fertig |
| Record         | Note On | 95    | Record               | `transport.record`                                | fertig |
| Loop           | Note On | 86    | Loop record toggle   | `transport.globalTransport(FPT_LoopRecord)`       | fertig |

---

## 2. DAW Commands — Track Controls (DAW Port · Note On · Kanal 1)

| Hardware-Label | Typ     | Data1 | Funktion        | FL API / Logik                          | Status |
|:---            |:---     |:---   |:---             |:---                                     |:---    |
| Record (Reihe 1) | Note On | 0  | SnapToggle      | `ui.snapOnOff`                          | fertig |
| Solo           | Note On | 8     | NewPattern      | `patterns.findFirstNextEmptyPat`        | fertig |
| Mute           | Note On | 16    | FocusMixer      | `ui.showWindow(widMixer)`               | fertig |
| Read           | Note On | 74    | TapTempo        | `transport.globalTransport(FPT_TapTempo)` | fertig |
| Write          | Note On | 75    | Undo/Cut        | Short=`general.undoUp` Long=`ui.cut`      | fertig |

---

## 3. DAW Commands — Global Controls (DAW Port · Note On · Kanal 1)

| Hardware-Label | Typ     | Data1 | Funktion            | FL API / Logik                                     | Status |
|:---            |:---     |:---   |:---                 |:---                                                |:---    |
| Save           | Note On | 80    | ToggleBrowserCR     | `ui.showWindow` toggle (Browser/CR)                 | fertig |
| In             | Note On | 87    | TogglePadMode       | Short: Drum Map ↔ Chromatic; Long: Pad Velocity On/Off | fertig |
| Out            | Note On | 88    | ToggleOverdub       | `transport.globalTransport(FPT_Overdub)`           | fertig |
| Metro          | Note On | 89    | MetronomeToggle     | `transport.globalTransport(FPT_Metronome)`         | fertig |
| Undo           | Note On | 81    | Redo                | `general.undoDown`                                 | fertig |
| Live/Bank+Part2 | Note On | 46 | Pad bank prev       | `pad_bank_offset` (beide Pad-Modi)                   | fertig |
| Live/Bank+Part1 | Note On | 47 | Pad bank next       | `pad_bank_offset` (beide Pad-Modi)                   | fertig |

---

## 4. Navigation (DAW Port)

| Hardware-Label   | Typ     | Data1 | Funktion            | FL API / Logik                               | Status |
|:---              |:---     |:---   |:---                 |:---                                          |:---    |
| Bank Left (<)    | Note On | 98    | Context bank/pattern | Plugin preset / Browser tab / Pattern        | fertig |
| Bank Right (>)   | Note On | 99    | Context bank/pattern | Plugin preset / Browser tab / Pattern        | fertig |
| Jog Wheel Drehen | CC      | 60    | Context navigation | Browser / Mixer track / Channel               | fertig |
| Jog Wheel Klick  | Note On | 84    | Context action       | Open plugin / Arm track / Browser enter      | fertig |

---

## 5. Mixer — Fader (DAW Port · Pitch Bend)

Fader senden Pitch Bend auf Kanälen 0–8. Touch-Sensor: Notes 104–112.

| Hardware-Label    | Typ        | Kanal      | Touch Note | Funktion            | FL API / Logik            | Status |
|:---               |:---        |:---        |:---        |:---                 |:---                       |:---    |
| Fader 1–8         | Pitch Bend | 0–7       | 104–111    | Vol (Mixer/CR)      | `mixer` / `channels` + bank | fertig |
| Fader 9 (Master)  | Pitch Bend | 8         | 112        | Master Volume       | `mixer.setTrackVolume(0)` | fertig |

Mixer vs Channel Rack: auto via `ui.getFocused(widMixer)`. Soft pickup + jitter filter in `keylab_mixer.py`.

---

## 6. Mixer — Encoder (DAW Port · CC · Relativ)

| Hardware-Label | Typ | Data1 | Funktion         | FL API / Logik         | Status |
|:---            |:--- |:---   |:---              |:---                    |:---    |
| Encoder 1–8    | CC  | 16–23 | Pan (relativ)    | `mixer` / `channels`   | fertig |
| Encoder 9      | CC  | 24    | Master Pan       | `mixer.setTrackPan(0)` | fertig |

Plugin-Mode: Encoder 1–8 → `keylab_plugin.py`. Free Mode: virtuelle Absolute-CCs.

---

## 7. Mixer — Track Buttons (DAW Port · Note On)

| Hardware-Label | Typ     | Data1 | Funktion        | FL API / Logik            | Status |
|:---            |:---     |:---   |:---             |:---                       |:---    |
| Button 1–8     | Note On | 24–31 | Short=Mute Long=Solo/Pan reset | kontextabhängig | fertig |
| Button 9       | Note On | 32    | Wie 1–8 (Master-Slot)        | kontextabhängig | fertig |

*Hinweis:* Verhalten weicht von alter Doku ab (Select per Short Press war geplant, Code: Short=Mute).

---

## 8. Mixer — Bank Buttons (DAW Port · Note On)

| Hardware-Label  | Typ     | Data1 | Funktion      | Logik               | Status |
|:---             |:---     |:---   |:---           |:---                 |:---    |
| Part 2 / Prev   | Note On | 48    | Bank -1 / Free Mode toggle (long) | `bank_offset`, `free_mode` | fertig |
| Part 1 / Next   | Note On | 49    | Bank +1       | `bank_offset += 1`  | fertig |

---

## 9. Pads (Keys Port · Kanal 10 raw → transponiert in Forward-Script)

| Hardware-Label | Typ     | Native Notes | Funktion                     | Status |
|:---            |:---     |:---          |:---                          |:---    |
| Pad 1–16       | Note On | 36–51 phys.  | **Chromatic:** C3+ Halbtöne, **Kanal 1** | in Arbeit |
| Pad 1–16       | Note On | 36–51 phys.  | **Drum Map:** GM Drum-Map, **Kanal 10**   | fertig |
| Pad bank       | DAW 46/47 | —         | ±1 Bank (×16 Halbtöne)       | fertig |

**Pad-Mode-Bug:** LCD-Toggle ohne hörbarer Wechsel — siehe `ROADMAP.md` Phase 10.1.

---

## 10. Performance — Keys Port (Kanal 1)

| Hardware-Label   | Typ        | Data1 | Funktion           | Status |
|:---              |:---        |:---   |:---                |:---    |
| Pitch Bend Rad   | Pitch Bend | 80    | Standard (passthrough) | offen |
| Mod Wheel        | CC         | 1     | Standard (passthrough) | offen |

---

## 11. Pedale (Keys Port · Kanal 1)

| Hardware-Label    | Typ | Data1 (CC) | Funktion           | Status |
|:---               |:--- |:---        |:---                |:---    |
| Sustain Pedal     | CC  | 64         | Standard Sustain   | offen |
| Expression Pedal  | CC  | 11         | Expression         | offen |
| Aux 1–3           | CC  | 12–14      | (TBD)              | offen |

---

## Modes & States

| Modus           | Auslöser                          | Beschreibung                                |
|:---             |:---                               |:---                                         |
| Mixer Mode      | Auto (`widMixer` fokussiert)      | Fader/Encoder → Mixer-Tracks + `bank_offset` |
| Channel Mode    | Auto (Channel Rack fokussiert)    | Fader/Encoder → Channel-Vol/Pan             |
| Plugin Mode     | Auto (`widPlugin` fokussiert)     | Encoder 1–8 → `plugin_database`             |
| Free Mode       | Long Press Bank Prev (≥0,75 s)    | Fader/Encoder 1–8 passthrough               |
| Pad Chromatic   | IN (Note 87), Default             | Halbtöne ab C3, Keys Port → Ch **1**          |
| Pad Drum Map    | IN short (Note 87)                | GM Drum-Map, Keys Port → Ch **10**            |
| Pad Velocity    | IN long (≥0,75 s, Note 87)         | Off = feste Velocity 95 (75%) auf Pad Note-On |
| Sequencer Mode  | (TBD)                             | Nicht implementiert                         |

---

*Quellen: [`hardware_map.md`](hardware_map.md) · [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md) · [`codemaps/CODEMAP_INDEX.md`](codemaps/CODEMAP_INDEX.md)*
