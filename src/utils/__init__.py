from .paths import (
    add_to_path,
    VENDOR_DIR,
    DATA_DIR,
    BASE_DIR,
    ICON_DIR,
    SRC_DIR,
    JS_DIR,
)
from .functions import (
    PUNCTUATION_EMOJI_SPACE,
    PUNCTUATION_EMOJI,
    SQUARE_BR,
    NUMBERS,
    set_value_space,
    set_value,
)
from .enums import OutputMode, ReadingType

CACHE_SIZE = 500000
add_to_path(VENDOR_DIR)
