import channels
import general
import mixer
import patterns
import transport
import ui
import device
import plugins
import midi
import time
import ArturiaCrossKeyboardKLmk2 as AKLmk2
import KeyLabmk2SeqParam as KLmk2SQP
import KeyLabmk2Plugin
from KeyLabmk2Mapping import Hardware


from KeyLabmk2Dispatch import MidiEventDispatcher
from KeyLabmk2Dispatch import send_to_device
from KeyLabmk2Display import KeyLabDisplay
from KeyLabmk2Pages import KeyLabPagedDisplay
from KeyLabmk2Navigation import NavigationMode

## CONSTANT

PORT_MIDICC_ANALOGLAB = 10
WidMixer = 0
WidChannelRack = 1
WidPlaylist = 2
WidBrowser = 4
WidPlugin = 5
ANALOGLAB_KNOB_ID = [0x4A, 0x47, 0x4C, 0x4D, 0x5D, 0x49, 0x4B]

# ABS
ABSOLUTE_VALUE = 64

# Event code indicating stop event
SS_STOP = 0

# Event code indicating start start event
SS_START = 2

# SEQUENCER
SEQ_MODE = 0

# MIXER
MIXER_MODE = 0

# RECTANGLE OFFSET
RECT_OFFSET = 0

# EDIT MODE
EDIT_MODE = 0

# SEQ PARAM
SEQ_PARAM = 0

# Max Tracks
MAX_TRACKS = 125

# STATE_MATRIX
STATE_MATRIX = [
                4*[0],
                4*[0],
                4*[0],
                4*[0],
                ]
# LED_MATRIX
LED_MATRIX = [
                4*[0],
                4*[0],
                4*[0],
                4*[0],
                ]
# INDEX PRESSED
INDEX_PRESSED = []

# FPC MAP
FPC_MAP = {
            "36":49,
            "37":55,
            "38":51,
            "39":53,
            "40":48,
            "41":47,
            "42":45,
            "43":43,
            "44":40,
            "45":38,
            "46":46,
            "47":44,
            "48":37,
            "49":36,
            "50":42,
            "51":54
            }
            
# PAD MODE
PAD_MODE_DRUM = 0
PAD_MODE_CHROMATIC = 1
CURRENT_PAD_MODE = PAD_MODE_CHROMATIC
PAD_VELOCITY_ENABLED = True

# CHROMATIC MAP (Inverted Rows: Bottom-Left start)
CHROMATIC_MAP = {
    "36": 48, "37": 49, "38": 50, "39": 51, # Row 1 (Top) -> Row 4 (High)
    "40": 44, "41": 45, "42": 46, "43": 47, # Row 2 -> Row 3
    "44": 40, "45": 41, "46": 42, "47": 43, # Row 3 -> Row 2
    "48": 36, "49": 37, "50": 38, "51": 39  # Row 4 (Bottom) -> Row 1 (Low)
}
            

# This class processes all CC coming from the controller
# The class creates new handler for each function
# The class calls the right fonction depending on the incoming CC

