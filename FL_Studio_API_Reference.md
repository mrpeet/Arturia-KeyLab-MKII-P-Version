# FL Studio MIDI Scripting API — Local Reference

**Official source:** [MIDI Scripting (Python)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm) (Image-Line FL Studio Online Manual)

**Snapshot note:** This file was produced from the public manual as of **April 2026**. Image-Line may add functions, modules, or constants in newer FL Studio builds; verify against the live page when in doubt.

---

## Script files and locations

- User scripts live under the FL Studio **User data folder**, typically:  
  `...\Documents\Image-Line\FL Studio\Settings\Hardware\<devicename>\device_<name>.py`
- The **controller name** in the MIDI Settings list comes from the first-line predefine, e.g. `# name=My Controller` (appears as “My Controller (user)”).
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
- **Time / tools:** `getVisTimeBar`, `getVisTimeTick`, `getVisTimeStep`, `selectTool`

### `channels` (core)

- **Selection / count:** `selectedChannel`, `channelNumber`, `channelCount`, `getChannelIndex`
- **Identity:** `getChannelName` / `setChannelName`, `getChannelColor` / `setChannelColor`, `getChannelType`
- **Mute/solo:** `isChannelMuted` / `muteChannel`, `isChannelSolo` / `soloChannel`
- **Levels:** `getChannelVolume` / `setChannelVolume`, `getChannelPan` / `setChannelPan`, `getChannelPitch` / `setChannelPitch` (optional `pickupMode`, `useGlobalIndex`)
- **Selection UI:** `isChannelSelected`, `selectOneChannel`, `selectChannel`, `selectAll` / `deselectAll`
- **Routing / MIDI:** `getChannelMidiInPort`, `getTargetFxTrack` / `setTargetFxTrack`, `isHighLighted`
- **REC / automation helpers:** `getRecEventId`, `incEventValue` (use with `general.processRECEvent` where applicable — note deprecation in manual for some flows)
- **Step sequencer / grid:** `isGridBitAssigned`, `getGridBit` / `setGridBit`, `getStepParam`, `getCurrentStepParam`, `setStepParameterByIndex`, `getGridBitWithLoop`, `showGraphEditor`, `isGraphEditorVisible`
- **Editors / activity:** `showEditor`, `focusEditor`, `showCSForm`, `midiNoteOn`, `getActivityLevel`, `quickQuantize`, `rerollLoopStarterLoop`

### `mixer` (core)

- **Track 0 = Master.** Selection: `trackNumber`, `setTrackNumber`, `getTrackCount`, `getTrackInfo`, `isTrackSelected`, `selectTrack`, `setActiveTrack`, `selectAll` / `deselectAll`
- **Names / colors:** `getTrackName` / `setTrackName`, `getTrackColor` / `setTrackColor`, `getSlotColor` / `setSlotColor`
- **Arm / solo / mute / enable:** `isTrackArmed` / `armTrack`, `isTrackSolo` / `soloTrack`, `isTrackEnabled` / `enableTrack`, `isTrackMuted` / `muteTrack`, `isTrackMuteLock` / `muteTrackLock`
- **Plugins:** `getTrackPluginId`, `isTrackPluginValid`, `getPluginMixLevel` / `setPluginMixLevel`, `focusEditor`, `getActiveEffectIndex`
- **Levels / pan / width:** `getTrackVolume` / `setTrackVolume`, `getTrackPan` / `setTrackPan`, `getTrackStereoSep` / `setTrackStereoSep`
- **Routing:** `setRouteTo`, `setRouteToLevel`, `getRouteToLevel`, `getRouteSendActive`, `afterRoutingChanged`, `linkTrackToChannel`, `linkChannelToTrack`
- **Automation / remote:** `getEventValue`, `remoteFindEventValue`, `getEventIDName`, `getEventIDValueString`, `getAutoSmoothEventValue`, `automateEvent`
- **Meters / time / misc:** `getTrackPeaks`, `getTrackRecordingFileName`, `getSongStepPos`, `getCurrentTempo` / `setCurrentTempo`, `getRecPPS`, `getSongTickPos`, `getLastPeakVol`, `getTrackDockSide`, `isTrackSlotsEnabled` / `enableTrackSlots`, `isTrackRevPolarity` / `revTrackPolarity`, `isTrackSwapChannels` / `swapTrackChannels`
- **EQ:** `getEqBandCount`, `getEqGain` / `setEqGain`, `getEqFrequency` / `setEqFrequency`, `getEqBandwidth` / `setEqBandwidth`

