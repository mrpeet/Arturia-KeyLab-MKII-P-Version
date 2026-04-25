# KeyLab mkII — Mixer Handler
# Handles: Fader (Volume), Encoder (Pan), Track Buttons, Bank Buttons
# Supports: Mixer Mode + Channel Rack Mode (auto-switch by focused window)
# Phase 8+9 — see ROADMAP.md

import time

import channels
import midi
import mixer
import ui

from keylab_config import (
    BankButton,
    Encoder,
    Fader,
    TrackButton,
    NOTE_ON_STATUS,
    NOTE_OFF_STATUS,
    CC_STATUS,
    PITCH_BEND_STATUS,
)


# ---------------------------------------------------------------------------
#  Pitch Bend value helpers
# ---------------------------------------------------------------------------

# FL Studio volume API: 0.8 = 100%, 1.0 = 125% (overdrive).
# We map fader full travel to 100% (0.8) to match the hardware expectation.
_FL_VOLUME_SCALE = 0.8


def _pb_to_float(data1, data2):
    """Convert 14-bit Pitch Bend (data1=LSB, data2=MSB) to 0.0–1.0."""
    return (data2 * 128 + data1) / 16383.0


def _pb_to_raw(data1, data2):
    """Convert Pitch Bend bytes to raw 14-bit integer (0–16383)."""
    return data2 * 128 + data1


# ---------------------------------------------------------------------------
#  Long-press state (Track Buttons + Bank Prev for Free Mode)
# ---------------------------------------------------------------------------
_btn_press_times = {}   # track button index → press timestamp
_bank_prev_press_time = 0.0
_LONG_PRESS_THRESHOLD = 1.0  # seconds


# ---------------------------------------------------------------------------
#  Free Mode: Jitter-Filtered Pitch Bend Passthrough for Faders
# ---------------------------------------------------------------------------

def handle_free_fader(event, state):
    """Jitter-filtered Pitch Bend passthrough for Free Mode faders.

    Returns True if event was filtered and should be passed to FL,
    False if not a Free Mode fader event.
    """
    if not state.free_mode:
        return False

    if event.midiId != PITCH_BEND_STATUS or event.midiChan not in Fader.ALL_CHANNELS:
        return False

    index = event.midiChan
    if index >= Fader.MASTER_CHANNEL:  # Master fader - let normal mixer handle it
        return False

    raw = _pb_to_raw(event.data1, event.data2)

    # Jitter filter - suppress noise from aging faders
    if abs(raw - state.fader_last_sent_value[index]) < state.FADER_JITTER_THRESHOLD:
        return False  # Swallow the event (jitter)

    state.fader_last_sent_value[index] = raw
    return True  # Pass filtered event to FL Studio


# ---------------------------------------------------------------------------
#  Free Mode: Virtual Absolute Encoders
# ---------------------------------------------------------------------------

def handle_free_encoder(event, state):
    """Convert relative encoder to absolute CC in Free Mode.

    Modifies event.data2 to the new absolute value (0-127).
    Returns True if event was modified (should be passed to FL),
    False if not a Free Mode encoder event.
    """
    if not state.free_mode:
        return False

    if event.midiId != CC_STATUS or event.midiChan != 0:
        return False

    if event.data1 not in Encoder.ALL_CCS:
        return False

    index = event.data1 - Encoder.FIRST
    if index >= 8:  # Master encoder (slot 9) - passthrough unchanged
        return False

    # Relative to absolute conversion with acceleration
    # Speed detection: 1-2=slow, 3-10=medium, 11-20=fast, 21+=very fast
    if event.data2 <= Encoder.INCREMENT_MAX:
        # Right: determine step size by rotation speed
        speed = event.data2
        if speed <= 2:
            step = 1
        elif speed <= 10:
            step = 3
        elif speed <= 20:
            step = 5
        else:
            step = 10
        state.free_encoder_values[index] = min(127, state.free_encoder_values[index] + step)
    else:
        # Left: determine step size by rotation speed (65=1, 127=63)
        speed = event.data2 - Encoder.DECREMENT_BASE
        if speed <= 2:
            step = 1
        elif speed <= 10:
            step = 3
        elif speed <= 20:
            step = 5
        else:
            step = 10
        state.free_encoder_values[index] = max(0, state.free_encoder_values[index] - step)

    # Modify event to absolute value for FL Studio
    event.data2 = state.free_encoder_values[index]
    return True


# ---------------------------------------------------------------------------
#  Main dispatcher
# ---------------------------------------------------------------------------

