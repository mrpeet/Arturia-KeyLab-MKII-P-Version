# KeyLab mkII — Plugin Launch Shift Mode
# Maps Track Button 9 (Master) to Shift, allowing Track Buttons 1-8 to load plugins.

import ui
import midi
import channels
import plugins

from plugin_slots import MIXER_SLOTS, CHANNEL_SLOTS
from keylab_feedback import _send_rgb, update_track_button_leds

def get_slots(focus_mode):
    if focus_mode == 'mixer':
        return MIXER_SLOTS
    else:
        return CHANNEL_SLOTS

def on_shift_press(state, pages):
    """Activated when BTN9 is pressed."""
    state.plugin_shift_held = True
    state.plugin_shift_pending = None
    _send_rgb(0x2A, 31, 31, 31)  # Turn on master button LED bright white
    show_plugin_shift_leds()
    pages.SetPageLines('shift', line1='Plugin Mode', line2='Select Slot 1-8')
    pages.SetActivePage('shift', expires=2000)

def on_shift_release(state, pages):
    """Deactivated when BTN9 is released."""
    state.plugin_shift_held = False
    state.plugin_shift_pending = None
    update_track_button_leds(state)
    pages.SetActivePage('main')

def show_plugin_shift_leds():
    """Update track button LEDs with colors from plugin_slots."""
    focus_mode = 'mixer' if ui.getFocused(midi.widMixer) else 'channel_rack'
    slots = get_slots(focus_mode)
    
    # Track buttons 1-8 correspond to LED IDs 0x22 to 0x29
    for i in range(8):
        btn_id = 0x22 + i
        slot_data = slots.get(i)
        if slot_data:
            r, g, b = slot_data["color"]
            _send_rgb(btn_id, r, g, b)
        else:
            _send_rgb(btn_id, 0, 0, 0) # Off if unassigned

def on_track_button_shift(index, state, pages):
    """Handles pressing a track button 1-8 while shift is held."""
    focus_mode = 'mixer' if ui.getFocused(midi.widMixer) else 'channel_rack'
    slots = get_slots(focus_mode)
    
    slot_data = slots.get(index)
    if not slot_data:
        pages.SetPageLines('shift', line1='Empty Slot', line2='---')
        pages.SetActivePage('shift', expires=1500)
        return

    plugin_name = slot_data["name"]

    if state.plugin_shift_pending == index:
        # Confirm and load
        pages.SetPageLines('shift', line1=plugin_name, line2='Loading...')
        pages.SetActivePage('shift', expires=2000)
        
        _load_plugin(plugin_name, focus_mode)
        state.plugin_shift_pending = None
        # Briefly flash the button LED bright white to confirm
        _send_rgb(0x22 + index, 31, 31, 31)
    else:
        # Preview
        state.plugin_shift_pending = index
        pages.SetPageLines('shift', line1=plugin_name, line2='Press again')
        pages.SetActivePage('shift', expires=2000)
        
        # Redraw all LEDs to highlight the selected one
        for i in range(8):
            btn_id = 0x22 + i
            sd = slots.get(i)
            if sd:
                if i == index:
                    # Highlight selected (max brightness)
                    r, g, b = sd["color"]
                    _send_rgb(btn_id, min(31, r + 15), min(31, g + 15), min(31, b + 15))
                else:
                    # Dim others
                    r, g, b = sd["color"]
                    _send_rgb(btn_id, r // 3, g // 3, b // 3)
            else:
                _send_rgb(btn_id, 0, 0, 0)

def _load_plugin(plugin_name, focus_mode):
    """Attempts to load a plugin into the currently selected channel/track."""
    try:
        # Using plugins.loadPlugin requires the exact plugin name as registered in FL Studio.
        chan = channels.selectedChannel()
        channels.setChannelName(chan, plugin_name)
        plugins.loadPlugin(chan, plugin_name)
    except Exception as e:
        print("Failed to load plugin:", e)
