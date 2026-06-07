# FL Studio MIDI Scripting API — Local Reference

**Official source:** [MIDI Scripting (Python)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm) (Image-Line FL Studio Online Manual)

**Snapshot note:** This file was updated from the live public manual on **June 2026** (API version ~41).  
Image-Line may add functions in newer FL Studio builds; always verify against the live page when in doubt.

---

## 🆕 Neue Funktionen seit letztem Stand (April 2026 → Juni 2026)

> [!IMPORTANT]
> Die folgenden Funktionen/Änderungen wurden in der aktuellen offiziellen Dokumentation gefunden, die in unserem vorherigen Snapshot noch nicht enthalten waren.

### `playlist` — Neu in API v40
| Funktion | Argumente | Ergebnis | Beschreibung |
|----------|-----------|----------|--------------|
| `selectTool` | `int index` | — | Wählt das aktive Tool im Playlist / Piano Roll. `index` → Tool-Konstante. **Neu in v40.** |

### `ui` — Neu in API v41
| Funktion | Argumente | Ergebnis | Beschreibung |
|----------|-----------|----------|--------------|
| `showPicker` | `int mode, (int category = -1)` | — | Zeigt Plugin Picker (mode=0) oder Project Picker (mode=1). Kategorie: 0 = Generators/Patterns, 1 = Effects/Channels. **Neu in v41.** |
| `isStartOnInputEnabled` | — | `int` | Gibt True zurück wenn „Start on Input" aktiviert ist. **Neu (war vorher nicht dokumentiert).** |
| `isPrecountEnabled` | — | `int` | Gibt True zurück wenn Precount aktiv ist. **Neu.** |

### `channels` — Neu in API v39
| Funktion | Argumente | Ergebnis | Beschreibung |
|----------|-----------|----------|--------------|
| `rerollLoopStarterLoop` | `int index, (bool useGlobalIndex = True)` | — | Entspricht dem Würfel-Button bei Loopstarter Audio-Loops. **Neu in v39.** |

### `mixer` — Neu in API v38
| Funktion | Argumente | Ergebnis | Beschreibung |
|----------|-----------|----------|--------------|
| `getTrackCount` | — | `int` | Gibt Anzahl Mixer-Tracks zurück. Ersetzt das veraltete `trackCount`. **Neu in v38.** |
| `getCurrentTempo` | `(int asInt = 0)` | `int/float` | Gibt Tempo zurück. Optional `asInt=1` für ganzzahligen Wert. |
| `setCurrentTempo` | `float/int tempo, (int asInt = 0)` | — | Setzt Tempo. **Neu in v38.** |

### `patterns` — Neu in API v39
| Funktion | Argumente | Ergebnis | Beschreibung |
|----------|-----------|----------|--------------|
| `setPatternLength` | `int index, int length` | — | Setzt Pattern-Länge in Beats. **Neu in v39.** |
| `incrementPatternLength` | `int index, int offset` | — | Inkrementiert Pattern-Länge um `offset` Beats. **Neu in v39.** |
| `movePattern` | `(int direction = 1)` | — | Verschiebt ausgewählte Pattern(s) im Picker nach oben (1) oder unten (-1). **Neu in v39.** |

### `general` — Neu in API v38
| Funktion | Argumente | Ergebnis | Beschreibung |
|----------|-----------|----------|--------------|
| `setRecPPQ` | `int ppq` | — | Setzt die aktuelle Timebase (PPQ). **Neu in v38.** |
| `setNumerator` | `int numerator` | — | Setzt Zähler der Taktart. **Neu in v38.** |
| `setDenominator` | `int denominator` | — | Setzt Nenner der Taktart. **Neu in v38.** |
| `getProjectTitle` | — | `string` | Gibt Projekttitel zurück. **Neu in v38.** |
| `getProjectAuthor` | — | `string` | Gibt Projektautor zurück. **Neu in v38.** |
| `getProjectGenre` | — | `string` | Gibt Projektgenre zurück. **Neu in v38.** |