def handle_mixer(event, state, pages):
    """Route fader, encoder and track button events.

    Returns True if handled, False otherwise.
    """
    # --- Fader: Pitch Bend on channels 0–8 ---
    if event.midiId == PITCH_BEND_STATUS and event.midiChan in Fader.ALL_CHANNELS:
        index = event.midiChan
        if index < Fader.MASTER_CHANNEL:
            if state.free_mode:
                return False  # Passthrough: slot 1–8 in Free Mode (handled by handle_free_fader)
            if state.plugin_mode:
                # Plugin focus without Free Mode: show hint that faders are disabled
                pages.SetPageLines('fader', line1='Fader %d' % (index + 1), line2='Use Free Mode')
                pages.SetActivePage('fader', expires=1000)
                event.handled = True
                return True  # Swallow the event
        _do_fader(event, state, pages)
        event.handled = True
        return True

    if event.midiId in (NOTE_ON_STATUS, NOTE_OFF_STATUS) and event.midiChan == 0:
        # --- Touch sensor: notes 104–112 ---
        if event.data1 in Fader.ALL_TOUCH_NOTES:
            index = event.data1 - Fader.TOUCH_1
            if index < Fader.MASTER_CHANNEL:
                if state.free_mode:
                    return False  # Passthrough touch in Free Mode
                if state.plugin_mode:
                    # Plugin focus without Free Mode: show hint
                    pages.SetPageLines('fader', line1='Fader %d' % (index + 1), line2='Use Free Mode')
                    pages.SetActivePage('fader', expires=1000)
                    event.handled = True
                    return True  # Swallow the event
            _do_fader_touch(event, state, pages)
            event.handled = True
            return True

        # --- Track buttons: notes 24–32 ---
        if event.data1 in TrackButton.ALL_NOTES:
            index = event.data1 - TrackButton.FIRST
            if state.plugin_mode and index < 8:
                return False  # Plugin focus: track buttons 1-8 disabled
            if state.free_mode and index < 8:
                return False  # Passthrough track buttons 1–8 in Free Mode
            _do_track_button(event, state, pages)
            event.handled = True
            return True

        # --- Bank Prev/Next: notes 48–49 ---
        if event.data1 in BankButton.ALL_NOTES:
            _do_bank(event, state, pages)
            event.handled = True
            return True

    # --- Encoder (Pan / Plugin): CC 16–24 ---
    if event.midiId == CC_STATUS and event.midiChan == 0 and event.data1 in Encoder.ALL_CCS:
        index = event.data1 - Encoder.FIRST
        if state.plugin_mode and index < 8:
            return False  # Plugin focus: encoders 1-8 disabled (handled by plugin handler)
        if state.free_mode and index < 8:
            return False  # Passthrough encoders 1–8 in Free Mode
        _do_encoder(event, state, pages)
        event.handled = True
        return True

    return False


# ---------------------------------------------------------------------------
#  Fader — Volume with jitter filter + soft pickup
# ---------------------------------------------------------------------------

def _do_fader(event, state, pages):
    """Handle Pitch Bend fader movement."""
    index = event.midiChan  # 0–8 (8 = Master)
    raw   = _pb_to_raw(event.data1, event.data2)
    value = _pb_to_float(event.data1, event.data2)

    # --- Jitter filter ---
    if abs(raw - state.fader_last_sent_value[index]) < state.FADER_JITTER_THRESHOLD:
        return

    # --- Determine target FL value for soft pickup ---
    # _get_current_fl_volume returns FL API scale (0.0–0.8 = 0–100%).
    # Convert to fader scale (0.0–1.0) for comparison with incoming value.
    fl_raw = _get_current_fl_volume(index, state)
    if fl_raw < 0.0:
        return  # Invalid slot
    fl_value = fl_raw / _FL_VOLUME_SCALE  # → 0.0–1.0 fader scale

    # --- Soft pickup ---
    if not state.fader_pickup_active[index]:
        if abs(value - fl_value) < 0.05:
            state.fader_pickup_active[index] = True
        else:
            _show_hint(pages, index, "-> %d%%" % int(fl_value * 100))
            return

    # --- Apply volume ---
    state.fader_last_sent_value[index] = raw
    _set_fl_volume(index, value, state)
    _show_hint(pages, index, "%d%%" % int(value * 100))  # Show 0–100 % to user


def _get_current_fl_volume(index, state):
    """Return current FL Studio volume for this fader slot (0.0–1.0), or -1 on error."""
    try:
        if index == Fader.MASTER_CHANNEL:
            return mixer.getTrackVolume(0)
        if ui.getFocused(midi.widMixer):
            track = index + 1 + state.bank_offset * 8
            if track >= mixer.getTrackCount():
                return -1.0
            return mixer.getTrackVolume(track)
        else:
            ch = index + state.bank_offset * 8
            if ch >= channels.channelCount():
                return -1.0
            return channels.getChannelVolume(ch)
    except Exception:
        return -1.0


