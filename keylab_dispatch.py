# MIT License
# Copyright (c) 2020 Ray Juang

import time

import device


# MIDI event dispatcher transforms the MIDI event into a value through a transform function provided at construction
# time. This value is then used as a key into a lookup table that provides a dispatcher and filter function. If the
# filter function returns true, then the event is sent to the dispatcher function.

class MidiEventDispatcher:

    def __init__(self, transform_fn):
        self._transform_fn = transform_fn
        # Table contains a mapping of status code -> (callback_fn, filter_fn)
        self._dispatch_map = {}

    def NewHandler(self, key, callback_fn, filter_fn=None):
        # param key: the result value of transform_fn(event) to match against.
        # param callback_fn: function that is called with the event in the event the transformed event matches.
        # param filter_fn: function that takes an event and returns true if the event should be dispatched. If false
        # is returned, then the event is dropped and never passed to callback_fn. Not specifying means that callback_fn
        # is always called if transform_fn matches the key.
        def _default_true_fn(_): return True
        if filter_fn is None:
            filter_fn = _default_true_fn
        self._dispatch_map[key] = (callback_fn, filter_fn)
        return self

    def NewHandlerForKeys(self, keys, callback_fn, filter_fn=None):
        # Same function but for a group of controls
        for k in keys:
            self.NewHandler(k, callback_fn, filter_fn=filter_fn)
        return self

    def Dispatch(self, event):
        key = self._transform_fn(event)
        processed = False
        if key in self._dispatch_map:
            callback_fn, filter_fn = self._dispatch_map[key]
            if filter_fn(event):
                callback_fn(event)
                processed = True
            else:
                processed = True
        return processed


# SysEx rate monitor: prints a warning to FL's Script Output when one script
# sends more than _SYSEX_WARN_PER_SEC messages within one second. Messages are
# never dropped here — LED/display caches assume every send reaches the device.
_SYSEX_WARN_PER_SEC = 150
_rate_window_start = 0.0
_rate_count = 0


def _track_sysex_rate():
    global _rate_window_start, _rate_count
    now = time.monotonic()
    if now - _rate_window_start >= 1.0:
        if _rate_count > _SYSEX_WARN_PER_SEC:
            print("KeyLab WARNING: %d SysEx/s to device (%s)" % (
                _rate_count, time.strftime("%H:%M:%S")))
        _rate_window_start = now
        _rate_count = 0
    _rate_count += 1


def send_to_device(data):
    _track_sysex_rate()
    device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]) + data + bytes([0xF7]))
