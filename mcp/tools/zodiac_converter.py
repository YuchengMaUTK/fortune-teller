#!/usr/bin/env python3
"""
Zodiac Sign Converter MCP Tool
Converts birth date to accurate zodiac sign with precise date ranges
"""

import json
import sys
from datetime import datetime, date
from typing import Dict, Any

# Zodiac sign data with precise date ranges (calculation-focused)
ZODIAC_SIGNS = [
    {
        "name": "水瓶座",
        "english": "Aquarius",
        "emoji": "♒",
        "element": "风",
        "element_en": "Air",
        "start_month": 1, "start_day": 20,
        "end_month": 2, "end_day": 18
    },
    {
        "name": "双鱼座",
        "english": "Pisces", 
        "emoji": "♓",
        "element": "水",
        "element_en": "Water",
        "start_month": 2, "start_day": 19,
        "end_month": 3, "end_day": 20
    },
    {
        "name": "白羊座",
        "english": "Aries",
        "emoji": "♈", 
        "element": "火",
        "element_en": "Fire",
        "start_month": 3, "start_day": 21,
        "end_month": 4, "end_day": 19
    },
    {
        "name": "金牛座",
        "english": "Taurus",
        "emoji": "♉",
        "element": "土",
        "element_en": "Earth", 
        "start_month": 4, "start_day": 20,
        "end_month": 5, "end_day": 20
    },
    {
        "name": "双子座",
        "english": "Gemini",
        "emoji": "♊",
        "element": "风", 
        "element_en": "Air",
        "start_month": 5, "start_day": 21,
        "end_month": 6, "end_day": 20
    },
    {
        "name": "巨蟹座",
        "english": "Cancer",
        "emoji": "♋",
        "element": "水",
        "element_en": "Water",
        "start_month": 6, "start_day": 21,
        "end_month": 7, "end_day": 22
    },
    {
        "name": "狮子座",
        "english": "Leo",
        "emoji": "♌",
        "element": "火",
        "element_en": "Fire",
        "start_month": 7, "start_day": 23,
        "end_month": 8, "end_day": 22
    },
    {
        "name": "处女座", 
        "english": "Virgo",
        "emoji": "♍",
        "element": "土",
        "element_en": "Earth",
        "start_month": 8, "start_day": 23,
        "end_month": 9, "end_day": 22
    },
    {
        "name": "天秤座",
        "english": "Libra", 
        "emoji": "♎",
        "element": "风",
        "element_en": "Air",
        "start_month": 9, "start_day": 23,
        "end_month": 10, "end_day": 22
    },
    {
        "name": "天蝎座",
        "english": "Scorpio",
        "emoji": "♏",
        "element": "水", 
        "element_en": "Water",
        "start_month": 10, "start_day": 23,
        "end_month": 11, "end_day": 21
    },
    {
        "name": "射手座",
        "english": "Sagittarius",
        "emoji": "♐",
        "element": "火",
        "element_en": "Fire",
        "start_month": 11, "start_day": 22,
        "end_month": 12, "end_day": 21
    },
    {
        "name": "摩羯座",
        "english": "Capricorn",
        "emoji": "♑",
        "element": "土",
        "element_en": "Earth", 
        "start_month": 12, "start_day": 22,
        "end_month": 1, "end_day": 19
    }
]

def get_zodiac_sign(month: int, day: int) -> Dict[str, Any]:
    """Get zodiac sign for given month and day"""
    try:
        # Validate input
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")
        if not (1 <= day <= 31):
            raise ValueError(f"Invalid day: {day}")
        
        # Check date validity
        try:
            datetime(2000, month, day)  # Use leap year for Feb 29
        except ValueError as e:
            raise ValueError(f"Invalid date: {month}-{day}")
        
        # Find matching zodiac sign
        for sign in ZODIAC_SIGNS:
            start_month = sign["start_month"]
            start_day = sign["start_day"]
            end_month = sign["end_month"]
            end_day = sign["end_day"]
            
            # Handle year boundary (Capricorn spans Dec-Jan)
            if start_month > end_month:  # Crosses year boundary
                if (month == start_month and day >= start_day) or \
                   (month == end_month and day <= end_day):
                    return sign
            else:  # Normal case
                if (month == start_month and day >= start_day) or \
                   (month == end_month and day <= end_day) or \
                   (start_month < month < end_month):
                    return sign
        
        # Should never reach here with valid input
        raise ValueError(f"No zodiac sign found for {month}-{day}")
        
    except Exception as e:
        raise ValueError(f"Error calculating zodiac sign: {e}")

def calculate_zodiac_info(year: int, month: int, day: int) -> Dict[str, Any]:
    """Calculate comprehensive zodiac information"""
    try:
        # Validate date
        birth_date = date(year, month, day)
        
        # Get zodiac sign
        zodiac_sign = get_zodiac_sign(month, day)
        
        # Calculate age
        today = date.today()
        age = today.year - year - ((today.month, today.day) < (month, day))
        
        # Calculate days until next birthday
        next_birthday = date(today.year, month, day)
        if next_birthday < today:
            next_birthday = date(today.year + 1, month, day)
        days_to_birthday = (next_birthday - today).days
        
        # Element compatibility
        element_compatibility = {
            "火": ["火", "风"],  # Fire compatible with Fire, Air
            "土": ["土", "水"],  # Earth compatible with Earth, Water  
            "风": ["风", "火"],  # Air compatible with Air, Fire
            "水": ["水", "土"]   # Water compatible with Water, Earth
        }
        
        compatible_elements = element_compatibility.get(zodiac_sign["element"], [])
        
        return {
            "success": True,
            "birth_info": {
                "year": year,
                "month": month,
                "day": day,
                "age": age,
                "days_to_birthday": days_to_birthday
            },
            "zodiac_sign": zodiac_sign,
            "element_compatibility": compatible_elements,
            "date_range": f"{zodiac_sign['start_month']}/{zodiac_sign['start_day']} - {zodiac_sign['end_month']}/{zodiac_sign['end_day']}",
            "calculation_date": str(today)
        }
        
    except ValueError as e:
        return {"success": False, "error": f"Invalid date: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """MCP Tool main function"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing command"}))
        return
    
    command = sys.argv[1]
    
    try:
        if command == "convert":
            # Parse date arguments
            if len(sys.argv) < 5:
                print(json.dumps({"error": "Missing date arguments. Usage: convert YYYY MM DD"}))
                return
            
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            day = int(sys.argv[4])
            
            # Calculate zodiac information
            result = calculate_zodiac_info(year, month, day)
            print(json.dumps(result, ensure_ascii=False))
            
        elif command == "info":
            # Return system information
            result = {
                "success": True,
                "system": "Western Zodiac Calculator",
                "total_signs": len(ZODIAC_SIGNS),
                "elements": ["火", "土", "风", "水"],
                "elements_en": ["Fire", "Earth", "Air", "Water"],
                "signs": [{"name": s["name"], "english": s["english"], "emoji": s["emoji"]} for s in ZODIAC_SIGNS]
            }
            print(json.dumps(result, ensure_ascii=False))
            
        else:
            print(json.dumps({"error": f"Unknown command: {command}"}))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
