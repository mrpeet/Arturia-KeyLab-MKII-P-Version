# name= Arturia Keylab mkII - Logger
import midi
import ui
import device

def OnInit():
    port_name = device.getName()
    print(f"--- Logger gestartet fuer Port: {port_name} ---")
    print("Druecke Tasten, Pads und bewege Fader...")

def OnMidiMsg(event):
    event.handled = True 
    port_name = device.getName()
    status_hex = hex(event.status)
    
    msg_type = "Unbekannt"
    if event.status >= 0x80 and event.status <= 0x8F:
        msg_type = "Note Off"
    elif event.status >= 0x90 and event.status <= 0x9F:
        msg_type = "Note On"
    elif event.status >= 0xB0 and event.status <= 0xBF:
        msg_type = "CC (Control Change)"
    elif event.status >= 0xE0 and event.status <= 0xEF:
        msg_type = "Pitch Bend"

    channel = (event.status & 0x0F) + 1

    print(f"[{port_name}] Kanal: {channel:02} | Typ: {msg_type:20} | Status: {status_hex} | Data1: {event.data1:3} | Data2: {event.data2:3}")

def OnSysEx(event):
    event.handled = True
    port_name = device.getName()
    print(f"[{port_name}] SysEx Nachricht empfangen: {event.sysex}")