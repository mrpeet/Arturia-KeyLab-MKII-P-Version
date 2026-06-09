# KeyLab mkII — Implementation Map

> **Status:** Work in Progress — aligned with the modular P-version (`keylab_*` modules).
>
> This document connects **physical MIDI data** (source: `hardware_map.md`) with
> **desired FL Studio functions** (source: own planning + `BRAINSTORM.md`).
>
> **Note:** `device_KeyLabmkII_Forward.py` runs on the **Keys Port** (pads + optional V-Collection).
> The main script runs on **MIDIIN2 / DAW Port**. Both must be assigned in FL MIDI Settings.
>
> **LED / LCD / Timing:** [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md) · Implementation `keylab_feedback.py`
>
> **Status legend:** open · in progress · done · dropped

---

## 1. Transport (DAW Port · Note On · Channel 1)

| Hardware Label | Type    | Data1 | Function             | FL API / Logic                                    | Status |
|:---            |:---     |:---   |:---                  |:---                                               |:---    |
| Rewind (<<)    | Note On | 91    | Continuous rewind    | `transport.continuousMove(-1, SS_Start/Stop)`      | done |
| Fast Fwd (>>)  | Note On | 92    | Continuous FF        | `transport.continuousMove(1, SS_Start/Stop)`       | done |
| Stop           | Note On | 93    | Stop                 | `transport.stop`                                  | done |
| Play           | Note On | 94    | Start                | `transport.start`                                 | done |
| Record         | Note On | 95    | Record               | `transport.record`                                | done |
| Loop           | Note On | 86    | Loop record toggle   | `transport.globalTransport(FPT_LoopRecord)`       | done |

---

## 2. DAW Commands — Track Controls (DAW Port · Note On · Channel 1)

| Hardware Label   | Type    | Data1 | Function        | FL API / Logic                          | Status |
|:---              |:---     |:---   |:---             |:---                                     |:---    |
| Record (row 1)   | Note On | 0     | Snap Toggle     | `ui.snapOnOff`                          | done |
| Solo             | Note On | 8     | New Pattern     | `patterns.findFirstNextEmptyPat`        | done |
| Mute             | Note On | 16    | Open Piano Roll | `ui.showWindow(widPianoRoll)` + `channels.showEditor` | done |
| Read             | Note On | 74    | Tap Tempo       | `transport.globalTransport(FPT_TapTempo)` | done |
| Write            | Note On | 75    | Redo / Cut      | Short=`general.undoDown` Long=`ui.cut`    | done |

---

## 3. DAW Commands — Global Controls (DAW Port · Note On · Channel 1)

| Hardware Label     | Type    | Data1 | Function            | FL API / Logic                                     | Status |
|:---                |:---     |:---   |:---                 |:---                                                |:---    |
| Save               | Note On | 80    | Cycle Browser/CR/Mixer | `ui.showWindow` 3-way (Browser→CR→Mixer) | done |
| In                 | Note On | 87    | Toggle Pad Mode     | Short: Drum Map ↔ Chromatic; Long: Pad Velocity On/Off | done |
| Out                | Note On | 88    | Toggle Overdub      | `transport.globalTransport(FPT_Overdub)`           | done |
| Metro              | Note On | 89    | Metronome Toggle    | `transport.globalTransport(FPT_Metronome)`         | done |
| Undo               | Note On | 81    | Undo                | `general.undoUp`                                   | done |
| Live/Bank+Part2    | Note On | 46    | Pad bank prev       | `pad_bank_offset` (both pad modes)                 | done |
| Live/Bank+Part1    | Note On | 47    | Pad bank next       | `pad_bank_offset` (both pad modes)                 | done |

---

## 4. Navigation (DAW Port)

| Hardware Label   | Type    | Data1 | Function            | FL API / Logic                               | Status |
|:---              |:---     |:---   |:---                 |:---                                          |:---    |
| Bank Left (<)    | Note On | 98    | Context bank/pattern | Plugin preset / Browser tab / Pattern        | done |
| Bank Right (>)   | Note On | 99    | Context bank/pattern | Plugin preset / Browser tab / Pattern        | done |
| Jog Wheel rotate | CC      | 60    | Context navigation  | Browser / Mixer track / Channel              | done |
| Jog Wheel click  | Note On | 84    | Context action      | Open plugin / Arm track / Browser enter      | done |

---

## 5. Mixer — Faders (DAW Port · Pitch Bend)

Faders send Pitch Bend on channels 0–8. Touch sensor: Notes 104–112.

| Hardware Label    | Type       | Channel    | Touch Note | Function            | FL API / Logic            | Status |
|:---               |:---        |:---        |:---        |:---                 |:---                       |:---    |
| Fader 1–8         | Pitch Bend | 0–7       | 104–111    | Vol (Mixer/CR) + LCD dB | `mixer.getTrackVolume(t,1)` + bank | done |
| Fader 9 (Master)  | Pitch Bend | 8         | 112        | Master Volume + LCD dB | `mixer.setTrackVolume(0)` | done |

Mixer vs Channel Rack: auto via `ui.getFocused(widMixer)`. Soft pickup + jitter filter in `keylab_mixer.py`.

---

## 6. Mixer — Encoders (DAW Port · CC · Relative)

| Hardware Label | Type | Data1 | Function         | FL API / Logic         | Status |
|:---            |:---  |:---   |:---              |:---                    |:---    |
| Encoder 1–8    | CC   | 16–23 | Pan (relative)   | `mixer` / `channels`   | done |
| Encoder 9      | CC   | 24    | Master Pan       | `mixer.setTrackPan(0)` | done |