### `mixer` — `setRouteTo` — Neue optionale Parameter (v36)
- `setRouteTo(int index, int destIndex, int value, (bool updateUI* = False))` — `updateUI` optional hinzugefügt in v36; wenn True, aktualisiert Mixer-UI automatisch (wie `afterRoutingChanged`).
- `setRouteToLevel(int index, int destIndex, float level)` — Setzt RouteTo-Level als normalisierten Wert. **Neu in v36.**
- `getRouteToLevel(int index, int destIndex)` — Gibt RouteTo-Level zurück. **Neu in v36.**

### Wichtige Deprecation-Änderungen
- `trackCount` (mixer): **deprecated in v38** — bitte `getTrackCount` verwenden.
- `general.processRECEvent`: **deprecated in v38** — bitte modul-spezifische Setter verwenden.
- `restoreUndo` (general): **deprecated** — bitte `undo` verwenden.
- `device.sendMsgGeneric`: **deprecated** — bitte `device.midiOutSysex` verwenden.

---

## 🎵 Swing-Steuerung — aktueller Stand

> [!NOTE]
> Es gibt **kein direktes `getSwing()` / `setSwing()` im globalen transport- oder general-Modul**.  
> Swing wird in FL Studio per Kanal gesteuert, nicht global als API-Funktion.

### Per-Channel Swing Mix (`REC_Chan_SwingMix`)

Der Swing-Mix eines einzelnen Kanals ist über den REC-Event-Mechanismus steuerbar:

```python
import channels, general, midi

# Swing Mix eines Kanals lesen (als normalisierter Wert 0..1 via processRECEvent)
# DEPRECATED-Weg (noch funktionell, aber veraltet):
event_id = channels.getRecEventId(0) + midi.REC_Chan_SwingMix
# general.processRECEvent(event_id, 0, midi.REC_GetValue)

# Moderner Ansatz: direkt über MIDI REC-Event-Knopf via Encoder
# Swing Mix = midi.REC_Chan_SwingMix + channels.getRecEventId(index)
# Wert-Bereich: 0 (kein Swing) bis 65536 (MaxInt, volles Swing)
```

**`REC_Chan_SwingMix` (value = 12):** Steuert den Swing-Mix des Kanals.  
Kombiniere mit `channels.getRecEventId(chanIndex)` → zusammen mit `channels.incEventValue` für Encoder-Steuerung.

### Globaler Swing: FPT_TapTempo / Workaround

Der **globale Swing-Knopf** im Channel Rack ist derzeit nicht als eigene Getter/Setter-Funktion in der Scripting-API exponiert. Mögliche Workarounds:

1. **`device.findEventID` + `device.getLinkedValue`:** Den globalen Swing-Knopf manuell linken (rechtsklick → Link to controller) und dann per `device.findEventID(controlId)` + `device.getLinkedValue(eventID)` auslesen.
2. **`ui.globalTransport(midi.FPT_TapTempo, ...)`:** Tap-Tempo simulieren.
3. **Piano Roll Script (`flpianoroll`):** Noten-Timing manuell offsetten für eigenes Swing-Groove.

---

## Script files and locations

- User scripts live under the FL Studio **User data folder**, typically:  
  `...\Documents\Image-Line\FL Studio\Settings\Hardware\<devicename>\device_<name>.py`
- The **controller name** in the MIDI Settings list comes from the first-line predefine, e.g. `# name=My Controller` (appears as "My Controller (user)").
- Optional **launchmap** pages: `Page(number).scr` in the same hardware folder.
- Extra Python modules may be placed in the shared Image-Line Python `Lib` folder (see manual for OS paths).

---

## Predefined parameters (script header)

| Predefine | Required | Purpose |
|-----------|----------|---------| 
| `# name=...` | Yes | Display name in Controller type menu |
| `# url=...` | No | Forum link (`https://forum.image-line.com/...`) |
| `# receiveFrom=...` | No | Receive `device.dispatch` messages from named sender device |
| `# supportedDevices=...` | No | Comma-separated names for auto-linking |
| `# supportedHardwareIds=...` | No | Comma-separated hardware IDs for auto-linking |

