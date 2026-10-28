# -*- coding: utf-8 -*-
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("datestranger.i18n")

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧", "direction": "ltr"},
    "id": {"name": "Indonesia", "flag": "🇮🇩", "direction": "ltr"},
    "ko": {"name": "한국어", "flag": "🇰🇷", "direction": "ltr"},
    "fa": {"name": "فارسی", "flag": "🇮🇷", "direction": "rtl"},
    "ru": {"name": "Русский", "flag": "🇷🇺", "direction": "ltr"},
}

DEFAULT_LANGUAGE = "en"


class I18nManager:
    def __init__(self, locales_dir: Optional[str] = None):
        if locales_dir is None:
            locales_dir = os.path.join(os.path.dirname(__file__), "locales")
        self.locales_dir = locales_dir
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_all()

    def load_all(self):
        """Loads all JSON translation files from locales_dir."""
        for lang in SUPPORTED_LANGUAGES:
            file_path = os.path.join(self.locales_dir, f"{lang}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.translations[lang] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load translation file {file_path}: {e}")
                    self.translations[lang] = {}
            else:
                logger.warning(f"Translation file missing: {file_path}")
                self.translations[lang] = {}

    def t(self, key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """
        Translates a key into the target language with fallback to 'en'.
        Safely interpolates placeholders.
        """
        if not lang or lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE

        # Lookup in requested language
        text = self.translations.get(lang, {}).get(key)

        # Fallback to default language 'en'
        if text is None and lang != DEFAULT_LANGUAGE:
            text = self.translations.get(DEFAULT_LANGUAGE, {}).get(key)

        # Final fallback to raw key if missing everywhere
        if text is None:
            text = key

        # Interpolate variables safely
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception as e:
                logger.warning(f"Failed to format key '{key}' in lang '{lang}': {e}")

        # RTL direction formatting for Persian if needed
        if self.is_rtl(lang) and text and not text.startswith("‏"):
            text = "‏" + text

        return text

    def get_direction(self, lang: str) -> str:
        return SUPPORTED_LANGUAGES.get(lang, {}).get("direction", "ltr")

    def is_rtl(self, lang: str) -> bool:
        return self.get_direction(lang) == "rtl"


# Global Instance
i18n = I18nManager()
t = i18n.t
get_direction = i18n.get_direction
is_rtl = i18n.is_rtl
