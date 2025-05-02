"""
Date and time utility functions for fortune telling applications.
"""
import datetime
import calendar
from typing import Tuple, Optional, Union, Dict, Any

__all__ = [
    'lunar_to_solar', 
    'solar_to_lunar', 
    'get_zodiac_sign',
    'get_chinese_zodiac',
    'get_day_of_week',
    'format_date'
]


def lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int,
                  is_leap_month: bool = False) -> Tuple[int, int, int]:
    """
    Convert Chinese lunar date to Gregorian solar date.
    This is a simplified implementation and not accurate for all dates.
    For production use, consider using specialized libraries.
    
    Args:
        lunar_year: Lunar year
        lunar_month: Lunar month
        lunar_day: Lunar day
        is_leap_month: Whether the month is a leap month
        
    Returns:
        Tuple of (solar_year, solar_month, solar_day)
    """
    # This is a placeholder implementation
    # For accurate lunar-solar conversion, use dedicated libraries like lunarcalendar
    
    # Simplified approximation (very rough)
    # Chinese New Year typically falls between Jan 21 and Feb 20
    cny_day = (lunar_year * 5 + 7) % 30
    cny_month = 1 if cny_day < 21 else 2
    cny_day = cny_day if cny_month == 2 else cny_day + 10
    
    # Calculate days since Chinese New Year
    days_since_cny = 0
    for m in range(1, lunar_month):
        # Alternate between 29 and 30 days per lunar month
        days_since_cny += 29 + (m % 2)
    
    days_since_cny += lunar_day - 1
    
    # Convert to solar date
    solar_date = datetime.date(lunar_year, cny_month, cny_day) + \
                 datetime.timedelta(days=days_since_cny)
                 
    return (solar_date.year, solar_date.month, solar_date.day)


def solar_to_lunar(solar_year: int, solar_month: int, solar_day: int) -> Dict[str, Any]:
    """
    Convert Gregorian solar date to Chinese lunar date.
    This is a simplified implementation and not accurate for all dates.
    For production use, consider using specialized libraries.
    
    Args:
        solar_year: Solar year
        solar_month: Solar month
        solar_day: Solar day
        
    Returns:
        Dictionary with lunar date information
    """
    # This is a placeholder implementation
    # For accurate solar-lunar conversion, use dedicated libraries like lunarcalendar
    
    # Simplified approximation (very rough)
    solar_date = datetime.date(solar_year, solar_month, solar_day)
    
    # Estimate Chinese New Year
    cny_day = (solar_year * 5 + 7) % 30
    cny_month = 1 if cny_day < 21 else 2
    cny_day = cny_day if cny_month == 2 else cny_day + 10
    cny_date = datetime.date(solar_year, cny_month, cny_day)
    
    # If before CNY, it's the previous lunar year
    if solar_date < cny_date:
        lunar_year = solar_year - 1
        days_since_cny = (cny_date - solar_date).days
        # Estimate lunar month and day (very rough)
        lunar_month = 12 - (days_since_cny // 30)
        lunar_day = 30 - (days_since_cny % 30)
    else:
        lunar_year = solar_year
        days_since_cny = (solar_date - cny_date).days
        # Estimate lunar month and day (very rough)
        lunar_month = 1 + (days_since_cny // 30)
        lunar_day = 1 + (days_since_cny % 30)
    
    # Adjust for impossible values
    if lunar_month > 12:
        lunar_month = 12
    if lunar_day > 30:
        lunar_day = 30
    
    return {
        'year': lunar_year,
        'month': lunar_month,
        'day': lunar_day,
        'leap_month': False,  # Simplified implementation doesn't detect leap months
        'zodiac_animal': get_chinese_zodiac(lunar_year)
    }


def get_zodiac_sign(month: int, day: int) -> Tuple[str, str]:
    """
    Get western zodiac sign name for a given month and day.
    
    Args:
        month: Month (1-12)
        day: Day (1-31)
        
    Returns:
        Tuple of (zodiac_name_en, zodiac_name_zh)
    """
    zodiac_signs = [
        ((1, 20), (2, 18), "Aquarius", "水瓶座"),
        ((2, 19), (3, 20), "Pisces", "双鱼座"),
        ((3, 21), (4, 19), "Aries", "白羊座"),
        ((4, 20), (5, 20), "Taurus", "金牛座"),
        ((5, 21), (6, 20), "Gemini", "双子座"),
        ((6, 21), (7, 22), "Cancer", "巨蟹座"),
        ((7, 23), (8, 22), "Leo", "狮子座"),
        ((8, 23), (9, 22), "Virgo", "处女座"),
        ((9, 23), (10, 22), "Libra", "天秤座"),
        ((10, 23), (11, 21), "Scorpio", "天蝎座"),
        ((11, 22), (12, 21), "Sagittarius", "射手座"),
        ((12, 22), (1, 19), "Capricorn", "摩羯座")
    ]
    
    for (start_m, start_d), (end_m, end_d), name_en, name_zh in zodiac_signs:
        # Handle special case of Capricorn (spans Dec-Jan)
        if start_m == 12 and end_m == 1:
            if (month == 12 and day >= start_d) or (month == 1 and day <= end_d):
                return name_en, name_zh
        else:
            if (month == start_m and day >= start_d) or \
               (month == end_m and day <= end_d) or \
               (start_m < month < end_m):
                return name_en, name_zh
    
    # Default fallback (should never reach here if data is correct)
    return "Unknown", "未知"


def get_chinese_zodiac(year: int) -> str:
    """
    Get Chinese zodiac animal for a given lunar year.
    
    Args:
        year: Lunar year
        
    Returns:
        Chinese zodiac animal name in Chinese
    """
    animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    return animals[(year - 4) % 12]


def get_day_of_week(year: int, month: int, day: int, return_chinese: bool = True) -> str:
    """
    Get the day of the week for a given date.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day (1-31)
        return_chinese: Whether to return the name in Chinese
        
    Returns:
        Day of the week name
    """
    weekday = datetime.date(year, month, day).weekday()
    
    if return_chinese:
        chinese_weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return chinese_weekdays[weekday]
    else:
        english_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return english_weekdays[weekday]


def format_date(date: Union[datetime.date, datetime.datetime, Tuple[int, int, int]], 
               format_str: str = "YYYY年MM月DD日") -> str:
    """
    Format a date according to a given format string.
    
    Args:
        date: Date object, datetime object, or tuple of (year, month, day)
        format_str: Format string, using placeholders:
                    YYYY: 4-digit year, YY: 2-digit year
                    MM: 2-digit month, M: 1-digit month
                    DD: 2-digit day, D: 1-digit day
                    
    Returns:
        Formatted date string
    """
    if isinstance(date, tuple) and len(date) >= 3:
        year, month, day = date
    elif isinstance(date, (datetime.date, datetime.datetime)):
        year, month, day = date.year, date.month, date.day
    else:
        raise ValueError("Unsupported date format")
    
    # Replace placeholders
    result = format_str.replace("YYYY", f"{year:04d}")
    result = result.replace("YY", f"{year % 100:02d}")
    result = result.replace("MM", f"{month:02d}")
    result = result.replace("M", f"{month}")
    result = result.replace("DD", f"{day:02d}")
    result = result.replace("D", f"{day}")
    
    return result