---

## Importable FL modules (callbacks target)

Use **lower camelCase** module names:

| Module | Role |
|--------|------|
| `playlist` | Playlist tracks, mute/solo/select, live performance, tools |
| `channels` | Channel rack: names, mute/solo, volume/pan, selection, step params, routing |
| `mixer` | Mixer tracks, routing, levels, EQ, peaks, plugin slots |
| `patterns` | Pattern list, picker, lengths, groups |
| `arrangement` | Markers, time selection, arrangement time |
| `ui` | Windows, hints, jog/strip, editing shortcuts, browser |
| `transport` | Play/stop/record, song position, loop mode, global transport |
| `device` | MIDI I/O to linked port, sysex, links, dispatch between devices |
| `plugins` | Generator/effect parameters, presets, pad info |
| `general` | Undo, project metadata, PPQ/time sig, scripting API version |
| `launchMapPages` | Optional launchmap overlay pages |

**Also:** `import midi` — constants (`REC_*`, `HW_Dirty_*`, `FPT_*`, window IDs, etc.) and conventions shared across modules.

---

## Script events (FL calls your functions)

Use **CamelCase** `def OnEventName(...):`

| Event | Arguments | Purpose |
|-------|-----------|---------| 
| `OnInit` | — | Script started |
| `OnDeInit` | — | Script stopping |
| `OnMidiIn` | `eventData` | First on MIDI in; set `handled` to stop further processing |
| `OnMidiMsg` | `eventData` | After `OnMidiIn` if not fully handled |
| `OnSysEx` | `eventData` | SysEx not handled earlier |
| `OnNoteOn` / `OnNoteOff` | `eventData` | If not handled in `OnMidiMsg` |
| `OnControlChange` | `eventData` | CC not handled earlier |
| `OnProgramChange` | `eventData` | Program change |
| `OnPitchBend` | `eventData` | Pitch bend |
| `OnKeyPressure` / `OnChannelPressure` | `eventData` | Poly / channel pressure |
| `OnMidiOutMsg` | `eventData` | Short message from MIDI Out plugin |
| `OnIdle` | — | Periodic light UI tasks |
| `OnProjectLoad` | `int status` | Project load lifecycle |
| `OnRefresh` | `int flags` | FL state changed (`HW_Dirty_*` bits) |
| `OnDoFullRefresh` | — | Full refresh |
| `OnUpdateBeatIndicator` | `int value` | Beat/bar LED timing |
| `OnDisplayZone` | — | Playlist display zone |
| `OnUpdateLiveMode` | `int lastTrack` | Performance mode |
| `OnDirtyMixerTrack` | `int index` | Mixer track dirty (refresh after `OnRefresh`) |
| `OnDirtyChannel` | `int index, int flag` | Channel dirty |
| `OnFirstConnect` | — | First-ever connect |
| `OnUpdateMeters` | — | Peak meters (requires `device.setHasMeters()` in `OnInit`) |
| `OnWaitingForInput` | — | Wait-for-input mode |
| `OnSendTempMsg` | `str message, int duration` | Hint for hardware display |

---

## Calling FL from Python

Syntax: **`module.functionName(arguments)`** — function names use **lower camelCase**.

### `playlist` (core)

