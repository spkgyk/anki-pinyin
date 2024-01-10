from .chinese import ChineseTokenizer

cn = ChineseTokenizer()


def tokenize(text: str, lang: str):
    if lang == "cn":
        return cn.tokenize(text)


def to_migaku(text: str, lang: str):
    if lang == "cn":
        return cn.to_migaku(text)


def strip_migaku(text: str, lang: str):
    if lang == "cn":
        return cn.strip_migaku(text)
