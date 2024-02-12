from jieba import cut
from opencc import OpenCC
from typing import Optional
from functools import lru_cache
from ToJyutping import get_jyutping_list
from pypinyin import lazy_pinyin, STYLE_TONE
from pypinyin.style.bopomofo import BopomofoConverter
from pypinyin_dict.phrase_pinyin_data import cc_cedict
from pypinyin.contrib.tone_convert import tone_to_tone3

from ..base import BaseToken, BaseTokenizer
from ...utils import (
    ReadingType,
    set_value_space,
    TRAILING_BR_TAGS,
    CACHE_SIZE,
    VENDOR_DIR,
    SQUARE_BR,
)

cc_cedict.load()
_bopomofo_converter = BopomofoConverter()
_open_cc_simp2trad = OpenCC("s2t")
_open_cc_trad2simp = OpenCC("t2s")
_simp_trad_map_path = VENDOR_DIR / "opencc" / "dictionary" / "STCharacters.txt"

simp_trad_map = {}
all_simp_chars = ""
with _simp_trad_map_path.open("r", encoding="utf-8") as f:
    simp_trad_map_list = f.readlines()
    for item in simp_trad_map_list:
        item = item.strip()
        simp, trads = item.split("\t")
        all_simp_chars += simp
        simp_trad_map[simp] = trads.split(" ")

zhuyin_tone_numbers = {"ˊ": "2", "ˇ": "3", "ˋ": "4", "˙": "5"}


class MandarinToken(BaseToken):
    def __init__(self, word: str, is_simplified: bool, reading_type: ReadingType.PINYIN_ACCENTS):
        super().__init__()

        self.surface: str = word
        self.display_token: str = self.surface
        self.reading_type: ReadingType = reading_type

        self.simplified = self.surface
        self.traditional = self.surface

        self.token: Optional[str] = set_value_space(self.surface)
        self.pinyin_tones: Optional[str] = None
        self.pinyin: Optional[str] = None
        self.zhuyin: Optional[str] = None
        self.jyutping: Optional[str] = None
        self.alternate_form: Optional[str] = None

        if self.token:
            pinyin = self._gen_pinyin(word)
            jyutping = self._gen_jyutping(word)
            if pinyin and pinyin[0] != self.token:
                self.pinyin = pinyin
                self.zhuyin = [self._to_zhuyin(p) for p in pinyin]
                self.pinyin_tones = [self._to_pinyin_tone(p) for p in pinyin]
                self.zhuyin_tones = [self._to_zhuyin_tone(p) for p in self.zhuyin]

                if is_simplified:
                    self.traditional = _open_cc_simp2trad.convert(self.token)
                    self.alternate_form = self.traditional
                else:
                    self.simplified = _open_cc_trad2simp.convert(self.token)
                    self.alternate_form = self.simplified

                reading = self.pinyin
                if reading_type == ReadingType.PINYIN_TONES:
                    reading = self.pinyin_tones
                elif reading_type == ReadingType.ZHUYIN_ACCENTS:
                    reading = self.zhuyin
                elif reading_type == ReadingType.ZHUYIN_TONES:
                    reading = self.zhuyin_tones

                if jyutping and jyutping[0] != self.token:
                    self.jyutping = jyutping

                if reading_type != ReadingType.JYUTPING:
                    self.display_token = "{}[{}]".format(self.token, " ".join(reading))
                elif self.jyutping and reading_type == ReadingType.JYUTPING:
                    self.display_token = "{}[{}]".format(self.token, " ".join(self.jyutping))

    @staticmethod
    @lru_cache(CACHE_SIZE)
    def _gen_pinyin(token: str):
        pinyin_output: list[str] = lazy_pinyin(token, STYLE_TONE)
        pinyin_output = [cleaned for cleaned in (set_value_space(char) for char in pinyin_output) if cleaned] or None
        return pinyin_output

    @staticmethod
    @lru_cache(CACHE_SIZE)
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
    def _to_pinyin_tone(char: str):
        return tone_to_tone3(char, v_to_u=False, neutral_tone_with_five=True)

    @staticmethod
    @lru_cache(CACHE_SIZE)
    def _to_zhuyin_tone(char: str):
        last = char[-1:]
        if last in zhuyin_tone_numbers:
            char = char[:-1] + zhuyin_tone_numbers[last]
        else:
            char += "1"
        return char


class ChineseTokenizer(BaseTokenizer):
    class TokenizationResult:
        def __init__(self, tokens: list[MandarinToken]):
            self.display_format = "".join(token.display_token for token in tokens)
            self.simplified = "".join(token.simplified for token in tokens)
            self.traditional = "".join(token.traditional for token in tokens)

    @staticmethod
    def strip_display_format(text: str):
        return TRAILING_BR_TAGS.sub("", SQUARE_BR.sub("", text))

    def tokenize(self, text: str, reading_type: ReadingType = ReadingType.PINYIN_ACCENTS):
        text = self.strip_display_format(text)
        is_simp = reading_type in [ReadingType.PINYIN_ACCENTS, ReadingType.PINYIN_TONES]
        tokens = [MandarinToken(x, is_simp, reading_type) for x in cut(text.strip())]
        return tokens

    def gen_display_format(self, text: str, reading_type: ReadingType = ReadingType.PINYIN_ACCENTS):
        tokens = self.tokenize(text, reading_type)
        return self.TokenizationResult(tokens)