- **Tracks:** `getTrackName` / `setTrackName`, `getTrackColor` / `setTrackColor`, `muteTrack` / `isTrackMuted`, `soloTrack` / `isTrackSolo`, `selectTrack` / `isTrackSelected`, `selectAll` / `deselectAll`, `muteTrackLock` / `isTrackMuteLock`
- **Activity / zone:** `getTrackActivityLevel`, `getTrackActivityLevelVis`, `getDisplayZone`, `lockDisplayZone`, `liveDisplayZone`
- **Performance / live:** `getLiveLoopMode`, `getLiveTriggerMode`, `getLivePosSnap`, `getLiveTrigSnap`, `getLiveStatus`, `getLiveBlockStatus`, `getLiveBlockColor`, `triggerLiveClip`, `refreshLiveClips`, `incLivePosSnap`, `incLiveTrigSnap`, `incLiveLoopMode`, `incLiveTrigMode`, `getPerformanceModeState`
- **Time / tools:** `getVisTimeBar`, `getVisTimeTick`, `getVisTimeStep`, `selectTool` *(v40 — wählt Playlist/Piano Roll Tool)*

### `channels` (core)

- **Selection / count:** `selectedChannel`, `channelNumber`, `channelCount`, `getChannelIndex`
- **Identity:** `getChannelName` / `setChannelName`, `getChannelColor` / `setChannelColor`, `getChannelType`
- **Mute/solo:** `isChannelMuted` / `muteChannel`, `isChannelSolo` / `soloChannel`
- **Levels:** `getChannelVolume` / `setChannelVolume`, `getChannelPan` / `setChannelPan`, `getChannelPitch` / `setChannelPitch` (optional `pickupMode`, `useGlobalIndex`)
- **Selection UI:** `isChannelSelected`, `selectOneChannel`, `selectChannel`, `selectAll` / `deselectAll`
- **Routing / MIDI:** `getChannelMidiInPort`, `getTargetFxTrack` / `setTargetFxTrack`, `isHighLighted`
- **REC / automation helpers:** `getRecEventId`, `incEventValue`
- **Step sequencer / grid:** `isGridBitAssigned`, `getGridBit` / `setGridBit`, `getStepParam`, `getCurrentStepParam`, `setStepParameterByIndex`, `getGridBitWithLoop`, `showGraphEditor`, `isGraphEditorVisible`
- **Editors / activity:** `showEditor`, `focusEditor`, `showCSForm`, `midiNoteOn`, `getActivityLevel`, `quickQuantize`, `rerollLoopStarterLoop` *(v39 — Loopstarter Würfel-Button)*

### `mixer` (core)

- **Track 0 = Master.** Selection: `trackNumber`, `setTrackNumber`, `getTrackCount` *(v38, ersetzt `trackCount`)*, `getTrackInfo`, `isTrackSelected`, `selectTrack`, `setActiveTrack`, `selectAll` / `deselectAll`
- **Names / colors:** `getTrackName` / `setTrackName`, `getTrackColor` / `setTrackColor`, `getSlotColor` / `setSlotColor`
- **Arm / solo / mute / enable:** `isTrackArmed` / `armTrack`, `isTrackSolo` / `soloTrack`, `isTrackEnabled` / `enableTrack`, `isTrackMuted` / `muteTrack`, `isTrackMuteLock` / `muteTrackLock`, `isTrackAutomationEnabled`
- **Plugins:** `getTrackPluginId`, `isTrackPluginValid`, `getPluginMixLevel` / `setPluginMixLevel`, `focusEditor`, `getActiveEffectIndex`
- **Levels / pan / width:** `getTrackVolume` / `setTrackVolume`, `getTrackPan` / `setTrackPan`, `getTrackStereoSep` / `setTrackStereoSep`
- **Routing:** `setRouteTo`, `setRouteToLevel` *(v36)*, `getRouteToLevel` *(v36)*, `getRouteSendActive`, `afterRoutingChanged`, `linkTrackToChannel`, `linkChannelToTrack`
- **Tempo:** `getCurrentTempo`, `setCurrentTempo` *(v38 — direkt Tempo setzen!)*
- **Automation / remote:** `getEventValue`, `remoteFindEventValue`, `getEventIDName`, `getEventIDValueString`, `getAutoSmoothEventValue`, `automateEvent`
- **Meters / time / misc:** `getTrackPeaks`, `getTrackRecordingFileName`, `getSongStepPos`, `getRecPPS`, `getSongTickPos`, `getLastPeakVol`, `getTrackDockSide`, `isTrackSlotsEnabled` / `enableTrackSlots`, `isTrackRevPolarity` / `revTrackPolarity`, `isTrackSwapChannels` / `swapTrackChannels`
- **EQ:** `getEqBandCount`, `getEqGain` / `setEqGain`, `getEqFrequency` / `setEqFrequency`, `getEqBandwidth` / `setEqBandwidth`