*Note:* Manual lists `trackCount` with deprecation notes in places; prefer `getTrackCount` where available.

### `patterns` (core)

`patternNumber`, `patternCount`, `patternMax`, `getPatternName` / `setPatternName`, `getPatternColor` / `setPatternColor`, `getPatternLength` / `setPatternLength`, `incrementPatternLength`, `getBlockSetStatus`, `ensureValidNoteRecord`, `jumpToPattern`, `findFirstNextEmptyPat`, picker helpers (`isPatternSelected`, `selectPattern`, `clonePattern`, `movePattern`, …), `burnLoop`, pattern group APIs (`getActivePatternGroup`, …)

### `arrangement` (core)

`jumpToMarker`, `getMarkerName`, `addAutoTimeMarker`, `liveSelection`, `liveSelectionStart`, `currentTime`, `currentTimeHint`, `selectionStart`, `selectionEnd`

### `transport` (core)

`globalTransport(command, value, pmeflags=..., flags=...)`, `start`, `stop`, `record`, `isRecording`, `getLoopMode` / `setLoopMode`, `getSongPos` / `setSongPos`, `getSongLength`, `getSongPosHint`, `isPlaying`, `markerJumpJog`, `markerSelJog`, `getHWBeatLEDState`, `rewind`, `fastForward`, `continuousMove`, `continuousMovePos`, `setPlaybackSpeed`

### `device` (core)

`isAssigned`, `getPortNumber`, `getName`, `midiOutMsg`, `midiOutNewMsg`, `midiOutSysex`, `processMIDICC`, `forwardMIDICC`, `directFeedback`, `repeatMidiEvent`, `stopRepeatMidiEvent`, `findEventID`, `getLinkedValue`, `getLinkedValueString`, `getLinkedChannel`, `getLinkedParamName`, `getLinkedInfo`, `linkToLastTweaked`, `getDeviceID`, refresh thread (`createRefreshThread`, `destroyRefreshThread`, `fullRefresh`), `isDoubleClick`, `setHasMeters`, `baseTrackSelect`, `hardwareRefreshMixerTrack`, `dispatch`, `dispatchReceiverCount`, `dispatchGetReceiverPortNumber`, `setMasterSync`, `getMasterSync`

### `plugins` (core)

`isValid`, `getPluginName`, `getParamCount`, `getParamName`, `getParamValue` / `setParamValue`, `getParamValueString`, `getColor`, `getName`, `getPadInfo`, `getPresetCount`, `nextPreset`, `prevPreset`

### `general` (core)

`saveUndo`, `undo`, `undoUp`, `undoDown`, `undoUpDown`, `restoreUndoLevel`, undo history getters/setters, `getRecPPB`, `getRecPPQ` / `setRecPPQ`, `setNumerator` / `setDenominator`, `getUseMetronome`, `getPrecount`, `getChangedFlag`, `getVersion`, `dumpScoreLog`, `clearLog`, `safeToEdit`, `getProjectTitle` / `getProjectAuthor` / `getProjectGenre`

*Deprecation note (manual):* `processRECEvent` marked deprecated in newer API versions — prefer module-specific setters where possible.

### `launchMapPages` (core)

`init`, `createOverlayMap`, `length`, `updateMap`, `getMapItemColor`, `getMapCount`, `getMapItemChannel`, `getMapItemAftertouch`, `processMapItem`, `releaseMapItem`, `checkMapForHiddenItem`, `setMapItemTarget`

### `ui` (grouped core)

