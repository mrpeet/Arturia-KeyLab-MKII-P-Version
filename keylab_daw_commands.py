# KeyLab mkII — DAW Commands Handler
# Handles: Snap, NewPattern, PianoRoll, Redo/Cut, Metronome, Overdub, TapTempo, Undo
# Phase 6 — see ROADMAP.md

import general
import midi
import patterns
import time
import transport
import ui

from keylab_config import (
    TrackControl,
    GlobalControl,
    LiveBankButton,
    NOTE_ON_STATUS,
    NOTE_OFF_STATUS,
    PRESSED,
    RELEASED,
)
import keylab_shared_state as pad_state
import keylab_long_press as long_press
from keylab_feedback import update_daw_command_leds


# ---------------------------------------------------------------------------
#  Main dispatcher
# ---------------------------------------------------------------------------

def handle_daw_commands(event, state, pages):
    """Route Note On events to DAW command actions.

    Returns True if handled, False otherwise.
    """
    if event.midiId not in (NOTE_ON_STATUS, NOTE_OFF_STATUS) or event.midiChan != 0:
        return False

    # Track Controls (Row 1 buttons)
    # Note: We handle BOTH press (data2>0) and release (data2==0) to prevent
    # Note Off events from leaking to the Channel Rack when dialogs block
    if event.data1 == TrackControl.RECORD:
        if event.data2 > 0:
            _do_snap_toggle(event, pages)
        return True

    if event.data1 == TrackControl.SOLO:
        if event.data2 > 0:
            _do_new_pattern(event, pages)
        return True

    if event.data1 == TrackControl.MUTE:
        if event.data2 > 0:
            _do_toggle_piano_roll(event, pages)
        return True

    if event.data1 == TrackControl.READ:
        if event.data2 > 0:
            _do_tap_tempo(event, pages)
        return True

    if event.data1 == TrackControl.WRITE:
        if event.data2 > 0:
            long_press.begin('write_btn', on_long=lambda: _do_cut(pages), on_short=lambda: _do_redo(pages))
        else:
            long_press.release('write_btn')
        return True

    # Global Controls (Row 2 buttons)
    if event.data1 == GlobalControl.SAVE:
        if event.data2 > 0:
            _do_cycle_browser_cr_mixer(pages)
        return True

    if event.data1 == GlobalControl.IN:
        if event.data2 > 0:
            long_press.begin('in_btn', on_long=lambda: _do_toggle_pad_velocity(state, pages), on_short=lambda: _do_toggle_pad_mode(state, pages))
        else:
            long_press.release('in_btn')
        return True

    if event.data1 == GlobalControl.OUT:
        if event.data2 > 0:
            _do_overdub_press(state, pages)
        else:
            _do_overdub_release()
        return True

    if event.data1 == GlobalControl.METRO:
        if event.data2 > 0:
            _do_toggle_metronome(event, pages)
        return True

    if event.data1 == GlobalControl.UNDO:
        if event.data2 > 0:
            _do_undo(pages)
        return True

    # Live/Bank modifier buttons for pad bank navigation (only in Chromatic mode)
    if event.data1 == LiveBankButton.PREV:
        if event.data2 > 0:
            _do_pad_bank_prev(event, state, pages)
        return True

    if event.data1 == LiveBankButton.NEXT:
        if event.data2 > 0:
            _do_pad_bank_next(event, state, pages)
        return True

    return False


# ---------------------------------------------------------------------------
#  Individual actions
# ---------------------------------------------------------------------------

def _do_track_arm(event, pages):
    """Arm currently selected mixer track."""
    if ui.getFocused(midi.widMixer):
        import mixer
        track = mixer.trackNumber()
        mixer.armTrack(track)
        _show_hint(pages, "Track %d Arm" % track)


def _do_snap_toggle(event, pages):
    """Toggle snap mode."""
    ui.snapOnOff()
    SNAP_MODE = {
        0: 'Line',
        1: 'Cell',
        3: 'None',
        4: '1/6 Step',
        5: '1/4 Step',
        6: '1/3 Step',
        7: '1/2 Step', 
        8: 'Step',
        9: '1/6 Beat',
        10: '1/4 Beat',
        11: '1/3 Step',
        12: '1/2 Beat',
        13: 'Beat',
        14: 'Bar'
    }
    snap_mode = ui.getSnapMode()
    snap_str = SNAP_MODE.get(snap_mode, "Unknown")
    _show_hint(pages, "Snap: " + snap_str)
    update_daw_command_leds()


