import os
import sys

from pathlib import Path
from typing import Union

# root dir
BASE_DIR = Path(__file__).resolve().parents[2]

# src
SRC_DIR = BASE_DIR / "src"

# sub-folders
DATA_DIR = SRC_DIR / "data"
VENDOR_DIR = SRC_DIR / "vendor"
TTS_DIR = SRC_DIR / "tts"

# data sub-folders
ICON_DIR = DATA_DIR / "icons"
AUDIO_DIR = DATA_DIR / "audio"

assert os.path.exists(BASE_DIR)
assert os.path.exists(SRC_DIR)
assert os.path.exists(DATA_DIR)
assert os.path.exists(VENDOR_DIR)
assert os.path.exists(ICON_DIR)
assert os.path.exists(TTS_DIR)
assert os.path.exists(AUDIO_DIR)


def add_to_path(path: Union[str, Path]):
    path = str(path)
    sys.path.insert(0, path)
