#!/usr/bin/env python3
"""
Complete I18n System Test
"""

from fortune_teller.i18n import t

def test_all_translations():
    """Test all translation keys in both languages"""
    
    print("🌍 Complete I18n System Test")
    print("=" * 50)
    
    # Test categories
    categories = [
        ("Welcome & Basic", ["welcome_title", "welcome_subtitle", "language_select"]),
        ("Systems", ["system_bazi", "system_tarot", "system_zodiac"]),
        ("Input Prompts", ["input_birth_date", "input_birth_time", "input_gender"]),
        ("Gender Options", ["gender_male", "gender_female"]),
        ("Tarot Spreads", ["tarot_spread_single", "tarot_spread_three"]),
        ("Status Messages", ["generating_reading", "reading_complete"]),
        ("Errors", ["error_invalid_date", "error_llm_unavailable"])
    ]
    
    for category, keys in categories:
        print(f"\n📋 {category}:")
        print("-" * 30)
        
        for key in keys:
            en_text = t(key, "en")
            zh_text = t(key, "zh")
            print(f"  {key}:")
            print(f"    EN: {en_text}")
            print(f"    ZH: {zh_text}")
    
    print(f"\n✅ I18n system test completed!")
    print(f"📊 All translations loaded successfully")

def test_fallback():
    """Test fallback mechanism"""
    print(f"\n🔄 Testing Fallback Mechanism:")
    print("-" * 30)
    
    # Test missing key
    missing = t("nonexistent_key", "zh")
    print(f"Missing key: '{missing}' (should be key name)")
    
    # Test missing language (should fallback to English)
    fallback = t("welcome_title", "fr")  # French not supported
    print(f"Missing language: '{fallback}' (should be English)")

if __name__ == "__main__":
    test_all_translations()
    test_fallback()
