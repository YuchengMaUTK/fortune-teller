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

def calculate_bazi(year: int, month: int, day: int, hour: int = 12, minute: int = 0, second: int = 0) -> Dict[str, Any]:
    """Calculate complete BaZi (Four Pillars)"""
    try:
        # Inputs are China Standard Time (UTC+08:00), without solar-time correction.
        # Sect 2 keeps the day pillar on the civil date until midnight.
        datetime.datetime(year, month, day, hour, minute, second)
        from lunar_python import Solar
        eight_char = Solar.fromYmdHms(
            year, month, day, hour, minute, second
        ).getLunar().getEightChar()
        eight_char.setSect(2)
        year_stem, year_branch = eight_char.getYear()
        month_stem, month_branch = eight_char.getMonth()
        day_stem, day_branch = eight_char.getDay()
        hour_stem, hour_branch = eight_char.getTime()

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
                "hour": hour,
                "minute": minute,
                "second": second
            },
            "calculation": {
                "timezone": "Asia/Shanghai",
                "day_boundary": "midnight",
                "solar_time_correction": False
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
        return {"success": False, "error": f"Invalid date/time: {e}"}
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
                print(json.dumps({"error": "Missing date arguments. Usage: convert YYYY MM DD [HH [mm [ss]]]"}))
                return

            year = int(sys.argv[2])
            month = int(sys.argv[3])
            day = int(sys.argv[4])
            hour = int(sys.argv[5]) if len(sys.argv) > 5 else 12  # Default noon

            # Calculate BaZi
            minute = int(sys.argv[6]) if len(sys.argv) > 6 else 0
            second = int(sys.argv[7]) if len(sys.argv) > 7 else 0
            result = calculate_bazi(year, month, day, hour, minute, second)
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
