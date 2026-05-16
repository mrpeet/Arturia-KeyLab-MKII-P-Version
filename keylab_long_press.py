# KeyLab mkII — Long-press detection (shared)
# Fires on_long via OnIdle when threshold is reached while the key is still held.
# on_short runs on release only if on_long did not fire.

import time

LONG_PRESS_THRESHOLD = 0.75  # seconds

_active = {}


def begin(key, on_long, on_short=None):
    """Register a held control. on_long runs once when threshold is reached."""
    _active[key] = {
        'start': time.time(),
        'fired': False,
        'on_long': on_long,
        'on_short': on_short,
    }


def release(key):
    """End a press; run on_short if long did not fire. Returns True if long fired."""
    entry = _active.pop(key, None)
    if entry is None:
        return False
    if not entry['fired'] and entry['on_short'] is not None:
        entry['on_short']()
    return entry['fired']


def cancel(key):
    """Drop tracking without running short or long."""
    _active.pop(key, None)


def poll():
    """Call from OnIdle — fire on_long when hold duration reaches threshold."""
    now = time.time()
    for key in list(_active.keys()):
        entry = _active[key]
        if entry['fired']:
            continue
        if now - entry['start'] >= LONG_PRESS_THRESHOLD:
            entry['fired'] = True
            if entry['on_long'] is not None:
                entry['on_long']()