*Note:* `trackCount` ist **deprecated in v38** — prefer `getTrackCount`.

### `patterns` (core)

`patternNumber`, `patternCount`, `patternMax`, `getPatternName` / `setPatternName`, `getPatternColor` / `setPatternColor`, `getPatternLength`, `setPatternLength` *(v39)*, `incrementPatternLength` *(v39)*, `getBlockSetStatus`, `ensureValidNoteRecord`, `jumpToPattern`, `findFirstNextEmptyPat`, `isPatternDefault`, picker helpers (`isPatternSelected`, `selectPattern`, `clonePattern`, `movePattern` *(v39)*, …), `burnLoop`, pattern group APIs (`getActivePatternGroup`, `getPatternGroupCount`, `getPatternGroupName`, `getPatternsInGroup`)

**`findFirstNextEmptyPat(flags)` — flags:** Image-Line hat No-Prompt-Flags in verschiedenen Builds umbenannt (`FFNEP_DontPrompt`, `FFNEP_DontPromptName`, …). Dieses Repo löst sie mit `hasattr(midi, name)` in `keylab_daw_commands._resolve_ffnep_no_prompt_flag()`.

### `arrangement` (core)

`jumpToMarker`, `getMarkerName`, `addAutoTimeMarker`, `liveSelection`, `liveSelectionStart`, `currentTime`, `currentTimeHint`, `selectionStart`, `selectionEnd`

### `transport` (core)

`globalTransport(command, value, pmeflags=..., flags=...)`, `start`, `stop`, `record`, `isRecording`, `getLoopMode` / `setLoopMode`, `getSongPos` / `setSongPos`, `getSongLength`, `getSongPosHint`, `isPlaying`, `markerJumpJog`, `markerSelJog`, `getHWBeatLEDState`, `rewind`, `fastForward`, `continuousMove`, `continuousMovePos`, `setPlaybackSpeed`

### `device` (core)

`isAssigned`, `getPortNumber`, `getName`, `midiOutMsg`, `midiOutNewMsg`, `midiOutSysex`, `processMIDICC`, `forwardMIDICC`, `directFeedback`, `repeatMidiEvent`, `stopRepeatMidiEvent`, `findEventID`, `getLinkedValue`, `getLinkedValueString`, `getLinkedChannel`, `getLinkedParamName`, `getLinkedInfo`, `linkToLastTweaked`, `getDeviceID`, refresh thread (`createRefreshThread`, `destroyRefreshThread`, `fullRefresh`), `isDoubleClick`, `setHasMeters`, `baseTrackSelect`, `hardwareRefreshMixerTrack`, `dispatch`, `dispatchReceiverCount`, `dispatchGetReceiverPortNumber`, `setMasterSync`, `getMasterSync`

*Deprecated:* `sendMsgGeneric` → bitte `midiOutSysex` verwenden.

### `plugins` (core)

`isValid`, `getPluginName`, `getParamCount`, `getParamName`, `getParamValue` / `setParamValue`, `getParamValueString`, `getColor`, **`getName(channel)`** (preset/bank title string), `getPadInfo`, `getPresetCount`, `nextPreset`, `prevPreset`

### `general` (core)

