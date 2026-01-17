import device
import ui
import time
import transport
import mixer
import channels
import patterns
import KeyLabmk2Process as KLmk2Pr
import ArturiaCrossKeyboardKLmk2 as AKLmk2

from KeyLabmk2Dispatch import send_to_device


# This class handles visual feedback functions.

## CONSTANT

COLOR_PLAY_ON = bytes([0x02, 0x00, 0x10, 0x6D, 0x7F]) 
COLOR_PLAY_OFF = bytes([0x02, 0x00, 0x10, 0x6D, 0x00])
NB_TRACK_MAX = 125
REFRESH_COUNT = 0
PASS = False
WidMixer = 0
WidChannelRack = 1
WidPlaylist = 2
WidBrowser = 4
WidPlugin = 5


# MAPS

PAD_MAP = [
        0x70, 0x71, 0x72, 0x73,
        0x74, 0x75, 0x76, 0x77,
        0x78, 0x79, 0x7A, 0x7B,
        0x7C, 0x7D, 0x7E, 0x7F]
        
COLOR_MAP = [
        [0x7F, 0x00, 0x00], # RED
        [0x00, 0x00, 0x7F], # GREEN
        [0x00, 0x7F, 0x00], # BLUE
        [0x7F, 0x00, 0x7F], # MAGENTA
        [0x00, 0x7F, 0x7F], # CYAN
        [0x7F, 0x7F, 0x00]] # YELLOW

SELECT_MAP = [24, 25, 26, 27, 28, 29, 30, 31] # Matches Note 24-31 (Buttons 1-8)

