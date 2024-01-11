from jieba import cut
from opencc import OpenCC
from typing import Optional
from functools import lru_cache
from pypinyin import lazy_pinyin, Style
from ToJyutping import get_jyutping_list
from pypinyin.style.bopomofo import BopomofoConverter
from pypinyin.contrib.tone_convert import tone_to_tone3

from ..utils import (
    BaseTokenizer,
    ReadingType,
    BaseToken,
    set_value_space,
    CACHE_SIZE,
    VENDOR_DIR,
    SQUARE_BR,
    NUMBERS,
)

_bopomofo_converter = BopomofoConverter()
_open_cc_simp2trad = OpenCC("s2t")
_open_cc_trad2simp = OpenCC("t2s")
_simp_trad_map_path = VENDOR_DIR / "opencc" / "dictionary" / "STCharacters.txt"

simp_trad_map = {}
all_simp_chars = ""
with _simp_trad_map_path.open("r") as f:
    simp_trad_map_list = f.readlines()
    for item in simp_trad_map_list:
        item = item.strip()
        simp, trads = item.split("\t")
        all_simp_chars += simp
        simp_trad_map[simp] = trads.split(" ")


class MandarinToken(BaseToken):
    def __init__(self, word: str, is_simplified: bool, reading_type: ReadingType.PINYIN):
        super().__init__()

        self.surface: str = word
        self.migaku_token: str = self.surface
        self.reading_type: ReadingType = reading_type

        self.token: Optional[str] = set_value_space(self.surface)
        self.tones: Optional[str] = None
        self.pinyin: Optional[str] = None
        self.zhuyin: Optional[str] = None
        self.jyutping: Optional[str] = None
        self.alternate_form: Optional[str] = None

        if self.token:
            pinyin = self._gen_pinyin(word)
            jyutping = self._gen_jyutping(word)
            if pinyin and pinyin[0] != self.surface:
                self.pinyin = pinyin
                self.zhuyin = [self._to_zhuyin(p) for p in pinyin]
                self.tones = [self._to_tone(p) for p in pinyin]

                if is_simplified:
                    self.alternate_form = _open_cc_simp2trad.convert(self.token)
                else:
                    self.alternate_form = _open_cc_trad2simp.convert(self.token)

                reading = self.tones
                if reading_type == ReadingType.BOPOMOFO:
                    reading = self.zhuyin

                if reading_type != ReadingType.JYUTPING:
                    self.migaku_token = "{}[{}]".format(self.surface, " ".join(reading))

                if jyutping and jyutping[0] != self.surface:
                    self.jyutping = jyutping

                if self.jyutping and reading_type == ReadingType.JYUTPING:
                    self.migaku_token = "{}[{}]".format(self.surface, " ".join(self.jyutping))

    @staticmethod
    @lru_cache(CACHE_SIZE)
    def _gen_pinyin(token: str):
        pinyin_output: list[str] = lazy_pinyin(token, style=Style.TONE)
        pinyin_output = [cleaned for cleaned in (set_value_space(char) for char in pinyin_output) if cleaned] or None
        return pinyin_output

    @staticmethod
    def _gen_jyutping(token: str):
        jyutping_output = [x[-1] for x in get_jyutping_list(token) if x and x[-1]] or None
        if jyutping_output:
            jyutping_output = [x for char in jyutping_output if (x := next(iter(char.split(" ")), False))] or None
        return jyutping_output

    @staticmethod
    @lru_cache(CACHE_SIZE)
    def _to_zhuyin(char: str):
        return _bopomofo_converter.to_bopomofo(char)

    @staticmethod
    @lru_cache(CACHE_SIZE)
    def _to_tone(char: str):
        return tone_to_tone3(char, v_to_u=False, neutral_tone_with_five=True)


class ChineseTokenizer(BaseTokenizer):
    @staticmethod
    def strip_migaku(text: str):
        return SQUARE_BR.sub("", text)

    def tokenize(self, text: str, reading_type: ReadingType = ReadingType.PINYIN):
        text = self.strip_migaku(text)
        is_simp = any(c in all_simp_chars for c in text) if reading_type != ReadingType.JYUTPING else False
        tokens = [MandarinToken(x, is_simp, reading_type) for x in cut(text.strip())]
        return tokens

    def to_migaku(self, text: str, reading_type: ReadingType = ReadingType.PINYIN):
        tokens = self.tokenize(text, reading_type)
        output = "".join(token.migaku_token for token in tokens)
        return output
