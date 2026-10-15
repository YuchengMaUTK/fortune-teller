"""
Zodiac/Astrology fortune telling system implementation.
"""
import datetime
import logging
import math
from typing import Dict, Any, List, Tuple

from fortune_teller.core import BaseFortuneSystem

# Configure logging
logger = logging.getLogger("ZodiacFortuneSystem")


class ZodiacFortuneSystem(BaseFortuneSystem):
    """
    Zodiac/Astrology fortune telling system.
    Based on western astrology and zodiac signs.
    """
    
    # Constants for zodiac calculations
    ZODIAC_SIGNS = [
        {"name": "白羊座", "english": "Aries", "start_date": (3, 21), "end_date": (4, 19),
         "element": "火", "quality": "主动", "ruler": "火星", "emoji": "🐏"},
        {"name": "金牛座", "english": "Taurus", "start_date": (4, 20), "end_date": (5, 20),
         "element": "土", "quality": "固定", "ruler": "金星", "emoji": "🐂"},
        {"name": "双子座", "english": "Gemini", "start_date": (5, 21), "end_date": (6, 20),
         "element": "风", "quality": "变动", "ruler": "水星", "emoji": "👯"},
        {"name": "巨蟹座", "english": "Cancer", "start_date": (6, 21), "end_date": (7, 22),
         "element": "水", "quality": "主动", "ruler": "月亮", "emoji": "🦀"},
        {"name": "狮子座", "english": "Leo", "start_date": (7, 23), "end_date": (8, 22),
         "element": "火", "quality": "固定", "ruler": "太阳", "emoji": "🦁"},
        {"name": "处女座", "english": "Virgo", "start_date": (8, 23), "end_date": (9, 22),
         "element": "土", "quality": "变动", "ruler": "水星", "emoji": "👧"},
        {"name": "天秤座", "english": "Libra", "start_date": (9, 23), "end_date": (10, 22),
         "element": "风", "quality": "主动", "ruler": "金星", "emoji": "⚖️"},
        {"name": "天蝎座", "english": "Scorpio", "start_date": (10, 23), "end_date": (11, 21),
         "element": "水", "quality": "固定", "ruler": "冥王星", "emoji": "🦂"},
        {"name": "射手座", "english": "Sagittarius", "start_date": (11, 22), "end_date": (12, 21),
         "element": "火", "quality": "变动", "ruler": "木星", "emoji": "🏹"},
        {"name": "摩羯座", "english": "Capricorn", "start_date": (12, 22), "end_date": (1, 19),
         "element": "土", "quality": "主动", "ruler": "土星", "emoji": "🐐"},
        {"name": "水瓶座", "english": "Aquarius", "start_date": (1, 20), "end_date": (2, 18),
         "element": "风", "quality": "固定", "ruler": "天王星", "emoji": "🏺"},
        {"name": "双鱼座", "english": "Pisces", "start_date": (2, 19), "end_date": (3, 20),
         "element": "水", "quality": "变动", "ruler": "海王星", "emoji": "🐟"}
    ]
    
    PLANETS = ["太阳", "月亮", "水星", "金星", "火星", "木星", "土星", "天王星", "海王星", "冥王星"]
    
    HOUSES = [
        "第一宫（上升宫）：自我意识、外表和个性",
        "第二宫：物质资源、价值观和财富",
        "第三宫：沟通、思维和短途旅行",
        "第四宫（天底宫）：家庭、根源和安全感",
        "第五宫：创造力、浪漫和娱乐",
        "第六宫：工作、健康和日常生活",
        "第七宫（下降宫）：伴侣关系、合作和公开的敌人",
        "第八宫：共享资源、转变和亲密关系",
        "第九宫：高等教育、哲学和长途旅行",
        "第十宫（中天宫）：职业、地位和公众形象",
        "第十一宫：友谊、社交圈和团体活动",
        "第十二宫：潜意识、秘密和自我限制"
    ]
    
    ELEMENTS = {
        "火": {"keywords": ["激情", "行动", "能量", "创造力"], "compatible": ["风"], "incompatible": ["水"], "emoji": "🔥"},
        "土": {"keywords": ["稳定", "实际", "可靠", "物质"], "compatible": ["水"], "incompatible": ["风"], "emoji": "🪨"},
        "风": {"keywords": ["思想", "沟通", "社交", "理智"], "compatible": ["火"], "incompatible": ["土"], "emoji": "🌪️"},
        "水": {"keywords": ["情感", "直觉", "敏感", "同理心"], "compatible": ["土"], "incompatible": ["火"], "emoji": "💧"}
    }
    
    QUALITIES = {
        "主动": "主动性格，喜欢发起行动，有领导力",
        "固定": "坚定稳固，有耐力，但可能固执",
        "变动": "适应性强，灵活多变，但可能缺乏决断力"
    }
    
    def display_processed_data(self, processed_data: Dict[str, Any]) -> None:
        from fortune_teller.ui.rendering import display_chart
        display_chart("zodiac", processed_data)

    def get_chat_system_prompt(self) -> str:
        """
        Get a system prompt for chat mode specific to Zodiac system.
        
        Returns:
            System prompt string for chat mode
        """
        return """你是"霄占"占星师，一位精通西方占星学的专家，有着丰富的占星咨询经验。
你融合了现代心理学与古典占星知识，能够透过星盘揭示人生的潜能与挑战。
你的风格既有专业深度，又不乏幽默感，能够用生动的比喻和实例解释复杂的星象。

现在你正在与求测者进行轻松的聊天互动。你可以谈论:
- 星座特质与元素属性
- 行星能量与相位解读
- 当前星象的影响与转机
- 如何更好地利用自己的星盘优势
- 应对挑战的实用建议

在回答问题时，你既尊重占星学的传统知识，又不会完全决定论，而是强调每个人都有自由意志来选择如何应对星象影响。
对话应简洁精炼，回答控制在200字以内，用优雅而生动的语言表达专业见解。"""
    
    def __init__(self):
        """Initialize the Zodiac fortune system."""
        super().__init__(
            name="zodiac",
            display_name="星座占星",
            description="基于西方占星学和十二星座的命运分析"
        )
    
    def get_required_inputs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about required inputs for this fortune system.
        
        Returns:
            Dictionary mapping input field names to their metadata
        """
        return {
            "birth_date": {
                "type": "date",
                "description": "出生日期 (YYYY-MM-DD)",
                "required": True
            },
            "birth_time": {
                "type": "time",
                "description": "出生时间 (HH:MM)",
                "required": False
            },
            "birth_place": {
                "type": "text",
                "description": "出生地点",
                "required": False
            },
            "question_area": {
                "type": "select",
                "description": "关注领域",
                "options": ["爱情", "事业", "健康", "财富", "人际关系", "整体运势"],
                "required": False
            }
        }
    
    def validate_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input for zodiac analysis.
        
        Args:
            user_input: Dictionary containing user input data
            
        Returns:
            Validated and normalized input data
            
        Raises:
            ValueError: If the input data is invalid
        """
        validated = {}
        
        # Validate birth_date
        if "birth_date" not in user_input:
            raise ValueError("出生日期是必须的")
        
        try:
            # Handle string date
            if isinstance(user_input["birth_date"], str):
                validated["birth_date"] = datetime.datetime.strptime(
                    user_input["birth_date"], "%Y-%m-%d"
                ).date()
            # Handle datetime or date object
            elif hasattr(user_input["birth_date"], "year"):
                validated["birth_date"] = user_input["birth_date"]
            else:
                raise ValueError("出生日期格式错误")
        except Exception as e:
            raise ValueError(f"出生日期格式错误: {e}")
        
        # Validate birth_time (optional)
        if "birth_time" in user_input and user_input["birth_time"]:
            try:
                # Handle string time
                if isinstance(user_input["birth_time"], str):
                    time_obj = datetime.datetime.strptime(
                        user_input["birth_time"], "%H:%M"
                    ).time()
                # Handle time object
                elif hasattr(user_input["birth_time"], "hour"):
                    time_obj = user_input["birth_time"]
                else:
                    raise ValueError("出生时间格式错误")
                
                validated["birth_time"] = time_obj
            except Exception as e:
                raise ValueError(f"出生时间格式错误: {e}")
        else:
            validated["birth_time"] = None
        
        # Validate birth_place (optional)
        if "birth_place" in user_input and user_input["birth_place"]:
            validated["birth_place"] = user_input["birth_place"].strip()
        else:
            validated["birth_place"] = None
        
        # Validate question_area (optional)
        valid_areas = ["爱情", "事业", "健康", "财富", "人际关系", "整体运势"]
        if "question_area" in user_input and user_input["question_area"]:
            if user_input["question_area"] not in valid_areas:
                raise ValueError(f"不支持的关注领域: {user_input['question_area']}")
            validated["question_area"] = user_input["question_area"]
        else:
            validated["question_area"] = "整体运势"  # Default
        
        return validated
    
    def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the validated input data according to zodiac/astrology rules.
        
        Args:
            validated_input: Validated user input
            
        Returns:
            Processed data ready for LLM prompt generation
        """
        birth_date = validated_input["birth_date"]
        birth_time = validated_input["birth_time"]
        birth_place = validated_input["birth_place"]
        question_area = validated_input["question_area"]
        
        # Determine zodiac sign
        zodiac_sign = self._get_zodiac_sign(birth_date.month, birth_date.day)
        
        # Determine current transits and aspects
        current_date = datetime.date.today()
        current_transits = self._get_current_transits(zodiac_sign, current_date)
        
        # Determine moon sign (simplified, would normally need birth time and location)
        moon_sign = self._get_simplified_moon_sign(birth_date)
        
        # Determine rising sign (simplified, would normally need birth time and location)
        rising_sign = None
        if birth_time:
            rising_sign = self._get_simplified_rising_sign(
                birth_date, birth_time
            )
        
        # Get compatibility with other signs
        compatibility = self._get_sign_compatibility(zodiac_sign)
        
        # Get element and quality information
        element = zodiac_sign["element"]
        quality = zodiac_sign["quality"]
        
        # Format the result
        processed_data = {
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "birth_time": birth_time.strftime("%H:%M") if birth_time else "未知",
            "birth_place": birth_place or "未知",
            "question_area": question_area,
            "zodiac_sign": {
                "name": zodiac_sign["name"],
                "english": zodiac_sign["english"],
                "element": element,
                "quality": quality,
                "ruler": zodiac_sign["ruler"],
                "date_range": f"{zodiac_sign['start_date'][0]}月{zodiac_sign['start_date'][1]}日 - {zodiac_sign['end_date'][0]}月{zodiac_sign['end_date'][1]}日"
            },
            "moon_sign": moon_sign["name"] if moon_sign else "未知",
            "rising_sign": rising_sign["name"] if rising_sign else "未知",
            "element_info": self.ELEMENTS[element],
            "quality_info": self.QUALITIES[quality],
            "compatibility": compatibility,
            "current_transits": current_transits
        }
        
        return processed_data
    
    def generate_llm_prompt(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate prompts for the LLM based on processed zodiac data.
        
        Args:
            processed_data: Data processed by the zodiac system
            
        Returns:
            Dictionary containing system_prompt and user_prompt for the LLM
        """
        # Create the system prompt
        system_prompt = f"""你是一位专业的占星师，精通西方占星学和星座分析。
请根据提供的星座信息，为咨询者提供详细且有洞见的占星解读。
你的分析应该包含以下内容：
1. 星座的基本特质和个性倾向
2. 元素和品质对性格的影响
3. 月亮星座和上升星座（如果已知）的额外影响
4. 行星位置和当前相位对各生活领域的影响
5. 针对咨询者关注领域的具体建议和见解
6. 近期运势趋势和重要时间点

你的分析应当平衡、客观，避免过于绝对化的预测。提供实用的建议和观点，帮助咨询者更好地理解自己和当前的能量影响。
请记住，占星解读是提供可能性的指引，而非确定性的命运。
"""
        
        # Get the zodiac information
        sign_info = processed_data["zodiac_sign"]
        moon_sign = processed_data["moon_sign"]
        rising_sign = processed_data["rising_sign"]
        element_info = processed_data["element_info"]
        quality_info = processed_data["quality_info"]
        compatibility = processed_data["compatibility"]
        current_transits = processed_data["current_transits"]
        question_area = processed_data["question_area"]
        
        # Create user prompt with the analyzed data
        user_prompt = f"""请为以下星座信息提供占星解读：

基本信息：
- 出生日期：{processed_data['birth_date']}
- 出生时间：{processed_data['birth_time']}
- 出生地点：{processed_data['birth_place']}
- 关注领域：{question_area}

星座信息：
- 太阳星座：{sign_info['name']} ({sign_info['english']})，{sign_info['date_range']}
- 月亮星座：{moon_sign}
- 上升星座：{rising_sign}

{sign_info['name']}的基本特质：
- 主宰星：{sign_info['ruler']}
- 元素：{sign_info['element']}（{', '.join(element_info['keywords'])}）
- 品质：{sign_info['quality']}（{quality_info}）

星座相合性：
"""
        
        # Add compatibility information
        for sign, level in compatibility.items():
            user_prompt += f"- 与{sign}：{level}\n"
        
        # Add current transits
        user_prompt += f"""
当前星象与影响：
"""
        
        for transit in current_transits:
            user_prompt += f"- {transit['description']}: {transit['influence']}\n"
        
        user_prompt += f"""
请根据以上信息，为咨询者提供详细的占星解读，特别针对"{question_area}"领域给出具体的见解和建议。
包括近期的能量变化趋势、可能的机遇或挑战，以及如何最佳利用当前的星象能量。
"""
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
    
    def format_result(self, llm_response: str) -> Dict[str, Any]:
        """
        Format the LLM response into a structured output.
        
        Args:
            llm_response: Raw response from the LLM
            
        Returns:
            Formatted and structured result
        """
        # For zodiac readings, we'll divide the response into sections
        # based on common section headers in astrology readings
        
        # Try to identify sections in the response
        sections = {}
        current_section = "总体解读"
        section_text = []
        
        for line in llm_response.split('\n'):
            # Check if line is a section header
            if line.strip().startswith('##'):
                # Save previous section
                if section_text:
                    sections[current_section] = '\n'.join(section_text).strip()
                    section_text = []
                
                # Extract new section name
                current_section = line.strip('#').strip()
            elif line.strip().startswith('#'):
                # Save previous section
                if section_text:
                    sections[current_section] = '\n'.join(section_text).strip()
                    section_text = []
                
                # Extract new section name
                current_section = line.strip('#').strip()
            else:
                section_text.append(line)
        
        # Save the last section
        if section_text:
            sections[current_section] = '\n'.join(section_text).strip()
        
        # If no sections were found, use the entire text as the general section
        if len(sections) <= 1:
            sections = {
                "总体解读": llm_response.strip()
            }
        
        return {
            "reading": sections,
            "full_text": llm_response,
            "format_version": "1.0"
        }
    
    def _get_zodiac_sign(self, month: int, day: int) -> Dict[str, Any]:
        """
        Determine zodiac sign based on birth month and day.
        
        Args:
            month: Birth month (1-12)
            day: Birth day (1-31)
            
        Returns:
            Zodiac sign information dictionary
        """
        for sign in self.ZODIAC_SIGNS:
            start_month, start_day = sign["start_date"]
            end_month, end_day = sign["end_date"]
            
            # Handle cases where sign spans across year boundary (e.g., Capricorn)
            if start_month > end_month:
                # If date is in start month and after/on start day, or
                # If date is in end month and before/on end day
                if (month == start_month and day >= start_day) or \
                   (month == end_month and day <= end_day):
                    return sign
            else:
                # Normal case: if date is between start and end dates
                if (month == start_month and day >= start_day) or \
                   (month == end_month and day <= end_day) or \
                   (start_month < month < end_month):
                    return sign
        
        # Default fallback (should never reach here if data is correct)
        logger.warning(f"Could not determine zodiac sign for {month}/{day}")
        return self.ZODIAC_SIGNS[0]
    
    def _get_simplified_moon_sign(self, birth_date: datetime.date) -> Dict[str, Any]:
        """
        Get a simplified approximation of moon sign based only on birth date.
        This is a gross simplification as real moon sign calculation requires
        precise time and location.
        
        Args:
            birth_date: Date of birth
            
        Returns:
            Moon sign information or None
        """
        # This is a very simplified approximation
        # The moon changes signs roughly every 2.5 days
        # We'll use the day of year as a rough estimate
        day_of_year = birth_date.timetuple().tm_yday
        sign_index = (day_of_year // 30) % 12
        
        return self.ZODIAC_SIGNS[sign_index]
    
    def _get_simplified_rising_sign(self, birth_date: datetime.date, 
                                   birth_time: datetime.time) -> Dict[str, Any]:
        """
        Get a simplified approximation of rising sign based on birth date and time.
        This is a gross simplification as real rising sign calculation requires
        precise time and location.
        
        Args:
            birth_date: Date of birth
            birth_time: Time of birth
            
        Returns:
            Rising sign information or None
        """
        # This is a very simplified approximation
        # The rising sign changes roughly every 2 hours
        # We'll use the hour of day as a rough estimate
        hour = birth_time.hour
        sign_index = (hour // 2) % 12
        
        return self.ZODIAC_SIGNS[sign_index]
    
    def _get_sign_compatibility(self, sign: Dict[str, Any]) -> Dict[str, str]:
        """
        Get compatibility of the given sign with other signs.
        
        Args:
            sign: Zodiac sign information
            
        Returns:
            Dictionary mapping sign names to compatibility levels
        """
        element = sign["element"]
        compatibility = {}
        
        for other_sign in self.ZODIAC_SIGNS:
            other_element = other_sign["element"]
            other_name = other_sign["name"]
            
            # Skip self comparison
            if other_name == sign["name"]:
                compatibility[other_name] = "自己"
                continue
            
            # Determine compatibility based on elements
            if other_element == element:
                compatibility[other_name] = "非常好"
            elif other_element in self.ELEMENTS[element]["compatible"]:
                compatibility[other_name] = "好"
            elif other_element in self.ELEMENTS[element]["incompatible"]:
                compatibility[other_name] = "需要努力"
            else:
                compatibility[other_name] = "一般"
        
        return compatibility
    
    def _get_current_transits(self, sign: Dict[str, Any], 
                             current_date: datetime.date) -> List[Dict[str, str]]:
        """
        Generate information about current planetary transits and their influence.
        This is a simplified version for demo purposes.
        
        Args:
            sign: Zodiac sign information
            current_date: Current date for transit calculation
            
        Returns:
            List of transit information dictionaries
        """
        # This is a simplified approximation for demo purposes
        # In a real astrology app, this would involve actual ephemeris calculations
        transits = [
            {
                "description": f"木星在{self._get_transit_position(current_date, 'Jupiter')}",
                "influence": "带来扩展和成长的机会"
            },
            {
                "description": f"土星在{self._get_transit_position(current_date, 'Saturn')}",
                "influence": "提示你关注责任和结构"
            },
            {
                "description": f"火星在{self._get_transit_position(current_date, 'Mars')}",
                "influence": "影响你的动力和行动力"
            },
            {
                "description": f"金星在{self._get_transit_position(current_date, 'Venus')}",
                "influence": "影响你的关系和价值观"
            },
            {
                "description": f"水星在{self._get_transit_position(current_date, 'Mercury')}",
                "influence": "影响你的沟通和思维方式"
            }
        ]
        
        # Add a special transit for the person's sun sign
        month = current_date.month
        day = current_date.day
        for s in self.ZODIAC_SIGNS:
            start_month, start_day = s["start_date"]
            end_month, end_day = s["end_date"]
            
            if (month == start_month and day >= start_day) or \
               (month == end_month and day <= end_day) or \
               (start_month < month < end_month):
                current_sign = s
                break
        else:
            current_sign = self.ZODIAC_SIGNS[0]  # fallback
        
        transits.append({
            "description": f"太阳目前在{current_sign['name']}",
            "influence": f"{'增强' if current_sign['element'] == sign['element'] else '挑战'}你的{sign['name']}能量"
        })
        
        return transits
    
    def _get_transit_position(self, date: datetime.date, planet: str) -> str:
        """
        Get a simplified transit position for a planet on a given date.
        This is a simplified version for demo purposes.
        
        Args:
            date: Date for transit calculation
            planet: Name of the planet
            
        Returns:
            Sign name where the planet is located
        """
        # This is a completely simplified approximation for demo purposes
        # In a real application, this would use proper ephemeris data
        day_of_year = date.timetuple().tm_yday
        
        # Different "speeds" for different planets
        if planet == "Moon":
            # Moon moves fastest, about 13 degrees per day
            sign_index = (day_of_year // 3) % 12
        elif planet == "Mercury" or planet == "Venus":
            # Mercury and Venus move relatively quickly
            sign_index = ((day_of_year // 30) + (hash(planet) % 5)) % 12
        elif planet == "Mars":
            sign_index = ((day_of_year // 60) + 3) % 12
        elif planet == "Jupiter":
            sign_index = ((day_of_year // 365) + 7) % 12
        elif planet == "Saturn":
            sign_index = ((day_of_year // 730) + 10) % 12
        else:
            # Other planets or points
            sign_index = ((day_of_year // 180) + hash(planet)) % 12
        
        return self.ZODIAC_SIGNS[sign_index]["name"]