- **Jog / strip:** `jog`, `jog2`, `strip`, `stripJog`, `stripHold`, `moveJog`
- **Navigation / edit:** `previous`, `next`, `up` / `down` / `left` / `right`, `horZoom`, `verZoom`, `snapOnOff`, `cut`, `copy`, `paste`, `insert`, `delete`, `enter`, `escape`, `yes`, `no`
- **Hints:** `getHintMsg`, `setHintMsg`, `getHintValue`, `getTimeDispMin`, `setTimeDispMin`
- **Windows:** `getVisible`, `showWindow`, `hideWindow`, `getFocused`, `setFocused`, `getFocusedFormCaption`, `getFocusedFormID`, `getFocusedPluginName`, `scrollWindow`, `nextWindow`, `selectWindow`, `launchAudioEditor`, `openEventEditor`, `showPicker`
- **Menus / helpers:** `isInPopupMenu`, `closeActivePopupMenu`, `isClosing`, metronome / precount / loop-rec getters, `getSnapMode` / `setSnapMode` / `snapMode`, `getStepEditMode` / `setStepEditMode`, `getProgTitle`, `getVersion`, `crDisplayRect`, `miDisplayRect`, `miDisplayDockRect`
- **Browser:** `navigateBrowser`, `toggleBrowserNode`, `navigateBrowserTabs`, `selectBrowserMenuItem`, `previewBrowserMenuItem`, `getFocusedNodeFileType`, `getFocusedNodeCaption`, `isBrowserAutoHide`, `setBrowserAutoHide`

---

## `eventData` (MIDI callback argument)

Writable / readable fields include: `handled`, `status`, `data1`, `data2`, `note`, `velocity`, `pressure`, `progNum`, `controlNum`, `controlVal`, `pitchBend`, `sysex`, `isIncrement`, `res`, `inEv`, `outEv`, `midiId`, `midiChan`, `midiChanEx`, `pmeflags`, `timestamp`, `port`, … (see manual table).

---

## `midi` constants — high-signal groups

Full tables live in the official manual; this repo uses many of these names in scripts.

### `OnRefresh` flags (`HW_Dirty_*`)

Examples: `HW_Dirty_Mixer_Sel`, `HW_Dirty_Mixer_Display`, `HW_Dirty_Mixer_Controls`, `HW_Dirty_RemoteLinks`, `HW_Dirty_FocusedWindow`, `HW_Dirty_Performance`, `HW_Dirty_LEDs`, `HW_Dirty_RemoteLinkValues`, `HW_Dirty_Patterns`, `HW_Dirty_Tracks`, `HW_Dirty_ControlValues`, `HW_Dirty_Colors`, `HW_Dirty_Names`, `HW_Dirty_ChannelRackGroup`, `HW_ChannelEvent`

### Channel REC helpers

Examples: `REC_Chan_Vol`, `REC_Chan_Pan`, `REC_Chan_FCut`, `REC_Chan_FRes`, `REC_Chan_Pitch`, … — combine with `channels.getRecEventId(index)` per manual.

### Mixer REC helpers

Examples: `REC_Mixer_Vol`, `REC_Mixer_Pan`, `REC_Mixer_SS`, `REC_Mixer_EQ_*` — combine with `mixer.getTrackPluginId(index, 0)` per manual.

### REC flags

Examples: `REC_UpdateValue`, `REC_GetValue`, `REC_ShowHint`, `REC_UpdateControl`, `REC_FromMIDI`, `REC_Control`, `REC_MIDIController`, …

### Global transport (`FPT_*`, `GT_*`, `SS_*`)

Used with `transport.globalTransport` / `ui` navigation helpers — e.g. `FPT_Play`, `FPT_Stop`, `FPT_Record`, `FPT_Rewind`, `FPT_FastForward`, `FPT_Metronome`, `FPT_Overdub`, `GT_All`, `SS_Start`, `SS_Stop`, `PME_System`, `PME_FromMIDI`, …

### FL window IDs

`widMixer`, `widChannelRack`, `widPlaylist`, `widPianoRoll`, `widBrowser`, `widPlugin`, `widPluginEffect`, `widPluginGenerator`

### Other common enums

Live block / clip flags (`LB_*`, `TLC_*`), channel types (`CT_*`), snap modes (`Snap_*`), pickup modes (`PIM_*`), step params (`pPitch`, `pVelocity`, …), browser node types (`SBN_*`), undo flags (`UF_*`).

---

## Debugging

- **View → Script output:** shows script name, `init ok`, unhandled MIDI when logging.
- Reload script after edits without restarting FL (per manual).

---

*End of local reference. For authoritative signatures, defaults, and newly added API members, always reconcile with the [official MIDI Scripting page](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm).*
