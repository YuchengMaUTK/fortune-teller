#!/usr/bin/env python3
"""
Tarot Card Random Picker MCP Tool
Provides high-quality randomness for tarot card drawing
"""

import json
import sys
import random
import secrets
from typing import List, Dict, Any

# Tarot card data
TAROT_CARDS = [
    {"id": 0, "name": "愚者", "english": "The Fool", "emoji": "🃏", "suit": "Major Arcana"},
    {"id": 1, "name": "魔术师", "english": "The Magician", "emoji": "🧙‍♂️", "suit": "Major Arcana"},
    {"id": 2, "name": "女祭司", "english": "The High Priestess", "emoji": "🔮", "suit": "Major Arcana"},
    {"id": 3, "name": "皇后", "english": "The Empress", "emoji": "👸", "suit": "Major Arcana"},
    {"id": 4, "name": "皇帝", "english": "The Emperor", "emoji": "👑", "suit": "Major Arcana"},
    {"id": 5, "name": "教皇", "english": "The Hierophant", "emoji": "⛪", "suit": "Major Arcana"},
    {"id": 6, "name": "恋人", "english": "The Lovers", "emoji": "💕", "suit": "Major Arcana"},
    {"id": 7, "name": "战车", "english": "The Chariot", "emoji": "🏇", "suit": "Major Arcana"},
    {"id": 8, "name": "力量", "english": "Strength", "emoji": "💪", "suit": "Major Arcana"},
    {"id": 9, "name": "隐者", "english": "The Hermit", "emoji": "🕯️", "suit": "Major Arcana"},
    {"id": 10, "name": "命运之轮", "english": "Wheel of Fortune", "emoji": "🎡", "suit": "Major Arcana"},
    {"id": 11, "name": "正义", "english": "Justice", "emoji": "⚖️", "suit": "Major Arcana"},
    {"id": 12, "name": "倒吊人", "english": "The Hanged Man", "emoji": "🙃", "suit": "Major Arcana"},
    {"id": 13, "name": "死神", "english": "Death", "emoji": "💀", "suit": "Major Arcana"},
    {"id": 14, "name": "节制", "english": "Temperance", "emoji": "🍷", "suit": "Major Arcana"},
    {"id": 15, "name": "恶魔", "english": "The Devil", "emoji": "😈", "suit": "Major Arcana"},
    {"id": 16, "name": "塔", "english": "The Tower", "emoji": "🗼", "suit": "Major Arcana"},
    {"id": 17, "name": "星星", "english": "The Star", "emoji": "⭐", "suit": "Major Arcana"},
    {"id": 18, "name": "月亮", "english": "The Moon", "emoji": "🌙", "suit": "Major Arcana"},
    {"id": 19, "name": "太阳", "english": "The Sun", "emoji": "☀️", "suit": "Major Arcana"},
    {"id": 20, "name": "审判", "english": "Judgement", "emoji": "📯", "suit": "Major Arcana"},
    {"id": 21, "name": "世界", "english": "The World", "emoji": "🌍", "suit": "Major Arcana"},

    # Minor Arcana - Wands
    {"id": 22, "name": "权杖王牌", "english": "Ace of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 23, "name": "权杖二", "english": "Two of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 24, "name": "权杖三", "english": "Three of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 25, "name": "权杖四", "english": "Four of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 26, "name": "权杖五", "english": "Five of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 27, "name": "权杖六", "english": "Six of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 28, "name": "权杖七", "english": "Seven of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 29, "name": "权杖八", "english": "Eight of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 30, "name": "权杖九", "english": "Nine of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 31, "name": "权杖十", "english": "Ten of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 32, "name": "权杖侍从", "english": "Page of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 33, "name": "权杖骑士", "english": "Knight of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 34, "name": "权杖王后", "english": "Queen of Wands", "emoji": "🔥", "suit": "Wands"},
    {"id": 35, "name": "权杖国王", "english": "King of Wands", "emoji": "🔥", "suit": "Wands"},

    # Minor Arcana - Cups
    {"id": 36, "name": "圣杯王牌", "english": "Ace of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 37, "name": "圣杯二", "english": "Two of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 38, "name": "圣杯三", "english": "Three of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 39, "name": "圣杯四", "english": "Four of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 40, "name": "圣杯五", "english": "Five of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 41, "name": "圣杯六", "english": "Six of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 42, "name": "圣杯七", "english": "Seven of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 43, "name": "圣杯八", "english": "Eight of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 44, "name": "圣杯九", "english": "Nine of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 45, "name": "圣杯十", "english": "Ten of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 46, "name": "圣杯侍从", "english": "Page of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 47, "name": "圣杯骑士", "english": "Knight of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 48, "name": "圣杯王后", "english": "Queen of Cups", "emoji": "💧", "suit": "Cups"},
    {"id": 49, "name": "圣杯国王", "english": "King of Cups", "emoji": "💧", "suit": "Cups"},

    # Minor Arcana - Swords
    {"id": 50, "name": "宝剑王牌", "english": "Ace of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 51, "name": "宝剑二", "english": "Two of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 52, "name": "宝剑三", "english": "Three of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 53, "name": "宝剑四", "english": "Four of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 54, "name": "宝剑五", "english": "Five of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 55, "name": "宝剑六", "english": "Six of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 56, "name": "宝剑七", "english": "Seven of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 57, "name": "宝剑八", "english": "Eight of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 58, "name": "宝剑九", "english": "Nine of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 59, "name": "宝剑十", "english": "Ten of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 60, "name": "宝剑侍从", "english": "Page of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 61, "name": "宝剑骑士", "english": "Knight of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 62, "name": "宝剑王后", "english": "Queen of Swords", "emoji": "⚔️", "suit": "Swords"},
    {"id": 63, "name": "宝剑国王", "english": "King of Swords", "emoji": "⚔️", "suit": "Swords"},

    # Minor Arcana - Pentacles
    {"id": 64, "name": "金币王牌", "english": "Ace of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 65, "name": "金币二", "english": "Two of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 66, "name": "金币三", "english": "Three of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 67, "name": "金币四", "english": "Four of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 68, "name": "金币五", "english": "Five of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 69, "name": "金币六", "english": "Six of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 70, "name": "金币七", "english": "Seven of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 71, "name": "金币八", "english": "Eight of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 72, "name": "金币九", "english": "Nine of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 73, "name": "金币十", "english": "Ten of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 74, "name": "金币侍从", "english": "Page of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 75, "name": "金币骑士", "english": "Knight of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 76, "name": "金币王后", "english": "Queen of Pentacles", "emoji": "🪙", "suit": "Pentacles"},
    {"id": 77, "name": "金币国王", "english": "King of Pentacles", "emoji": "🪙", "suit": "Pentacles"}
]

