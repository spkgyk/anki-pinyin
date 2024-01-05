from ..vendor.regex import compile


PUNCTUATION_EMOJI = compile(r"[\p{P}\p{Extended_Pictographic}\n]")
PUNCTUATION_EMOJI_SPACE = compile(r"[\p{P}\p{Extended_Pictographic}\n\s]")


def set_value(attribute: str):
    value = None
    if attribute:
        value = PUNCTUATION_EMOJI.sub("", attribute) or None
    return value


def set_value_space(attribute: str):
    value = None
    if attribute:
        value = PUNCTUATION_EMOJI_SPACE.sub("", attribute) or None
    return value
