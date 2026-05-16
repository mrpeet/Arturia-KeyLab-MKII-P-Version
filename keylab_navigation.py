# KeyLab mkII — Navigation Handler
# Handles: Jog Wheel (context-sensitive), Bank Left/Right, Window switching
# Phase 7 — see ROADMAP.md

import channels
import midi
import mixer
import patterns
import plugins
import ui

from keylab_config import (
    Navigation,
    NOTE_ON_STATUS,
    NOTE_OFF_STATUS,
    CC_STATUS,
)
from keylab_plugin import handle_plugin_special_jog


# ---------------------------------------------------------------------------
#  Jog Wheel CC values (relative encoding)
# ---------------------------------------------------------------------------
# KeyLab jog wheel sends relative values:
#   1-63   = increment (right turn), speed = value (1=slow, 63=fast)
#   64-127 = decrement (left turn), speed = value - 64 (64=slow, 127=fast)
_JOG_RIGHT_MAX = 63
_JOG_LEFT_BASE = 64


# ---------------------------------------------------------------------------
#  Main dispatcher
# ---------------------------------------------------------------------------

def handle_navigation(event, state, pages):
    """Route navigation events (Jog CC, Jog Click, Bank buttons).

    Returns True if handled, False otherwise.
    """
    # --- Jog Wheel (CC 60) ---
    if event.midiId == CC_STATUS and event.midiChan == 0 and event.data1 == Navigation.JOG_WHEEL_CC:
        if handle_plugin_special_jog(event, state, pages):
            return True
        _do_jog(event, pages, state)
        event.handled = True
        return True

    # --- Note On / Note Off: Jog Click + Bank buttons ---
    if event.midiId in (NOTE_ON_STATUS, NOTE_OFF_STATUS) and event.midiChan == 0:
        if event.data1 == Navigation.JOG_WHEEL_CLICK:
            if event.data2 > 0:
                _do_jog_click(event, pages)
            event.handled = True
            return True

        if event.data1 == Navigation.BANK_LEFT:
            if event.data2 > 0:
                _do_bank(event, state, pages, direction=-1)
            event.handled = True
            return True

        if event.data1 == Navigation.BANK_RIGHT:
            if event.data2 > 0:
                _do_bank(event, state, pages, direction=1)
            event.handled = True
            return True

    return False


# ---------------------------------------------------------------------------
#  Jog Wheel — context-sensitive
# ---------------------------------------------------------------------------

def _do_jog(event, pages, state):
    """Route jog wheel to context-sensitive navigation action."""
    # Determine direction and speed from relative value
    if event.data2 <= _JOG_RIGHT_MAX:
        direction = 1  # Right
    else:
        direction = -1  # Left

    if ui.getFocused(midi.widBrowser):
        # Browser → navigate items
        if ui.isInPopupMenu():
            if direction < 0:
                ui.up()
            else:
                ui.down()
        else:
            if direction < 0:
                ui.previous()
            else:
                ui.next()
        _show_hint(pages, ui.getFocusedNodeCaption())
        return

    if ui.getFocused(midi.widMixer):
        # Mixer focused → select tracks
        current = mixer.trackNumber()
        new_track = max(0, current + direction)
        mixer.setTrackNumber(new_track)
        # Auto-sync bank so the selected track is visible on faders
        if new_track > 0:
            target_bank = (new_track - 1) // 8
            if target_bank != state.bank_offset:
                state.bank_offset = target_bank
                _show_hint(pages, "Bank %d: %s" % (target_bank + 1, mixer.getTrackName(new_track)))
            else:
                _show_hint(pages, mixer.getTrackName(new_track))
        else:
            _show_hint(pages, mixer.getTrackName(new_track))
        return

    # Default: Channel Rack / anything else → select channels
    if direction < 0:
        ui.previous()
    else:
        ui.next()


# ---------------------------------------------------------------------------
#  Jog Click — context-sensitive window switch
# ---------------------------------------------------------------------------

def _do_jog_click(event, pages):
    """Jog push: context-sensitive window action."""
    if ui.getFocused(midi.widChannelRack):
        # Channel Rack → open plugin editor for selected channel
        channels.showEditor(channels.channelNumber(), 1)
        _show_hint(pages, "Open Plugin")

    elif ui.getFocused(midi.widPlugin):
        # Plugin open → close it, return to Channel Rack
        channels.showEditor(channels.channelNumber(), 0)
        ui.showWindow(midi.widChannelRack)
        _show_hint(pages, "Close Plugin")

    elif ui.getFocused(midi.widMixer):
        # Mixer → arm the selected track
        track = mixer.trackNumber()
        mixer.armTrack(track)
        _show_hint(pages, "Arm: " + mixer.getTrackName(track))

    elif ui.getFocused(midi.widBrowser):
        # Browser → folder: toggle open/close; file: load/select
        node_type = ui.getFocusedNodeFileType()
        if node_type == -1:
            return  # Nothing focused
        elif node_type <= -100:
            ui.toggleBrowserNode()  # Folder → expand/collapse
        else:
            ui.selectBrowserMenuItem()  # File → load
        _show_hint(pages, ui.getFocusedNodeCaption())

    else:
        # Fallback → cycle to next window
        ui.nextWindow()
        _show_hint(pages, "Window")


# ---------------------------------------------------------------------------
#  Bank Left / Right — context-sensitive
# ---------------------------------------------------------------------------

def _do_bank(event, state, pages, direction):
    """Bank buttons: context-sensitive pattern/preset/browser navigation."""
    if ui.getFocused(midi.widPlugin):
        # Plugin focused → cycle presets
        ch = channels.channelNumber()
        if direction > 0:
            plugins.nextPreset(ch)
            _show_hint(pages, "Next Preset")
        else:
            plugins.prevPreset(ch)
            _show_hint(pages, "Prev Preset")

    elif ui.getFocused(midi.widBrowser):
        # Browser focused → navigate browser tabs
        try:
            if direction > 0:
                ui.navigateBrowserTabs(midi.FPT_Right)
                _show_hint(pages, "Browser ->")
            else:
                ui.navigateBrowserTabs(midi.FPT_Left)
                _show_hint(pages, "Browser <-")
        except AttributeError:
            if direction > 0:
                ui.next()
            else:
                ui.previous()

    elif ui.getFocused(midi.widMixer):
        # Mixer → move between mixer tracks
        current = mixer.trackNumber()
        new_track = max(0, min(mixer.getTrackCount() - 1, current + direction))
        mixer.setTrackNumber(new_track)
        _show_hint(pages, mixer.getTrackName(new_track))

    else:
        # Default → jump patterns
        current = patterns.patternNumber()
        target = max(1, current + direction)
        patterns.jumpToPattern(target)
        _show_hint(pages, patterns.getPatternName(target))


# ---------------------------------------------------------------------------
#  Display helper
# ---------------------------------------------------------------------------

def _show_hint(pages, text):
    """Show navigation hint on LCD for 1 second."""
    pages.SetPageLines('nav', line1='Nav', line2=text if text else '')
    pages.SetActivePage('nav', expires=1000)
