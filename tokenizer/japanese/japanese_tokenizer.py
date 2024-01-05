from typing import Any
from functools import lru_cache

from ..vendor.regex import compile
from ..vendor.yaml import safe_load
from ..vendor.jaconv import kata2hira

from .fugashi_wrapper import Fugashi, FugashiToken
from ..utils import BaseTokenizer, CACHE_SIZE, BASE_DIR


LONG = compile(r"(.)ー")
NUMBERS = compile(r"[\d]+")
SMALL_KANA = compile(r"(?![ァィゥェォャュョ]).|ー")

DATA_PATH = BASE_DIR / "data" / "japanese_exceptions.yml"


# global instances
with open(DATA_PATH) as f:
    japanese_exceptions: dict[str, dict[str, Any]] = safe_load(f)


@lru_cache(maxsize=CACHE_SIZE)
def count_mora(katakana_word: str):
    return len(SMALL_KANA.findall(katakana_word))


@lru_cache(maxsize=CACHE_SIZE)
def find_furigana_end_index(word: str, hiragana: str):
    i = -1
    while abs(i) <= len(word) and abs(i) <= len(hiragana) and word[i] == hiragana[i]:
        i -= 1
    return i + 1


@lru_cache(maxsize=CACHE_SIZE)
def gen_hira(pronunciation: str):
    if not pronunciation:
        return None

    return kata2hira(pronunciation)


class JapaneseToken(FugashiToken):
    def __init__(self, word: FugashiToken):
        self._init_from_token(word)
        self._parse_pitch_information()
        self._get_hiragana()
        self._get_furigana()
        self._get_migaku_token()

    def _parse_pitch_information(self):
        drop_moras = [int(x) for x in self.drop_moras.split(",") if NUMBERS.match(x)] if self.drop_moras else []

        word_struct = japanese_exceptions.get(self.lemma)
        if word_struct:
            katakana_replacement = word_struct.get("common")

            self.token_katakana = katakana_replacement
            self.base_token_katakana = katakana_replacement
            self.token_pronunciation_katakana = katakana_replacement
            self.base_token_pronunciation_katakana = katakana_replacement

            drop_moras = word_struct.get("drop")

        self.token_mora_length = count_mora(self.token_katakana) if self.token_katakana else None
        self.base_token_mora_length = count_mora(self.base_token_katakana) if self.base_token_katakana else None

        pitch_accent_patterns = []
        for drop_mora in drop_moras:
            if (self.part_of_speech in ["動詞", "形容詞"]) and (drop_mora > 0):
                pitch_accent_patterns.append(f"k{str(drop_mora)}")
            elif drop_mora == 0:
                pitch_accent_patterns.append(f"h")
            elif drop_mora == self.base_token_mora_length:
                pitch_accent_patterns.append(f"o")
            elif drop_mora == 1:
                pitch_accent_patterns.append("a")
            elif drop_mora < self.base_token_mora_length:
                pitch_accent_patterns.append(f"n{str(drop_mora)}")
            else:
                raise Exception(f"Pitch accent error for {self.lemma}({self.base_token_katakana}), drop mora: {drop_mora}.")

        self.drop_moras = drop_moras or None
        self.pitch_accent_patterns = pitch_accent_patterns or None

    def _get_hiragana(self):
        self.lemma_hiragana = gen_hira(self.lemma_katakana)
        self.token_hiragana = gen_hira(self.token_katakana)
        self.token_pronunciation_hiragana = gen_hira(self.token_pronunciation_katakana)
        self.base_token_hiragana = gen_hira(self.base_token_katakana)
        self.base_token_pronunciation_hiragana = gen_hira(self.base_token_pronunciation_katakana)

    def _get_furigana(self):
        self.furigana = None
        self.kanji_only_length = None

        if self.base_token != self.base_token_hiragana and self.base_token != self.base_token_katakana:
            index = find_furigana_end_index(self.base_token, self.base_token_hiragana)
            self.furigana = self.base_token_hiragana[:index] if index != 0 else self.base_token_hiragana
            trailing_hiragana_length = len(self.base_token_hiragana) - len(self.furigana)
            self.kanji_only_length = len(self.base_token[:-trailing_hiragana_length] or self.token)

    def _get_migaku_token(self):
        self.migaku_token = self.surface + " "

        if self.base_token_hiragana:
            joined_pitch_info = ",".join(self.pitch_accent_patterns) if self.pitch_accent_patterns else ""

            if self.part_of_speech in ["動詞", "形容詞"]:
                if self.furigana:
                    self.migaku_token = "{}[{},{};{}]{} ".format(
                        self.surface[: self.kanji_only_length],
                        self.furigana,
                        self.base_token_hiragana,
                        joined_pitch_info,
                        self.surface[self.kanji_only_length :],
                    )
                else:
                    self.migaku_token = "{}[,{};{}] ".format(
                        self.surface,
                        self.base_token_hiragana,
                        joined_pitch_info,
                    )
            else:
                if self.furigana:
                    if self.furigana != self.base_token_hiragana:
                        self.migaku_token = "{}[{},{};{}]{} ".format(
                            self.surface[: self.kanji_only_length],
                            self.furigana,
                            self.base_token_hiragana,
                            joined_pitch_info,
                            self.surface[self.kanji_only_length :],
                        )
                    else:
                        self.migaku_token = "{}[{};{}] ".format(
                            self.surface,
                            self.base_token_hiragana,
                            joined_pitch_info,
                        )
                elif joined_pitch_info:
                    self.migaku_token = "{}[;{}] ".format(self.surface, joined_pitch_info)


class JapaneseTokenizer(BaseTokenizer):
    def __init__(self) -> None:
        self.fugashi = Fugashi()

    def tokenize(self, text: str) -> list[JapaneseToken]:
        tokens = [JapaneseToken(x) for x in self.fugashi(text)]
        return tokens
