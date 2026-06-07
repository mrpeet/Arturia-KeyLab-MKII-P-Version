# name= KeyLab mkII P Version (MIDIIN2 · Port 1)

"""
[[
	Surface:	KeyLab mkII
	Original:	Farès MEZDOUR
	Display/Dispatch: Ray Juang (MIT License, 2020)
	P Version:	Refactored modular rewrite
]]
"""

import time
import ui
import channels
import mixer
import patterns
import midi
from keylab_display import KeyLabDisplay
from keylab_pages import KeyLabPagedDisplay
from keylab_dispatch import send_to_device
from keylab_state import KeyLabState
from keylab_transport import handle_transport
from keylab_daw_commands import handle_daw_commands
from keylab_navigation import handle_navigation
from keylab_mixer import (
    handle_mixer,
    handle_free_fader,
    handle_free_encoder,
    reset_soft_pickup_on_focus_change,
    reset_fader_state,
)
from keylab_plugin import handle_plugin_encoder, handle_plugin_special_jog
from keylab_feedback import (
    update_all_feedback,
    update_refresh_feedback,
    update_transport_leds,
    tick_feedback_idle,
    update_track_button_leds,
    clear_all_leds,
)
import keylab_long_press

# Set True only while debugging MIDI routing in Script Output
_DEBUG_MIDI = False


# ---------------------------------------------------------------------------
#  Global instances (created in OnInit)
# ---------------------------------------------------------------------------
_state = None       # type: KeyLabState
_display = None     # type: KeyLabDisplay
_pages = None       # type: KeyLabPagedDisplay

_boot_time_ms = 0.0
_boot_leds_refreshed = False


# ---------------------------------------------------------------------------
#  FL Studio Callbacks
# ---------------------------------------------------------------------------

def OnInit():
    global _state, _display, _pages, _boot_time_ms, _boot_leds_refreshed
    _state = KeyLabState()
    _display = KeyLabDisplay()
    _pages = KeyLabPagedDisplay(_display)
    
    _boot_time_ms = time.monotonic() * 1000.0
    _boot_leds_refreshed = False

    print("### INIT KEYLAB mkII P Version ###")

    # Welcome message on LCD
    _sync_main_display()
    _pages.SetPageLines('welcome', line1='KeyLab mkII', line2=ui.getProgTitle())
    _pages.SetActivePage('welcome', expires=1500)
    _pages.SetActivePage('main')

    reset_fader_state(_state)
    update_all_feedback(_state)

    print("### KeyLab mkII P Version ready ###")


def OnDeInit():
    _pages.SetPageLines('goodbye', line1='KeyLab mkII', line2='Disconnected')
    _pages.SetActivePage('goodbye')
    clear_all_leds()


def OnMidiMsg(event):
    """Central dispatcher — routes MIDI events through the handler chain.

    Order: Free Encoder (modifies to absolute) → Transport → DAW Commands → Navigation → Plugin → Mixer
    First handler that returns True wins; unhandled events are logged.
    """
    if _DEBUG_MIDI and event.midiId == midi.PITCH_BEND_STATUS:
        print("DEBUG: Fader chan=%d data1=%d data2=%d" % (event.midiChan, event.data1, event.data2))

    # --- Free Mode: Jitter-filtered fader passthrough (must be first) ---
    free_fader = handle_free_fader(event, _state)
    if free_fader == 1:
        event.handled = False  # Pass filtered Pitch Bend to FL Studio
        return
    if free_fader == 2:
        event.handled = True   # Swallow jitter in Free Mode
        return

    # --- Free Mode: Convert relative encoders to absolute ---
    if handle_free_encoder(event, _state):
        event.handled = False  # Pass modified absolute event to FL Studio
        return

    # --- Handler chain ---
    if handle_transport(event, _state, _pages):
        event.handled = True
        return

    if handle_daw_commands(event, _state, _pages):
        event.handled = True
        return

    if handle_navigation(event, _state, _pages):
        event.handled = True
        return

    if handle_plugin_encoder(event, _state, _pages):
        event.handled = True
        return

    if handle_mixer(event, _state, _pages):
        event.handled = True
        return

    # Note: Pad events (Channel 10, Notes 36-51) arrive on the Keys port and
    # are transposed by device_KeyLabmkII_Forward.py based on pad_mode +
    # pad_bank_offset stored in keylab_shared_state. They never reach this
    # script (DAW port).

    if _DEBUG_MIDI:
        print("MIDI | id: %d  data1: %d  data2: %d  chan: %d  port: %d" % (
            event.midiId, event.data1, event.data2, event.midiChan, event.port))


