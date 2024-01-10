from .chinese import ChineseTokenizer

cn = ChineseTokenizer()


def tokenize(text: str, lang: str):
    if lang == "cn":
        return cn.tokenize(text)


def to_migaku(text: str, lang: str):
    tokens = tokenize(text, lang)
    return "".join(token.migaku_token for token in tokens)
