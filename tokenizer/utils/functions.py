import re

punctuation_pattern = r"\u2000-\u206F\u3000-\u303F\uFF00-\uFFEF" + re.escape("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
emoji_pattern = (
    r"\U0001F600-\U0001F64F"  # Emoticons
    r"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
    r"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    r"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
)
newline = r"\n"
space_newline = r"\s\n"

SQUARE_BR = re.compile(r'\[.*?\]')
PUNCTUATION_EMOJI = re.compile(f"[{punctuation_pattern}{emoji_pattern}{newline}]")
PUNCTUATION_EMOJI_SPACE = re.compile(f"[{punctuation_pattern}{emoji_pattern}{space_newline}]")


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