def OnRefresh(flags):
    """Called by FL Studio when internal state changes (play/stop/record/etc.)."""
    _sync_main_display()
    update_refresh_feedback(_state, flags)
    # HW_Dirty_Mixer_Sel (1): mixer track selected (e.g. mouse click) — update LEDs immediately
    if flags & 1:
        _sync_bank()
        update_track_button_leds(_state)


def OnDirtyMixerTrack(index):
    """Called when a mixer track changes (name, color, mute, solo, etc.)."""
    if _state is not None:
        _sync_bank()
        update_track_button_leds(_state)


def OnDirtyChannel(index, flag):
    """Called when a channel changes. flag=4 (CE_Select) = channel was selected."""
    if _state is not None:
        _sync_bank()
        update_track_button_leds(_state)


def OnIdle():
    global _boot_leds_refreshed
    if not _boot_leds_refreshed and _state is not None:
        if (time.monotonic() * 1000.0) - _boot_time_ms > 1500.0:
            update_all_feedback(_state)
            _boot_leds_refreshed = True

    _pages.Refresh()
    keylab_long_press.poll()
    _update_plugin_mode()
    _sync_bank()
    reset_soft_pickup_on_focus_change(_state)
    tick_feedback_idle(_state)


def OnUpdateBeatIndicator(value):
    """Beat indicator: 0=off, 1=beat, 2=bar."""
    update_transport_leds(beat_value=value)


def OnSysEx(event):
    # Swallow inbound SysEx to avoid feedback / re-detection loops
    if _DEBUG_MIDI:
        print("DEBUG SysEx: " + str(event.sysex)[:50] + "...")
    event.handled = True


# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------

def _update_plugin_mode():
    """Auto-detect plugin focus and toggle plugin_mode in state."""
    if _state.free_mode:
        return  # Free Mode overrides everything — no auto plugin detection
    import plugins as _plugins
    focused = ui.getFocused(midi.widPlugin)
    if focused != _state.plugin_mode:
        _state.plugin_mode = focused
        if focused:
            try:
                name = _plugins.getPluginName(channels.channelNumber())
            except Exception:
                name = "Plugin"
            _pages.SetPageLines('plugin', line1=name, line2='Plugin Mode')
            _pages.SetActivePage('plugin', expires=1200)


def _sync_bank():
    """Auto-sync bank offset to selected mixer track or channel so it's always visible.

    When mixer or channel rack is focused and a track/channel is selected,
    automatically switch to the correct bank so it is on faders 1-8.
    """
    target_bank = _state.bank_offset

    if ui.getFocused(midi.widMixer):
        current_track = mixer.trackNumber()
        if current_track > 0:  # Master (0) is always on fader 9
            target_bank = (current_track - 1) // 8
    else:
        # Channel Rack or other windows (fallback to Channel Rack)
        current_ch = channels.channelNumber()
        target_bank = current_ch // 8

    if target_bank != _state.bank_offset:
        _state.bank_offset = target_bank
        reset_fader_state(_state)
        from keylab_feedback import update_track_button_leds
        update_track_button_leds(_state)


def _sync_main_display():
    """Update the persistent 'main' page with current channel/pattern info."""
    active_index = channels.channelNumber()
    channel_name = channels.getChannelName(active_index)
    pattern_number = patterns.patternNumber()
    pattern_name = patterns.getPatternName(pattern_number)

    tag = '--'
    try:
        if ui.getFocused(midi.widMixer):
            tag = 'Mx'
        elif ui.getFocused(midi.widChannelRack):
            tag = 'CR'
        elif ui.getFocused(midi.widPlugin):
            tag = 'PI'
        elif ui.getFocused(midi.widBrowser):
            tag = 'BR'
    except Exception:
        pass

    _pages.SetPageLines(
        'main',
        line1='%s %d-%s' % (tag, active_index + 1, channel_name),
        line2='%s' % pattern_name)
