from enum import Enum


class OutputMode(Enum):
    APPEND = "Append"
    IF_EMPTY = "If Empty"
    OVERWRITE = "Overwrite"


class ReadingType(Enum):
    JYUTPING = "Jyutping"
    PINYIN_TONES = "Pinyin Tones"
    PINYIN_ACCENTS = "Pinyin Accents"
    ZHUYIN_TONES = "Zhuyin Tones"
    ZHUYIN_ACCENTS = "Zhuyin Accents"


class ReadingMode(Enum):
    HIDDEN = "Hidden"
    ENABLED = "Enabled"
    DISABLED = "Disabled"
    ON_HOVER = "On Hover"


class ToneColoring(Enum):
    DISABLED = "Disabled"
    ENABLED = "Enabled"
    ON_HOVER = "On Hover"


class Language(Enum):
    CANTONESE = "Cantonese"
    SIMPLIFIED = "Chinese Simplified"
    TRADITIONAL = "Chinese Traditional"