def _set_fl_volume(index, value, state):
    """Apply volume to the correct FL Studio target.

    Scales 0.0–1.0 fader range to 0.0–0.8 FL API range (0.8 = 100%).
    """
    fl_value = value * _FL_VOLUME_SCALE
    if index == Fader.MASTER_CHANNEL:
        mixer.setTrackVolume(0, fl_value)
        return
    if ui.getFocused(midi.widMixer):
        track = index + 1 + state.bank_offset * 8
        if track < mixer.getTrackCount():
            mixer.setTrackVolume(track, fl_value)
    else:
        ch = index + state.bank_offset * 8
        if ch < channels.channelCount():
            channels.setChannelVolume(ch, fl_value)


# ---------------------------------------------------------------------------
#  Touch sensor — show track name on touch, restore on release
# ---------------------------------------------------------------------------

def _do_fader_touch(event, state, pages):
    """Show track/channel name when fader is touched; release = pickup reset."""
    index = event.data1 - Fader.TOUCH_1  # 0–8

    if event.data2 > 0:
        # Touched — show name
        name = _get_slot_name(index, state)
        pages.SetPageLines('fader', line1='Fader %d' % (index + 1), line2=name)
        pages.SetActivePage('fader', expires=2000)
    else:
        # Released — reset pickup so FL mouse moves don't cause drift
        state.fader_pickup_active[index] = False


def _get_slot_name(index, state):
    """Return mixer track or channel name for this fader slot."""
    try:
        if index == Fader.MASTER_CHANNEL:
            return mixer.getTrackName(0)
        if ui.getFocused(midi.widMixer):
            track = index + 1 + state.bank_offset * 8
            return mixer.getTrackName(track) if track < mixer.getTrackCount() else "---"
        else:
            ch = index + state.bank_offset * 8
            return channels.getChannelName(ch) if ch < channels.channelCount() else "---"
    except Exception:
        return "---"


# ---------------------------------------------------------------------------
#  Encoder — Pan (relative)
# ---------------------------------------------------------------------------

_PAN_STEP = 0.02  # Pan delta per encoder tick


def _do_encoder(event, state, pages):
    """Relative encoder → Pan control."""
    index = event.data1 - Encoder.FIRST  # 0–8

    # Relative value: 0-63 = increment (right), 64-127 = decrement (left)
    raw = event.data2
    if raw <= Encoder.INCREMENT_MAX:
        # Increment: scale by speed, minimum 1
        speed = max(1, raw) if raw >= Encoder.INCREMENT_MIN else 1
        delta = speed * _PAN_STEP
    else:
        # Decrement: 64 = -1, 65 = -2, ... 127 = -63
        speed = max(1, raw - Encoder.DECREMENT_BASE)  # 64->0->1, 65->1, 127->63
        delta = -speed * _PAN_STEP

    if delta == 0:
        return

    _apply_pan(index, delta, state, pages)


def _apply_pan(index, delta, state, pages):
    """Apply pan delta to mixer track or channel."""
    try:
        if ui.getFocused(midi.widMixer):
            track = index + 1 + state.bank_offset * 8
            if track >= mixer.getTrackCount():
                return
            current = mixer.getTrackPan(track)
            new_val = max(-1.0, min(1.0, current + delta))
            mixer.setTrackPan(track, new_val)
            label = mixer.getTrackName(track)
        else:
            ch = index + state.bank_offset * 8
            if ch >= channels.channelCount():
                return
            current = channels.getChannelPan(ch)
            new_val = max(-1.0, min(1.0, current + delta))
            channels.setChannelPan(ch, new_val)
            label = channels.getChannelName(ch)
        _show_pan_hint(pages, index, label, new_val)
    except Exception:
        pass


def _show_pan_hint(pages, index, label, pan_value):
    """Show pan value as L/C/R percentage on LCD."""
    if pan_value < -0.01:
        pan_str = "L %d%%" % int(-pan_value * 100)
    elif pan_value > 0.01:
        pan_str = "R %d%%" % int(pan_value * 100)
    else:
        pan_str = "Center"
    pages.SetPageLines('enc', line1=label, line2=pan_str)
    pages.SetActivePage('enc', expires=800)


# ---------------------------------------------------------------------------
#  Track Buttons — Short press = Reset Pan, Long press = Toggle Mute
# ---------------------------------------------------------------------------

def _do_track_button(event, state, pages):
    """Track button handler — behavior depends on focused window.

    Mixer focus:
        Short press = Reset Pan
        Long press = Toggle Mute

    Channel Rack focus:
        Short press = Toggle Mute
        Long press = Toggle Solo
    """
    index = event.data1 - TrackButton.FIRST  # 0–8

    if event.data2 > 0:
        _btn_press_times[index] = time.time()
    else:
        duration = time.time() - _btn_press_times.get(index, 0)
        is_mixer = ui.getFocused(midi.widMixer)
        if duration >= _LONG_PRESS_THRESHOLD:
            # Long press: Mute (Mixer) or Solo (Channel Rack)
            if is_mixer:
                _toggle_mute(index, state, pages)
            else:
                _toggle_solo(index, state, pages)
        else:
            # Short press: Pan Reset (Mixer) or Mute (Channel Rack)
            if is_mixer:
                _reset_pan(index, state, pages)
            else:
                _toggle_mute(index, state, pages)