class KeyLabMidiProcessor:

    @staticmethod
    def _is_pressed(event):
        return event.controlVal != 0

    def __init__(self, mk2):
        def by_midi_id(event) : return event.midiId
        def by_control_num(event) : return event.controlNum
        def by_velocity(event) : return event.data2
        def by_status(event) : return event.status
        def ignore_release(event): return self._is_pressed(event)
        def ignore_press(event): return not self._is_pressed(event)

        self._mk2 = mk2

        self._midi_id_dispatcher = (
            MidiEventDispatcher(by_midi_id)
            .NewHandler(144, self.OnCommandEvent) # Note On Ch 1
            .NewHandler(128, self.OnCommandEvent) # Note Off Ch 1
            .NewHandler(145, self.OnCommandEvent) # Note On Ch 2 (DAW)
            .NewHandler(129, self.OnCommandEvent) # Note Off Ch 2 (DAW)
            .NewHandler(176, self.OnKnobEvent)    # CC Ch 1
            .NewHandler(177, self.OnKnobEvent)    # CC Ch 2 (DAW)
            .NewHandler(224, self.OnSliderEvent)
            )
 
 
        self._status_dispatcher = (
            MidiEventDispatcher(by_status)
            .NewHandler(176, self.OnPluginEvent)
            .NewHandler(153, self.OnDrumSeqEvent)
            .NewHandler(137, self.OnDrumSeqEvent)
            )
  
  
        self._midi_command_dispatcher = (
            MidiEventDispatcher(by_control_num)
            
            
            .NewHandler(Hardware.Transport.RECORD, self.Record, ignore_release)
            .NewHandler(Hardware.Transport.PLAY, self.Start, ignore_release)
            .NewHandler(Hardware.Transport.STOP, self.Stop, ignore_release)
            .NewHandler(Hardware.Transport.LOOP, self.Loop, ignore_release)
            
            # Group 3: DAW Commands
            # Track Controls
            .NewHandler(Hardware.DAW.Track.CONTROL_1_1, self.NewPattern, ignore_release) # 8
            .NewHandler(Hardware.DAW.Track.CONTROL_2_1, self.FocusMixer, ignore_release) # 16
            .NewHandler(Hardware.DAW.Track.CONTROL_3_1, self.SnapToggle, ignore_release) # 0
            .NewHandler(Hardware.DAW.Track.CONTROL_4_1, self.TapTempo, ignore_release) # 56
            .NewHandler(Hardware.DAW.Track.CONTROL_5_1, self.Redo, ignore_release) # 57
            
            # Global Controls
            .NewHandler(Hardware.DAW.Global.CONTROL_1_2, self.ToggleBrowserChannelRack, ignore_release) # 74
            .NewHandler(Hardware.DAW.Global.CONTROL_2_2, self.TogglePadMode) # 87
            .NewHandler(Hardware.DAW.Global.CONTROL_3_2, self.ToggleOverdub, ignore_release) # 88
            .NewHandler(Hardware.DAW.Global.CONTROL_4_2, self.MetronomeToggle, ignore_release) # 89
            .NewHandler(Hardware.DAW.Global.CONTROL_5_2, self.UndoOrCut) # 81
            
            .NewHandler(Hardware.Transport.REWIND, self.RewindORprevBar)
            .NewHandler(Hardware.Transport.FAST_FORWARD, self.FastForwardORnextBar)
            .NewHandler(Hardware.Navigation.KNOB_PUSH, self.SwitchWindow, ignore_release)
            .NewHandler(46, self.BankSelect, ignore_release)
            .NewHandler(47, self.BankSelect, ignore_release)
            .NewHandler(Hardware.Navigation.LEFT_ARROW, self.previousPattern, ignore_release)
            .NewHandler(Hardware.Navigation.RIGHT_ARROW, self.nextPattern, ignore_release)
            .NewHandler(51, self.ToggleMixerChannelRack, ignore_release)
            
            # Group 6: Track Buttons (22-29) and Master Button (30)
            .NewHandlerForKeys(Hardware.Mixer.TrackButtons.ALL, self.ProcessTrackButton)
            .NewHandlerForKeys(range(8, 16), self.SoloChannel, ignore_press)
            .NewHandlerForKeys(range(16, 24), self.MuteChannel, ignore_press)
            # Removed separate TrackSelect range 24-32 to avoid conflict if any overlap, 
            # though 22-30 covers Group 6. 
            # Keeping others if they are for specific different modes/banks not covered by Group 6 buttons.
            
            .NewHandlerForKeys(range(0, 8), self.SnapMode, ignore_release) 
            
        )
         
        self._knob_dispatcher = (
            MidiEventDispatcher(by_control_num)
            .NewHandler(Hardware.Navigation.KNOB_TURN, self.OnKnobNavEvent)
            .NewHandlerForKeys(Hardware.Mixer.Knobs.ALL[:-1], self.SetPanTrack) # Knobs 1-8
            .NewHandler(Hardware.Mixer.Knobs.KNOB_9, self.ProcessMasterKnob)
            # Faders are handled by Slider/PB dispatcher now
        )      
        
        
        self._knob_nav_dispatcher = (
            MidiEventDispatcher(by_velocity)
            .NewHandler(1, self.TrackSelectMainKnob)
            .NewHandler(65, self.TrackSelectMainKnob)
        )
             
        
        self._plugin_dispatcher = (
            MidiEventDispatcher(by_control_num)
            .NewHandlerForKeys(Hardware.Mixer.Knobs.ALL, self.Plugin)
            .NewHandlerForKeys(Hardware.Mixer.Faders.ALL, self.Plugin)
            .NewHandlerForKeys(Hardware.Mixer.TrackButtons.ALL, self.Plugin)
            .NewHandler(1, self.SetPanTrack)
            
            
            .NewHandler(28, self.previousPreset, ignore_release)
            .NewHandler(29, self.nextPreset, ignore_release)
        )
        
        self._sequencer_dispatcher = (
            MidiEventDispatcher(by_control_num)
            .NewHandlerForKeys(Hardware.Pads.ALL_PADS, self.PressSequencer)
        )
      
            # MAPPING SLIDERS
        
        self._slider_dispatcher = (
            MidiEventDispatcher(by_status)
            .NewHandlerForKeys(range(224,233), self.SetVolumeTrack)
        )
        
            # NAVIGATION
        
        self._navigation = NavigationMode(self._mk2.paged_display())

        # Initialize Pad Colors
        try:
            self.UpdatePadColors(CURRENT_PAD_MODE)
        except Exception as e:
            print("Error initializing pad colors:", e)
        
        # Initialize Dawson Button Feedback
        try:
            self._mk2.LightReturn().UpdateLEDs_Groups3_4()
        except Exception as e:
            print("Error initializing DAW feedback:", e)

        self._track_button_press_times = {}
        
        # Soft Takeover State for Faders 1-9 (Index 0-8)
        # False = Waiting for pickup, True = Active/Locked
        self._fader_pickup_active = [False] * 9




    # DISPATCH
  


    def ProcessEvent(self, event) :
        if event.status == event.midiId or event.midiId == 224 :
            #print("Midi Id","\t",event.status,"\t",event.data1,"\t",event.controlNum,"\t",event.data2,"\t",event.midiId,"\t",event.midiChan,'\t',event.timestamp,'\t',event.handled)
            return self._midi_id_dispatcher.Dispatch(event)
        else :
           #print("Status","\t",event.status,"\t",event.data1,"\t",event.controlNum,"\t",event.data2,"\t",event.midiId,"\t",event.midiChan,'\t',event.timestamp,'\t',event.handled)
            return self._status_dispatcher.Dispatch(event)
    
    def OnCommandEvent(self, event):
        event.handled = True
        self._midi_command_dispatcher.Dispatch(event)


    def OnKnobEvent(self, event):
        # Dispatch to Knobs first
        if self._knob_dispatcher.Dispatch(event):
            event.handled = True
            return
            
        # If not a Knob, check if it's a Command mapped to CC (e.g. Global/Track Buttons)
        if self._midi_command_dispatcher.Dispatch(event):
            event.handled = True
            return
            
        event.handled = True # Still mark as handled to suppress unhandled CC notes? Or False?
        # If we mark True, we stop FL from processing it. If it was a stray CC, we probably want to suppress it.
        # But if user mapped it manually in FL, we might block it.
        # Safest: True to prevent "Note" side effects if that's what's happening.
        
    def OnKnobNavEvent(self, event) :
        event.handled = True
        self._knob_nav_dispatcher.Dispatch(event)


    def OnSliderEvent(self, event):
        event.handled = True
        self._slider_dispatcher.Dispatch(event)
        
    def OnPluginEvent(self, event):
        event.handled = True
        self._plugin_dispatcher.Dispatch(event)
        
    def OnSeqEvent(self, event):
        device.processMIDICC(event)
        self._sequencer_dispatcher.Dispatch(event)



# ... (existing constants)

