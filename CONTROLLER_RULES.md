# KeyLab mkII — Controller Rules

Cross-cutting behaviour for UI, timing, and LEDs. Implementation lives in the Python modules referenced below; this file is the specification.

## Timing

| Rule | Value | Code |
|------|-------|------|
| Long press threshold | **0.75 s** | `keylab_long_press.LONG_PRESS_THRESHOLD` |
| Long press action | Fire **on threshold** (while held), not on release | `keylab_long_press.poll()` in `OnIdle` |
| Short press | On button **release** if long did not fire | `keylab_long_press.release()` |

## LCD Hints

| Control | Short | Long |
|---------|-------|------|
| IN (87) | `Pads: Chromatic` / `Pads: Drum Map` | `Pad Velo: On` / `Pad Velo: Off` |
| Fader move | Line 1: track/channel name | Line 2: dB from FL (`getTrackVolume(t,1)` / `getChannelVolume(ch,1)`) |

## Monochrome LEDs

SysEx: `F0 00 20 6B 7F 42 02 00 10 <led_id> <value> F7` via `send_to_device()`.

| Level | Value | Use |
|-------|-------|-----|
| On | `0x7F` (100%) | Active toggle, mode/action buttons, Part Prev/Next |
| Dim | `0x26` (~30%) | Inactive toggle state |
| Off | `0x00` | Transport record blink off-phase |

**Toggle (reflects FL on/off):** Metro, Snap, Overdub/Loop — dim when off, full when on.

**Always on (100%):** Save, IN, Undo, Tap Tempo, New Pattern, Redo, Navigation Bank L/R, Jog click, **Part Prev/Next (48/49)**.

## RGB LEDs (pads, track buttons)

SysEx: `02 00 16 <id> <R> <G> <B> 0x7F`.

FL colour is BGR in `getTrackColor` / `getChannelColor`. Scale with brightness 0.0–1.0, clamp to 0–127.

### Pads (`keylab_shared_state.pad_mode`)

| Mode | Default | Colour |
|------|---------|--------|
| Chromatic | **yes** | **White** |
| Drum Map (`fpc`) | no | **Purple** |

| State | Brightness | Code |
|-------|------------|------|
| Idle (not pressed) | **50%** | `keylab_pad_leds.refresh_all_pads_idle()` |
| Pressed | **50% → 100%** by MIDI velocity | `set_pad_color(pad_index, velocity)` on Keys port |
| Release | back to 50% idle | `set_pad_color(pad_index, 0)` |

Pad RGB **only** on Keys port: **`device_KeyLabmkII_Forward.py`** (`OnMidiIn` press/release, `OnInit` idle). MCC: set all pads to **Off** (not "Light when triggered" — that is firmware blue).

DAW script sets `pad_led_dirty` after IN (pad mode); Forward `OnIdle` refreshes idle colours once.

**LED slot:** `Pad.NOTE_TO_LED_SLOT` in [`keylab_config.py`](keylab_config.py) — vertical flip vs `Pad.NOTES` (Pad 1 → LED index 12 on hardware). Do **not** use `note - 36`.

**Nav / Part Prev/Next:** mono LEDs set once on init (`0x62`/`0x63` nav, `0x1A`/`0x1B` part per archive). Track buttons 24–31: 0% / 20% / 100% when selection changes only.

### Pad Banking

| Mode | Banks | Default bank | Chromatic base | Pad 1 default note |
|------|-------|-------------|---------------|-------------------|
| Chromatic | 0–7 | **4** | MIDI 20 | 20 + 0 + 4×16 = **84 (C5)** |
| Drum Map | 0–7 | **1** | native 36 + (bank−1)×16 | 36 + 0 = **36 (C1/GM)** |

Bank offsets are stored separately per mode in `keylab_shared_state.py` and restored on toggle.

### Track buttons (notes 24–31, slots 1–8)

| State | Brightness |
|-------|------------|
| Muted | **0%** (RGB off) |
| In bank, not selected | **20%** of FL colour |
| Selected (focused) | **100%** of FL colour |

Colour source: `mixer.getTrackColor` (Mixer focus) or `channels.getChannelColor` (Channel Rack).  
Refresh: `OnRefresh`, throttled `OnIdle` (~80 ms), after jog / bank change.

## LED ID Map (mono)

Documented in `keylab_feedback.py` (from `_archive/KeyLabmk2Return.py`). Part Prev/Next IDs (`0x50`/`0x51`) may need hardware verification.

## Related Docs

- [ROADMAP.md](ROADMAP.md) — phases 10–13
- [USERGUIDE.md](USERGUIDE.md) — user-facing behaviour
- [codemaps/long_press.md](codemaps/long_press.md) — long-press flow