`saveUndo`, `undo`, **`undoUp`**, **`undoDown`**, `undoUpDown`, `restoreUndoLevel`, undo history getters/setters (`getUndoLevelHint`, `getUndoHistoryPos`, `getUndoHistoryCount`, `getUndoHistoryLast`, `setUndoHistoryPos`, `setUndoHistoryCount`, `setUndoHistoryLast`), `getRecPPB`, `getRecPPQ`, `setRecPPQ` *(v38)*, `setNumerator` *(v38)*, `setDenominator` *(v38)*, `getUseMetronome`, `getPrecount`, `getChangedFlag`, `getVersion`, `dumpScoreLog`, `clearLog`, `safeToEdit`, `getProjectTitle` *(v38)*, `getProjectAuthor` *(v38)*, `getProjectGenre` *(v38)*

*Deprecation:* `processRECEvent` ist in v38 als **deprecated** markiert — bitte modul-spezifische Setter verwenden.  
*Deprecated:* `restoreUndo` → bitte `undo` verwenden.

### `launchMapPages` (core)

`init`, `createOverlayMap`, `length`, `updateMap`, `getMapItemColor`, `getMapCount`, `getMapItemChannel`, `getMapItemAftertouch`, `processMapItem`, `releaseMapItem`, `checkMapForHiddenItem`, `setMapItemTarget`

### `ui` (grouped core)

- **Jog / strip:** `jog`, `jog2`, `strip`, `stripJog`, `stripHold`, `moveJog`
- **Navigation / edit:** `previous`, `next`, `up` / `down` / `left` / `right`, `horZoom`, `verZoom`, `snapOnOff`, `cut`, `copy`, `paste`, `insert`, `delete`, `enter`, `escape`, `yes`, `no`
- **Hints:** `getHintMsg`, `setHintMsg`, `getHintValue`, `getTimeDispMin`, `setTimeDispMin`
- **Windows:** `getVisible`, `showWindow`, `hideWindow`, `getFocused`, `setFocused`, `getFocusedFormCaption`, `getFocusedFormID`, `getFocusedPluginName`, `scrollWindow`, `nextWindow`, `selectWindow`, `launchAudioEditor`, `openEventEditor`, `showPicker` *(v41 — Plugin/Project Picker)*
- **Menus / helpers:** `isInPopupMenu`, `closeActivePopupMenu`, `isClosing`, **`isMetronomeEnabled()`**, **`isStartOnInputEnabled()`** *(neu)*, **`isPrecountEnabled()`** *(neu)*, **`isLoopRecEnabled()`**, `getSnapMode` / `setSnapMode` / `snapMode`, `getStepEditMode` / `setStepEditMode`, `getProgTitle`, `getVersion`, `crDisplayRect`, `miDisplayRect`, `miDisplayDockRect`
- **Browser:** `navigateBrowser`, `toggleBrowserNode`, `navigateBrowserTabs`, `selectBrowserMenuItem`, `previewBrowserMenuItem`, `getFocusedNodeFileType`, `getFocusedNodeCaption`, `isBrowserAutoHide`, `setBrowserAutoHide`

---

## `eventData` (MIDI callback argument)

Writable / readable fields include: `handled`, `status`, `data1`, `data2`, `note`, `velocity`, `pressure`, `progNum`, `controlNum`, `controlVal`, `pitchBend`, `sysex`, `isIncrement`, `res`, `inEv`, `outEv`, `midiId`, `midiChan`, `midiChanEx`, `pmeflags`, `timestamp`, `port`, … (see manual table).

**Routing tip:** Handlers in this repo often branch on **`event.midiId`** (status nybble) *or* **`event.status`** (full status byte including channel). Pad logic in `device_KeyLabmkII_Forward.py` uses `event.status` (e.g. `0x99` = Note On channel 10). You can rewrite `event.status` and `event.midiChan` to move notes to another MIDI channel (e.g. melodic channel 1 instead of GM drum channel 10).

---

## `midi` constants — high-signal groups

Full tables live in the official manual; this repo uses many of these names in scripts.

### `OnRefresh` flags (`HW_Dirty_*`)

| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `HW_Dirty_Mixer_Sel` | 1 | Mixer-Auswahl geändert |
| `HW_Dirty_Mixer_Display` | 2 | Mixer-Display geändert |
| `HW_Dirty_Mixer_Controls` | 4 | Mixer-Controls geändert |
| `HW_Dirty_RemoteLinks` | 16 | Remote-Links hinzugefügt/entfernt |
| `HW_Dirty_FocusedWindow` | 32 | Fokussiertes Fenster geändert |
| `HW_Dirty_Performance` | 64 | Performance-Layout geändert |
| `HW_Dirty_LEDs` | 256 | LED-Update nötig (Play/Stop/Rec/...) |
| `HW_Dirty_RemoteLinkValues` | 512 | Remote-Link-Wert geändert |
| `HW_Dirty_Patterns` | 1024 | Pattern-Änderungen |
| `HW_Dirty_Tracks` | 2048 | Track-Änderungen |
| `HW_Dirty_ControlValues` | 4096 | Plugin-Control-Wert geändert |
| `HW_Dirty_Colors` | 8192 | Plugin-Farben geändert |
| `HW_Dirty_Names` | 16384 | Plugin-Namen geändert |
| `HW_Dirty_ChannelRackGroup` | 32768 | Channel Rack Gruppe geändert |
| `HW_ChannelEvent` | 65536 | Kanal-Änderungen |

### Channel REC helpers (mit `channels.getRecEventId`)

| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `REC_Chan_Vol` | 0 | Channel Volume |
| `REC_Chan_Pan` | 1 | Channel Pan |
| `REC_Chan_FCut` | 2 | Channel Filter Cutoff |
| `REC_Chan_FRes` | 3 | Channel Filter Resonance |
| `REC_Chan_Pitch` | 4 | Channel Pitch |
| `REC_Chan_FType` | 5 | Channel Filter Type |
| `REC_Chan_PortaTime` | 6 | Channel Portamento Time |
| `REC_Chan_Mute` | 7 | Channel Mute |
| `REC_Chan_FXTrack` | 8 | Channel FX Target |
| `REC_Chan_GateTime` | 9 | Channel Gate Time |
| `REC_Chan_Crossfade` | 10 | Channel Crossfade |
| `REC_Chan_TimeOfs` | 11 | Time Offset |
| **`REC_Chan_SwingMix`** | **12** | **Swing Mix ← für Swing-Steuerung!** |
| `REC_Chan_SmpOfs` | 13 | Sample Offset |
| `REC_Chan_StretchTime` | 14 | Time Stretch |
| `REC_Chan_OfsPan` | 16 | Levels Adjustment Pan |
| `REC_Chan_OfsVol` | 17 | Levels Adjustment Volume |
| `REC_Chan_OfsPitch` | 18 | Levels Adjustment Pitch |
| `REC_Chan_OfsFCut` | 19 | Levels Adjustment Mod X |
| `REC_Chan_OfsFRes` | 20 | Levels Adjustment Mod Y |

Verwendung: `midi.REC_Chan_SwingMix + channels.getRecEventId(index)`

### Mixer REC helpers (mit `mixer.getTrackPluginId`)

| Konstante | Bedeutung |
|-----------|-----------|
| `REC_Mixer_Vol` | Mixer Volume |
| `REC_Mixer_Pan` | Mixer Pan |
| `REC_Mixer_SS` | Mixer Stereo Separation |
| `REC_Mixer_EQ_Gain` | Mixer EQ Gain |
| `REC_Mixer_EQ_Freq` | Mixer EQ Frequency |
| `REC_Mixer_EQ_Q` | Mixer EQ Q/Bandwidth |
| `REC_Mixer_EQ_Type` | Mixer EQ Type |

### REC flags

| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `REC_UpdateValue` | 1 | Wert aktualisieren |
| `REC_GetValue` | 2 | Wert abrufen |
| `REC_ShowHint` | 4 | Hint anzeigen |
| `REC_UpdatePlugLabel` | 16 | Plugin-Label aktualisieren |
| `REC_UpdateControl` | 32 | Wheel/Knob aktualisieren |
| `REC_FromMIDI` | 64 | Wert kommt aus MIDI (0..FromMIDI_Max) |
| `REC_Store` | 128 | Wert bei Automation-Recording speichern |
| `REC_MIDIController` | — | Für MIDI-Controller-Eingaben |