def _do_new_pattern(event, pages):
    """Create a new pattern without prompt."""
    flag = _resolve_ffnep_no_prompt_flag()
    if flag is not None:
        patterns.findFirstNextEmptyPat(flag)
    else:
        patterns.findFirstNextEmptyPat(1)
    pat_num = patterns.patternNumber()
    _show_hint(pages, "Pat %d" % pat_num)
    update_daw_command_leds()


def _do_tap_tempo(event, pages):
    """Trigger tap tempo."""
    transport.globalTransport(midi.FPT_TapTempo, 1)
    import mixer
    tempo = mixer.getCurrentTempo(1)
    _show_hint(pages, "Tempo: %d BPM" % tempo)
    update_daw_command_leds()


def _do_cycle_browser_cr_mixer(pages):
    """3-way toggle: Browser → Channel Rack → Mixer → Browser …"""
    if ui.getFocused(midi.widBrowser):
        ui.showWindow(midi.widChannelRack)
        ui.setFocused(midi.widChannelRack)
        _show_hint(pages, "Channel Rack")
    elif ui.getFocused(midi.widChannelRack):
        ui.showWindow(midi.widMixer)
        ui.setFocused(midi.widMixer)
        _show_hint(pages, "Mixer")
    else:
        ui.showWindow(midi.widBrowser)
        ui.setFocused(midi.widBrowser)
        _show_hint(pages, "Browser")


def _do_track_solo(event, pages):
    """Solo currently selected track/channel."""
    if ui.getFocused(midi.widMixer):
        import mixer
        mixer.soloTrack(mixer.trackNumber())
        _show_hint(pages, "Solo Track")
    else:
        import channels
        channels.soloChannel(channels.channelNumber())
        _show_hint(pages, "Solo Channel")


def _do_track_mute(event, pages):
    """Mute currently selected track/channel."""
    if ui.getFocused(midi.widMixer):
        import mixer
        mixer.muteTrack(mixer.trackNumber())
        _show_hint(pages, "Mute Track")
    else:
        import channels
        channels.muteChannel(channels.channelNumber())
        _show_hint(pages, "Mute Channel")


def _do_toggle_piano_roll(event, pages):
    """Toggle Piano Roll open/close for the currently selected channel.
    
    If Piano Roll is currently focused → close it (switch focus to Channel Rack).
    Otherwise → open Piano Roll.
    LED reflects state via update_daw_command_leds (100% open / 3% closed).
    """
    if ui.getFocused(midi.widPianoRoll):
        ui.showWindow(midi.widChannelRack)
        ui.setFocused(midi.widChannelRack)
        _show_hint(pages, "Piano Roll off")
    else:
        ui.showWindow(midi.widPianoRoll)
        ui.setFocused(midi.widPianoRoll)
        _show_hint(pages, "Piano Roll")
    update_daw_command_leds()


def _do_toggle_pattern_song(event, pages):
    """Toggle between Pattern and Song mode (kept for reference)."""
    new_mode = 1 if not transport.getLoopMode() else 0
    transport.setLoopMode(new_mode)
    mode_str = "Pattern" if new_mode else "Song"
    _show_hint(pages, mode_str)
    update_daw_command_leds()


def _do_undo(pages):
    """Undo button (GlobalControl.UNDO) = Undo."""
    general.undoUp()
    _show_hint(pages, "Undo")


def _do_redo(pages):
    """Short press on Write = Redo."""
    general.undoDown()
    _show_hint(pages, "Redo")


def _do_cut(pages):
    """Long press on Write = Cut (fires at threshold via OnIdle)."""
    _show_and_focus_channel_rack()
    ui.cut()
    _show_hint(pages, "Cut")


def _do_cycle_windows(pages):
    """Cycle focus between Channel Rack, Mixer, and Browser."""
    if ui.getFocused(midi.widChannelRack):
        ui.showWindow(midi.widMixer)
        ui.setFocused(midi.widMixer)
        _show_hint(pages, "Mixer")
    elif ui.getFocused(midi.widMixer):
        ui.showWindow(midi.widBrowser)
        ui.setFocused(midi.widBrowser)
        _show_hint(pages, "Browser")
    else:
        ui.showWindow(midi.widChannelRack)
        ui.setFocused(midi.widChannelRack)
        _show_hint(pages, "Channel Rack")


def _do_toggle_pad_mode(state, pages):
    """Toggle between Drum Map (GM drums, ch10) and Chromatic (C3+, ch1)."""
    if state.pad_mode == pad_state.PAD_MODE_FPC:
        state.pad_mode = pad_state.PAD_MODE_CHROMATIC
        _show_hint(pages, "Pads: Chromatic")
    else:
        state.pad_mode = pad_state.PAD_MODE_FPC
        _show_hint(pages, "Pads: Drum Map")
    pad_state.mark_pad_led_dirty()
    print("Pad mode -> %s (shared state + file)" % state.pad_mode)


