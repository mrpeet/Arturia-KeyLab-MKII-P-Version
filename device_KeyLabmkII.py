# name= KeyLab mkII P Version (MIDIIN2 · Port 1)

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
from keylab_transport import handle_transport
from keylab_daw_commands import handle_daw_commands
from keylab_navigation import handle_navigation
from keylab_mixer import handle_mixer
from keylab_feedback import update_transport_leds, clear_all_leds


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

    # Sync transport LEDs to current FL state
    update_transport_leds()

    print("### KeyLab mkII P Version ready ###")


def OnDeInit():
    _pages.SetPageLines('goodbye', line1='KeyLab mkII', line2='Disconnected')
    _pages.SetActivePage('goodbye')
    clear_all_leds()


def OnMidiMsg(event):
    """Central dispatcher — routes MIDI events through the handler chain.

    Order: Transport → DAW Commands → Navigation → Mixer → Plugin
    First handler that returns True wins; unhandled events are logged.
    """
    # --- Handler chain (add new handlers here in order) ---
    if handle_transport(event, _state, _pages):
        event.handled = True
        return

    if handle_daw_commands(event, _state, _pages):
        event.handled = True
        return

    if handle_navigation(event, _state, _pages):
        event.handled = True
        return

    if handle_mixer(event, _state, _pages):
        event.handled = True
        return

    # --- Future handlers (uncomment as implemented) ---
    # if handle_plugin_encoder(event, _state, _pages):
    #     return

    # --- Unhandled: log for development ---
    print("MIDI | id: %d  data1: %d  data2: %d  chan: %d  port: %d" % (
        event.midiId, event.data1, event.data2, event.midiChan, event.port))


def OnRefresh(flags):
    """Called by FL Studio when internal state changes (play/stop/record/etc.)."""
    _sync_main_display()
    update_transport_leds()


def OnIdle():
    _pages.Refresh()


def OnUpdateBeatIndicator(value):
    """Beat indicator: 0=off, 1=beat, 2=bar."""
    update_transport_leds(beat_value=value)


def OnSysEx(event):
    # DEBUG: Log SysEx but don't process to avoid feedback loops
    # Some Arturia SysEx messages can trigger device re-detection
    print("DEBUG SysEx received: " + str(event.sysex)[:50] + "...")
    event.handled = True  # Mark as handled to stop propagation


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
