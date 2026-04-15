# KeyLab mkII — DAW Commands Handler
# Handles: Snap, NewPattern, FocusMixer, Undo/Cut, Metronome, Overdub, TapTempo, Redo
# Phase 6 — see ROADMAP.md

import time

import general
import midi
import patterns
import transport
import ui

from keylab_config import (
    TrackControl,
    GlobalControl,
    NOTE_ON_STATUS,
    NOTE_OFF_STATUS,
    PRESSED,
    RELEASED,
)


# ---------------------------------------------------------------------------
#  Long-Press Detection State (for Undo/Cut)
# ---------------------------------------------------------------------------
_undo_press_start = 0.0
_LONG_PRESS_THRESHOLD = 1.0  # seconds


# ---------------------------------------------------------------------------
#  Main dispatcher
# ---------------------------------------------------------------------------

def handle_daw_commands(event, state, pages):
    """Route Note On events to DAW command actions.

    Returns True if handled, False otherwise.
    """
    global _undo_press_start

    if event.midiId not in (NOTE_ON_STATUS, NOTE_OFF_STATUS) or event.midiChan != 0:
        return False

    # Track Controls (Row 1 buttons)
    # Note: We handle BOTH press (data2>0) and release (data2==0) to prevent
    # Note Off events from leaking to the Channel Rack when dialogs block
    if event.data1 == TrackControl.RECORD:
        if event.data2 > 0:
            _do_snap_toggle(event, pages)
        return True  # Always consume to prevent note leaking

    if event.data1 == TrackControl.SOLO:
        if event.data2 > 0:
            _do_new_pattern(event, pages)
        return True

    if event.data1 == TrackControl.MUTE:
        if event.data2 > 0:
            _do_focus_mixer(event, pages)
        return True

    if event.data1 == TrackControl.READ:
        if event.data2 > 0:
            _do_tap_tempo(event, pages)
        return True

    if event.data1 == TrackControl.WRITE:
        if event.data2 > 0:
            _undo_press_start = time.time()
        else:
            _do_undo_or_cut(event, pages)
        return True

    # Global Controls (Row 2 buttons)
    if event.data1 == GlobalControl.SAVE:
        if event.data2 > 0:
            _do_toggle_browser_cr(event, pages)
        return True

    if event.data1 == GlobalControl.IN:
        if event.data2 > 0:
            _do_toggle_pad_mode(event, state, pages)
        return True

    if event.data1 == GlobalControl.OUT:
        if event.data2 > 0:
            _do_toggle_overdub(event, pages)
        return True

    if event.data1 == GlobalControl.METRO:
        if event.data2 > 0:
            _do_toggle_metronome(event, pages)
        return True

    if event.data1 == GlobalControl.UNDO:
        if event.data2 > 0:
            _do_redo(event, pages)
        return True

    return False


# ---------------------------------------------------------------------------
#  Individual actions
# ---------------------------------------------------------------------------

def _do_snap_toggle(event, pages):
    """Toggle snap mode on/off."""
    ui.snapOnOff()
    _show_hint(pages, "Snap: " + ("On" if ui.getSnapMode() else "Off"))


def _do_new_pattern(event, pages):
    """Create and jump to next empty pattern."""
    flags = _resolve_ffnep_no_prompt_flag()
    if flags is not None:
        patterns.findFirstNextEmptyPat(flags)
    else:
        # Fallback for FL versions without FFNEP no-prompt constants:
        # jump directly to a new pattern slot (default naming, no rename prompt).
        patterns.jumpToPattern(patterns.patternMax() + 1)
    _show_hint(pages, "New Pattern")


def _do_focus_mixer(event, pages):
    """Show and focus the mixer window."""
    ui.showWindow(midi.widMixer)
    _show_hint(pages, "Mixer")


def _do_tap_tempo(event, pages):
    """Tap tempo detection."""
    transport.globalTransport(midi.FPT_TapTempo, 1)
    _show_hint(pages, "Tap Tempo")


def _do_undo_or_cut(event, pages):
    """Short press = Undo, Long press (>1s) = Cut."""
    global _undo_press_start
    duration = time.time() - _undo_press_start

    if duration > _LONG_PRESS_THRESHOLD:
        # Long press = Cut
        _show_and_focus_channel_rack()
        ui.cut()
        _show_hint(pages, "Cut")
    else:
        # Short press = Undo
        general.undoUp()
        _show_hint(pages, "Undo")


def _do_toggle_browser_cr(event, pages):
    """Toggle between Browser and Channel Rack focus."""
    if ui.getFocused(midi.widBrowser):
        ui.showWindow(midi.widChannelRack)
        _show_hint(pages, "Channel Rack")
    else:
        ui.showWindow(midi.widBrowser)
        _show_hint(pages, "Browser")


def _do_toggle_pad_mode(event, state, pages):
    """Toggle between FPC and Chromatic pad modes."""
    if state.pad_mode == "fpc":
        state.pad_mode = "chromatic"
        _show_hint(pages, "Pads: Chromatic")
    else:
        state.pad_mode = "fpc"
        _show_hint(pages, "Pads: FPC")


def _do_toggle_overdub(event, pages):
    """Toggle overdub/loop record mode."""
    transport.globalTransport(midi.FPT_Overdub, 1)
    _show_hint(pages, "Overdub")


def _do_toggle_metronome(event, pages):
    """Toggle metronome on/off."""
    transport.globalTransport(midi.FPT_Metronome, 1)
    _show_hint(pages, "Metro: " + ("On" if ui.isMetronomeEnabled() else "Off"))


def _do_redo(event, pages):
    """Redo last undone action."""
    general.undoDown()
    _show_hint(pages, "Redo")


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
