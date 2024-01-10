import sys

from pathlib import Path
from typing import Union

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
VENDOR_DIR = BASE_DIR / "vendor"


def add_to_path(path: Union[str, Path]):
    path = str(path)
    sys.path.insert(0, path)