class KeyLabLightReturn:
    def __init__(self):
        self._cache = {}

    def _send_cached(self, key, data):
        """Sends data to device only if it differs from the cached value."""
        if self._cache.get(key) != data:
            send_to_device(data)
            self._cache[key] = data

    def init(self) :
        self._cache = {} # Reset cache on init
        
        # FOR METRONOME
        self._step = 0
    
        # FOR INIT
        for i in range(0,16) :
            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x00, 0x00, 0x00, 0x7F]))
        
        for j in range(len(COLOR_MAP)) :
            
            colour = COLOR_MAP[j]
            
            for i in range(0,16) :
                time.sleep(0.01)
                send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[i], colour[0], colour[1], colour[2], 0x7F]))
                
            for i in range(0,16) :
                time.sleep(0.01)
                send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x00, 0x00, 0x00, 0x7F]))
        
        time.sleep(0.5)
        for i in range(0,16) :
            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x7F, 0x7F, 0x7F, 0x7F]))
        time.sleep(0.5)
        for i in range(0,16) :
            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x00, 0x00, 0x00, 0x7F]))


    def MetronomeReturn(self) :
        if ui.isMetronomeEnabled() :
            self._send_cached('metronome', bytes([0x02, 0x00, 0x10, 0x68, 0x7F]))
        else :
            self._send_cached('metronome', bytes([0x02, 0x00, 0x10, 0x68, 0x09]))

            
    def CountdownReturn(self) :
        if ui.isPrecountEnabled() :
            self._send_cached('countdown', bytes([0x02, 0x00, 0x10, 0x65, 0x7F]))
        else :
            self._send_cached('countdown', bytes([0x02, 0x00, 0x10, 0x65, 0x09]))


    def LoopReturn(self) :
        if ui.isLoopRecEnabled() :
            self._send_cached('loop', bytes([0x02, 0x00, 0x10, 0x6F, 0x7F]))
        else :
            self._send_cached('loop', bytes([0x02, 0x00, 0x10, 0x6F, 0x09]))


    def RecordReturn(self) :
        if transport.isRecording() :
            self._send_cached('record', bytes([0x02, 0x00, 0x10, 0x6E, 0x7F]))
        else :
            self._send_cached('record', bytes([0x02, 0x00, 0x10, 0x6E, 0x09]))


    def PlayReturn(self) :
        # Stop Button LED IDs: Try 0x6C (Original) and 0x5D (CC 93)
        # Play Button LED ID: 0x6D (Original)
        
        if transport.isPlaying():
            # Playing: Stop = 20% (0x14), Play = 100% (0x7F)
            stop_val = 0x14
            play_val = 0x7F
        else:
            # Stopped: Stop = 100% (0x7F), Play = Dim (0x14)
            stop_val = 0x7F
            play_val = 0x14
            
        # Send to 0x6C (Likely Stop)
        self._send_cached('stop_led_6c', bytes([0x02, 0x00, 0x10, 0x6C, stop_val]))
        # Send to 0x5D (CC 93 - Just in case)
        self._send_cached('stop_led_5d', bytes([0x02, 0x00, 0x10, 0x5D, stop_val]))
        
        # Send to Play
        self._send_cached('play_led', bytes([0x02, 0x00, 0x10, 0x6D, play_val]))


    def IsChannelSolo(self) :
        if not ui.getFocused(WidMixer):
            if channels.isChannelSolo(channels.channelNumber()) :
                self._send_cached('solo', bytes([0x02, 0x00, 0x10, 0x60, 0x7F]))              
            else :
                self._send_cached('solo', bytes([0x02, 0x00, 0x10, 0x60, 0x09]))
            
    def IsTrackSolo(self) :
        if ui.getFocused(WidMixer):
            if mixer.isTrackSolo(mixer.trackNumber()) :
                self._send_cached('solo', bytes([0x02, 0x00, 0x10, 0x60, 0x7F]))              
            else :
                self._send_cached('solo', bytes([0x02, 0x00, 0x10, 0x60, 0x09]))
    
 
    def IsChannelMuted(self) :
        if not ui.getFocused(WidMixer):
            if channels.isChannelMuted(channels.channelNumber()) :
                self._send_cached('mute', bytes([0x02, 0x00, 0x10, 0x61, 0x7F]))
            else :
                self._send_cached('mute', bytes([0x02, 0x00, 0x10, 0x61, 0x09]))
            
    def IsTrackMuted(self) :
        if ui.getFocused(WidMixer):
            if mixer.isTrackMuted(mixer.trackNumber()) :
                self._send_cached('mute', bytes([0x02, 0x00, 0x10, 0x61, 0x7F]))
            else :
                self._send_cached('mute', bytes([0x02, 0x00, 0x10, 0x61, 0x09]))

    
    def SetChannelMap(self) :
        if KLmk2Pr.MIXER_MODE :
            ACTIVE_CHANNELS = NB_TRACK_MAX
            NB_BANK = (ACTIVE_CHANNELS//8)+1
            ITEMS = (ACTIVE_CHANNELS%8)
            CHANNEL_MAP = NB_BANK*[8*[0]]
            for i in range(NB_BANK-1) :
                CHANNEL_MAP[i] = 8*[1]
            for i in range(ITEMS) :
                CHANNEL_MAP[NB_BANK-1][i] = 1
            return CHANNEL_MAP
        else :
            ACTIVE_CHANNELS = channels.channelCount()
            NB_BANK = (ACTIVE_CHANNELS//8)+1
            ITEMS = (ACTIVE_CHANNELS%8)
            CHANNEL_MAP = NB_BANK*[8*[0]]
            for i in range(NB_BANK-1) :
                CHANNEL_MAP[i] = 8*[1]
            for i in range(ITEMS) :
                CHANNEL_MAP[NB_BANK-1][i] = 1
            return CHANNEL_MAP
    

    def IntToRGB(self, value):
        # FL Studio Colors are often 0xBBGGRR or similar.
        # Standard INT in Python from FL API seems to be BGR or RGB depending on context?
        # Let's try standard extraction.
        # If value is 0xBBGGRR
        b = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        r = value & 0xFF
        return r, g, b

    def SelectedChannel(self) :
        # Update Button 9 (Master Sep) Feedback first
        btn9_id = 51
        sep = mixer.getTrackStereoSep(0)
        is_merged = (abs(sep - 1.0) < 0.1)
        
        if is_merged:
            should_light = (int(time.time() * 4) % 2) == 0 
            if should_light:
                self._send_cached("btn9", bytes([0x02, 0x00, 0x16, btn9_id, 0x7F, 0x00, 0x00, 0x7F]))
            else:
                self._send_cached("btn9", bytes([0x02, 0x00, 0x16, btn9_id, 0x00, 0x00, 0x00, 0x7F]))
        else:
            self._send_cached("btn9", bytes([0x02, 0x00, 0x16, btn9_id, 0x00, 0x7F, 0x40, 0x7F]))

        # Track Buttons 1-8
        
        # Determine Context
        is_mixer_focused = ui.getFocused(WidMixer)
        # Fallback to internal flag if focus check is unreliable or user toggled mode manually without focus change
        # But generally focus is best. Let's sync KLmk2Pr.MIXER_MODE if we can, or just use focus.
        # The user mentioned: "FL Studio’s API does not natively provide a direct “focused window” state" 
        # Wait, user prompt says: "detecting Focused Channel/Fader ... channels.selectedChannel() ... mixer.getTrackSelection()"
        # And "FL Studio’s API does not natively provide a direct 'focused window' state". 
        # ACTUALLY, ui.getFocused(WidMixer) IS available and works for many windows. 
        # If user says it doesn't provide it, maybe they mean for specific sub-windows? 
        # I will trust ui.getFocused(WidMixer) for now as I saw it used in KeyLabmk2Process.py.
        
        # We need to calculate which bank/offset we are in.
        # KeyLabmk2Pages.py/Navigation likely handles the offset variables (AKLmk2.MX_OFFSET, AKLmk2.CH_OFFSET).
        
        if is_mixer_focused:
            offset = AKLmk2.MX_OFFSET
            base_index = offset * 8 + 1 # Mixer tracks are 1-based usually for getTrackColor? 
            # mixer.getTrackColor(0) is Master. mixer.getTrackColor(1) is Insert 1.
            # Our buttons 1-8 map to checks 1-8, 9-16 etc.
            
            for i in range(8):
                track_idx = base_index + i
                btn_id = SELECT_MAP[i]
                cache_key = f"btn_rgb_{i}" # Cache by Physical Button Index, NOT Track Index!

                if track_idx > KLmk2Pr.MAX_TRACKS:
                    self._send_cached(cache_key, bytes([0x02, 0x00, 0x16, btn_id, 0x00, 0x00, 0x00, 0x7F]))
                    continue

                is_selected = (mixer.trackNumber() == track_idx)
                is_muted = mixer.isTrackMuted(track_idx)
                
                if is_muted:
                     # Red for Muted
                    self._send_cached(cache_key, bytes([0x02, 0x00, 0x16, btn_id, 0x7F, 0x00, 0x00, 0x7F]))
                else:
                    col = mixer.getTrackColor(track_idx)
                    r, g, b = self.IntToRGB(col)
                    
                    # If not selected, dim it
                    if not is_selected:
                        # Simple dimming
                        r = r // 8
                        g = g // 8
                        b = b // 8
                        # Ensure at least some visibility if it was bright? Or just allow it to be very dim.
                    
                    # Ensure range 0-127
                    r = min(127, max(0, r))
                    g = min(127, max(0, g))
                    b = min(127, max(0, b))

                    self._send_cached(cache_key, bytes([0x02, 0x00, 0x16, btn_id, r, g, b, 0x7F]))

        else:
            # Channel Rack Mode
            offset = AKLmk2.CH_OFFSET
            base_index = offset * 8 
            
            for i in range(8):
                chan_idx = base_index + i
                btn_id = SELECT_MAP[i]
                cache_key = f"btn_rgb_{i}"

                if chan_idx >= channels.channelCount():
                     self._send_cached(cache_key, bytes([0x02, 0x00, 0x16, btn_id, 0x00, 0x00, 0x00, 0x7F]))
                     continue

                is_selected = channels.isChannelSelected(chan_idx)
                is_muted = channels.isChannelMuted(chan_idx)

                if is_muted:
                    # Red for Muted
                    self._send_cached(cache_key, bytes([0x02, 0x00, 0x16, btn_id, 0x7F, 0x00, 0x00, 0x7F]))
                else:
                    col = channels.getChannelColor(chan_idx)
                    r, g, b = self.IntToRGB(col)

                    if not is_selected:
                        r = r // 8
                        g = g // 8
                        b = b // 8
                    
                    r = min(127, max(0, r))
                    g = min(127, max(0, g))
                    b = min(127, max(0, b))

                    self._send_cached(cache_key, bytes([0x02, 0x00, 0x16, btn_id, r, g, b, 0x7F]))


    def SequencerReturn(self) :
        if KLmk2Pr.SEQ_MODE == 1 :
            if not transport.getLoopMode() :
                for i in range (len(PAD_MAP)) :
                    if channels.getGridBit(channels.channelNumber(),i+(16*KLmk2Pr.RECT_OFFSET)) == 1 :
                        bit_velocity = channels.getCurrentStepParam( channels.channelNumber(), i+(16*KLmk2Pr.RECT_OFFSET), 1)
                        self._send_cached(f"seq_{i}", bytes([0x02, 0x00, 0x16, PAD_MAP[i], bit_velocity//4, bit_velocity//4, 0x00, 0x7F]))
                    else :
                        self._send_cached(f"seq_{i}", bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x7F, 0x7F, 0x7F, 0x7F]))
            else :
                for i in range(0,16) :
                    self._send_cached(f"seq_{i}", bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x7F, 0x00, 0x7F, 0x7F]))
        else :
            # Check Pad Mode and set color accordingly
            if KLmk2Pr.CURRENT_PAD_MODE == KLmk2Pr.PAD_MODE_CHROMATIC:
                r, g, b = KLmk2Pr.Hardware.Pads.COLOR_PURPLE_DIM
            else:
                r, g, b = KLmk2Pr.Hardware.Pads.COLOR_YELLOW_DIM
                
            for i in range (len(PAD_MAP)) :
                    self._send_cached(f"seq_{i}", bytes([0x02, 0x00, 0x16, PAD_MAP[i], r, g, b, 0x7F]))


    def ProcessPlayBlink(self, value):
        COLOR_PLAY_ON = bytes([0x02, 0x00, 0x10, 0x6D, 0x7F]) 
        COLOR_PLAY_OFF = bytes([0x02, 0x00, 0x10, 0x6D, 0x09])

        if value == 0 :
            self._send_cached('play_blink', COLOR_PLAY_OFF)        
        else :
            self._send_cached('play_blink', COLOR_PLAY_ON)

        
    def ProcessRecordBlink(self, value) :
        if transport.isRecording() :            
            COLOR_RECORDING_ON = bytes([0x02, 0x00, 0x10, 0x6E, 0x7F]) 
            COLOR_RECORDING_OFF = bytes([0x02, 0x00, 0x10, 0x6E, 0x09])
            if value == 0 :
                self._send_cached('rec_blink', COLOR_RECORDING_OFF)
            else :
                self._send_cached('rec_blink', COLOR_RECORDING_ON)
                 
    
    def ProcessSequencerBlink(self, value) :
        if KLmk2Pr.SEQ_MODE == 1 :
            if not transport.getLoopMode() :
                global REFRESH_COUNT
                global PASS
                PASS = False
                REFRESH_COUNT = 0
                actual_step = mixer.getSongStepPos()
                self.SequencerReturn()
                if actual_step in range (KLmk2Pr.RECT_OFFSET*16,16+KLmk2Pr.RECT_OFFSET*16) :
                    # This is dynamic, might need careful caching or just let it pass if it changes often
                    # But for now, let's cache it too
                    self._send_cached(f"seq_blink_{actual_step%16}", bytes([0x02, 0x00, 0x16, PAD_MAP[actual_step%16], 0x00, 0x00, 0x7F, 0x7F]))
                else :
                    self._send_cached(f"seq_blink_{actual_step%16}", bytes([0x02, 0x00, 0x16, PAD_MAP[actual_step%16], 0x7F, 0x00, 0x00, 0x7F]))

    
    def RefreshTime(self) :
        # Triggers a Fake OnUpdateBeatIndicator for sixteen notes  
        if KLmk2Pr.SEQ_MODE == 1 and mixer.getSongTickPos() != 0 :
            if not transport.getLoopMode() :
                global REFRESH_COUNT
                global PASS
                REFRESH_COUNT += 1
                tempo = mixer.getCurrentTempo(1)
                tresh = (60/tempo)/4
                if REFRESH_COUNT/22 >= tresh and PASS == False :
                    PASS = True
                    actual_step = mixer.getSongStepPos()
                    self.SequencerReturn()
                    if actual_step % 2 != 0 :
                        if actual_step in range (KLmk2Pr.RECT_OFFSET*16,16+KLmk2Pr.RECT_OFFSET*16) :
                            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[(actual_step)%16], 0x00, 0x00, 0x7F, 0x7F]))
                        else :
                            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[(actual_step)%16], 0x7F, 0x00, 0x00, 0x7F]))
                    else :
                        if actual_step in range (KLmk2Pr.RECT_OFFSET*16,16+KLmk2Pr.RECT_OFFSET*16) :
                            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[(actual_step+1)%16], 0x00, 0x00, 0x7F, 0x7F]))
                        else :
                            send_to_device(bytes([0x02, 0x00, 0x16, PAD_MAP[(actual_step+1)%16], 0x7F, 0x00, 0x00, 0x7F]))


    def NotBlinkingLed(self) :
    
        # DAW CONTROL LED
        # These are static, so we can check if they are already set.
        # We can use a single key for all of them if they always go together, 
        # or just cache each one.
        
        if self._cache.get('static_leds_sent'):
            return

        # Navigation Keys: Left (0x62/98), Right (0x63/99)
        send_to_device(bytes([0x02, 0x00, 0x10, 0x62, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x63, 0x7F]))
        
        # Track Buttons (0x64 - 0x6B) are handled by SelectedChannel with RGB.
        # Do NOT set them here, otherwise it overwrites with White.
        
        # Other static LEDs if any...
        # 0x69, 0x6A, 0x6B are in the original list... 
        # If mapped to Global/Track functions, they might be needed?
        # Hardware.DAW.Track has 0x38, 0x39 (56, 57).
        # Hardware.DAW.Global has 74, 87, 88, 89, 81.
        # The IDs here 0x64 to 0x6B are 100 to 107.
        # These are definitely the Track Select Buttons.
        # So we remove them entirely from here.
        
        # CENTER LED (Navigation?)
        # Original: 0x1A, 0x1B. 
        # Adding Navigation Keys: Left (0x62/98), Right (0x63/99), Knob (0x54/84)
        
        send_to_device(bytes([0x02, 0x00, 0x10, 0x1A, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x1B, 0x7F]))
        
        # Try to light up Navigation Keys (100% brightness)
        # Left Arrow
        send_to_device(bytes([0x02, 0x00, 0x10, 0x62, 0x7F]))
        # Right Arrow
        send_to_device(bytes([0x02, 0x00, 0x10, 0x63, 0x7F]))
        # Knob Push / Center
        send_to_device(bytes([0x02, 0x00, 0x10, 0x54, 0x7F]))
        
        # CHANNELS LEDS
        send_to_device(bytes([0x02, 0x00, 0x16, 0x2A, 0x7F, 0x7F, 0x7F, 0x7F]))
        
        self._cache['static_leds_sent'] = True
