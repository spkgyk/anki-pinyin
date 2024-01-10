from .chinese import ChineseTokenizer
from .utils import ReadingType

cn = ChineseTokenizer()


def tokenize(text: str, lang: str):
    if lang == "cn":
        return cn.tokenize(text)


def to_migaku(text: str, lang: str, reading_type: ReadingType):
    if lang == "cn":
        return cn.to_migaku(text, reading_type)


def strip_migaku(text: str, lang: str):
    if lang == "cn":
        return cn.strip_migaku(text)