def fisher_yates_shuffle(cards: List[Dict]) -> List[Dict]:
    """High-quality Fisher-Yates shuffle using cryptographic randomness"""
    shuffled = cards.copy()
    for i in range(len(shuffled) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled

def draw_cards(count: int = 1, allow_reversed: bool = True) -> List[Dict[str, Any]]:
    """Draw random tarot cards with optional reversal"""
    if count < 1 or count > 78:
        raise ValueError("Card count must be between 1 and 78")

    # Shuffle the deck with high-quality randomness
    shuffled_deck = fisher_yates_shuffle(TAROT_CARDS)

    # Draw the requested number of cards
    drawn = [card.copy() for card in shuffled_deck[:count]]

    # Add reversal information if requested
    if allow_reversed:
        for card in drawn:
            card["reversed"] = secrets.choice([True, False])
    else:
        for card in drawn:
            card["reversed"] = False

    return drawn

def main():
    """MCP Tool main function"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing command"}))
        return

    command = sys.argv[1]

    try:
        if command == "draw":
            # Parse arguments
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            allow_reversed = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True

            # Draw cards
            cards = draw_cards(count, allow_reversed)

            # Return result
            result = {
                "success": True,
                "cards": cards,
                "count": len(cards),
                "timestamp": str(random.getrandbits(64))  # Unique draw ID
            }
            print(json.dumps(result, ensure_ascii=False))

        elif command == "info":
            # Return deck information
            result = {
                "success": True,
                "total_cards": len(TAROT_CARDS),
                "major_arcana": len([c for c in TAROT_CARDS if c["suit"] == "Major Arcana"]),
                "minor_arcana": len([c for c in TAROT_CARDS if c["suit"] != "Major Arcana"]),
                "suits": list(set(c["suit"] for c in TAROT_CARDS))
            }
            print(json.dumps(result, ensure_ascii=False))

        else:
            print(json.dumps({"error": f"Unknown command: {command}"}))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
