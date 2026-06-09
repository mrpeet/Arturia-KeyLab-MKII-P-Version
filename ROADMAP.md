# KeyLab mkII P Version — Roadmap

> Overview of all development phases. Each phase is self-contained and testable.
>
> **Controller rules (LED, LCD, Long-Press):** [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md)
>
> **Principles:**
> - No magic numbers — all MIDI values via `keylab_config.py`
> - State only via `keylab_state.py` — no module-level mutable state
> - Each phase is marked ✅ in `IMPLEMENTATION_MAP.md` when done
> - Archive code (`_archive/`) is reference only — never imported

---

## Phase 1 — Inventory & Analysis ✅

**Goal:** Fully understand, document, and identify bugs and dead code in the old script.

| Result | File |
|:-------|:-----|
| Architecture analysis (import graph, coupling, dead code, bugs) | `architecture.md` |
| Hardware MIDI map (all ports, channels, Note/CC/PB) | `hardware_map.md` |
| Old script archived (14 files) | `_archive/` |

---

## Phase 2 — Documentation ✅

**Goal:** Create reference documents for the new implementation.

| Result | File |
|:-------|:-----|
| FL Studio MIDI Scripting API — local reference | `FL_Studio_API_Reference.md` |
| Implementation plan: Hardware ↔ Functions | `IMPLEMENTATION_MAP.md` |
| Feature ideas & design decisions | `BRAINSTORM.md` |
| Project README with setup, credits, file structure | `README.md` |
| AI-Agent crosscheck rules | `.cursorrules` |

---

## Phase 3 — Skeleton & Infrastructure ✅

**Goal:** Modular foundation that loads in FL Studio and drives the LCD.

| Result | File | Origin |
|:-------|:-----|:-------|
| Hardware constants (Transport, Encoder, Fader, Pads, Pedals) | `keylab_config.py` | New |
| Central state (Modes, Banking, Fader-Pickup, Plugin-State) | `keylab_state.py` | New |
| Event dispatcher (transform → lookup → callback) | `keylab_dispatch.py` | Ported (Ray Juang, MIT) |
| LCD SysEx builder with scrolling | `keylab_display.py` | Ported (Ray Juang, MIT) |
| Timed-page manager | `keylab_pages.py` | Ported (Ray Juang, MIT) |
| FL callbacks entry point (DAW port) | `device_KeyLabmkII.py` | New (Skeleton) |
| V-Collection CC forwarding (Keys port) | `device_KeyLabmkII_Forward.py` | Done |

**Testable:** Script loads in FL Studio, LCD shows channel + pattern.

---

## Phase 4 — Plugin Database ✅

**Goal:** 300+ plugin parameter mappings for encoder control.

| Result | File |
|:-------|:-----|
| 309 plugins with 8-macro-slot schema, lookup API | `plugin_database.py` |
| Plugin encoder handler (logic done, not yet wired) | `keylab_plugin.py` |
| User-defined mappings (data source for merge) | `user_defined_plugin_mappings.py` |

**Sources:** CPS Community Spreadsheet + user_defined_plugin_mappings.py (FLKey Community)

---

## Phase 5 — Transport ✅

**Goal:** Play/Stop/Record/Loop/Rewind/FastForward working. Build dispatcher chain.

| Task | File | Status |
|:-----|:-----|:-------|
| Transport handler (6 buttons → FL API) | `keylab_transport.py` | ✅ |
| Dispatcher chain in OnMidiMsg | `device_KeyLabmkII.py` | ✅ |
| Transport LED feedback (Play/Record/Loop) | `keylab_feedback.py` | ✅ |
| Beat indicator LED (OnUpdateBeatIndicator) | `keylab_feedback.py` | ✅ |

---

## Phase 6 — DAW Commands ✅

**Goal:** Utility buttons for workflow acceleration.

| Task | File | Status |
|:-----|:-----|:-------|
| Snap toggle, NewPattern, FocusMixer | `keylab_daw_commands.py` | ✅ |
| Undo (short press) / Cut (long press) | `keylab_daw_commands.py` | ✅ |
| Metronome toggle, Overdub toggle | `keylab_daw_commands.py` | ✅ |
| Tap Tempo, Redo | `keylab_daw_commands.py` | ✅ |

