#!/usr/bin/env python3
"""
BaZi Time Converter MCP Tool
Converts birth date/time to Chinese Four Pillars (八字)
"""

import json
import sys
import datetime
from typing import Dict, Any, Tuple

# 天干 (Heavenly Stems)
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支 (Earthly Branches)
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行 (Five Elements)
FIVE_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", 
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", 
    "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", 
    "戌": "土", "亥": "水"
}

# 阴阳 (Yin Yang)
YIN_YANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴",
    "子": "阳", "丑": "阴", "寅": "阳", "卯": "阴", "辰": "阳",
    "巳": "阴", "午": "阳", "未": "阴", "申": "阳", "酉": "阴",
    "戌": "阳", "亥": "阴"
}

def get_stem_branch_from_year(year: int) -> Tuple[str, str]:
    """Calculate stem and branch for year"""
    # 1984年是甲子年，作为基准
    base_year = 1984
    year_offset = (year - base_year) % 60
    
    stem_index = year_offset % 10
    branch_index = year_offset % 12
    
    return HEAVENLY_STEMS[stem_index], EARTHLY_BRANCHES[branch_index]

def get_stem_branch_from_month(year: int, month: int) -> Tuple[str, str]:
    """Calculate stem and branch for month"""
    # 月支固定：寅月(正月)、卯月(二月)...
    month_branches = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    branch = month_branches[month - 1]
    
    # 月干计算：甲己年丙作首，乙庚年戊为头...
    year_stem = get_stem_branch_from_year(year)[0]
    year_stem_index = HEAVENLY_STEMS.index(year_stem)
    
    # 月干起始表
    month_stem_start = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}  # 甲年丙寅月开始
    start_index = month_stem_start[year_stem_index]
    stem_index = (start_index + month - 1) % 10
    
    return HEAVENLY_STEMS[stem_index], branch

def get_stem_branch_from_day(year: int, month: int, day: int) -> Tuple[str, str]:
    """Calculate stem and branch for day using Julian day number"""
    # 计算儒略日数
    if month <= 2:
        year -= 1
        month += 12
    
    a = year // 100
    b = 2 - a + a // 4
    
    julian_day = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524
    
    # 甲子日的儒略日数为基准
    base_julian = 1758289  # 1984年2月2日甲子日
    day_offset = (julian_day - base_julian) % 60
    
    stem_index = day_offset % 10
    branch_index = day_offset % 12
    
    return HEAVENLY_STEMS[stem_index], EARTHLY_BRANCHES[branch_index]

def get_stem_branch_from_hour(hour: int, day_stem: str) -> Tuple[str, str]:
    """Calculate stem and branch for hour"""
    # 时支固定
    hour_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    branch_index = (hour + 1) // 2 % 12
    branch = hour_branches[branch_index]
    
    # 时干计算：甲己还加甲，乙庚丙作初...
    day_stem_index = HEAVENLY_STEMS.index(day_stem)
    hour_stem_start = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
    start_index = hour_stem_start[day_stem_index]
    stem_index = (start_index + branch_index) % 10
    
    return HEAVENLY_STEMS[stem_index], branch

def calculate_bazi(year: int, month: int, day: int, hour: int = 12) -> Dict[str, Any]:
    """Calculate complete BaZi (Four Pillars)"""
    try:
        # Validate date
        datetime.date(year, month, day)
        
        # Calculate each pillar
        year_stem, year_branch = get_stem_branch_from_year(year)
        month_stem, month_branch = get_stem_branch_from_month(year, month)
        day_stem, day_branch = get_stem_branch_from_day(year, month, day)
        hour_stem, hour_branch = get_stem_branch_from_hour(hour, day_stem)
        
        # Build pillars
        year_pillar = year_stem + year_branch
        month_pillar = month_stem + month_branch
        day_pillar = day_stem + day_branch
        hour_pillar = hour_stem + hour_branch
        
        # Calculate five elements distribution
        all_chars = [year_stem, year_branch, month_stem, month_branch, 
                    day_stem, day_branch, hour_stem, hour_branch]
        
        element_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        for char in all_chars:
            element = FIVE_ELEMENTS[char]
            element_count[element] += 1
        
        # Calculate yin yang distribution
        yin_yang_count = {"阳": 0, "阴": 0}
        for char in all_chars:
            yy = YIN_YANG[char]
            yin_yang_count[yy] += 1
        
        return {
            "success": True,
            "birth_info": {
                "year": year,
                "month": month, 
                "day": day,
                "hour": hour
            },
            "four_pillars": {
                "year": year_pillar,
                "month": month_pillar,
                "day": day_pillar,
                "hour": hour_pillar
            },
            "detailed_pillars": {
                "year": {"stem": year_stem, "branch": year_branch},
                "month": {"stem": month_stem, "branch": month_branch},
                "day": {"stem": day_stem, "branch": day_branch},
                "hour": {"stem": hour_stem, "branch": hour_branch}
            },
            "day_master": day_stem,
            "five_elements": element_count,
            "yin_yang": yin_yang_count,
            "element_analysis": {
                "strongest": max(element_count, key=element_count.get),
                "weakest": min(element_count, key=element_count.get),
                "missing": [k for k, v in element_count.items() if v == 0]
            }
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
                print(json.dumps({"error": "Missing date arguments. Usage: convert YYYY MM DD [HH]"}))
                return
            
            year = int(sys.argv[2])
            month = int(sys.argv[3])
            day = int(sys.argv[4])
            hour = int(sys.argv[5]) if len(sys.argv) > 5 else 12  # Default noon
            
            # Calculate BaZi
            result = calculate_bazi(year, month, day, hour)
            print(json.dumps(result, ensure_ascii=False))
            
        elif command == "info":
            # Return system information
            result = {
                "success": True,
                "system": "BaZi Four Pillars",
                "heavenly_stems": HEAVENLY_STEMS,
                "earthly_branches": EARTHLY_BRANCHES,
                "five_elements": ["木", "火", "土", "金", "水"],
                "yin_yang": ["阴", "阳"]
            }
            print(json.dumps(result, ensure_ascii=False))
            
        else:
            print(json.dumps({"error": f"Unknown command: {command}"}))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
