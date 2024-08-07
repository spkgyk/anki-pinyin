from .paths import (
    add_to_path,
    VENDOR_DIR,
    AUDIO_DIR,
    DATA_DIR,
    BASE_DIR,
    ICON_DIR,
    SRC_DIR,
    TTS_DIR,
)
from .functions import (
    PUNCTUATION_EMOJI_SPACE,
    PUNCTUATION_EMOJI,
    TRAILING_BR_TAGS,
    SQUARE_BR,
    NUMBERS,
    apply_output_mode,
    set_value_space,
    set_value,
)
from .enums import (
    ToneColoring,
    ReadingType,
    ReadingMode,
    OutputMode,
    Language,
)
from .classes import (
    FieldOutputModeDict,
    ToneColorDict,
)

CACHE_SIZE = 500000
add_to_path(VENDOR_DIR)
