# Arturia KeyLab mkII — User Guide

**Script: KeyLab mkII P Version**  
Last updated: 2026-06-09

---

## Contents

1. [Modes & Contexts](#1-modes--contexts)
2. [Transport](#2-transport)
3. [DAW Commands](#3-daw-commands)
4. [Navigation (Jog Wheel + Bank)](#4-navigation-jog-wheel--bank)
5. [Mixer Faders (Volume)](#5-mixer-faders-volume)
6. [Mixer Encoders (Pan)](#6-mixer-encoders-pan)
7. [Track Buttons](#7-track-buttons)
8. [Bank Buttons](#8-bank-buttons)
9. [Plugin Control](#9-plugin-control)
10. [Free Mode](#10-free-mode)
11. [LCD Feedback](#11-lcd-feedback)
12. [Pads](#12-pads)
13. [LED Rules](#13-led-rules)

---

## 1. Modes & Contexts

The script automatically switches between control contexts depending on which FL Studio window is currently focused. **No manual switching is required** — except for [Free Mode](#10-free-mode).

| Focused Window   | Encoder 1–8        | Fader 1–8          | Jog Wheel            |
|:-----------------|:-------------------|:-------------------|:---------------------|
| **Channel Rack** | Pan (channels)     | Volume (channels)  | Switch channel       |
| **Mixer**        | Pan (mixer tracks) | Volume (mixer tracks) | Switch mixer track |
| **Plugin Editor**| Plugin parameters  | Volume (mixer tracks) | Preset navigation* |
| **Browser**      | Pan (channel rack) | Volume (channel rack) | Navigate browser  |
| **Free Mode**    | MIDI passthrough   | MIDI passthrough   | Normal               |

*Only for plugins with a defined `jog_wheel` function in `plugin_database.py`.

---

## 2. Transport

Transport buttons send their actions to FL Studio and provide LED feedback.

| Button | Function | LED |
|:-------|:---------|:----|
| **Play** | Play / Pause | Lit during playback |
| **Stop** | Stop | — |
| **Record** | Start/stop recording | Lit during recording |
| **Loop** | Toggle loop | Lit when loop is active |
| **Rewind** | Rewind (fast while held) | — |
| **Fast Forward** | Fast forward (fast while held) | — |

---

## 3. DAW Commands

The utility buttons in the upper-left section.

| Button | Short Press | Long Press (≥0.75 s) |
|:-------|:------------|:--------------------|
| **Save** | Cycle: Browser → Channel Rack → Mixer | — |
| **In** | Toggle Pad Mode (Chromatic / Drum Map) | Toggle Pad Velocity on/off |
| **Out** | Overdub toggle | — |
| **Metro** | Metronome toggle | — |
| **Undo** (global) | Redo | — |
| **Write** (track) | Undo | Cut |
| **Record** (track) | Snap toggle | — |
| **Solo** (track) | New Pattern | — |
| **Mute** (track) | Focus Mixer | — |
| **Read** (track) | Tap Tempo | — |

> **Long Press:** The action and LCD hint fire at **0.75 s hold time** — before you release. Short press = action fires on release.

---

## 4. Navigation (Jog Wheel + Bank)

### Jog Wheel — Rotate

Context-sensitive:

| Context | Action |
|:--------|:-------|
| **Channel Rack / Default** | Next / previous channel |
| **Mixer** | Next / previous mixer track |
| **Browser** | Next / previous item |
| **Browser (popup menu)** | Up / down in menu |
| **Plugin with jog mapping** | Next / previous preset |

### Jog Wheel — Click

| Context | Action |
|:--------|:-------|
| **Channel Rack** | Open plugin editor |
| **Plugin Editor** | Close plugin editor |
| **Mixer** | Arm / un-arm track |
| **Browser (folder)** | Expand / collapse folder |
| **Browser (file)** | Load file |
| **Other** | Next window |

### Bank Left / Right (arrow keys at top)

| Context | Action |
|:--------|:-------|
| **Plugin focused** | Previous / next preset |
| **Browser** | Previous / next browser tab |
| **Mixer** | Previous / next track |
| **Default** | Previous / next pattern |

---

## 5. Mixer Faders (Volume)

The 9 faders control volume:

| Fader | Context: Mixer | Context: Channel Rack |
|:------|:---------------|:----------------------|
| **1–8** | Mixer tracks 1–8 (+ bank offset) | Channels 0–7 (+ bank offset) |
| **9 (Master)** | Always: Master volume | Always: Master volume |

### Soft Pickup

On the first fader move after loading, the LCD shows the current FL value in dB (e.g. `-> -6.0 dB`). The fader must **cross** this value before it becomes active — preventing jumps.

While moving: **Line 1** = track/channel name, **Line 2** = volume in **dB** (read from FL, not hardware position — accurate even at fast fader speed).

> **Tip:** Touching a fader shows the track name (line 1) and current dB (line 2).

### Banking

Use the [Bank Buttons (Prev/Next)](#8-bank-buttons) (Part 48/49) to move in steps of 8 inserts/channels — up to the **last** track in the project. The LCD shows the real range (e.g. `Tracks 25–31`, not `25–32` if the last slot is empty). Soft pickup resets on bank change.

---

## 6. Mixer Encoders (Pan)

Encoders 1–8 control panning:

| Encoder | Context: Mixer | Context: Channel Rack |
|:--------|:---------------|:----------------------|
| **1–8** | Pan mixer track | Pan channel |
| **9 (Master)** | *(reserved)* | *(reserved)* |

LCD shows: `TrackName / L 30%` or `Center` or `R 45%`

> **In Plugin Mode**, encoders 1–8 control plugin parameters instead (see [Plugin Control](#9-plugin-control)).

---

## 7. Track Buttons

The 9 buttons below the encoders:

| Action | Function |
|:-------|:---------|
| **Short press** | Mute / un-mute track or channel |
| **Long press (≥0.75 s)** | Pan reset (Mixer) or Solo (Channel Rack) — LCD hint at threshold |

> Button 9 (Master) is reserved.

---

## 8. Bank Buttons

The two buttons to the left of the faders (`<` and `>`):

| Button | Short Press | Long Press (≥0.75 s) |
|:-------|:------------|:--------------------|
| **`<` (Bank Prev)** | Bank back by 8 (min. 0) | **Free Mode** on/off (LCD hint at threshold) |
| **`>` (Bank Next)** | Bank forward by 8 | — |

LCD shows on bank change: `Bank / Tracks 9–16` (last bank only up to the highest existing track)

---

## 9. Plugin Control

When a plugin editor is focused, **encoders 1–8 automatically switch** to plugin mode.

### Known Plugins

Over 300 plugins have parameters defined in `plugin_database.py`. The 8 encoder slots follow this schema:

| Slot | Typical Function |
|:-----|:-----------------|
| 1 | Filter Cutoff |
| 2 | Resonance |
| 3 | Attack |
| 4 | Release |
| 5 | Modulation |
| 6 | FX1 Level |
| 7 | FX2 Level |
| 8 | Volume / Level |

LCD shows: `ParameterName / 67%`

### Unknown Plugins

If a plugin is **not** in `plugin_database.py`:
- LCD shows: `PluginName / Not mapped!`
- Encoders are **blocked** (no action — no accidental pan changes)

> **Add a plugin:** Create a new entry in `plugin_database.py`. The debug function `scan_plugin_params()` in `keylab_plugin.py` lists all available parameter indices.

### Plugin Jog (Preset Navigation)

Plugins with `"special": {"jog_wheel": "preset_navigation"}` in the database use the jog wheel for preset navigation instead of channel switching.

---

## 10. Free Mode

**Free Mode** is a manually activated mode that releases the entire mixer section (faders 1–8, encoders 1–8, track buttons 1–8) from automatic control, making them available as a **blank MIDI controller**.

### Activate / Deactivate

**Long Press `<` (Bank Prev) for ≥0.75 seconds** → Free Mode on/off (LCD hint at threshold)

LCD shows: `FREE MODE / Active` or `FREE MODE / Off`

### Behaviour in Free Mode

| Element | Free Mode OFF | Free Mode ON |
|:--------|:-------------|:------------|
| Faders 1–8 | Volume (Mixer/Channel) | MIDI passthrough |
| Encoders 1–8 | Pan / Plugin parameters | MIDI passthrough |
| Track Buttons 1–8 | Pan reset / Mute | MIDI passthrough |
| **Fader 9 (Master)** | Master Volume | **Always Master Volume** |
| **Encoder 9** | *(reserved)* | *(reserved)* |
| **Track Button 9** | *(reserved)* | *(reserved)* |
| Plugin Mode | Auto-detect | **Disabled** |

> **MIDI Passthrough** means: FL Studio receives the raw MIDI events (Pitch Bend / CC / Note) and you can assign them freely via MIDI Learn or other scripts.

> **Important:** Free Mode is **not** automatically disabled when the window changes. Only another long press on `<` deactivates it.

---

## 11. LCD Feedback

The LCD shows context-sensitive information. Display duration varies:

| Context | Line 1 | Line 2 | Duration |
|:--------|:-------|:-------|:---------|
| Default | Channel name | Pattern name | permanent |
| Fader | Track name | Volume dB (FL readback) | 0.8 s |
| Fader (touch) | Track name | dB (current) | 2 s |
| Encoder | Track name | `L 30%` / `Center` / `R 45%` | 0.8 s |
| Navigation | `Nav` | Description | 1 s |
| Plugin | Plugin name | Parameter / `Not mapped!` | 1.5 s |
| Bank (mixer) | `Bank` | `Tracks 9–16` | 1.2 s |
| Pad mode | `Pads:` | `Chromatic` / `Drum Map` | 1.5 s |
| Pad velocity | `Pad Velo:` | `On` / `Off` | 1.5 s |
| Pad bank | `Pad Bank` | `3/8` (bank number / total) | 1.2 s |
| Free Mode | `FREE MODE` | `Active` / `Off` | 1.5 s |
| Transport | — | — | immediate via LED |

---

## 12. Pads

**Layout (Pad 1 top-left):** Row 1 = notes 36–39, Row 4 bottom = 48–51 (see `hardware_map.md`).

### Modes

| Mode | Default | Output channel | Pad 1 default note |
|:-----|:--------|:--------------|:------------------|
| **Chromatic** | ✅ Yes | **MIDI ch. 1** | C5 (MIDI 84, bank 4) |
| **Drum Map** | No | **MIDI ch. 10** | C1/GM 36 (bank 1) |

### Mode Toggle

Press **IN** (short) to switch between Chromatic and Drum Map mode.  
- LED hint on LCD at switch: `Pads: Chromatic` or `Pads: Drum Map`  
- Pad LEDs update immediately: **white** (Chromatic) / **purple** (Drum Map)

### Pad Velocity

Press **IN** (long, ≥0.75 s) to toggle pad velocity.  
- **On:** Full velocity sensitivity (default)  
- **Off:** Fixed velocity at 75% (MIDI 95) — LCD: `Pad Velo: Off`

### Pad Banking

Both modes support 8 banks (Bank 0–7). Each bank shifts all pads by 16 semitones.

**Chromatic Mode:**

| Bank | Pad 1 note | Range |
|:-----|:-----------|:------|
| 0 | MIDI 20 (G#0) | 20–35 |
| 1 | MIDI 36 (C1) | 36–51 |
| 2 | MIDI 52 (E2) | 52–67 |
| 3 | MIDI 68 (G#3) | 68–83 |
| **4 (default)** | **MIDI 84 (C5)** | **84–99** |
| 5 | MIDI 100 (E6) | 100–115 |
| 6 | MIDI 116 (G#7) | 116–127 |
| 7 | MIDI 127 (clamped) | 127 |

**Drum Map Mode (GM layout):**

| Bank | Pad 1 MIDI note | Notable drums |
|:-----|:---------------|:-------------|
| 0 | MIDI 20 | — |
| **1 (default)** | **MIDI 36 (C1)** | **Bass Drum 1** |
| 2 | MIDI 52 | — |
| 3 | MIDI 68 | — |
| 4+ | MIDI 84+ | — |

> Use **Pad Bank Prev/Next** (Notes 46/47 on DAW port) to step through banks.  
> The bank is remembered **separately per mode** — switching mode restores the mode's last bank.

### Pad LEDs

- **Chromatic:** White at 50% idle → 100% on press (velocity-scaled)
- **Drum Map:** Purple at 50% idle → 100% on press (velocity-scaled)
- **On release:** Returns to 50% idle colour

> **Arturia MIDI Control Center:** Set pad LED mode to **Off** (not "Light when triggered" — that gives firmware blue, overriding the script colours).

---

## 13. LED Rules

Full specification: [`CONTROLLER_RULES.md`](CONTROLLER_RULES.md)

### Monochrome LEDs

| Level | Value | When used |
|:------|:------|:---------|
| Full (100%) | `0x7F` | Active state, always-on buttons |
| Dim (~30%) | `0x26` | Inactive toggle state |
| Off | `0x00` | Disabled or blink-off phase |

- **Toggle buttons** (Metro, Snap, Overdub, Loop): dim when off, full when on
- **Always full (100%):** Save, IN, Undo, Tap Tempo, New Pattern, Redo, Nav Bank L/R, Jog click, Part Prev/Next

### RGB LEDs (Track Buttons 1–8)

| State | Brightness |
|:------|:-----------|
| Muted | **0%** (off) |
| In bank, not selected | **20%** of FL track colour |
| Selected (focused) | **100%** of FL track colour |

Colour source: `mixer.getTrackColor` (Mixer) or `channels.getChannelColor` (Channel Rack).

---

*For technical details and plugin mappings see `plugin_database.py` and `ROADMAP.md`*
