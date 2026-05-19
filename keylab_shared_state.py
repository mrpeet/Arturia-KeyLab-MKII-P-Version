# KeyLab mkII - Shared State (cross-port)
# State shared between device_KeyLabmkII.py (DAW port) and
# device_KeyLabmkII_Forward.py (Keys port).
#
# FL Studio may give each device script its own module namespace, so plain
# module-level globals are NOT reliably shared. We use:
#   1. `sys._keylab_pad_state` when both scripts share one interpreter
#   2. `keylab_pad_state.json` in this hardware folder as file fallback

import os
import sys as _sys

PAD_BANK_COUNT = 6

PAD_MODE_FPC = 'fpc'
PAD_MODE_CHROMATIC = 'chromatic'

_KEY = '_keylab_pad_state'
_DEFAULTS = {
    'pad_mode': PAD_MODE_CHROMATIC,  # Default: Chromatic from C3 (see ROADMAP 10.1)
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


def _read_file_state():
    """Return dict from JSON file or None."""
    path = _state_file_path()
    try:
        with open(path, 'r') as f:
            text = f.read().strip()
        if not text:
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
                data['pad_bank_offset'] = int(val)
            elif key == 'pad_velocity_enabled':
                data['pad_velocity_enabled'] = val in ('1', 'true', 'True', 'on', 'On')
            elif key == 'pad_led_dirty':
                data['pad_led_dirty'] = val in ('1', 'true', 'True', 'on', 'On')
        return data if data else None
    except Exception:
        return None


def _write_file_state(data):
    path = _state_file_path()
    try:
        with open(path, 'w') as f:
            f.write('pad_mode=%s\n' % data.get('pad_mode', PAD_MODE_CHROMATIC))
            f.write('pad_bank_offset=%d\n' % int(data.get('pad_bank_offset', 0)))
            vel = data.get('pad_velocity_enabled', True)
            f.write('pad_velocity_enabled=%d\n' % (1 if vel else 0))
            dirty = data.get('pad_led_dirty', False)
            f.write('pad_led_dirty=%d\n' % (1 if dirty else 0))
    except Exception:
        pass


def _store():
    s = getattr(_sys, _KEY, None)
    if s is None:
        s = dict(_DEFAULTS)
        file_data = _read_file_state()
        if file_data:
            s.update(file_data)
        setattr(_sys, _KEY, s)
    return s


def _sync_file_from_store():
    _write_file_state(_store())


def get_pad_mode():
    file_data = _read_file_state()
    if file_data and 'pad_mode' in file_data:
        mode = file_data['pad_mode']
        if mode in (PAD_MODE_FPC, PAD_MODE_CHROMATIC):
            _store()['pad_mode'] = mode
            return mode
    return _store()['pad_mode']


def set_pad_mode(value):
    if value not in (PAD_MODE_FPC, PAD_MODE_CHROMATIC):
        value = PAD_MODE_CHROMATIC
    _store()['pad_mode'] = value
    _sync_file_from_store()


def get_pad_bank_offset():
    file_data = _read_file_state()
    if file_data and 'pad_bank_offset' in file_data:
        offset = max(0, min(PAD_BANK_COUNT - 1, int(file_data['pad_bank_offset'])))
        _store()['pad_bank_offset'] = offset
        return offset
    return _store()['pad_bank_offset']


def set_pad_bank_offset(value):
    offset = max(0, min(PAD_BANK_COUNT - 1, int(value)))
    _store()['pad_bank_offset'] = offset
    _sync_file_from_store()


def get_pad_velocity_enabled():
    file_data = _read_file_state()
    if file_data and 'pad_velocity_enabled' in file_data:
        enabled = bool(file_data['pad_velocity_enabled'])
        _store()['pad_velocity_enabled'] = enabled
        return enabled
    return bool(_store().get('pad_velocity_enabled', True))


def set_pad_velocity_enabled(value):
    enabled = bool(value)
    _store()['pad_velocity_enabled'] = enabled
    _sync_file_from_store()


def mark_pad_led_dirty():
    """Forward script refreshes pad idle colors on next OnIdle."""
    _store()['pad_led_dirty'] = True
    _sync_file_from_store()


def consume_pad_led_dirty():
    """True once after DAW requested pad LED refresh (e.g. IN mode toggle)."""
    file_data = _read_file_state()
    dirty = False
    if file_data and 'pad_led_dirty' in file_data:
        dirty = bool(file_data['pad_led_dirty'])
    elif _store().get('pad_led_dirty'):
        dirty = True
    if dirty:
        _store()['pad_led_dirty'] = False
        _sync_file_from_store()
    return dirty
