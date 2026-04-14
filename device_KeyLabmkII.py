# name= KeyLab mkII P Version

"""
[[
	Surface:	KeyLab mkII
	Original:	Farès MEZDOUR
	Display/Dispatch: Ray Juang (MIT License, 2020)
	P Version:	Refactored modular rewrite
]]
"""

import ui
import channels
import patterns

from keylab_display import KeyLabDisplay
from keylab_pages import KeyLabPagedDisplay
from keylab_dispatch import send_to_device
from keylab_state import KeyLabState


# ---------------------------------------------------------------------------
#  Global instances (created in OnInit)
# ---------------------------------------------------------------------------
_state = None       # type: KeyLabState
_display = None     # type: KeyLabDisplay
_pages = None       # type: KeyLabPagedDisplay


# ---------------------------------------------------------------------------
#  FL Studio Callbacks
# ---------------------------------------------------------------------------

def OnInit():
    global _state, _display, _pages
    _state = KeyLabState()
    _display = KeyLabDisplay()
    _pages = KeyLabPagedDisplay(_display)

    print("### INIT KEYLAB mkII P Version ###")

    # Welcome message on LCD
    _sync_main_display()
    _pages.SetPageLines('welcome', line1='KeyLab mkII', line2=ui.getProgTitle())
    _pages.SetActivePage('welcome', expires=1500)
    _pages.SetActivePage('main')

    print("### KeyLab mkII P Version ready ###")


def OnDeInit():
    _pages.SetPageLines('goodbye', line1='KeyLab mkII', line2='Disconnected')
    _pages.SetActivePage('goodbye')
    # Turn off all LEDs
    send_to_device(bytes([0x02, 0x7D, 0x7D, 0x0B, 0x00]))


def OnMidiMsg(event):
    # Skeleton: log all unhandled events for development
    print("MIDI | id: %d  data1: %d  data2: %d  chan: %d  port: %d" % (
        event.midiId, event.data1, event.data2, event.midiChan, event.port))


def OnRefresh(flags):
    _sync_main_display()


def OnIdle():
    _pages.Refresh()


def OnUpdateBeatIndicator(value):
    pass  # LED feedback will be added in Iteration 2


def OnSysEx(event):
    print("SysEx: " + str(event.sysex))


# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------

def _sync_main_display():
    """Update the persistent 'main' page with current channel/pattern info."""
    active_index = channels.selectedChannel()
    channel_name = channels.getChannelName(active_index)
    pattern_number = patterns.patternNumber()
    pattern_name = patterns.getPatternName(pattern_number)

    _pages.SetPageLines(
        'main',
        line1='%d - %s' % (active_index + 1, channel_name),
        line2='%s' % pattern_name)
