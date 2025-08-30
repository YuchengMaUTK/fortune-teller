#!/usr/bin/env python3
"""
Test keyboard navigation - run this interactively to see smooth navigation
"""

from fortune_teller.ui.keyboard_input import select_language, select_gender, select_tarot_spread

def test_language():
    print("🌍 Testing Language Selection:")
    result = select_language()
    print(f"Selected: {result}")
    return result

def test_gender(language="zh"):
    print(f"\n👤 Testing Gender Selection ({language}):")
    result = select_gender(language)
    print(f"Selected: {result}")
    return result

def test_tarot_spread(language="zh"):
    print(f"\n🃏 Testing Tarot Spread Selection ({language}):")
    result = select_tarot_spread(language)
    print(f"Selected: {result}")
    return result

if __name__ == "__main__":
    print("🎯 Keyboard Navigation Test")
    print("=" * 40)
    
    try:
        # Test language selection
        lang = test_language()
        
        if lang:
            # Test gender selection
            gender = test_gender(lang)
            
            # Test tarot spread selection
            spread = test_tarot_spread(lang)
            
            print(f"\n✅ All tests completed!")
            print(f"Language: {lang}, Gender: {gender}, Spread: {spread}")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
