from ..utils import ReadingType
from .chinese import ChineseTokenizer

cn = ChineseTokenizer()


def tokenize(text: str, lang: str, reading_type: ReadingType):
    if lang == "cn":
        return cn.tokenize(text, reading_type)


def gen_display_format(text: str, lang: str, reading_type: ReadingType):
    if lang == "cn":
        return cn.gen_display_format(text, reading_type)


def strip_display_format(text: str, lang: str):
    if lang == "cn":
        return cn.strip_display_format(text)