def _reset_pan(index, state, pages):
    """Reset pan to center for this slot."""
    try:
        if ui.getFocused(midi.widMixer):
            track = index + 1 + state.bank_offset * 8
            if track < mixer.getTrackCount():
                mixer.setTrackPan(track, 0.0)
                pages.SetPageLines('enc', line1=mixer.getTrackName(track), line2='Pan Reset')
                pages.SetActivePage('enc', expires=800)
        else:
            ch = index + state.bank_offset * 8
            if ch < channels.channelCount():
                channels.setChannelPan(ch, 0.0)
                pages.SetPageLines('enc', line1=channels.getChannelName(ch), line2='Pan Reset')
                pages.SetActivePage('enc', expires=800)
    except Exception:
        pass


def _do_bank(event, state, pages):
    """Bank Prev/Next handling.

    Bank Prev short press  → bank_offset - 1
    Bank Prev long press   → toggle Free Mode
    Bank Next short press  → bank_offset + 1
    """
    global _bank_prev_press_time

    if event.data1 == BankButton.PART2_PREV:
        if event.data2 > 0:
            # Record press time
            _bank_prev_press_time = time.time()
        else:
            # Release — decide short vs long
            duration = time.time() - _bank_prev_press_time
            if duration >= _LONG_PRESS_THRESHOLD:
                state.free_mode = not state.free_mode
                if state.free_mode:
                    pages.SetPageLines('bank', line1='FREE MODE', line2='Active')
                else:
                    pages.SetPageLines('bank', line1='FREE MODE', line2='Off')
                pages.SetActivePage('bank', expires=1500)
            else:
                state.bank_offset = max(0, state.bank_offset - 1)
                _show_bank_hint(state, pages)
    else:
        # Bank Next — only on press
        if event.data2 > 0:
            state.bank_offset += 1
            _show_bank_hint(state, pages)
    # Reset fader pickup after any bank change
    state.fader_pickup_active = [False] * Fader.COUNT


def _show_bank_hint(state, pages):
    pages.SetPageLines('bank', line1='Bank', line2='Tracks %d-%d' % (
        state.bank_offset * 8 + 1, state.bank_offset * 8 + 8))
    pages.SetActivePage('bank', expires=1200)


def _toggle_mute(index, state, pages):
    """Toggle mute for this slot."""
    try:
        if ui.getFocused(midi.widMixer):
            track = index + 1 + state.bank_offset * 8
            if track < mixer.getTrackCount():
                mixer.muteTrack(track)
                status = 'Muted' if mixer.isTrackMuted(track) else 'Unmuted'
                pages.SetPageLines('enc', line1=mixer.getTrackName(track), line2=status)
                pages.SetActivePage('enc', expires=1000)
        else:
            ch = index + state.bank_offset * 8
            if ch < channels.channelCount():
                channels.muteChannel(ch)
                status = 'Muted' if channels.isChannelMuted(ch) else 'Unmuted'
                pages.SetPageLines('enc', line1=channels.getChannelName(ch), line2=status)
                pages.SetActivePage('enc', expires=1000)
    except Exception:
        pass


def _toggle_solo(index, state, pages):
    """Toggle solo for Channel Rack channel (Mixer: fallback to track solo)."""
    try:
        if ui.getFocused(midi.widMixer):
            track = index + 1 + state.bank_offset * 8
            if track < mixer.getTrackCount():
                mixer.soloTrack(track)
                status = 'Solo' if mixer.isTrackSolo(track) else 'Unsolo'
                pages.SetPageLines('enc', line1=mixer.getTrackName(track), line2=status)
                pages.SetActivePage('enc', expires=1000)
        else:
            ch = index + state.bank_offset * 8
            if ch < channels.channelCount():
                channels.soloChannel(ch)
                status = 'Solo' if channels.isChannelSolo(ch) else 'Unsolo'
                pages.SetPageLines('enc', line1=channels.getChannelName(ch), line2=status)
                pages.SetActivePage('enc', expires=1000)
    except Exception:
        pass


# ---------------------------------------------------------------------------
#  Display helper
# ---------------------------------------------------------------------------

def _show_hint(pages, fader_index, value_str):
    """Show fader value hint on LCD."""
    label = "Master" if fader_index == Fader.MASTER_CHANNEL else "Fader %d" % (fader_index + 1)
    pages.SetPageLines('fader', line1=label, line2=value_str)
    pages.SetActivePage('fader', expires=800)