**Testable:** All 10 DAW buttons have defined actions, LCD shows feedback.

---

## Phase 7 — Navigation ✅

**Goal:** Jog Wheel and Bank buttons for context-sensitive navigation.

| Task | File | Status |
|:-----|:-----|:-------|
| Jog Wheel rotate → context-sensitive | `keylab_navigation.py` | ✅ |
| Jog Wheel click → Plugin/Folder/Arm | `keylab_navigation.py` | ✅ |
| Bank Left/Right → Pattern/Preset/Browser | `keylab_navigation.py` | ✅ |
| LCD feedback navigation | `keylab_navigation.py` | ✅ |

**Testable:** Jog switches tracks/patterns/browser items, bank buttons switch patterns/presets/browser tabs.

---

## Phase 8 — Mixer Faders ✅

**Goal:** 9 faders (8 + master) control mixer volume with jitter filter and soft pickup.

| Task | File | Status |
|:-----|:-----|:-------|
| Pitch Bend → mixer.setTrackVolume (+ banking) | `keylab_mixer.py` | ✅ |
| Jitter filter (FADER_JITTER_THRESHOLD) | `keylab_mixer.py` | ✅ |
| Soft Pickup (fader must cross software value) | `keylab_mixer.py` | ✅ |
| Touch-sensor events (fader touch/release) | `keylab_mixer.py` | ✅ |

**Testable:** Faders control mixer volume, no jumps on bank change.

---

## Phase 9 — Mixer Encoder + Track Buttons ✅

**Goal:** Encoders control pan, track buttons select/solo/mute tracks.

| Task | File | Status |
|:-----|:-----|:-------|
| Relative encoder → mixer.setTrackPan (+ banking) | `keylab_mixer.py` | ✅ |
| Track buttons: Short=ResetPan, Long=ToggleMute | `keylab_mixer.py` | ✅ |
| Bank Prev/Next → bank_offset ±1 | `keylab_mixer.py` | ✅ |

**Testable:** Encoder controls pan, buttons select tracks, banking works.

---

## Phase 10 — Plugin Control ✅

**Goal:** Encoders 1–8 control plugin parameters when a plugin is focused.

| Task | File | Status |
|:-----|:-----|:-------|
| Plugin mode auto-detect (OnIdle → widPlugin) | `device_KeyLabmkII.py` | ✅ |
| Encoder → plugin parameter (from plugin_database.py) | `keylab_plugin.py` | ✅ |
| Jog Wheel → preset navigation (plugins with special) | `keylab_navigation.py` | ✅ |
| LCD: parameter name + value display | `keylab_plugin.py` | ✅ |
| Fallback: unknown plugins → Free Mode / Generic | `keylab_plugin.py` | ✅ |

**Testable:** Open plugin → encoders control the right parameters, LCD shows plugin name.

---

## Phase 10.1 — Foundation Sync / Stabilisation ✅

**Goal:** Bind docs/codemaps to the active `keylab_*` architecture, fix base bugs, get Pad Mode toggle running.

| Task | File | Status |
|:-----|:-----|:-------|
| Roadmap + `IMPLEMENTATION_MAP.md` up to code state | `ROADMAP.md`, `IMPLEMENTATION_MAP.md` | ✅ |
| Codemaps + `FL_Studio_API_Reference.md` supplemented | `codemaps/*`, `FL_Studio_API_Reference.md` | ✅ |
| Pad mode IN ↔ Forward script | `keylab_shared_state.py`, `device_KeyLabmkII_Forward.py` | ✅ |
| Long press 0.75 s + immediate LCD | `keylab_long_press.py` | ✅ |
| Mixer bank / fader dB LCD | `keylab_mixer.py` | ✅ |
| Free mode, plugin focus, jog | various | ✅ |

Pad mode toggle (Chromatic channel 1 / Drum Map channel 10) is solved — see `CONTROLLER_RULES.md`.

---

## Phase 11 — Pads ✅

**Goal:** Pad mode, velocity, cross-port state.

