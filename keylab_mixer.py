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
#  Track Button long-press state
# ---------------------------------------------------------------------------
_btn_press_times = {}  # index → press timestamp
_LONG_PRESS_THRESHOLD = 1.0  # seconds


# ---------------------------------------------------------------------------
#  Main dispatcher
# ---------------------------------------------------------------------------

def handle_mixer(event, state, pages):
    """Route fader, encoder and track button events.

    Returns True if handled, False otherwise.
    """
    # --- Fader: Pitch Bend on channels 0–8 ---
    if event.midiId == PITCH_BEND_STATUS and event.midiChan in Fader.ALL_CHANNELS:
        _do_fader(event, state, pages)
        event.handled = True
        return True

    if event.midiId in (NOTE_ON_STATUS, NOTE_OFF_STATUS) and event.midiChan == 0:
        # --- Touch sensor: notes 104–112 ---
        if event.data1 in Fader.ALL_TOUCH_NOTES:
            _do_fader_touch(event, state, pages)
            event.handled = True
            return True

        # --- Track buttons: notes 24–32 ---
        if event.data1 in TrackButton.ALL_NOTES:
            _do_track_button(event, state, pages)
            event.handled = True
            return True

        # --- Bank Prev/Next: notes 48–49 ---
        if event.data1 in BankButton.ALL_NOTES:
            if event.data2 > 0:
                _do_bank(event, state, pages)
            event.handled = True
            return True

    # --- Encoder (Pan): CC 16–24 ---
    if event.midiId == CC_STATUS and event.midiChan == 0 and event.data1 in Encoder.ALL_CCS:
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

    # Relative value: 1–63 = right, 65–127 = left
    raw = event.data2
    if raw < 64:
        delta = raw * _PAN_STEP
    else:
        delta = -(raw - 64) * _PAN_STEP

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
    """Short press = Reset Pan, Long press = Toggle Mute."""
    index = event.data1 - TrackButton.FIRST  # 0–8

    if event.data2 > 0:
        _btn_press_times[index] = time.time()
    else:
        duration = time.time() - _btn_press_times.get(index, 0)
        if duration >= _LONG_PRESS_THRESHOLD:
            _toggle_mute(index, state, pages)
        else:
            _reset_pan(index, state, pages)


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
    """Shift bank offset left or right by 8 channels/tracks."""
    if event.data1 == BankButton.PART2_PREV:
        state.bank_offset = max(0, state.bank_offset - 1)
    else:
        state.bank_offset += 1
    # Reset fader pickup so values don't jump after bank change
    state.fader_pickup_active = [False] * Fader.COUNT
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


# ---------------------------------------------------------------------------
#  Display helper
# ---------------------------------------------------------------------------

def _show_hint(pages, fader_index, value_str):
    """Show fader value hint on LCD."""
    label = "Master" if fader_index == Fader.MASTER_CHANNEL else "Fader %d" % (fader_index + 1)
    pages.SetPageLines('fader', line1=label, line2=value_str)
    pages.SetActivePage('fader', expires=800)
