import os
import sys

from pathlib import Path
from typing import Union

BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
DATA_DIR = SRC_DIR / "data"
VENDOR_DIR = SRC_DIR / "vendor"
ICON_DIR = DATA_DIR / "icons"
JS_DIR = DATA_DIR / "js"

assert os.path.exists(BASE_DIR)
assert os.path.exists(SRC_DIR)
assert os.path.exists(DATA_DIR)
assert os.path.exists(VENDOR_DIR)


def add_to_path(path: Union[str, Path]):
    path = str(path)
    sys.path.insert(0, path)
