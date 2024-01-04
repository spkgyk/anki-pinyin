from pathlib import Path

from .base import BaseToken, BaseTokenizer
from .functions import set_value, set_value_space, PUNCTUATION_EMOJI, PUNCTUATION_EMOJI_SPACE

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

CACHE_SIZE = 500000
