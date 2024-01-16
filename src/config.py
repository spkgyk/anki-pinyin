import json

from aqt import mw
from typing import Any

from .utils import BASE_DIR, ReadingType, FieldOutputModeDict, ToneColorDict


class Config:
    with (BASE_DIR / "config.json").open("r", encoding="utf8") as f:
        _default_config: dict[str, Any] = json.load(f)

    __default_reading_type = ReadingType(_default_config.get("reading_type"))
    __default_traditional_icons = bool(_default_config.get("traditional_icons"))
    __default_simp_fields = FieldOutputModeDict(_default_config.get("simp_fields"))
    __default_trad_fields = FieldOutputModeDict(_default_config.get("trad_fields"))
    __default_variant_fields = FieldOutputModeDict(_default_config.get("variant_fields"))
    __default_profiles = list(_default_config.get("profiles"))
    __default_active_fields = _default_config.get("active_fields")
    __default_mandarin_tones = ToneColorDict(_default_config.get("mandarin_tones"))
    __default_cantonese_tones = ToneColorDict(_default_config.get("cantonese_tones"))
    __default_auto_generate_css_js = bool(_default_config.get("auto_generate_css_js"))
    __default_ruby_font_scale_factor = int(_default_config.get("ruby_font_scale_factor"))

    if mw and mw.addonManager:
        _config = mw.addonManager.getConfig(__name__)
    else:
        _config = _default_config

    reading_type = ReadingType(_config.get("reading_type"))
    traditional_icons = bool(_config.get("traditional_icons"))
    simp_fields = FieldOutputModeDict(_config.get("simp_fields"))
    trad_fields = FieldOutputModeDict(_config.get("trad_fields"))
    variant_fields = FieldOutputModeDict(_config.get("variant_fields"))
    profiles = list(_config.get("profiles"))
    active_fields = _config.get("active_fields")
    mandarin_tones = ToneColorDict(_config.get("mandarin_tones"))
    cantonese_tones = ToneColorDict(_config.get("cantonese_tones"))
    auto_generate_css_js = bool(_config.get("auto_generate_css_js"))
    ruby_font_scale_factor = int(_config.get("ruby_font_scale_factor"))

    def load_default():
        Config.reading_type = Config.__default_reading_type
        Config.traditional_icons = Config.__default_traditional_icons
        Config.simp_fields = Config.__default_simp_fields
        Config.trad_fields = Config.__default_trad_fields
        Config.variant_fields = Config.__default_variant_fields
        Config.profiles = Config.__default_profiles
        Config.active_fields = Config.__default_active_fields
        Config.mandarin_tones = Config.__default_mandarin_tones
        Config.cantonese_tones = Config.__default_cantonese_tones
        Config.auto_generate_css_js = Config.__default_auto_generate_css_js
        Config.ruby_font_scale_factor = Config.__default_ruby_font_scale_factor
        Config.write()

    def write():
        config = {
            "reading_type": Config.reading_type.value,
            "traditional_icons": Config.traditional_icons,
            "simp_fields": Config.simp_fields.to_json(),
            "trad_fields": Config.trad_fields.to_json(),
            "variant_fields": Config.variant_fields.to_json(),
            "profiles": Config.profiles,
            "active_fields": Config.active_fields,
            "mandarin_tones": Config.mandarin_tones.to_json(),
            "cantonese_tones": Config.cantonese_tones.to_json(),
            "auto_generate_css_js": Config.auto_generate_css_js,
            "ruby_font_scale_factor": Config.ruby_font_scale_factor,
        }
        mw.addonManager.writeConfig(__name__, config)

    @classmethod
    def has(cls, key: str):
        return hasattr(cls, key)
