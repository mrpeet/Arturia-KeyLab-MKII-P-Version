# Arturia KeyLab mkII — FL Studio MIDI Script (P Version)

Custom FL Studio user MIDI script for the **Arturia KeyLab mkII** keyboard controller. Provides transport control, mixer integration (faders, encoders, track buttons), pad modes, navigation, display feedback, and more.

> **Status:** 🚧 Modular rebuild in progress — Phases 1–11 complete. Phase 12 (LED polish) and Phase 13 (edge cases) are next.

---

## Credits & License

This project is based on the work of several developers:

### Ray Juang — Original author (MIT License, 2020)
- **Base:** [github.com/rjuang/flstudio-arturia-keylab-mk2](https://github.com/rjuang/flstudio-arturia-keylab-mk2)
- **Ported to:** `keylab_dispatch.py`, `keylab_display.py`, `keylab_pages.py`
- Architecture, event dispatcher, LCD SysEx, scrolling, timed-page-manager, plugin control, encoder/slider logic
- License: MIT License — Copyright (c) 2020 Ray Juang

### Farès MEZDOUR — Adaptations (Arturia)
- **Files:** see `_archive/` — adaptations to the original script
- Plugin mapping tables (FLEX, Sytrus, Harmor etc.), LED feedback, step sequencer integration

### P Version — Modular rebuild
- Complete modular rewrite with clean architecture
- Inventory, documentation and API verification
- Own feature planning and implementation

---

## Setup

### Requirements
- **FL Studio** (with MIDI scripting support)
- **Arturia KeyLab mkII** (in DAW mode / MCU mode)

### Installation
1. Copy this entire folder to:
   ```
   [FL Studio User Data]\Settings\Hardware\Arturia KeyLab MKII P Version\
   ```
   Typical path on Windows:
   ```
   Documents\Image-Line\FL Studio\Settings\Hardware\Arturia KeyLab MKII P Version\
   ```

2. Open FL Studio → **Options → MIDI Settings**

3. Assign two MIDI inputs:

   | FL Studio Input | Hardware name | Script | Port |
   |:----------------|:--------------|:-------|:-----|
   | `MIDIIN2 (KeyLab mkII 61)` | DAW Port | **KeyLab mkII P Version (MIDIIN2 · Port 1)** | 1 |
   | `KeyLab mkII 61` | Keys Port | **KeyLab mkII Forward (KeyLab mkII 61 · Port 0)** *(optional — only for V-Collection + pad transposition)* | 0 |

---

## File Structure

### Python scripts (new — modular structure)

| File | Role | Status |
|:-----|:-----|:-------|
| `device_KeyLabmkII.py` | FL callbacks / entry point + dispatcher chain | ✅ Phases 5–10 |
| `device_KeyLabmkII_Forward.py` | Keys port: pad transposition + V-Collection CC forwarding | ✅ Phase 11 |
| `keylab_config.py` | Hardware constants (Note/CC/PB from `hardware_map.md`) | ✅ Done |
| `keylab_state.py` | Central state (modes, banking, pickup) | ✅ Done |
| `keylab_shared_state.py` | Cross-port pad state (mode, bank, velocity) — file + sys | ✅ Phase 10.1 |
| `keylab_dispatch.py` | Event dispatcher + `send_to_device` (SysEx) | ✅ Ported |
| `keylab_display.py` | LCD SysEx builder with scrolling | ✅ Ported |
| `keylab_pages.py` | Timed-page manager for the display | ✅ Ported |
| `keylab_transport.py` | Transport handler (Play/Stop/Record/Loop/RW/FF) | ✅ Phase 5 |
| `keylab_mixer.py` | Mixer handler (fader/encoder/buttons/banks) | ✅ Phases 8–9 |
| `keylab_navigation.py` | Jog / arrows / window switching | ✅ Phase 7 |
| `keylab_daw_commands.py` | DAW command buttons (Snap/Undo/Metro/Redo…) | ✅ Phase 6 |
| `keylab_feedback.py` | LED and pad feedback | ✅ Phases 5, 8, 11 |
| `keylab_pad_leds.py` | Pad LED colours and animations | ✅ Phase 11 |
| `keylab_plugin.py` | Plugin encoder control | ✅ Phase 10 |
| `plugin_database.py` | 309 plugin parameter mappings | ✅ Phase 4 |
| `user_defined_plugin_mappings.py` | User-defined plugin mappings | ✅ Phase 4 |

### Archive (reference for porting)

| Folder | Contents |
|:-------|:---------|
| `_archive/` | All 14 original `.py` files of the old script (Farès MEZDOUR + Ray Juang) |

### Documentation

| File | Contents |
|:-----|:---------|
| [`architecture.md`](architecture.md) | Module dependencies, import graph, dead code, known bugs & risks |
| [`hardware_map.md`](hardware_map.md) | Physical MIDI data for all controls (ports, channels, Note/CC/PB numbers) |
| [`FL_Studio_API_Reference.md`](FL_Studio_API_Reference.md) | FL Studio MIDI scripting API — local reference |
| [`IMPLEMENTATION_MAP.md`](IMPLEMENTATION_MAP.md) | Implementation plan: hardware MIDI ↔ desired functions |
| [`BRAINSTORM.md`](BRAINSTORM.md) | Feature ideas with feasibility tracking |
| [`USERGUIDE.md`](USERGUIDE.md) | End-user guide: all controls, modes, pad banking |
| [`ROADMAP.md`](ROADMAP.md) | Development phases and status |
| [`.cursorrules`](.cursorrules) | Mandatory crosschecks for AI agents |

---

## For AI Agents

Before any code change in this workspace, consult the following references (see also `.cursorrules`):

1. **`FL_Studio_API_Reference.md`** — Verify every FL API call
2. **`hardware_map.md`** — Verify all MIDI assumptions
3. **`IMPLEMENTATION_MAP.md`** — Check desired function mapping
4. **`keylab_state.py`** — Central state (single source for modes, banking, jitter)
5. **`keylab_shared_state.py`** — Cross-port pad state (mode, bank, velocity, LED dirty flag)
6. **`keylab_config.py`** — Hardware constants (never hardcode MIDI values)
7. **`BRAINSTORM.md`** — Feature context and design decisions

**Performance:** The script runs in FL Studio's real-time MIDI pipeline. No allocations in event handlers, no blocking, respect SysEx throttling.
