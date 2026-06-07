# KeyLab mkII - Shared State (cross-port)
# State shared between device_KeyLabmkII.py (DAW port) and
# device_KeyLabmkII_Forward.py (Keys port).
#
# FL Studio gives each device script its own Python interpreter, so plain
# module-level globals are NOT shared between ports. We use two layers:
#   1. `sys._keylab_pad_state`  — in-memory dict, fast, local to this interpreter
#   2. `keylab_pad_state.json`  — file on disk, slow, visible to both interpreters
#
# READ STRATEGY (solves two bugs at once):
#   - If this interpreter WROTE the file last (_last_write_mtime == current mtime)
#     → the in-memory store is already up-to-date; return it directly.
#     (Prevents the stale-cache overwrite: DAW script's freshly-set value is
#      never clobbered by a re-read of the same file it just wrote.)
#   - If the file is NEWER than our last write
#     → another interpreter (e.g. Forward) wrote it; sync store from file.
#     (Keeps the Forward script's store fresh when the DAW script changes state.)

import os
import sys as _sys

PAD_BANK_COUNT = 6

PAD_MODE_FPC = 'fpc'
PAD_MODE_CHROMATIC = 'chromatic'

_KEY = '_keylab_pad_state'
_DEFAULTS = {
    'pad_mode': PAD_MODE_CHROMATIC,
    'pad_bank_offset': 0,
    'pad_velocity_enabled': True,
    'pad_led_dirty': False,
}

_STATE_FILENAME = 'keylab_pad_state.json'


def _state_file_path():
    try:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), _STATE_FILENAME)
    except Exception:
        return _STATE_FILENAME


# ---------------------------------------------------------------------------
#  File cache
# ---------------------------------------------------------------------------

_last_write_mtime = 0.0   # mtime of the file as WE last wrote it (0 = never)
_last_read_mtime = 0.0    # mtime of the file as WE last read it
_cached_file_data = None


def _read_file_state():
    """Parse the state file; return dict or None. Caches by mtime."""
    global _last_read_mtime, _cached_file_data
    path = _state_file_path()
    try:
        mtime = os.path.getmtime(path)
        if mtime == _last_read_mtime and _cached_file_data is not None:
            return _cached_file_data

        with open(path, 'r') as f:
            text = f.read().strip()

        _last_read_mtime = mtime

        if not text:
            _cached_file_data = None
            return None

        data = {}
        for line in text.splitlines():
            if '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.strip()
            val = val.strip()
            if key == 'pad_mode':
                data['pad_mode'] = val
            elif key == 'pad_bank_offset':
                try:
                    data['pad_bank_offset'] = int(val)
                except ValueError:
                    pass
            elif key == 'pad_velocity_enabled':
                data['pad_velocity_enabled'] = val in ('1', 'true', 'True', 'on', 'On')
            elif key == 'pad_led_dirty':
                data['pad_led_dirty'] = val in ('1', 'true', 'True', 'on', 'On')

        _cached_file_data = data if data else None
        return _cached_file_data
    except Exception:
        return _cached_file_data


def _write_file_state(data):
    """Write state to file; record the resulting mtime so we know WE wrote it."""
    global _last_write_mtime, _last_read_mtime, _cached_file_data
    path = _state_file_path()
    try:
        with open(path, 'w') as f:
            f.write('pad_mode=%s\n' % data.get('pad_mode', PAD_MODE_CHROMATIC))
            f.write('pad_bank_offset=%d\n' % int(data.get('pad_bank_offset', 0)))
            vel = data.get('pad_velocity_enabled', True)
            f.write('pad_velocity_enabled=%d\n' % (1 if vel else 0))
            dirty = data.get('pad_led_dirty', False)
            f.write('pad_led_dirty=%d\n' % (1 if dirty else 0))
        mtime = os.path.getmtime(path)
        _last_write_mtime = mtime
        _last_read_mtime = mtime      # suppress unnecessary re-read from self
        _cached_file_data = dict(data)
    except Exception:
        pass


# ---------------------------------------------------------------------------
#  In-memory store
# ---------------------------------------------------------------------------

def _store():
    """Return (or initialise) the per-interpreter in-memory dict on sys."""
    s = getattr(_sys, _KEY, None)
    if s is None:
        s = dict(_DEFAULTS)
        file_data = _read_file_state()
        if file_data:
            s.update(file_data)
        setattr(_sys, _KEY, s)
    return s


def _sync_file_from_store():
    """Write current store to file so the other interpreter can pick it up."""
    _write_file_state(_store())


def _sync_store_from_file_if_changed():
    """If the file was written by ANOTHER interpreter, pull its values into our store.

    We detect 'written by another interpreter' as: current file mtime differs
    from _last_write_mtime (the mtime of the file as WE last wrote it).
    When _last_write_mtime == 0 (we never wrote), any real file is 'from another'.
    """
    path = _state_file_path()
    try:
        mtime = os.path.getmtime(path)
        if mtime == _last_write_mtime:
            return  # We wrote this file — store is already current
        # File was changed externally — update our store
        file_data = _read_file_state()
        if file_data:
            _store().update(file_data)
    except Exception:
        pass


# ---------------------------------------------------------------------------
#  Public API
# ---------------------------------------------------------------------------

def get_pad_mode():
    _sync_store_from_file_if_changed()
    return _store()['pad_mode']


def set_pad_mode(value):
    if value not in (PAD_MODE_FPC, PAD_MODE_CHROMATIC):
        value = PAD_MODE_CHROMATIC
    _store()['pad_mode'] = value
    _sync_file_from_store()


def get_pad_bank_offset():
    _sync_store_from_file_if_changed()
    return _store()['pad_bank_offset']


def set_pad_bank_offset(value):
    offset = max(0, min(PAD_BANK_COUNT - 1, int(value)))
    _store()['pad_bank_offset'] = offset
    _sync_file_from_store()


def get_pad_velocity_enabled():
    _sync_store_from_file_if_changed()
    return bool(_store().get('pad_velocity_enabled', True))


def set_pad_velocity_enabled(value):
    _store()['pad_velocity_enabled'] = bool(value)
    _sync_file_from_store()


def mark_pad_led_dirty():
    """Signal the Forward script to refresh pad LED colours on next OnIdle."""
    _store()['pad_led_dirty'] = True
    _sync_file_from_store()


def consume_pad_led_dirty():
    """Return True (once) when a pad LED refresh has been requested.

    Checks both the store (same interpreter) and syncs from file (other
    interpreter) so neither DAW-script nor Forward-script writes are missed.
    """
    _sync_store_from_file_if_changed()
    store = _store()
    dirty = bool(store.get('pad_led_dirty', False))
    if dirty:
        store['pad_led_dirty'] = False
        _sync_file_from_store()
    return dirty