### Global transport (`FPT_*`, `GT_*`, `SS_*`)

Used with `transport.globalTransport` / `ui` navigation helpers:

`FPT_Play`, `FPT_Stop`, `FPT_Record`, `FPT_Rewind`, `FPT_FastForward`, **`FPT_Metronome`**, **`FPT_Overdub`**, **`FPT_TapTempo`**, **`FPT_LoopRecord`**, `FPT_Up`, `FPT_Down`, `FPT_Left`, `FPT_Right`, `GT_All`, **`SS_Start`**, **`SS_Stop`** (with `transport.continuousMove` for rewind/FF hold), `PME_System`, `PME_FromMIDI`, …

### Loop / record indicators (do not mix these up)

| API | Meaning in this project |
|-----|-------------------------|
| `transport.globalTransport(midi.FPT_LoopRecord, …)` | Toggle loop-*record* / pattern record behavior |
| `transport.getLoopMode()` | Song vs pattern loop mode (transport hint text) |
| `ui.isLoopRecEnabled()` | Loop-record button state (transport LED in `keylab_feedback.py`) |

### FL window IDs

`widMixer`, `widChannelRack`, `widPlaylist`, `widPianoRoll`, `widBrowser`, `widPlugin`, `widPluginEffect`, `widPluginGenerator`

### `OnProjectLoad` status

| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `PL_Start` | 0 | Projekt-Laden hat begonnen |
| `PL_LoadOk` | 100 | Projekt erfolgreich geladen |
| `PL_LoadError` | 101 | Fehler beim Laden |

### `OnDirtyChannel` flags (`CE_*`)

`CE_New` (0), `CE_Delete` (1), `CE_Replace` (2), `CE_Rename` (3), `CE_Select` (4)

### Other common enums

Live block / clip flags (`LB_*`, `TLC_*`), channel types (`CT_Sampler`, `CT_Hybrid`, `CT_GenPlug`, `CT_Layer`, `CT_AudioClip`, `CT_AutoClip`), snap modes (`Snap_*`), pickup modes (`PIM_*`), step params (`pPitch`, `pVelocity`, …), browser node types (`SBN_*`), undo flags (`UF_*`), track solo modes (`fxSoloModeWithSourceTracks`, `fxSoloModeWithDestTracks`, `fxSoloModeIgnorePrevious`).

### Mixer Solo Mode (`soloTrack` mode parameter)

| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `fxSoloModeWithSourceTracks` | 1 | Solo inkl. zulaufende Tracks |
| `fxSoloModeWithDestTracks` | 2 | Solo inkl. Send-Tracks |
| `fxSoloModeWithSourceTracks + fxSoloModeWithDestTracks` | 3 | Wie Alt+Klick in FL |
| `fxSoloModeIgnorePrevious` | 4 | Nur diesen Track solo |

---

## Multiple device scripts (this repo)

- **DAW port:** `device_KeyLabmkII.py` — transport, mixer, DAW buttons, display.
- **Keys port:** `device_KeyLabmkII_Forward.py` — pad transposition, optional V-Collection `device.forwardMIDICC`.
- **Shared pad state:** `keylab_shared_state.py` uses `sys` plus `keylab_pad_state.json` in the hardware folder when FL isolates script namespaces.
- Optional header: `# receiveFrom=...` for `device.dispatch()` between scripts (not used for pad mode currently).

---

## Debugging

- **View → Script output:** shows script name, `init ok`, unhandled MIDI when logging.
- Reload script after edits without restarting FL (per manual).

---

*End of local reference. For authoritative signatures, defaults, and newly added API members, always reconcile with the [official MIDI Scripting page](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm).*
