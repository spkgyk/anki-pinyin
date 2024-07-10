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
    __default_audio_fields = FieldOutputModeDict(_default_config.get("audio_fields"))

    if mw and mw.addonManager:
        _config = mw.addonManager.getConfig(__name__)
    else:
        _config = _default_config

    reading_type = ReadingType(_config.get("reading_type"))
    traditional_icons = bool(_config.get("traditional_icons"))
    simp_fields = FieldOutputModeDict(_config.get("simp_fields"))
    trad_fields = FieldOutputModeDict(_config.get("trad_fields"))
    variant_fields = FieldOutputModeDict(_config.get("variant_fields"))
    audio_fields = FieldOutputModeDict(_config.get("audio_fields"))

    def load_default():
        Config.reading_type = Config.__default_reading_type
        Config.traditional_icons = Config.__default_traditional_icons
        Config.simp_fields = Config.__default_simp_fields
        Config.trad_fields = Config.__default_trad_fields
        Config.variant_fields = Config.__default_variant_fields
        Config.audio_fields = Config.__default_audio_fields
        Config.write()

    def write():
        config = {
            "reading_type": Config.reading_type.value,
            "traditional_icons": Config.traditional_icons,
            "simp_fields": Config.simp_fields.to_json(),
            "trad_fields": Config.trad_fields.to_json(),
            "variant_fields": Config.variant_fields.to_json(),
            "audio_fields": Config.audio_fields.to_json(),
        }
        mw.addonManager.writeConfig(__name__, config)

    @classmethod
    def has(cls, key: str):
        return hasattr(cls, key)
