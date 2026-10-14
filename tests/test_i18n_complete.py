from fortune_teller.i18n import TranslationManager, t


def test_all_translations():
    manager = TranslationManager()
    assert set(manager.get_available_languages()) == {"zh", "en"}
    assert set(manager.translations["zh"]) == set(manager.translations["en"])
    for language in ("zh", "en"):
        for key, text in manager.translations[language].items():
            assert isinstance(text, str) and text.strip(), (language, key)
            assert t(key, language) == text


def test_fallback():
    assert t("nonexistent_key", "zh") == "nonexistent_key"
    assert t("welcome_title", "fr") == t("welcome_title", "en")
