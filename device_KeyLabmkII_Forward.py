# name= KeyLab mkII Forward (KeyLab mkII 61 · Port 0)

"""
[[
	Surface:	KeyLab mkII
	Original:	Farès MEZDOUR
	P Version:	Entkoppeltes Forward-Script für V-Collection / Analog Lab
]]
"""

# This script forwards CCs and Pitch Bend from the Keys Port (KeyLab mkII 61)
# to Port 10 so that Arturia V-Collection plugins receive hardware control data.
#
# Setup in FL Studio → Options → MIDI Settings:
#   Input:  "KeyLab mkII 61"
#   Script: "KeyLab mkII Forward (KeyLab mkII 61 · Port 0)"
#   Port:   0
#
# This script is INDEPENDENT — it does NOT import the main DAW script.

import ui
import midi
import device


# ---------------------------------------------------------------------------
#  V-Collection plugin names (forwarding only active when one is focused)
# ---------------------------------------------------------------------------
V_COLLECTION = {
    'Analog Lab V',
    'Analog Lab 4',
    'ARP 2600 V3',
    'B-3 V2',
    'Buchla Easel V',
    'Clavinet V',
    'CMI V',
    'CS-80 V3',
    'CZ V',
    'DX7 V',
    'Emulator II V',
    'Farfisa V',
    'Jun-6 V',
    'Jup-8 V4',
    'Matrix-12 V2',
    'Mellotron V',
    'Mini V3',
    'Modular V3',
    'OB-Xa V',
    'PatchWorks',
    'Piano V2',
    'Prophet V3',
    'SEM V2',
    'Solina V2',
    'Stage-73 V2',
    'SQ80 V',
    'Synclavier V',
    'Synthi V',
    'Synthopedia',
    'Vocoder V',
    'Vox Continental V2',
    'Wurli V2',
}


# ---------------------------------------------------------------------------
#  FL Studio Callbacks
# ---------------------------------------------------------------------------

def OnInit():
    print("### INIT KeyLab mkII Forward (Port 0) ###")


def OnDeInit():
    return


def OnMidiIn(event):
    """Intercept before FL processing: forward CCs/PB to port 10 for V-Collection."""
    focused_plugin = ui.getFocusedPluginName()
    is_vcol = focused_plugin in V_COLLECTION

    # Forward CC events when a V-Collection plugin is focused,
    # and always forward Pitch Bend (0xE0) for expression control.
    if (event.status == midi.MIDI_CONTROLCHANGE and is_vcol) or event.status == 0xE0:
        msg = event.status + (event.data1 << 8) + (event.data2 << 16) + (10 << 24)
        device.forwardMIDICC(msg, 2)

    # Let FL Studio handle the event normally as well
    event.handled = False


def OnMidiMsg(event):
    event.handled = False
