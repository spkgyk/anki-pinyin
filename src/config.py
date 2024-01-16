import json

from aqt import mw
from typing import Any

from .utils import BASE_DIR, ReadingType, FieldOutputModeDict


class Config:
    with (BASE_DIR / "config.json").open("r", encoding="utf8") as f:
        _default_config: dict[str, Any] = json.load(f)

    __default_reading_type = ReadingType(_default_config.get("reading_type"))
    __default_traditional_icons = bool(_default_config.get("traditional_icons"))
    __default_simp_fields = FieldOutputModeDict(_default_config.get("simp_fields"))
    __default_trad_fields = FieldOutputModeDict(_default_config.get("trad_fields"))
    __default_variant_fields = FieldOutputModeDict(_default_config.get("variant_fields"))

    if mw and mw.addonManager:
        _config = mw.addonManager.getConfig(__name__)
    else:
        _config = _default_config

    reading_type = ReadingType(_config.get("reading_type"))
    traditional_icons = bool(_config.get("traditional_icons"))
    simp_fields = FieldOutputModeDict(_config.get("simp_fields"))
    trad_fields = FieldOutputModeDict(_config.get("trad_fields"))
    variant_fields = FieldOutputModeDict(_config.get("variant_fields"))
    # profiles = list(_config.get("profiles"))
    # active_fields = _config.get("active_fields")
    # auto_generate_css_js = bool(_config.get("auto_generate_css_js"))
    # ruby_font_scale_factor = int(_config.get("ruby_font_scale_factor"))
    # mandarin_tones = _config.get("mandarin_tones")
    # cantonese_tones = _config.get("cantonese_tones")
    # hanziConversion = _config.get("hanziConversion")
    # readingConversion = _config.get("readingConversion")

    def load_default(self):
        self.reading_type = self.__default_reading_type
        self.traditional_icons = self.__default_traditional_icons
        self.simp_fields = self.__default_simp_fields
        self.trad_fields = self.__default_trad_fields
        self.variant_fields = self.__default_variant_fields
        self.write()

    def write(self):
        config = {
            "reading_type": self.reading_type.value,
            "traditional_icons": self.traditional_icons,
            "simp_fields": self.simp_fields,
            "trad_fields": self.trad_fields,
            "variant_fields": self.variant_fields,
        }
        mw.addonManager.writeConfig(__name__, config)

    @classmethod
    def has(cls, key: str):
        return hasattr(cls, key)
