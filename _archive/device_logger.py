# name=Arturia Keylab mkII - Logger
import midi
import ui
import device

def OnInit():
    port_name = device.getName()
    print(f"--- Markdown-Logger gestartet fuer: {port_name} ---")

def OnMidiMsg(event):
    event.handled = True 
    port_name = device.getName()
    
    # Port grob zuordnen für die Tabelle (MIDIIN2/DAW vs Keys)
    port_short = "DAW" if "MIDIIN2" in port_name or "DAW" in port_name else "Keys"
    
    msg_type = "Unbekannt"
    if event.status >= 0x80 and event.status <= 0x8F:
        msg_type = "Note Off"
    elif event.status >= 0x90 and event.status <= 0x9F:
        msg_type = "Note On "
    elif event.status >= 0xA0 and event.status <= 0xAF:
        msg_type = "PolyAft " # Polyphonic Aftertouch der Pads!
    elif event.status >= 0xB0 and event.status <= 0xBF:
        msg_type = "CC      "
    elif event.status >= 0xE0 and event.status <= 0xEF:
        msg_type = "PitchBnd"

    channel = (event.status & 0x0F) + 1

    # Nur "Note On", CCs, PitchBend und PolyAft anzeigen, um Spam durch "Note Off" zu vermeiden
    if msg_type != "Note Off":
        # Hier ist die Magie: Es druckt eine fertige Markdown-Zeile!
        print(f"| ??? | {port_short} | {msg_type} | {event.data1:3} | (Wert/Vel: {event.data2:3}, Kanal: {channel:02}) |")

def OnSysEx(event):
    event.handled = True
    port_name = device.getName()
    print(f"| SysEx | {port_name} | - | - | {event.sysex} |")