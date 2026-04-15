# KeyLab mkII — Transport Handler
# Handles: Play, Stop, Record, Loop, Rewind, FastForward
# Phase 5 — see ROADMAP.md

import transport
import midi

from keylab_config import Transport, NOTE_ON_STATUS, NOTE_OFF_STATUS, PRESSED, RELEASED


# ---------------------------------------------------------------------------
#  Transport button handlers
# ---------------------------------------------------------------------------

def handle_transport(event, state, pages):
    """Route a Note On event to the correct transport action.

    Args:
        event:  FL eventData (midiId, data1, data2, ...)
        state:  KeyLabState instance
        pages:  KeyLabPagedDisplay instance

    Returns:
        True if the event was handled, False otherwise.
    """
    # Only respond to Note On on channel 1 (midiChan 0)
    if event.midiId not in (NOTE_ON_STATUS, NOTE_OFF_STATUS) or event.midiChan != 0:
        return False

    if event.data1 not in Transport.ALL_NOTES:
        return False

    # Transport buttons: consume BOTH press and release to prevent leaking
    # Only act on press (data2 > 0), except Rewind/FastForward which need release too
    if event.data1 == Transport.PLAY:
        if event.data2 == PRESSED:
            _do_play(event, pages)
    elif event.data1 == Transport.STOP:
        if event.data2 == PRESSED:
            _do_stop(event, pages)
    elif event.data1 == Transport.RECORD:
        if event.data2 == PRESSED:
            _do_record(event, pages)
    elif event.data1 == Transport.LOOP:
        if event.data2 == PRESSED:
            _do_loop(event, pages)
    elif event.data1 == Transport.REWIND:
        _do_rewind(event, pages)
    elif event.data1 == Transport.FAST_FWD:
        _do_fast_forward(event, pages)
    else:
        return False

    event.handled = True
    return True


# ---------------------------------------------------------------------------
#  Individual transport actions
# ---------------------------------------------------------------------------

def _do_play(event, pages):
    """Toggle playback."""
    transport.start()
    _show_hint(pages, "Play" if transport.isPlaying() else "Paused")


def _do_stop(event, pages):
    """Stop playback. Double-click returns to start."""
    transport.stop()
    _show_hint(pages, "Stop")


def _do_record(event, pages):
    """Toggle recording."""
    transport.record()
    _show_hint(pages, "Record" if transport.isRecording() else "Rec Off")


def _do_loop(event, pages):
    """Toggle loop/pattern mode."""
    transport.globalTransport(midi.FPT_LoopRecord, 1)
    mode = "Pattern" if transport.getLoopMode() else "Song"
    _show_hint(pages, "Loop: " + mode)


def _do_rewind(event, pages):
    """Continuous rewind while held, stop on release."""
    if event.data2 == PRESSED:
        transport.continuousMove(-1, midi.SS_Start)
        _show_hint(pages, "<< Rewind")
    else:
        transport.continuousMove(-1, midi.SS_Stop)


def _do_fast_forward(event, pages):
    """Continuous fast-forward while held, stop on release."""
    if event.data2 == PRESSED:
        transport.continuousMove(1, midi.SS_Start)
        _show_hint(pages, ">> Forward")
    else:
        transport.continuousMove(1, midi.SS_Stop)


# ---------------------------------------------------------------------------
#  Display helper
# ---------------------------------------------------------------------------

def _show_hint(pages, text):
    """Show a transport action hint on the LCD for 1 second."""
    pages.SetPageLines('transport', line1='Transport', line2=text)
    pages.SetActivePage('transport', expires=1000)
