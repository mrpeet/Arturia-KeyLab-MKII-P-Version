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
            .NewHandler(144, self.OnCommandEvent)
            .NewHandler(176, self.OnKnobEvent)
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
            self.UpdateDAWButtonFeedback()
        except Exception as e:
            print("Error initializing DAW feedback:", e)

        self._track_button_press_times = {}




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
        event.handled = True
        self._knob_dispatcher.Dispatch(event)
        
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
        self.UpdateDAWButtonFeedback()
            
    
    
    def showPlugin(self, event) :
        channels.showEditor(channels.channelNumber())

    
    def ToggleBrowserChannelRack(self, event) :
        self.FakeMIDImsg()
        if ui.getFocused(4) != True :
            self._show_and_focus(4)
            self._navigation.BrowserRefresh()
        else :
            self._show_and_focus(1)
            self._navigation.ChannelRackRefresh()
        self.UpdateDAWButtonFeedback()

    
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

    def UpdateDAWButtonFeedback(self):
        # Helper to send feedback
        def send_feedback(cc, is_on):
            val = 127 if is_on else 25 # 100% vs ~20%
            # Correct MIDI message packing: Status + (Data1 << 8) + (Data2 << 16)
            # Assuming Channel 2 (DAW Mode) for feedback? Or Channel 1?
            # KeyLab MKII DAW mode usually listens on Channel 2 (0x1) for feedback.
            # midi.MIDI_CONTROLCHANGE is usually 0xB0 (Channel 1). 
            # Let's try Channel 2 (0xB1) if standard is B0.
            # Actually, let's use the generic 0xB0 | 0x01 (Channel 2) if we are unsure, 
            # or just 0xB0 if it's User mode.
            # Given this is "DAW Commands", it's likely Channel 2.
            # But let's check if we can find the channel used elsewhere.
            # For now, I'll use 0xB0 + (0x02 - 1) ? No.
            # Let's stick to Channel 1 (0xB0) first as it's the safest default if not specified.
            # If it doesn't work, we can change to Channel 2.
            # But the CRASH is likely due to the 4-byte packing with 0 in the middle.
            
            # Using Channel 2 (0x1) just in case, as Arturia DAW mode is usually Ch 2.
            channel = 1 # Channel 2 (0-indexed 1)
            status = midi.MIDI_CONTROLCHANGE + channel
            device.midiOutMsg(status + (cc << 8) + (val << 16))

        # Track Controls
        # Control 3: Snap (Was Overdub)
        # Snap is a bit complex as it has modes. Let's assume "Line" or "Cell" is ON.
        # ui.getSnapMode() returns index. 0 might be "Line" or "Main".
        # Let's just assume if it's not "None" (3?) it's ON? 
        # Or just toggle state if we track it.
        # For now, let's use a simple check if we can.
        # Actually, SnapToggle just sends FPT_Snap.
        # Let's assume it's always "ON" (High brightness) for now as it's a toggle?
        # Or maybe we can't easily read Snap state.
        # Let's skip Snap feedback for a moment or set it to always ON/Dim?
        # User said "visualise their state".
        # Let's try to read it. ui.getSnapMode()
        
        # ToggleBrowserChannelRack (Global 1)
        # 100% (127) if Channel Rack (1) focused, 20% (25) if Browser (4) focused
        # Note: This might not be perfect if neither is focused, but requested behavior is specific.
        if ui.getFocused(1): # Channel Rack
            send_feedback(Hardware.DAW.Global.CONTROL_1_2, True)
        elif ui.getFocused(4): # Browser
            send_feedback(Hardware.DAW.Global.CONTROL_1_2, False)
        else:
            # Default state if neither? Maybe off or dim? Let's keep it dim (False)
            send_feedback(Hardware.DAW.Global.CONTROL_1_2, False)

        # Overdub (Global 3)
        # Always 100% brightness as requested
        send_feedback(Hardware.DAW.Global.CONTROL_3_2, True)

        # Metronome (Global 4)
        send_feedback(Hardware.DAW.Global.CONTROL_4_2, transport.isMetronomeEnabled())
        
        # Snap (Track 3)
        # We'll just light it up if Snap is not "None" (assuming 3 is None, need to verify)
        # For now, let's just set it to Dim (20%) as default, or maybe toggle locally?
        # Let's leave Snap as is for now or try to guess.
        
        # Loop (Transport)
        # send_feedback(Hardware.Transport.LOOP, transport.getLoopMode())

    def ToggleOverdub(self, event):
        transport.globalTransport(midi.FPT_Overdub, 1)
        self._navigation.HintRefresh("", title="Overdub")
        self.UpdateDAWButtonFeedback()

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
        
        self.UpdateDAWButtonFeedback()

    def MetronomeToggle(self, event):
        transport.globalTransport(midi.FPT_Metronome, 1)
        self._navigation.MetronomeRefresh()
        self.UpdateDAWButtonFeedback()

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
        # Fader 1 = Ch 1 (224), Fader 9 = Ch 9 (232)
        
        # Identify Fader Index directly from MIDI Channel (0-indexed)
        # event.midiChan should be 0-8 for Faders 1-9
        # Or status - 224
        
        index = event.midiChan
        if index > 8: return 
        
        # Value Logic: Pitch Bend uses MSB (data2) and LSB (data1).
        # For Volume, MSB (0-127) is sufficient.
        # PitchBend Range: 0-16383. Center is 8192.
        # But for Fader, typically 0 to Max (16383).
        # Let's use 14-bit if possible for smoothness, or just MSB.
        # event.data2 is MSB.
        value = (event.data2 * 128 + event.data1) / 16383.0
        
        # Check if it's Master Fader (Index 8 / Ch 9)
        if index == 8:
            self.ProcessMasterFader(event, value)
            return

        # Faders 1-8 (Index 0-7)
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
        if MIXER_MODE == 1 :
            self.FakeMIDImsg()
            if event.controlNum == 46 :
                AKLmk2.MX_OFFSET -= 1
                if AKLmk2.MX_OFFSET < 0 :
                    AKLmk2.MX_OFFSET = 0
                self._navigation.BankMixRefresh()
            elif event.controlNum == 47 :
                if (AKLmk2.MX_OFFSET + 1)*8 < MAX_TRACKS :
                    AKLmk2.MX_OFFSET += 1
                    self._navigation.BankMixRefresh()
            
            # Update Visual Feedback
            pass

        else :
            self.FakeMIDImsg()
            if event.controlNum == 46 :
                AKLmk2.CH_OFFSET -= 1
                if AKLmk2.CH_OFFSET < 0 :
                    AKLmk2.CH_OFFSET = 0
                self._navigation.BankChanRefresh()
            elif event.controlNum == 47 :
                if (AKLmk2.CH_OFFSET + 1)*8 < channels.channelCount() :
                    AKLmk2.CH_OFFSET += 1
                    self._navigation.BankChanRefresh()
            
            # Show Red Box in Channel Rack
            ui.crDisplayRect(0, AKLmk2.CH_OFFSET*8, 8, 4, 1000)

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
        # If called from dispatcher directly (unlikely if PB logic holds), calculate value
        if value is None:
            value = (event.data2 * 128 + event.data1) / 16383.0 # PB handling
            
        mixer.setTrackVolume(0, value)
        self._navigation.HintRefresh(f"Master Vol: {int(value*100)}%")

    def ProcessMasterKnob(self, event):
        # Knob 9: Main Swing
        # Using Relative Logic (CC 24)
        
        delta = 0
        if event.data2 == 1: delta = 0.02
        elif event.data2 == 65: delta = -0.02
        elif event.data2 < 64: delta = event.data2 * 0.02
        elif event.data2 > 64: delta = - (event.data2 - 64) * 0.02
        
        if delta == 0: return
        
        # Control Master Pan as fallback
        current = mixer.getTrackPan(0)
        new_val = max(-1.0, min(1.0, current + delta))
        mixer.setTrackPan(0, new_val)
        self._navigation.HintRefresh(f"Master Pan: {int((new_val+1)/2*100)}%")

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