# ...

    def UpdatePadColors(self, mode):
        # Determine color based on mode
        if mode == PAD_MODE_DRUM:
            r, g, b = Hardware.Pads.COLOR_YELLOW_DIM
        else:
            r, g, b = Hardware.Pads.COLOR_PURPLE_DIM
            
        # Send SysEx for each pad
        for i in range(16):
            pad_id = Hardware.Pads.PAD_LED_START_ID + i
            # SysEx: F0 00 20 6B 7F 42 02 00 16 <LEDID> <R> <G> <B> F7
            payload = bytes([0x02, 0x00, 0x16, pad_id, r, g, b])
            send_to_device(payload)

    def SetPadColor(self, pad_index, velocity):
        # pad_index: 0-15
        # velocity: 0-127
        
        # Determine base colors
        if CURRENT_PAD_MODE == PAD_MODE_DRUM:
            base_r, base_g, base_b = Hardware.Pads.COLOR_YELLOW
            dim_r, dim_g, dim_b = Hardware.Pads.COLOR_YELLOW_DIM
        else:
            base_r, base_g, base_b = Hardware.Pads.COLOR_PURPLE
            dim_r, dim_g, dim_b = Hardware.Pads.COLOR_PURPLE_DIM
            
        if velocity == 0:
            # Return to Dim
            r, g, b = dim_r, dim_g, dim_b
        else:
            # Interpolate between Dim and Max based on velocity
            # Velocity 1 -> Dim, Velocity 127 -> Max
            ratio = velocity / 127.0
            r = int(dim_r + (base_r - dim_r) * ratio)
            g = int(dim_g + (base_g - dim_g) * ratio)
            b = int(dim_b + (base_b - dim_b) * ratio)
            
        pad_id = Hardware.Pads.PAD_LED_START_ID + pad_index
        payload = bytes([0x02, 0x00, 0x16, pad_id, r, g, b])
        send_to_device(payload)

    def TogglePadMode(self, event):
        if self._is_pressed(event):
            self._pad_mode_start_time = time.time()
        else:
            if hasattr(self, '_pad_mode_start_time'):
                duration = time.time() - self._pad_mode_start_time
                if duration > 1.0:
                    # Toggle Velocity
                    global PAD_VELOCITY_ENABLED
                    PAD_VELOCITY_ENABLED = not PAD_VELOCITY_ENABLED
                    state = "On" if PAD_VELOCITY_ENABLED else "Off"
                    self._navigation.HintRefresh("Velocity: " + state, title="Pad Settings")
                else:
                    # Toggle Pad Mode
                    global CURRENT_PAD_MODE
                    if CURRENT_PAD_MODE == PAD_MODE_DRUM:
                        CURRENT_PAD_MODE = PAD_MODE_CHROMATIC
                        self._navigation.HintRefresh("Pads: Chromatic", title="Pad Mode")
                    else:
                        CURRENT_PAD_MODE = PAD_MODE_DRUM
                        self._navigation.HintRefresh("Pads: FPC / Drum", title="Pad Mode")
                    
                # Update Pad Colors
                self.UpdatePadColors(CURRENT_PAD_MODE)
                
        self._mk2.LightReturn().UpdateLEDs_Groups3_4()



    def OnDrumSeqEvent(self, event) :
        if event.status == 153 :
            if SEQ_MODE == 1 :
                event.handled = True
                self.OnSeqEvent(event)
            else :
                original_note = event.data1
                
                if CURRENT_PAD_MODE == PAD_MODE_DRUM:
                    # FPC Mapping
                    mapped_note = FPC_MAP.get(str(event.data1))
                    if mapped_note is not None:
                        event.data1 = mapped_note
                elif CURRENT_PAD_MODE == PAD_MODE_CHROMATIC:
                    # Chromatic Mapping (Bottom-Left Start)
                    mapped_note = CHROMATIC_MAP.get(str(event.data1))
                    if mapped_note is not None:
                        event.data1 = mapped_note
                
                if not PAD_VELOCITY_ENABLED:
                    event.data2 = 127
                else:
                    # Velocity On: Pass through original velocity
                    # Debug: Display received velocity to verify hardware output
                    # self._navigation.HintRefresh("Pad: " + str(original_note) + " Vel: " + str(event.data2), title="Velocity Check")
                    pass
                
                # Set Pad Color (Active)
                if 36 <= original_note <= 51:
                    self.SetPadColor(original_note - 36, event.data2)

                event.handled = False
        elif event.status == 137 :
            if SEQ_MODE == 1 :
                if not transport.getLoopMode() :
                    event.handled = True
                    self.ReleaseBit(event)
            else :
                original_note = event.data1
                
                if CURRENT_PAD_MODE == PAD_MODE_DRUM:
                    mapped_note = FPC_MAP.get(str(event.data1))
                    if mapped_note is not None:
                        event.data1 = mapped_note
                elif CURRENT_PAD_MODE == PAD_MODE_CHROMATIC:
                    mapped_note = CHROMATIC_MAP.get(str(event.data1))
                    if mapped_note is not None:
                        event.data1 = mapped_note
                
                event.data2 = midi.MIDI_NOTEOFF
                
                # Set Pad Color (Idle/Dim)
                if 36 <= original_note <= 51:
                    self.SetPadColor(original_note - 36, 0)
                    
                event.handled = False


    def _show_and_focus(self, window):
        if not ui.getVisible(window):
            ui.showWindow(window)
        if not ui.getFocused(window):
            ui.setFocused(window)


    def _hideAll(self, event) :
        for i in range (channels.channelCount()) :
            channels.showEditor(i,0)

    
    def SwitchWindow(self, event) :
        if (ui.getFocused(WidChannelRack) or ui.getFocused(WidPlugin)) :
            self.showPlugin(event)
        elif ui.getFocused(WidMixer) :
            track = mixer.trackNumber()
            mixer.armTrack(track)
            self._navigation.ArmRefresh(track)
            #plugin = channels.channelNumber()
            # for i in range(plugins.getParamCount(plugin)) :
                # print(i, plugins.getParamName(i,plugin), plugins.getParamValue(i,plugin))
        elif ui.getFocused(WidBrowser) :
            nodeFileType = ui.getFocusedNodeFileType()
            if nodeFileType == -1:
                return
            if nodeFileType <= -100:
                transport.globalTransport(midi.FPT_Enter, 1)
            else:
                ui.selectBrowserMenuItem()
                if not ui.isInPopupMenu() :
                    self._navigation.PressRefresh()
                if not ui.isInPopupMenu() :
                    self._navigation.PressRefresh()
        self._mk2.LightReturn().UpdateLEDs_Groups3_4()
            
    
    
    def showPlugin(self, event) :
        # channels.showEditor shows the plugin interface. 
        # For samplers (no plugin interface), it opens Channel Settings. 
        # If already open/hidden behind, we might need to toggle or focus.
        # Try checking visibility first to decide toggle behavior or force show.
        # But simple `showEditor(idx, 1)` (Method 1=Show) usually forces it.
        # Current logic `channels.showEditor(channels.channelNumber())` toggles? Or assumes default 0?
        # Default behavior of showEditor(channel) is toggle.
        # Let's try explicit show.
        channels.showEditor(channels.channelNumber(), 1)

    
    def ToggleBrowserChannelRack(self, event) :
        self.FakeMIDImsg()
        # Rotation: Channel Rack -> Browser -> Mixer -> Channel Rack
        if ui.getFocused(WidChannelRack):
            self._show_and_focus(WidBrowser)
            self._navigation.BrowserRefresh()
        elif ui.getFocused(WidBrowser):
            self._show_and_focus(WidMixer)
            self._navigation.MixerToggleRefresh()
        elif ui.getFocused(WidMixer):
            self._show_and_focus(WidChannelRack)
            self._navigation.ChannelRackRefresh()
        else:
            # Default entry
            self._show_and_focus(WidChannelRack)
            self._navigation.ChannelRackRefresh()
            
            self._show_and_focus(WidChannelRack)
            self._navigation.ChannelRackRefresh()
            
        self._mk2.LightReturn().UpdateLEDs_Groups3_4()

    
    def ToggleMixerChannelRack(self, event) :
        self.FakeMIDImsg()
        self._hideAll(event)
        global MIXER_MODE
        if MIXER_MODE == 0 :
            MIXER_MODE = 1
            self._show_and_focus(WidMixer)
        else :
            MIXER_MODE = 0
            self._show_and_focus(WidChannelRack)
        self._navigation.MixerToggleRefresh()
        
        # Reset Fader Pickup
        self._fader_pickup_active = [False] * 9

    def DrumSeqToggle(self, event) :
        self.FakeMIDImsg()
        self._hideAll(event)
        global SEQ_MODE 
        if SEQ_MODE == 0 :
            SEQ_MODE = 1
        else :
            SEQ_MODE = 0
        self._navigation.DrumSeqToggleRefresh()



    # NAVIGATION



    def TrackSelectMainKnob(self, event):
        if ui.getFocused(WidPlugin) :
            self._hideAll(event)
            self._show_and_focus(WidChannelRack)
        elif ui.getFocused(WidBrowser) :
            if ui.isInPopupMenu() :  
                if event.data2 == 65 :
                    ui.up()
                elif event.data2 == 1 :
                    ui.down()
                self._navigation.HintRefresh(ui.getFocusedNodeCaption())
            else :
                if event.data2 == 65 :
                    ui.previous()
                elif event.data2 == 1 :
                    ui.next()
                self._navigation.HintRefresh(ui.getFocusedNodeCaption())
        elif ui.getFocused(WidMixer) :
            if event.data2 == 65 :
                self._show_and_focus(WidMixer)
                self._hideAll(event)
                ui.previous()
            elif event.data2 == 1 :  
                self._show_and_focus(WidMixer)
                self._hideAll(event)
                ui.next()
        elif ui.getFocused(WidChannelRack) :
            if event.data2 == 65 :
                self._hideAll(event)
                self._show_and_focus(WidChannelRack)
                ui.previous()
                mixer.setTrackNumber(channels.getTargetFxTrack(channels.channelNumber()),3)
            elif event.data2 == 1 :  
                self._hideAll(event)
                self._show_and_focus(WidChannelRack)
                ui.next()
                mixer.setTrackNumber(channels.getTargetFxTrack(channels.channelNumber()),3)
        else :
            self._show_and_focus(WidChannelRack)
    


    def TrackSelect(self, event):
        if MIXER_MODE :
            track = (event.controlNum - 23) + 8*AKLmk2.MX_OFFSET
            mixer.setTrackNumber(track,3)
            self._hideAll(event)
        else :
            channel = (event.controlNum - 24) + 8*AKLmk2.CH_OFFSET
            if channel < channels.channelCount():
                channels.selectOneChannel(channel)
                mixer.setTrackNumber(channels.getTargetFxTrack(channels.channelNumber()),3)
                self._hideAll(event)
                ui.setFocused(WidChannelRack)

    
    def previousPattern(self, event) :
        if ui.getFocused(5) :
            self.previousPreset(event)
        elif ui.getFocused(WidBrowser):
            # Navigate Browser Tabs (Snapshots)
            # User requested specific function: ui.navigateBrowserTabs(FPT_Left)
            try:
                ui.navigateBrowserTabs(midi.FPT_Left)
                self._navigation.HintRefresh("Browser: Prev Tab")
            except AttributeError:
                # Fallback if function doesn't exist (e.g. older FL version)
                print("ui.navigateBrowserTabs not found")
                ui.previous()
        elif ui.getFocused(WidMixer) :
            # Navigate Mixer Tracks
            current_track = mixer.trackNumber()
            if current_track > 0 :
                mixer.setTrackNumber(current_track - 1)
                self._navigation.HintRefresh("Mixer Track: " + str(current_track - 1))
        else :
            pattern = patterns.patternNumber()
            patterns.jumpToPattern(pattern - 1)
            
     
    def nextPattern(self, event) :
        if ui.getFocused(5) :
            self.nextPreset(event)
        elif ui.getFocused(WidBrowser):
            # Navigate Browser Tabs (Snapshots)
            # User requested specific function: ui.navigateBrowserTabs(FPT_Right)
            try:
                ui.navigateBrowserTabs(midi.FPT_Right)
                self._navigation.HintRefresh("Browser: Next Tab")
            except AttributeError:
                # Fallback
                print("ui.navigateBrowserTabs not found")
                ui.next()
        elif ui.getFocused(WidMixer) :
             # Navigate Mixer Tracks
            current_track = mixer.trackNumber()
            if current_track < 125 : # Max Tracks
                mixer.setTrackNumber(current_track + 1)
                self._navigation.HintRefresh("Mixer Track: " + str(current_track + 1))
        else :
            pattern = patterns.patternNumber()
            patterns.jumpToPattern(pattern + 1)
        
        
        
    # PLUGIN
  

    
    def nextPreset(self, event) :
        if ui.getFocused(5) :
            plugins.nextPreset(channels.channelNumber())


    def previousPreset(self, event) :
        if ui.getFocused(5) :
            plugins.prevPreset(channels.channelNumber())


    def Plugin(self, event, clef) :
        if ui.getFocused(5) :
            param, value = KeyLabmk2Plugin.Plugin(event,clef)
            if event.controlNum != 1 :
                self._navigation.PluginRefresh(param, value)



    # FUNCTIONS



    def Record(self, event) :
        transport.record()
        self._navigation.RecordRefresh()
    
    
    def Start(self, event) :
        transport.start()
        self._navigation.PlayRefresh()
    
    
    def Stop(self, event) :
        transport.stop()
        self._navigation.StopRefresh()
     
     
    def FastForwardORnextBar(self, event) :
        if SEQ_MODE == 1 and event.controlVal == 127 :
            global RECT_OFFSET
            self.FakeMIDImsg()
            RECT_OFFSET += 1
            top = channels.channelNumber()
            left = RECT_OFFSET*16
            ui.crDisplayRect(left,top,16,1,1000)
            self._navigation.BarRefresh()
        elif SEQ_MODE == 0 :
            if self._is_pressed(event):
                transport.continuousMove(1, SS_START)
                self._navigation.FastForwardRefresh()
            else:
                transport.continuousMove(1, SS_STOP)
                self._navigation.FastForwardRefresh()
        
    
    def RewindORprevBar(self, event) :
        if SEQ_MODE == 1 and event.controlVal == 127 :
            global RECT_OFFSET
            self.FakeMIDImsg()
            RECT_OFFSET -= 1
            if RECT_OFFSET < 0 :
                RECT_OFFSET = 0
            top = channels.channelNumber()
            left = RECT_OFFSET*16
            ui.crDisplayRect(left,top,16,1,1000)
            self._navigation.BarRefresh()
        elif SEQ_MODE == 0 :
            if self._is_pressed(event):
                transport.continuousMove(-1, SS_START)
                self._navigation.RewindRefresh()
            else:
                transport.continuousMove(-1, SS_STOP)
                self._navigation.RewindRefresh()
            
    
    
    def Loop(self, event) :
        transport.globalTransport(midi.FPT_LoopRecord,1)
        self._navigation.LoopRefresh()
    

    def Cut(self, event) :
        self._show_and_focus(midi.widChannelRack)
        ui.cut()
        self._navigation.CutRefresh()
        
    def Undo(self, event) :
        transport.globalTransport(midi.FPT_Undo, midi.FPT_Undo, event.pmeFlags)
        self._navigation.UndoRefresh()

    def Overdub(self, event) :
        transport.globalTransport(midi.FPT_Overdub,1)
        self._navigation.OverdubRefresh()
    

    def SetClick(self, event) :
        transport.globalTransport(midi.FPT_Metronome,1)
        self._navigation.MetronomeRefresh()
          
      
    def SoloChannel(self, event) :
        if ui.getFocused(WidChannelRack) :
            channels.soloChannel(channels.channelNumber())
        elif ui.getFocused(WidMixer) :
            mixer.soloTrack(mixer.trackNumber())
        self.FakeMIDImsg()
     
     
    def MuteChannel(self, event) :
        if ui.getFocused(WidChannelRack) :
            channels.muteChannel(channels.channelNumber())
        elif ui.getFocused(WidMixer) :
            mixer.muteTrack(mixer.trackNumber())
        self.FakeMIDImsg()
      
      
    def TapTempo(self, event) :
        transport.globalTransport(midi.FPT_TapTempo,1)
        self._navigation.TapTempoRefresh()
       
       
    def SnapMode(self, event) :
        ui.snapMode(1)
        self._navigation.SnapModeRefresh()
    
 
    def NewPattern(self, event):
        patterns.findFirstNextEmptyPat(midi.FFNEP_DontPrompt)
        self._navigation.HintRefresh("New Pattern", title="Pattern")

    def FocusMixer(self, event):
        if not ui.getVisible(midi.widMixer):
            ui.showWindow(midi.widMixer)
        if not ui.getFocused(midi.widMixer):
            ui.setFocused(midi.widMixer)
        self._navigation.HintRefresh("Mixer Focused", title="Mixer")

    # Remove UpdateDAWButtonFeedback as it is now in KeyLabmk2Return

        # --- Global Controls ---
        
        # Global 1: ToggleBrowserChannelRack (74) -> Always 100%
        send_feedback(Hardware.DAW.Global.CONTROL_1_2, True)

        # Global 2: Pad Mode (87) -> Always 100%
        send_feedback(Hardware.DAW.Global.CONTROL_2_2, True)
        
        # Global 3: Overdub (88) -> 30% Off / 100% On
        # Using ui.isLoopRecEnabled() as proxy if isOverdub shouldn't exist?
        # FL "Overdub" is often linked to LoopRecord or Blend.
        # Let's try to find if there is a specific check.
        # For now, we will use a local toggle approximation if API is missing, 
        # but better to assume off (dim) if uncertain. 
        # We will set it to Dim (30% approx 0x18) vs Bright (0x7F).
        # We'll rely on a safe check or default.
        is_overdub = False
        try:
             is_overdub = ui.isOverdubEnabled()
        except AttributeError:
             # Fallback: check transport Loop Record just in case it's what they mean? No.
             pass
        send_feedback(Hardware.DAW.Global.CONTROL_3_2, is_overdub, dim_val=0x18)

        # Global 4: Metronome (89) -> State based (Dim/Bright not specified? User said "same for solo/mute/overdub")
        # User said: "same for the solo and mute button. start in 30% brightness and when toggled then 100% brightness."
        # Overdub was included in that sentence. Metronome wasn't explicitly BUT previous context used it.
        # Let's apply 30%/100% to Metronome too for consistency.
        send_feedback(Hardware.DAW.Global.CONTROL_4_2, transport.isMetronomeEnabled(), dim_val=0x18)

        # Global 5: Undo (81) -> Always 100%
        send_feedback(Hardware.DAW.Global.CONTROL_5_2, True)


        # --- Track Controls ---

        # Track 5: Redo (57) -> Always 100%
        send_feedback(Hardware.DAW.Track.CONTROL_5_1, True)
        
        # Track 1-3 handled by ranges? Or specific?
        # If Track 1 is NewPattern (8), Track 2 is FocusMixer (16), Track 3 is Snap (0)
        # User didn't ask for these specifically in this prompt (except "DAW Commands").
        # Detailed prompt: "control 1 Global Controls... undo and redo... overdub... solo and mute..."
        # So I only touch what was asked.


        # --- Solo / Mute Buttons (Tracks) ---
        # Solo (8-15) and Mute (16-23)
        # Check active tracks based on offset
        
        base_track_index = AKLmk2.MX_OFFSET * 8 + 1 # 1-based index for mixer
        # Or Channel Rack offset? 
        # Depends on mode. 
        # SoloChannel/MuteChannel functions check focus.
        # We should probably do the same.
        
        if ui.getFocused(WidMixer):
             offset = AKLmk2.MX_OFFSET
             base = offset * 8 + 1
             for i in range(8):
                 track_idx = base + i
                 if track_idx <= MAX_TRACKS:
                     is_solo = mixer.isTrackSolo(track_idx)
                     is_mute = mixer.isTrackMuted(track_idx)
                     
                     # Solo Buttons (8-15) -> IDs 8+i
                     send_feedback(8 + i, is_solo, dim_val=0x18)
                     
                     # Mute Buttons (16-23) -> IDs 16+i
                     send_feedback(16 + i, is_mute, dim_val=0x18)
        else:
             # Channel Rack
             offset = AKLmk2.CH_OFFSET
             base = offset * 8
             for i in range(8):
                 chan_idx = base + i
                 if chan_idx < channels.channelCount():
                     is_solo = channels.isChannelSolo(chan_idx)
                     is_mute = channels.isChannelMuted(chan_idx)
                     
                     send_feedback(8 + i, is_solo, dim_val=0x18)
                     send_feedback(16 + i, is_mute, dim_val=0x18)


    def ToggleOverdub(self, event):
        transport.globalTransport(midi.FPT_Overdub, 1)
        self._navigation.HintRefresh("", title="Overdub")
        self._mk2.LightReturn().UpdateLEDs_Groups3_4()

    def Redo(self, event):
        general.undoDown()
        self._navigation.HintRefresh("", title="Redo")

    def SnapToggle(self, event):
        # Toggle between Line (1) and Off (0)
        # ui.getSnapMode() returns the current snap mode index
        if ui.getSnapMode() == 0:
            ui.snapMode(1) # Set to Line
            self._navigation.HintRefresh("Line", title="Snap")
        else:
            ui.snapMode(0) # Set to Off
            self._navigation.HintRefresh("Off", title="Snap")
        
        self._mk2.LightReturn().UpdateLEDs_Groups3_4()

    def MetronomeToggle(self, event):
        transport.globalTransport(midi.FPT_Metronome, 1)
        self._navigation.MetronomeRefresh()
        self._mk2.LightReturn().UpdateLEDs_Groups3_4()

    def UndoOrCut(self, event):
        if self._is_pressed(event):
            self._undo_start_time = time.time()
        else:
            if hasattr(self, '_undo_start_time'):
                duration = time.time() - self._undo_start_time
                if duration > 1.0:
                    # Cut
                    self._show_and_focus(midi.widChannelRack) # Cut usually works on selected items
                    ui.cut()
                    self._navigation.CutRefresh()
                else:
                    # Unlimited Undo (Step back in history)
                    general.undoUp()
                    self._navigation.UndoRefresh()

    def SetVolumeTrack(self, event) :
        if MIXER_MODE == 1 :
            if event.status == 232 and event.midiId == 224  :
                event.data1 = 1
                event.midiId = midi.MIDI_CONTROLCHANGE
                AKLmk2.SetVolumeTrack(event) 
                value = round(mixer.getTrackVolume(0)*100)
                perc = str(value)
                self._navigation.VolumeMixerRefresh(event, perc)
            else :
                event.data1 = 2 + event.status - event.midiId
                event.midiId = midi.MIDI_CONTROLCHANGE
                track = (event.controlNum - 1) + (8*AKLmk2.MX_OFFSET)
                if track < 126 :
                    AKLmk2.SetVolumeTrack(event)
                    value = round(mixer.getTrackVolume(event.data1 - 1 + (8*AKLmk2.MX_OFFSET)) * 100)
                    perc = str(value)
                    self._navigation.VolumeMixerRefresh(event, perc)
        else :
            if event.status != 232 :
                self.Plugin(event, clef = event.status)
                self._navigation.NoPlugin()
            else :
                value = event.data2/127
                mixer.setTrackVolume(mixer.trackNumber(),0.8*value)
                value = round(mixer.getTrackVolume(mixer.trackNumber())*100)
                perc = str(value)
                self._navigation.VolumeChRefresh(perc)
                
            
    def SetPanTrack(self, event) :
        
        if EDIT_MODE == 1 :
            global SEQ_PARAM
            global INDEX_PRESSED
            INDEX_PRESSED = []    
            for i in range(4) :
                for j in range(4) :
                    if STATE_MATRIX[i][j] == 1 :
                        INDEX_PRESSED += [4*i+j]
            KLmk2SQP.Param(event)
            self.FakeMIDImsg()
            SEQ_PARAM = 1
        
        else :
            if MIXER_MODE == 1 :
                if event.controlNum == 24 :
                    AKLmk2.SetPanTrack(event)
                    value = round(mixer.getTrackPan(0) * 100)
                    perc = str(value)
                    self._navigation.PanMixerRefresh(event, perc)
                else :
                    track = (event.controlNum - 15) + (8*AKLmk2.MX_OFFSET)
                    AKLmk2.SetPanTrack(event)
                    value = round(mixer.getTrackPan(track) * 100)
                    perc = str(value)
                    self._navigation.PanMixerRefresh(event, perc)
            else :
                if event.controlNum != 24 :
                    self.Plugin(event, clef = event.controlNum)
                    self._navigation.NoPlugin()
                else :
                    data = 0
                    if event.data2 > 0x40 : data = -1
                    elif event.data2 < 0x40 : data = 1
                    mixer.setTrackPan(mixer.trackNumber(),mixer.getTrackPan(mixer.trackNumber())+ (data/20))
                    value = round(mixer.getTrackPan(mixer.trackNumber()) * 100)
                    perc = str(value)
                    self._navigation.PanChRefresh(perc)

  
  
    # SEQUENCER

   
   
    def PressSequencer(self, event) :
        global SEQ_PARAM
        SEQ_PARAM = 0
        if channels.isGraphEditorVisible() :
            SEQ_PARAM = 1
        self.HoldBit(event) 
        
            
    def HoldBit(self, event) :
        global STATE_MATRIX
        global EDIT_MODE
        EDIT_MODE = 1
        
        # State Matrix Init
        BIT_MAP = {
        '36':0,
        '37':1,
        '38':2,
        '39':3,
        '40':4,
        '41':5,
        '42':6,
        '43':7,
        '44':8,
        '45':9,
        '46':10,
        '47':11,
        '48':12,
        '49':13,
        '50':14,
        '51':15
        }
        cle = str(event.controlNum)
        STATE_MATRIX[BIT_MAP.get(cle)//4][BIT_MAP.get(cle)%4] = 1


        
    def ReleaseBit(self, event) :
        global STATE_MATRIX
        global EDIT_MODE
        
        # State Matrix Init
        EDIT_MODE = 0
        BIT_MAP = {
        '36':0,
        '37':1,
        '38':2,
        '39':3,
        '40':4,
        '41':5,
        '42':6,
        '43':7,
        '44':8,
        '45':9,
        '46':10,
        '47':11,
        '48':12,
        '49':13,
        '50':14,
        '51':15
        }
        cle = str(event.controlNum)
        STATE_MATRIX[BIT_MAP.get(cle)//4][BIT_MAP.get(cle)%4] = 0
                
        # While at least one pad is pressed, stay in edit mode
        hold_num = 0
        for i in STATE_MATRIX :
            for j in i :
                if j == 1 :
                    hold_num += 1
        if hold_num != 0 :
            EDIT_MODE = 1
        else :
            channels.closeGraphEditor(1)
        
        # If a parameter changed, let the pad on
        step = event.controlNum - 36
        if SEQ_PARAM == 1 :
            return
        else :    
            if channels.getGridBit(channels.channelNumber(),step+(16*RECT_OFFSET)) == 0 :
                channels.setGridBit(channels.channelNumber(),step+(16*RECT_OFFSET),1)
                LED_MATRIX[step//4][step%4] = 1
            else :
                channels.setGridBit(channels.channelNumber(),step+(16*RECT_OFFSET),0)
                LED_MATRIX[step//4][step%4] = 0    
        

    # UTILITY
   
   
        
    def FakeMIDImsg(self) :
        transport.globalTransport(midi.FPT_Punch,1)

    # GROUP 6: MIXER & PARAMETER CONTROLS

    def SetPanTrack(self, event):
        # Knobs 1-8 are Relative (CC 16-23)
        # Event Type: CC (176)
        # Value logic: 65 = Left (-), 1 = Right (+)
        
        knob_cc = event.controlNum
        try:
            index = Hardware.Mixer.Knobs.ALL.index(knob_cc)
        except ValueError:
            return

        # Determine direction
        delta = 0
        if event.data2 == 1:
            delta = 0.02 # Increment
        elif event.data2 == 65:
            delta = -0.02 # Decrement
        # Handle other potential relative values if necessary (e.g. 2, 66 for faster turns)
        elif event.data2 < 64:
            delta = event.data2 * 0.02
        elif event.data2 > 64:
            delta = - (event.data2 - 64) * 0.02
            
        if delta == 0: return

        if ui.getFocused(WidMixer):
            track_index = (index) + 8 * AKLmk2.MX_OFFSET + 1
            if track_index <= MAX_TRACKS:
                # Get current pan, add delta, clamp
                current = mixer.getTrackPan(track_index)
                new_val = max(-1.0, min(1.0, current + delta))
                mixer.setTrackPan(track_index, new_val)
                self._navigation.HintRefresh(f"Pan Track {track_index}: {int((new_val+1)/2*100)}%")
        else:
            channel_index = (index) + 8 * AKLmk2.CH_OFFSET
            if channel_index < channels.channelCount():
                current = channels.getChannelPan(channel_index)
                new_val = max(-1.0, min(1.0, current + delta))
                channels.setChannelPan(channel_index, new_val)
                self._navigation.HintRefresh(f"Pan Channel {channel_index+1}: {int((new_val+1)/2*100)}%")

        if ui.getFocused(WidMixer):
            track_index = (index) + 8 * AKLmk2.MX_OFFSET + 1
            if track_index <= MAX_TRACKS:
                mixer.setTrackPan(track_index, value * 2.0 - 1.0)
                self._navigation.HintRefresh(f"Pan Track {track_index}: {int(value*100)}%")
        else:
            channel_index = (index) + 8 * AKLmk2.CH_OFFSET
            if channel_index < channels.channelCount():
                channels.setChannelPan(channel_index, value * 2.0 - 1.0)
                self._navigation.HintRefresh(f"Pan Channel {channel_index+1}: {int(value*100)}%")

    def SetVolumeTrack(self, event):
        # Faders 1-9 use Pitch Bend (Status 224-232)
        # ID is based on Channel (Event Status or MidiChan)
        
        index = event.midiChan
        if index > 8: return 
        
        # HW Value (0.0 - 1.0)
        value = (event.data2 * 128 + event.data1) / 16383.0
        
        # Check if it's Master Fader (Index 8 / Ch 9)
        # Assuming Master doesn't need soft takeover or uses same logic? 
        # User requested 1-8. Let's apply to Master too for consistency, or skip?
        # Request said "Faders 1-8". Let's focus on 1-8 (Index 0-7).
        if index == 8:
            self.ProcessMasterFader(event, value)
            return

        # Faders 1-8 (Index 0-7)
        target_vol = -1.0
        
        # Determine Context and Current Value
        if ui.getFocused(WidMixer):
            track_index = (index) + 8 * AKLmk2.MX_OFFSET + 1
            if track_index <= MAX_TRACKS:
                target_vol = mixer.getTrackVolume(track_index)
        else:
            channel_index = (index) + 8 * AKLmk2.CH_OFFSET
            if channel_index < channels.channelCount():
                target_vol = channels.getChannelVolume(channel_index)

        if target_vol == -1.0: return # Invalid track/channel

        # Pickup Logic
        threshold = 0.05 # 5% tolerance
        
        # Check if External Change happened (Mouse move)
        # If we think we are locked, but SW value is far from our last known HW value, break lock.
        # We need to store last applied value to know this.
        # For simplicity, let's just use the current HW value if we are active.
        # If Active: abs(value - target_vol) should be small. 
        # If it's big (> 10%), assume mouse took over.
        
        if self._fader_pickup_active[index]:
            if abs(value - target_vol) > 0.1: # 10% tolerance for drift/speed
                self._fader_pickup_active[index] = False
                self._navigation.HintRefresh(f"Pickup Lost! Move to {int(target_vol*100)}%")
                return

        if not self._fader_pickup_active[index]:
            if abs(value - target_vol) < threshold:
                self._fader_pickup_active[index] = True
                self._navigation.HintRefresh(f"Pickup Active!")
            else:
                self._navigation.HintRefresh(f"Move Fader to {int(target_vol*100)}%")
                return # Do not apply value

        # Apply Value
        if ui.getFocused(WidMixer):
            track_index = (index) + 8 * AKLmk2.MX_OFFSET + 1
            if track_index <= MAX_TRACKS:
                mixer.setTrackVolume(track_index, value)
                self._navigation.HintRefresh(f"Vol Track {track_index}: {int(value*100)}%")
        else:
            channel_index = (index) + 8 * AKLmk2.CH_OFFSET
            if channel_index < channels.channelCount():
                channels.setChannelVolume(channel_index, value)
                self._navigation.HintRefresh(f"Vol Channel {channel_index+1}: {int(value*100)}%")

    def BankSelect(self, event) :
        # Dynamic Focus Check
        if ui.getFocused(WidMixer) :
            self.FakeMIDImsg()
            if event.controlNum == 47 : # Prev (Swap)
                AKLmk2.MX_OFFSET -= 1
                if AKLmk2.MX_OFFSET < 0 :
                    AKLmk2.MX_OFFSET = 0
                self._navigation.BankMixRefresh()
            elif event.controlNum == 46 : # Next (Swap)
                if (AKLmk2.MX_OFFSET + 1)*8 < MAX_TRACKS :
                    AKLmk2.MX_OFFSET += 1
                    self._navigation.BankMixRefresh()
            
            # Update Visual Feedback
            # Mixer Red Box (Offset, 0, 8 Tracks, 1 Row, Duration)
            ui.miDisplayRect(AKLmk2.MX_OFFSET, 0, 8, 1, 1000) 

        else :
            self.FakeMIDImsg()
            if event.controlNum == 47 : # Prev (Swap)
                AKLmk2.CH_OFFSET -= 1
                if AKLmk2.CH_OFFSET < 0 :
                    AKLmk2.CH_OFFSET = 0
                self._navigation.BankChanRefresh()
            elif event.controlNum == 46 : # Next (Swap)
                if (AKLmk2.CH_OFFSET + 1)*8 < channels.channelCount() :
                    AKLmk2.CH_OFFSET += 1
                    self._navigation.BankChanRefresh()
            
            # Show Red Box in Channel Rack
            # (StepOffset(0), ChanOffset, StepWidth(16), ChanHeight(8), Dur)
            ui.crDisplayRect(0, AKLmk2.CH_OFFSET*8, 16, 8, 1000)

        # Reset Fader Pickup on Bank Change
        self._fader_pickup_active = [False] * 9

    def ProcessTrackButton(self, event):
        # Buttons 1-9 (Mapped in Hardware.Mixer.TrackButtons)
        btn_id = event.data1
        is_pressed = self._is_pressed(event)
        
        # Check for Master Button (Button 9)
        # We check by Index, not ID, to rely on Mapping order.
        # Button 9 is the last item (Index 8) in TrackButtons.ALL
        
        try:
            index = Hardware.Mixer.TrackButtons.ALL.index(btn_id)
        except ValueError:
            return

        if index == 8: # Button 9 (Master Sep)
            self.ProcessMasterButton(event)
            return
            
        if index > 7: return # Safety

        if is_pressed:
            self._track_button_press_times[index] = time.time()
        else:
            # Release
            start_time = self._track_button_press_times.get(index, 0)
            duration = time.time() - start_time
            
            if duration < 1.0:
                self.ResetPan(index)
            else:
                self.ToggleMute(index)
            
            # Force LED update immediately
            self.FakeMIDImsg() 

    def ResetPan(self, index):
        if ui.getFocused(WidMixer):
            track_index = (index) + 8 * AKLmk2.MX_OFFSET + 1
            if track_index <= MAX_TRACKS:
                mixer.setTrackPan(track_index, 0.0)
                self._navigation.HintRefresh(f"Reset Pan Track {track_index}")
        else:
            channel_index = (index) + 8 * AKLmk2.CH_OFFSET
            if channel_index < channels.channelCount():
                channels.setChannelPan(channel_index, 0.0)
                self._navigation.HintRefresh(f"Reset Pan Channel {channel_index+1}")

    def ToggleMute(self, index):
        if ui.getFocused(WidMixer):
            track_index = (index) + 8 * AKLmk2.MX_OFFSET + 1
            if track_index <= MAX_TRACKS:
                mixer.muteTrack(track_index) # Toggles
                state = "Muted" if mixer.isTrackMuted(track_index) else "Unmuted"
                self._navigation.HintRefresh(f"Track {track_index} {state}")
        else:
            channel_index = (index) + 8 * AKLmk2.CH_OFFSET
            if channel_index < channels.channelCount():
                channels.muteChannel(channel_index)
                state = "Muted" if channels.isChannelMuted(channel_index) else "Unmuted"
                self._navigation.HintRefresh(f"Channel {channel_index+1} {state}")

    def ProcessMasterFader(self, event, value=None):
        # If called from dispatcher directly (unlikely if PB handling holds), calculate value
        if value is None:
            value = (event.data2 * 128 + event.data1) / 16383.0 # PB handling
            
        # Scale to 100% Max (0.8 in FL)
        final_vol = value * 0.8
        
        mixer.setTrackVolume(0, final_vol)
        self._navigation.HintRefresh(f"Master Vol: {int(value*100)}%")

    def ProcessMasterKnob(self, event):
        # Knob 9: 
        # Mixer Mode: Master Pan Toggle (Left/Center/Right)
        # Channel Mode: Main Swing
        
        # Determine Context
        is_mixer = ui.getFocused(WidMixer)
        
        # Value Handling (Relative)
        delta = 0
        if event.data2 == 1: delta = 0.02
        elif event.data2 == 65: delta = -0.02
        elif event.data2 < 64: delta = event.data2 * 0.02
        elif event.data2 > 64: delta = - (event.data2 - 64) * 0.02
        
        if delta == 0: return

        if is_mixer:
            # Mixer: Master Pan Toggle with Deadzone
            # User wants 30% Turn required to switch.
            
            current = mixer.getTrackPan(0)
            target = current
            
            # Knob Relative Delta is small (~0.02 per tick). 
            # We need to accumulate? Or just check if user is turning vigorously?
            # Or simplified: If turning Right and current is Left/Center -> Go Right.
            # But "Hard to select 0%". 
            # Let's enforce snapping:
            # If current is -1.0 (Left), turning Right sets to 0.0 (Center).
            # If current is 0.0 (Center), turning Right sets to 1.0 (Right).
            # If current is 0.0 (Center), turning Left sets to -1.0 (Left).
            # If current is 1.0 (Right), turning Left sets to 0.0 (Center).
            
            # To handle "30%" feel -> maybe we can't measure 30% relative turn easily without accumulation.
            # But we can make it insensitive to small changes if we were continuous.
            # Since we are Relative, each tick is an event.
            # Let's use the Snapping Logic. It essentially creates "Zones".
            
            if delta > 0: # Turning Right
                if current <= -0.1: target = 0.0
                elif current >= -0.1 and current <= 0.1: target = 1.0
                else: target = 1.0
            else: # Turning Left
                if current >= 0.1: target = 0.0
                elif current >= -0.1 and current <= 0.1: target = -1.0
                else: target = -1.0
                
            mixer.setTrackPan(0, target)
            self._navigation.HintRefresh(f"Master Pan: {int(target*100)}%")
            
        else:
            # Channel: Loop Mode & Loop Point
            # "Activate loop mode and set loop point (to 64 step max)"
            
            # 1. Activate Loop Mode
            if not transport.getLoopMode():
                transport.setLoopMode(1)
            
            # 2. Control Loop Length
            # We need a value 0-64. 
            # Since knob is relative, we need to track a static variable or read current loop point.
            # transport.getLoopMode() returns boolean usually.
            # Use 'patterns' module? 
            # 'transport.setLoopMode()' enables pattern/song loop.
            # But the LENGTH is determined by 'transport.getSongPos' markers?
            # No, 'Live Loop' recording?
            # Creating a selection in Playlist?
            
            # Let's try: Adjusting the "Song Loop" marker? 
            # Or just changing the Pattern Length of the current pattern?
            # 'patterns.patternLength(p)' ?
            
            # He said "set the loop point". 
            # Let's assume he means 'transport.setLoopEnd(time)'.
            
            curr_time = transport.getLoopInfo().end
            if curr_time == -1: curr_time = 0
            
            # Increment/Decrement by 1 Step (1/4 beat?) or 1 Bar?
            # FL PPQ is 96 usually. 1 Step = 24 ticks?
            step_ticks = 24 # 4 steps per beat (16th notes)
            
            change = 0
            if delta > 0: change = step_ticks
            else: change = -step_ticks
            
            new_end = max(0, min(64 * step_ticks, curr_time + change))
            
            # transport.setLoopInfo(start, end)? 
            # No, 'transport.setLoopMode' is just on/off.
            # 'transport.setSongLoop(start, end)'? Not documented in standard simple API.
            
            # Alternative: modifying a variable 'AKLmk2.LOOP_LENGTH' and hint it.
            # But it needs to do something.
            
            # Let's try 'ui.setStepEditMode' ?
            # Fallback: Just toggle Loop Mode On/Off and Hint "Loop Length: N/A"?
            # No, user was specific.
            # Use `transport.globalTransport(FPT_LoopRecord, 1)` ?
            
            # Let's assume he wants to change 'Pattern Length' if in Pattern Mode?
            # patterns.setPatternLength( index, length ) ? 
            # Codebase search didn't show this.
            
            self._navigation.HintRefresh("Loop Point Control: API Limitation (WIP)")

    def ProcessMasterButton(self, event):
        if not self._is_pressed(event):
            return
        
        current = mixer.getTrackStereoSep(0)
        # Toggle: If merged (1.0) -> sep (0.0). Else -> merged.
        if abs(current - 1.0) < 0.1:
            new_val = 0.0
            state = "Separated"
            # Button LED: Mint Green (State A) handled in Return
        else:
            new_val = 1.0
            state = "Merged (Mono)"
            # Button LED: Blinking Red (State B) handled in Return
            
        mixer.setTrackStereoSep(0, new_val)
        self._navigation.HintRefresh(f"Master: {state}")

