"""
Internationalization (i18n) module for Fortune Teller
Simple JSON-based translation system for en/zh
"""

from .manager import TranslationManager

# Global translation manager instance
_manager = TranslationManager()

def t(key: str, lang: str = "zh") -> str:
    """
    Get translated text for a key and language
    
    Args:
        key: Translation key (e.g., "welcome_title")
        lang: Language code ("en" or "zh")
    
    Returns:
        Translated text, falls back to English, then key if not found
    """
    return _manager.get(key, lang)

def get_available_languages():
    """Get list of available language codes"""
    return _manager.get_available_languages()

def reload_translations():
    """Reload translation files (useful for development)"""
    _manager.reload()
