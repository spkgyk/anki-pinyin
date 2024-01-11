from .paths import (
    add_to_path,
    VENDOR_DIR,
    DATA_DIR,
    BASE_DIR,
    SRC_DIR,
)
from .functions import (
    PUNCTUATION_EMOJI_SPACE,
    PUNCTUATION_EMOJI,
    SQUARE_BR,
    NUMBERS,
    set_value_space,
    set_value,
)
from .reading_type import ReadingType
from .output_mode import OutputMode

CACHE_SIZE = 500000
add_to_path(VENDOR_DIR)
