"""
Translation Manager - Loads and manages JSON translation files
"""

import json
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TranslationManager:
    """Manages translation files and provides text lookup"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.locales_dir = os.path.join(os.path.dirname(__file__), "locales")
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files from locales directory"""
        self.translations = {}
        
        if not os.path.exists(self.locales_dir):
            logger.warning(f"Locales directory not found: {self.locales_dir}")
            return
        
        for filename in os.listdir(self.locales_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # Remove .json extension
                file_path = os.path.join(self.locales_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    logger.debug(f"Loaded translations for {lang_code}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
    
    def get(self, key: str, lang: str = "zh") -> str:
        """
        Get translated text with fallback chain: requested_lang → en → key
        
        Args:
            key: Translation key
            lang: Language code
            
        Returns:
            Translated text or fallback
        """
        # Try requested language
        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]
        
        # Fallback to English
        if lang != "en" and "en" in self.translations and key in self.translations["en"]:
            return self.translations["en"][key]
        
        # Final fallback to key itself
        logger.warning(f"Translation missing: {key} for {lang}")
        return key
    
    def get_available_languages(self) -> list:
        """Get list of available language codes"""
        return list(self.translations.keys())
    
    def reload(self):
        """Reload all translation files"""
        self.load_translations()
