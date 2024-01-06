from typing import Any, Optional
from fugashi import Tagger, UnidicNode

from ..utils import BaseToken, set_value_space


class FugashiToken(BaseToken):
    def __init__(self, word: UnidicNode):
        super().__init__()
        # structure of the features:
        #     surface and orth are different (if punctuation, surface will be the punctuation, orth will be None)
        #     surface/orth:
        #         - pron
        #         - kana
        #     lemma:
        #         - lForm
        #     orthBase:
        #         - pronBase
        #         - kanaBase

        feature = word.feature
        self.surface: str = word.surface
        self.part_of_speech: str = feature.pos1
        self.conjugation_type: str = feature.cType
        self.conjugation_form: str = feature.cForm

        # pitch accent
        self.drop_moras: str = feature.aType

        # The lemma is a non-inflected "dictionary form" of a word.
        self.lemma: Optional[str] = set_value_space(feature.lemma.split("-", 1)[0]) if feature.lemma else None
        self.lemma_katakana: Optional[str] = set_value_space(feature.lForm)

        # Orthographic representation: the word as it appears in text.
        self.token: Optional[str] = set_value_space(feature.orth)
        self.token_katakana: Optional[str] = set_value_space(feature.kana)
        self.token_pronunciation_katakana: Optional[str] = set_value_space(feature.pron)

        # Uninflected form of the word using its current written form
        self.base_token: Optional[str] = set_value_space(feature.orthBase)
        self.base_token_katakana: Optional[str] = set_value_space(feature.kanaBase)
        self.base_token_pronunciation_katakana: Optional[str] = set_value_space(feature.pronBase)

        # Etymological category. In order of frequency, 和, 固, 漢, 外, 混, 記号, 不明. Defined for all dictionary words, blank for unks.
        self.goshu: Optional[str] = set_value_space(feature.goshu)

    def update(self, new_token: "FugashiToken"):
        self.surface += new_token.surface
        if self.token:
            self.token += new_token.token
            self.token_katakana += new_token.token_katakana
            self.token_pronunciation_katakana += new_token.token_pronunciation_katakana
        else:
            self.token = new_token.token
            self.token_katakana = new_token.token_katakana
            self.token_pronunciation_katakana = new_token.token_pronunciation_katakana


class Fugashi:
    def __init__(self) -> None:
        self._fugashi = Tagger()

    @staticmethod
    def _update_required(jp_token: FugashiToken, list_length: int) -> bool:
        return list_length and (
            (jp_token.part_of_speech == "助詞" and jp_token.token in ["て", "って", "ば"])
            or (jp_token.part_of_speech == "助動詞" and jp_token.base_token not in ["だ", "です"])
        )

    def tokenize(self, text: str):
        fugashi_outputs = [FugashiToken(x) for x in self._fugashi(text)]
        tokens: list[FugashiToken] = []
        for jp_token in fugashi_outputs:
            if self._update_required(jp_token, len(tokens)):
                tokens[-1].update(jp_token)
            else:
                tokens.append(jp_token)

        return tokens

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.tokenize(*args, **kwds)