Plugin mode: Encoder 1–8 → `keylab_plugin.py`. Free mode: virtual absolute CCs.

---

## 7. Mixer — Track Buttons (DAW Port · Note On)

| Hardware Label | Type    | Data1 | Function        | FL API / Logic            | Status |
|:---            |:---     |:---   |:---             |:---                       |:---    |
| Button 1–8     | Note On | 24–31 | Short=Mute Long=Solo/Pan reset | context-dependent | done |
| Button 9       | Note On | 32    | Like 1–8 (master slot)        | context-dependent | done |

*Note:* Behaviour differs from old docs (Select on short press was planned, code: Short=Mute).

---

## 8. Mixer — Bank Buttons (DAW Port · Note On)

| Hardware Label  | Type    | Data1 | Function      | Logic               | Status |
|:---             |:---     |:---   |:---           |:---                 |:---    |
| Part 2 / Prev   | Note On | 48    | Bank -1 / Free Mode toggle (long) | `bank_offset`, `_max_bank_offset()` | done |
| Part 1 / Next   | Note On | 49    | Bank +1 (up to last insert) | `bank_offset`, bank hint tracks N–M | done |

---

## 9. Pads (Keys Port · Channel 10 raw → transposed in Forward script)

Hardware pads send on MIDI channel 10 (0-indexed: `Pad.PAD_CHANNEL = 9`), notes 36–51 physical.
The Forward script (`device_KeyLabmkII_Forward.py`) intercepts these events and transposes them.

| Hardware Label | Type    | Native Notes | Function                     | Status |
|:---            |:---     |:---          |:---                          |:---    |
| Pad 1–16       | Note On | 36–51 phys.  | **Chromatic:** base = MIDI 20, Pad idx + bank×16, **Channel 1** | done |
| Pad 1–16       | Note On | 36–51 phys.  | **Drum Map:** base = native note + (bank−1)×16, **Channel 10** | done |
| Pad bank       | DAW 46/47 | —          | ±1 Bank (×16 semitones), clamped 0–7 | done |
| Pad LEDs       | SysEx (Keys) | —       | Chromatic = white, Drum Map = purple | done |

### Pad banking defaults

| Mode | Default bank offset | Pad 1 output note | Note name |
|:-----|:-------------------|:-----------------|:----------|
| Chromatic | **4** | MIDI 20 + 0 + 4×16 = **84** | C5 (≈ middle C+1 oct.) |
| Drum Map  | **1** | native 36 + (1−1)×16 = **36** | C1 / GM Bass Drum 1 |

Bank offsets are per-mode and restored when toggling back.

---

## 10. Performance — Keys Port (Channel 1)

| Hardware Label   | Type       | Data1 | Function           | Status |
|:---              |:---        |:---   |:---                |:---    |
| Pitch Bend wheel | Pitch Bend | 80    | Standard (passthrough) | open |
| Mod Wheel        | CC         | 1     | Standard (passthrough) | open |

---

## 11. Pedals (Keys Port · Channel 1)

| Hardware Label    | Type | Data1 (CC) | Function           | Status |
|:---               |:---  |:---        |:---                |:---    |
| Sustain Pedal     | CC   | 64         | Standard sustain   | open |
| Expression Pedal  | CC   | 11         | Expression         | open |
| Aux 1–3           | CC   | 12–14      | (TBD)              | open |

---

## Modes & States

| Mode           | Trigger                          | Description                                |
|:---            |:---                              |:---                                        |
| Mixer Mode     | Auto (`widMixer` focused)        | Fader/Encoder → Mixer tracks + `bank_offset` |
| Channel Mode   | Auto (Channel Rack focused)      | Fader/Encoder → Channel Vol/Pan            |
| Plugin Mode    | Auto (`widPlugin` focused)       | Encoder 1–8 → `plugin_database`            |
| Free Mode      | Long Press Bank Prev (≥0.75 s)   | Fader/Encoder 1–8 passthrough              |
| Pad Chromatic  | IN (Note 87), **Default**        | Pad 1 = C5 (bank 4), +semitones, Keys → Ch **1** |
| Pad Drum Map   | IN short (Note 87)               | GM Drum map, Pad 1 = MIDI 36 (bank 1), Keys → Ch **10** |
| Pad Velocity   | IN long (≥0.75 s, Note 87)       | Off = fixed velocity 95 (75%) on Pad Note-On |
| Sequencer Mode | (TBD)                            | → Phase 13 (optional)                     |

---

## 12. LED Feedback (DAW Port · SysEx)

Specification: [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md). Code: `keylab_feedback.py`.

| Area | Rule | Status |
|:-----|:-----|:-------|
| Transport | Play/Stop/Record/Loop + beat blink | done |
| DAW Commands | Toggle 30%/100%; Save/IN/Undo/Tap always 100%; Overdub On=100%/Off=3% | done |
| Navigation | Bank L/R, jog click always 100% | done |
| Part Prev/Next (48/49) | Always 100% | done |
| Track buttons 24–31 | Muted off; 20% / 100% FL colour | done |
| Pads | White / purple per `pad_mode` | done |
| Sync | `OnInit`/`OnRefresh` → `update_all_feedback`; `OnIdle` throttled | done |

---

*Sources: [`hardware_map.md`](hardware_map.md) · [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md) · [`codemaps/CODEMAP_INDEX.md`](codemaps/CODEMAP_INDEX.md) · [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md)*
