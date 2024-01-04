from .chinese import ChineseTokenizer
from .japanese import JapaneseTokenizer

cn = ChineseTokenizer()
jp = JapaneseTokenizer()


def tokenize(text: str, lang: str):
    if lang == "jp":
        return jp.tokenize(text)
    elif lang == "cn":
        return cn.tokenize(text)


def to_migaku(text: str, lang: str):
    tokens = tokenize(text, lang)
    return "".join(token.migaku_token for token in tokens)