def _do_toggle_pad_velocity(state, pages):
    """Toggle pad velocity sensitivity (off = fixed 75% MIDI velocity)."""
    state.pad_velocity_enabled = not state.pad_velocity_enabled
    label = "On" if state.pad_velocity_enabled else "Off"
    _show_hint(pages, "Pad Velo: " + label)
    print("Pad velocity -> %s (shared state + file)" % label)


# ---------------------------------------------------------------------------
#  Overdub — press/release pair + debounce
# ---------------------------------------------------------------------------

_OVERDUB_DEBOUNCE_MS = 200.0  # Minimum ms between toggles (prevents HW bounce)
_overdub_last_press_ms = 0.0


def _do_overdub_press(state, pages):
    """Note On: toggle overdub state + send FPT_Overdub press signal.

    FL Studio's globalTransport treats FPT_Overdub like a held button —
    it needs both press (value=1) AND release (value=0) to confirm the
    action reliably. Without the release, FL queues the command but may
    ignore it or fire it twice on the next unrelated event.

    A 200ms debounce prevents hardware button-bounce double-fires.
    """
    global _overdub_last_press_ms
    now_ms = time.monotonic() * 1000.0
    if now_ms - _overdub_last_press_ms < _OVERDUB_DEBOUNCE_MS:
        return  # Debounce: discard bounce / repeated press within window
    _overdub_last_press_ms = now_ms

    state.overdub_enabled = not state.overdub_enabled
    transport.globalTransport(midi.FPT_Overdub, 1)
    label = "Overdub On" if state.overdub_enabled else "Overdub Off"
    _show_hint(pages, label)
    update_daw_command_leds(state)


def _do_overdub_release():
    """Note Off: send FPT_Overdub release signal (value=0).

    This completes the press/release pair that FL Studio expects for
    globalTransport toggle commands to process cleanly.
    """
    transport.globalTransport(midi.FPT_Overdub, 0)


def _do_toggle_metronome(event, pages):
    """Toggle metronome on/off."""
    transport.globalTransport(midi.FPT_Metronome, 1)
    _show_hint(pages, "Metro: " + ("On" if ui.isMetronomeEnabled() else "Off"))
    update_daw_command_leds()




def _do_pad_bank_prev(event, state, pages):
    """Decrement pad bank offset (works in both Drum Map and Chromatic mode)."""
    if state.pad_bank_offset > 0:
        state.pad_bank_offset -= 1
    _show_pad_bank_hint(state, pages)


def _do_pad_bank_next(event, state, pages):
    """Increment pad bank offset (works in both Drum Map and Chromatic mode)."""
    if state.pad_bank_offset < state.pad_bank_count - 1:
        state.pad_bank_offset += 1
    _show_pad_bank_hint(state, pages)


def _show_pad_bank_hint(state, pages):
    """Show pad bank number and note range on display."""
    # Chromatic range starts at C3 (48); Drum Map uses GM drum notes in same span
    base_low = 48 + state.pad_bank_offset * 16
    base_high = 48 + 15 + state.pad_bank_offset * 16
    note_range = "(%s-%s)" % (_note_to_name(base_low), _note_to_name(base_high))
    pages.SetPageLines('padbank', line1='Pads: Bank %d' % (state.pad_bank_offset + 1), line2=note_range)
    pages.SetActivePage('padbank', expires=1500)


def _note_to_name(note_num):
    """Convert MIDI note number to note name (e.g., 60 -> 'C4')."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note_num // 12) - 2
    note_idx = note_num % 12
    return '%s%d' % (notes[note_idx], octave)


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

def _show_hint(pages, text):
    """Show a DAW command hint on the LCD for 1 second."""
    pages.SetPageLines('daw', line1='DAW', line2=text)
    pages.SetActivePage('daw', expires=1000)


def _show_and_focus_channel_rack():
    """Ensure Channel Rack is visible and focused."""
    ui.showWindow(midi.widChannelRack)


def _resolve_ffnep_no_prompt_flag():
    """Resolve FL constant for no-prompt new-pattern creation across versions."""
    candidate_names = (
        'FFNEP_DontPrompt',
        'FFNEP_DontPromptName',
        'FFNEP_DONTPROMPT',
        'FFNEP_DONTPROMPTNAME',
    )
    for name in candidate_names:
        if hasattr(midi, name):
            return getattr(midi, name)
    return None
