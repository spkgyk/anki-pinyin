from .utils import BASE_DIR

import json

from aqt import mw

if mw and mw.addonManager:
    _config = mw.addonManager.getConfig(__name__)
    assert _config
else:
    with (BASE_DIR / "config.json").open("r", encoding="utf8") as f:
        _config = json.load(f)
        assert _config


def write():
    mw.addonManager.writeConfig(__name__, _config)


def get(key, default=None):
    return _config.get(key, default)


def set(key, value, do_write=False):
    _config[key] = value
    if do_write:
        write()


def has(key):
    return key in _config
