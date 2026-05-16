# KeyLab mkII — Plugin Parameter Handler
# Maps hardware encoders 1-8 to plugin parameters via plugin_database.py.
# Iteration 7 of Phase 5.

import plugins
import channels
import midi
import ui

from keylab_config import (
    Encoder,
    NOTE_ON_STATUS,
    NOTE_OFF_STATUS,
    CC_STATUS,
)
from plugin_database import (
    get_plugin_params,
    get_plugin_special,
    is_plugin_known,
    NOT_MAPPED,
)


# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------

# Relative encoder step size (fraction of 0.0–1.0 range per click)
ENCODER_STEP = 0.01
ENCODER_STEP_FINE = 0.002


# ---------------------------------------------------------------------------
#  Core handler: Encoder → Plugin Parameter
# ---------------------------------------------------------------------------

def handle_plugin_encoder(event, state, pages):
    """Handle an encoder CC event in plugin mode.

    Returns True if handled, False if the event should fall through (free mode).
    """
    if state.free_mode:
        return False  # Passthrough: let FL Studio handle it directly

    if not state.plugin_mode:
        return False

    # Determine which encoder (0–7)
    encoder_index = event.data1 - Encoder.FIRST
    if encoder_index < 0 or encoder_index > 7:
        return False  # Encoder 9 (master) not used for plugin macros

    # Detect focused plugin
    plugin_name = _get_focused_plugin_name()
    if plugin_name is None:
        return False

    # Look up in database
    params = get_plugin_params(plugin_name)
    if params is None:
        # Unknown plugin — block event and warn on LCD (do NOT fall through to Pan!)
        pages.SetPageLines('plugin', line1=plugin_name, line2='Not mapped!')
        pages.SetActivePage('plugin', expires=2000)
        event.handled = True
        return True

    # Get the parameter for this encoder slot
    if encoder_index >= len(params):
        return False

    param_index, param_name = params[encoder_index]
    if param_index == NOT_MAPPED:
        event.handled = True  # Swallow the event (slot not mapped)
        return True

    # Resolve channel index
    chan_index = channels.selectedChannel()

    # Compute new value from relative encoder movement
    # data2 0-63 = increment (right), 64-127 = decrement (left)
    if event.data2 <= Encoder.INCREMENT_MAX:
        direction = 1
        speed = max(1, event.data2) if event.data2 >= Encoder.INCREMENT_MIN else 1
    else:
        direction = -1
        speed = max(1, event.data2 - Encoder.DECREMENT_BASE)  # 64->0->1, 65->1, 127->63
    current_value = plugins.getParamValue(param_index, chan_index)
    step = ENCODER_STEP * speed
    new_value = max(0.0, min(1.0, current_value + direction * step))

    # Apply
    plugins.setParamValue(new_value, param_index, chan_index)

    # Cache for state
    if encoder_index < len(state.plugin_encoder_values):
        state.plugin_encoder_values[encoder_index] = new_value

    # Display feedback
    display_name = param_name if param_name else plugins.getParamName(param_index, chan_index)
    display_value = _format_value(new_value)
    pages.SetPageLines('plugin', line1=display_name, line2=display_value)
    pages.SetActivePage('plugin', expires=1500)

    event.handled = True
    return True


# ---------------------------------------------------------------------------
#  Special handler: Plugin-specific hardware bindings
# ---------------------------------------------------------------------------

def handle_plugin_special_jog(event, state, pages):
    """Handle jog wheel events for plugins with special jog bindings.

    Returns True if handled, False otherwise.
    """
    if not state.plugin_mode:
        return False

    plugin_name = _get_focused_plugin_name()
    if plugin_name is None:
        return False

    special = get_plugin_special(plugin_name)
    if special is None:
        return False

    jog_action = special.get("jog_wheel")
    if jog_action is None:
        return False

    chan_index = channels.selectedChannel()

    if jog_action == "preset_navigation":
        if event.data2 <= Encoder.INCREMENT_MAX:
            direction = 1
        else:
            direction = -1
        if direction > 0:
            plugins.nextPreset(chan_index)
        else:
            plugins.prevPreset(chan_index)

        # Display feedback
        preset_name = plugins.getName(chan_index)
        pages.SetPageLines('plugin', line1=plugin_name, line2=preset_name)
        pages.SetActivePage('plugin', expires=1500)

        event.handled = True
        return True

    return False


# ---------------------------------------------------------------------------
#  Plugin detection utility
# ---------------------------------------------------------------------------

def scan_plugin_params(max_params=30):
    """Debug helper: print all parameter names for the focused plugin.

    Call this from FL Studio Script Output to discover parameter indices
    for adding new plugins to plugin_database.py.
    """
    plugin_name = _get_focused_plugin_name()
    if plugin_name is None:
        print("[Plugin] No plugin focused")
        return

    chan_index = channels.selectedChannel()
    print("[Plugin] Scanning '%s' (channel %d):" % (plugin_name, chan_index))
    for i in range(max_params):
        try:
            name = plugins.getParamName(i, chan_index)
            value = plugins.getParamValue(i, chan_index)
            print("  [%3d] %-30s = %.4f" % (i, name, value))
        except Exception:
            break


# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------

def _get_focused_plugin_name():
    """Get the name of the currently focused plugin, or None."""
    try:
        if ui.getFocused(midi.widPlugin):
            return plugins.getPluginName(channels.selectedChannel())
    except Exception:
        pass
    return None


def _format_value(value):
    """Format a 0.0–1.0 parameter value as percentage string."""
    return "%d%%" % int(value * 100 + 0.5)