| Task | File | Status |
|:-----|:-----|:-------|
| Pad mode Chromatic / Drum Map (IN short) | `keylab_daw_commands.py`, Forward | ✅ |
| Velocity toggle (IN long, `Pad Velo: On/Off`) | `keylab_daw_commands.py`, Forward | ✅ |
| Pad banking: 8 banks × 16 semitones, separate defaults | `keylab_shared_state.py`, Forward | ✅ |
| Chromatic default: Bank 4 offset → Pad 1 = C5 (MIDI 80) | `keylab_shared_state.py` | ✅ |
| Drum Map default: Bank 1 offset → Pad 1 = MIDI 36 (C1) | `keylab_shared_state.py`, Forward | ✅ |
| Pad LED colours (white / purple) | `keylab_feedback.py`, `keylab_pad_leds.py` | ✅ |
| Step sequencer on pads | — | → Phase 13 (optional) |

**Pad bank behaviour:**

| Mode | Banks | Bank range | Default bank | Pad 1 base note |
|:-----|:------|:-----------|:------------|:----------------|
| Chromatic | 0–7 (8 banks) | MIDI 20–127 | **Bank 4** | C5 (MIDI 80) |
| Drum Map | 0–7 (8 banks) | MIDI 20–127 | **Bank 1** | C1 / GM 36 (MIDI 36) |

Bank offset is stored per-mode and restored when toggling back.

---

## Phase 12 — LED Feedback ⬜

**Goal:** Coherent LED logic and bug fixes — specification in [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md).

| Area | Rule | Status |
|:-----|:-----|:-------|
| **Pads** | IN button toggles mode instantly, colours not overwritten by blue | ⬜ |
| **DAW Commands** | Init state correct, Save button cycle (CR → Mixer → Browser) | ⬜ |
| **Transports** | Rewind/FastForward at 100% | ⬜ |
| **Navigation** | Nav LEDs no longer glitch on jog wheel turn | ⬜ |
| **Track Buttons** | Brightness raised (visible), conflict with Part Prev/Next resolved | ⬜ |
| **Mixer Part 48/49** | Prev/Next on correct IDs | ⬜ |

---

## Phase 13 — Polish & Edge Cases ⬜

**Goal:** Fine-tuning, performance, robustness.

| Task | File |
|:-----|:-----|
| Step sequencer on pads (optional) | TBD |
| All LEDs correctly synchronised (fine-tuning) | `keylab_feedback.py` |
| Display fine-tuning (truncation, special characters) | `keylab_display.py` |
| Error handling for all FL API calls | All handlers |
| Channel Rack mode (auto-switch when CR focused) | `keylab_mixer.py` |
| Free Mode (Long Press Bank Prev → fader/encoder passthrough toggle) | `keylab_mixer.py`, `keylab_state.py` |
| Performance check (no allocations in event handlers) | All handlers |
| Finalise documentation | All .md files |

---

## File Overview (Target State)

| File | Role | Phase |
|:-----|:-----|:------|
| `device_KeyLabmkII.py` | Entry point + dispatcher chain | 3, 5 |
| `device_KeyLabmkII_Forward.py` | V-Collection CC forwarding + pad transposition | 3, 10.1, 11 |
| `keylab_config.py` | Hardware constants | 3 |
| `keylab_state.py` | Central state | 3 |
| `keylab_dispatch.py` | Event dispatcher + SysEx | 3 |
| `keylab_display.py` | LCD driver | 3 |
| `keylab_pages.py` | Page manager | 3 |
| `keylab_transport.py` | Transport handler | 5 |
| `keylab_feedback.py` | LED/pad feedback | 5, 8, 11 |
| `keylab_daw_commands.py` | DAW command buttons | 6 |
| `keylab_navigation.py` | Jog/bank/window | 7 |
| `keylab_mixer.py` | Fader/encoder/buttons/banking | 8, 9 |
| `keylab_plugin.py` | Plugin encoder control | 10 |
| `keylab_shared_state.py` | Pad mode/bank (cross-port) | 10.1 |
| `keylab_pad_leds.py` | Pad LED animations | 11 |
| `plugin_database.py` | 309 plugin mappings | 4 |

---

*Last updated: 2026-06-09 — Phase 11 pads complete including dual-mode banking*
