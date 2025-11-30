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

SELECT_MAP = [0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29]

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
        if mixer.getSongTickPos() != 0 :
            self._send_cached('play', bytes([0x02, 0x00, 0x10, 0x6D, 0x7F]) + bytes([0x02, 0x00, 0x10, 0x6C, 0x09]))
        else :
            self._send_cached('play', bytes([0x02, 0x00, 0x10, 0x6D, 0x09]) + bytes([0x02, 0x00, 0x10, 0x6C, 0x7F]))


    def IsChannelSolo(self) :
        if ui.getFocused(WidChannelRack):
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
        if ui.getFocused(WidChannelRack):
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
    

    def SelectedChannel(self) :
        # Optimization: Construct the full message payload and check against cache
        # instead of sending individual messages.
        
        current_state_key = f"selected_ch_{KLmk2Pr.MIXER_MODE}_{AKLmk2.MX_OFFSET if KLmk2Pr.MIXER_MODE else AKLmk2.CH_OFFSET}_{channels.channelNumber() if not KLmk2Pr.MIXER_MODE else mixer.trackNumber()}"
        
        # We also need to account for selection/mute changes in the bank
        # This is complex to cache perfectly without reading all states, 
        # but we can at least prevent re-sending if nothing changed in the focused window/bank.
        
        # For now, let's just cache the individual LED messages to avoid spamming the same color.
        
        if KLmk2Pr.MIXER_MODE :
            CHANNEL_MAP = self.SetChannelMap()
            ACTIVE_CHANNEL = mixer.trackNumber()-1
            BANK_SELECTED = AKLmk2.MX_OFFSET
            for j in range(len(CHANNEL_MAP[BANK_SELECTED])) :
                if CHANNEL_MAP[BANK_SELECTED][j] == 1 :
                    index = j+(8*BANK_SELECTED)+1
                    cache_key = f"sel_mix_{j}"
                    msg = None
                    
                    if ACTIVE_CHANNEL//8 != BANK_SELECTED :
                        if mixer.isTrackSelected(index) and not mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x7F, 0x00, 0x7F])
                        elif mixer.isTrackSelected(index) and mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                        elif not mixer.isTrackSelected(index) and not mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x00, 0x00, 0x7F, 0x7F])
                        elif not mixer.isTrackSelected(index) and mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                    elif ACTIVE_CHANNEL//8 == BANK_SELECTED :
                        if mixer.isTrackSelected(index) and not mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x7F, 0x00, 0x7F])
                        elif mixer.isTrackSelected(index) and mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                        elif not mixer.isTrackSelected(index) and not mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x00, 0x00, 0x7F, 0x7F])
                        elif not mixer.isTrackSelected(index) and mixer.isTrackMuted(index) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                    
                    if msg: self._send_cached(cache_key, msg)

                else :
                    self._send_cached(f"sel_mix_{j}", bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x00, 0x00, 0x00, 0x7F]))
        else :
            CHANNEL_MAP = self.SetChannelMap()
            ACTIVE_CHANNEL = channels.channelNumber()
            BANK_SELECTED = AKLmk2.CH_OFFSET
            for j in range(len(CHANNEL_MAP[BANK_SELECTED])) :
                if CHANNEL_MAP[BANK_SELECTED][j] == 1 :
                    cache_key = f"sel_chan_{j}"
                    msg = None
                    if ACTIVE_CHANNEL//8 != BANK_SELECTED :
                        if channels.isChannelSelected(j+(8*BANK_SELECTED)) and not channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x7F, 0x00, 0x7F])
                        elif channels.isChannelSelected(j+(8*BANK_SELECTED)) and channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                        elif not channels.isChannelSelected(j+(8*BANK_SELECTED)) and not channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x7F, 0x7F])
                        elif not channels.isChannelSelected(j+(8*BANK_SELECTED)) and channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                    elif ACTIVE_CHANNEL//8 == BANK_SELECTED :
                        if channels.isChannelSelected(j+(8*BANK_SELECTED)) and not channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x7F, 0x00, 0x7F])
                        elif channels.isChannelSelected(j+(8*BANK_SELECTED)) and channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                        elif not channels.isChannelSelected(j+(8*BANK_SELECTED)) and not channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x7F, 0x7F])
                        elif not channels.isChannelSelected(j+(8*BANK_SELECTED)) and channels.isChannelMuted(j+(8*BANK_SELECTED)) :
                            msg = bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x7F, 0x00, 0x00, 0x7F])
                    
                    if msg: self._send_cached(cache_key, msg)
                else :
                    self._send_cached(f"sel_chan_{j}", bytes([0x02, 0x00, 0x16, SELECT_MAP[j], 0x00, 0x00, 0x00, 0x7F]))


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
            for i in range (len(PAD_MAP)) :
                    self._send_cached(f"seq_{i}", bytes([0x02, 0x00, 0x16, PAD_MAP[i], 0x7F, 0x00, 0x00, 0x7F]))


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

        send_to_device(bytes([0x02, 0x00, 0x10, 0x62, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x63, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x64, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x65, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x66, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x67, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x69, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x6A, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x6B, 0x7F]))
        
        # CENTER LED
        
        send_to_device(bytes([0x02, 0x00, 0x10, 0x1A, 0x7F]))
        send_to_device(bytes([0x02, 0x00, 0x10, 0x1B, 0x7F]))
        
        # CHANNELS LEDS
        
        send_to_device(bytes([0x02, 0x00, 0x16, 0x2A, 0x7F, 0x7F, 0x7F, 0x7F]))
        
        self._cache['static_leds_sent'] = True
