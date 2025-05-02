"""
BaZi (Eight Characters) fortune telling system implementation.
"""
import datetime
import logging
from typing import Dict, Any, List, Tuple

from fortune_teller.core import BaseFortuneSystem

# Configure logging
logger = logging.getLogger("BaziFortuneSystem")


class BaziFortuneSystem(BaseFortuneSystem):
    """
    BaZi (Chinese Eight Characters) fortune telling system.
    Based on the Chinese traditional fortune telling method using a person's birth time.
    """
    
    def display_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """
        Display processed BaZi data (eight characters and five elements).
        
        Args:
            processed_data: Processed BaZi data
        """
        from fortune_teller.ui.colors import Colors, ELEMENT_COLORS
        
        # 获取基础信息
        gender = processed_data.get("gender", "未知")
        birth_date = processed_data.get("birth_date", "未知")
        birth_time = processed_data.get("birth_time", "未知")
        location = processed_data.get("location", "未知")
        
        # 获取四柱八字信息
        four_pillars = processed_data.get("four_pillars", {})
        year_pillar = four_pillars.get("year", "")
        month_pillar = four_pillars.get("month", "")
        day_pillar = four_pillars.get("day", "")
        hour_pillar = four_pillars.get("hour", "")
        
        # 获取年柱信息
        year_data = processed_data.get("year_pillar", {})
        year_stem = year_data.get("stem", "")
        year_branch = year_data.get("branch", "")
        year_stem_element = year_data.get("stem_element", "")
        year_branch_element = year_data.get("branch_element", "")
        
        # 获取月柱信息
        month_data = processed_data.get("month_pillar", {})
        month_stem = month_data.get("stem", "")
        month_branch = month_data.get("branch", "")
        month_stem_element = month_data.get("stem_element", "")
        month_branch_element = month_data.get("branch_element", "")
        
        # 获取日柱信息
        day_data = processed_data.get("day_pillar", {})
        day_stem = day_data.get("stem", "")
        day_branch = day_data.get("branch", "")
        day_stem_element = day_data.get("stem_element", "")
        day_branch_element = day_data.get("branch_element", "")
        
        # 获取时柱信息
        hour_data = processed_data.get("hour_pillar", {})
        if hour_data:
            hour_stem = hour_data.get("stem", "")
            hour_branch = hour_data.get("branch", "")
            hour_stem_element = hour_data.get("stem_element", "")
            hour_branch_element = hour_data.get("branch_element", "")
        else:
            hour_stem = hour_branch = hour_stem_element = hour_branch_element = "未知"
        
        # 获取五行统计
        elements_data = processed_data.get("elements", {})
        element_counts = elements_data.get("counts", {})
        strongest = elements_data.get("strongest", "未知")
        weakest = elements_data.get("weakest", "未知")
        
        # 获取日主信息
        day_master_data = processed_data.get("day_master", {})
        day_master = day_master_data.get("character", "")
        day_master_element = day_master_data.get("element", "")
        relationships = day_master_data.get("relationships", {})
        
        # 显示标题
        print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 八字命盘信息 ✨{Colors.ENDC}")
        print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
        
        # 显示基本信息
        print(f"{Colors.BOLD}【基本信息】{Colors.ENDC}")
        print(f"性别: {gender}")
        print(f"出生日期: {birth_date}")
        print(f"出生时间: {birth_time}")
        print(f"出生地点: {location}")
        print()
        
        # 显示八字四柱
        print(f"{Colors.BOLD}【四柱八字】{Colors.ENDC}")
        print(f"      {Colors.YELLOW}年柱{Colors.ENDC}         {Colors.YELLOW}月柱{Colors.ENDC}         {Colors.YELLOW}日柱{Colors.ENDC}         {Colors.YELLOW}时柱{Colors.ENDC}")
        
        # 显示天干
        stem_line = "天干:  "
        for stem, element in [(year_stem, year_stem_element), 
                             (month_stem, month_stem_element), 
                             (day_stem, day_stem_element), 
                             (hour_stem, hour_stem_element)]:
            color = ELEMENT_COLORS.get(element, Colors.ENDC)
            stem_line += f"{color}{stem}{Colors.ENDC} ({element})      "
        print(stem_line)
        
        # 显示地支
        branch_line = "地支:  "
        for branch, element in [(year_branch, year_branch_element), 
                               (month_branch, month_branch_element), 
                               (day_branch, day_branch_element), 
                               (hour_branch, hour_branch_element)]:
            color = ELEMENT_COLORS.get(element, Colors.ENDC)
            branch_line += f"{color}{branch}{Colors.ENDC} ({element})      "
        print(branch_line)
        print()
        
        # 显示五行统计
        print(f"{Colors.BOLD}【五行统计】{Colors.ENDC}")
        elements_line = ""
        for element, count in element_counts.items():
            color = ELEMENT_COLORS.get(element, Colors.ENDC)
            emoji = self.ELEMENT_EMOJIS.get(element, "")
            elements_line += f"{color}{element}{emoji}{Colors.ENDC}: {count}  "
        print(elements_line)
        
        # 显示最强最弱五行
        strongest_emoji = self.ELEMENT_EMOJIS.get(strongest, "")
        weakest_emoji = self.ELEMENT_EMOJIS.get(weakest, "")
        print(f"最强五行: {ELEMENT_COLORS.get(strongest, Colors.ENDC)}{strongest}{strongest_emoji}{Colors.ENDC}")
        print(f"最弱五行: {ELEMENT_COLORS.get(weakest, Colors.ENDC)}{weakest}{weakest_emoji}{Colors.ENDC}")
        print()
        
        # 显示日主信息
        print(f"{Colors.BOLD}【日主】{Colors.ENDC}")
        print(f"日主: {ELEMENT_COLORS.get(day_master_element, Colors.ENDC)}{day_master}{Colors.ENDC} ({day_master_element})")
        
        # 显示五行关系
        print(f"{Colors.BOLD}【五行关系】{Colors.ENDC}")
        for element, relationship in relationships.items():
            print(f"{ELEMENT_COLORS.get(day_master_element, Colors.ENDC)}{day_master_element}{Colors.ENDC} 与 {ELEMENT_COLORS.get(element, Colors.ENDC)}{element}{Colors.ENDC}: {relationship}")
        
        print(f"\n{Colors.CYAN}" + "-" * 60 + f"{Colors.ENDC}")
    
    def get_chat_system_prompt(self) -> str:
        """
        Get a system prompt for chat mode specific to BaZi system.
        
        Returns:
            System prompt string for chat mode
        """
        return """你是"霄占"八字命理大师，一位来自中国的传统命理学专家，已有30年的占卜经验。
你精通天干地支、五行生克、纳音、神煞等传统命理学知识，能够深入分析八字命盘。
你的性格风趣幽默又不失智慧，常常用生动的比喻解释复杂的命理概念。

现在你正在与求测者进行轻松的聊天互动。你可以谈论:
- 八字命理的基本原理与应用
- 五行相生相克的规律
- 十天干与十二地支的意义
- 八字与人生运势的关系
- 如何通过调整行为来改善命运

用生动有趣的语言表达，偶尔引用古诗词或俏皮话，让谈话充满趣味性。
对话应简洁精炼，回答控制在200字以内，保持亲切而专业的语气。
不要生硬地说教，而是像一位和蔼的老朋友一样分享智慧。"""
    
    # Constants for BaZi calculations
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # Element emojis
    ELEMENT_EMOJIS = {
        "木": "🌳",
        "火": "🔥",
        "土": "🪨",
        "金": "🥇",
        "水": "💧"
    }
    
    ELEMENTS = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木",
        "辰": "土", "巳": "火", "午": "火", "未": "土",
        "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    ELEMENT_RELATIONS = {
        "木": {"木": "比和", "火": "生", "土": "克", "金": "被克", "水": "被生"},
        "火": {"木": "被生", "火": "比和", "土": "生", "金": "克", "水": "被克"},
        "土": {"木": "被克", "火": "被生", "土": "比和", "金": "生", "水": "克"},
        "金": {"木": "克", "火": "被克", "土": "被生", "金": "比和", "水": "生"},
        "水": {"木": "生", "火": "克", "土": "被克", "金": "被生", "水": "比和"}
    }
    
    def __init__(self):
        """Initialize the BaZi fortune system."""
        super().__init__(
            name="bazi",
            display_name="八字命理",
            description="传统中国八字命理，基于出生年、月、日、时分析命运"
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
            "gender": {
                "type": "select",
                "description": "性别",
                "options": ["男", "女"],
                "required": True
            },
            "location": {
                "type": "text",
                "description": "出生地点",
                "required": False
            }
        }
    
    def validate_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input for BaZi analysis.
        
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
        
        # Validate gender
        if "gender" not in user_input:
            raise ValueError("性别是必须的")
        
        if user_input["gender"] not in ["男", "女"]:
            raise ValueError("性别必须是'男'或'女'")
        
        validated["gender"] = user_input["gender"]
        
        # Validate location (optional)
        if "location" in user_input and user_input["location"]:
            validated["location"] = user_input["location"]
        else:
            validated["location"] = None
        
        return validated
    
    def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the validated input data according to BaZi rules.
        
        Args:
            validated_input: Validated user input
            
        Returns:
            Processed data ready for LLM prompt generation
        """
        birth_date = validated_input["birth_date"]
        birth_time = validated_input["birth_time"]
        gender = validated_input["gender"]
        location = validated_input["location"]
        
        # Calculate BaZi (eight characters)
        year_stem, year_branch = self._get_year_pillar(birth_date.year)
        month_stem, month_branch = self._get_month_pillar(
            birth_date.year, birth_date.month
        )
        day_stem, day_branch = self._get_day_pillar(
            birth_date.year, birth_date.month, birth_date.day
        )
        
        if birth_time:
            hour_stem, hour_branch = self._get_hour_pillar(
                day_stem, birth_time.hour
            )
        else:
            hour_stem, hour_branch = None, None
        
        # Construct pillars
        year_pillar = f"{year_stem}{year_branch}"
        month_pillar = f"{month_stem}{month_branch}"
        day_pillar = f"{day_stem}{day_branch}"
        hour_pillar = f"{hour_stem}{hour_branch}" if hour_stem else "未知"
        
        # Calculate elements for each stem and branch
        elements = []
        for char in [year_stem, year_branch, month_stem, month_branch, 
                    day_stem, day_branch]:
            if char in self.ELEMENTS:
                elements.append(self.ELEMENTS[char])
        
        if hour_stem and hour_branch:
            elements.extend([
                self.ELEMENTS[hour_stem], 
                self.ELEMENTS[hour_branch]
            ])
        
        # Count elements
        element_counts = {
            "木": elements.count("木"),
            "火": elements.count("火"),
            "土": elements.count("土"),
            "金": elements.count("金"),
            "水": elements.count("水")
        }
        
        # Determine the strongest and weakest elements
        strongest = max(element_counts, key=element_counts.get)
        weakest = min(element_counts, key=element_counts.get)
        
        # Analyze day master (day stem)
        day_master = day_stem
        day_master_element = self.ELEMENTS[day_master]
        
        # Analyze relationships between day master and other elements
        relationships = {}
        for element, count in element_counts.items():
            if count > 0:
                relationships[element] = self.ELEMENT_RELATIONS[day_master_element][element]
        
        # Format the result
        processed_data = {
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "birth_time": birth_time.strftime("%H:%M") if birth_time else "未知",
            "gender": gender,
            "location": location or "未知",
            "four_pillars": {
                "year": year_pillar,
                "month": month_pillar,
                "day": day_pillar,
                "hour": hour_pillar
            },
            "year_pillar": {
                "stem": year_stem,
                "branch": year_branch,
                "stem_element": self.ELEMENTS[year_stem],
                "branch_element": self.ELEMENTS[year_branch]
            },
            "month_pillar": {
                "stem": month_stem,
                "branch": month_branch,
                "stem_element": self.ELEMENTS[month_stem],
                "branch_element": self.ELEMENTS[month_branch]
            },
            "day_pillar": {
                "stem": day_stem,
                "branch": day_branch,
                "stem_element": self.ELEMENTS[day_stem],
                "branch_element": self.ELEMENTS[day_branch]
            },
            "elements": {
                "counts": element_counts,
                "strongest": strongest,
                "weakest": weakest
            },
            "day_master": {
                "character": day_master,
                "element": day_master_element,
                "relationships": relationships
            }
        }
        
        if hour_stem and hour_branch:
            processed_data["hour_pillar"] = {
                "stem": hour_stem,
                "branch": hour_branch,
                "stem_element": self.ELEMENTS[hour_stem],
                "branch_element": self.ELEMENTS[hour_branch]
            }
        else:
            processed_data["hour_pillar"] = None
        
        return processed_data
    
    def generate_llm_prompt(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate prompts for the LLM based on processed BaZi data.
        
        Args:
            processed_data: Data processed by the BaZi system
            
        Returns:
            Dictionary containing system_prompt and user_prompt for the LLM
        """
        # Create the system prompt with a more engaging, friendly persona
        system_prompt = f"""你是"霄占"命理大师，一位来自中国的八字命理学专家，已有30年的占卜经验，性格风趣幽默又不失智慧。
你的特点是：用生动有趣的语言解读命理，偶尔引用网络流行语和古代诗词，让严肃的命理学充满趣味性。
你对每位求测者都充满好奇和热情，像对老朋友一样亲切自然，经常使用"哎呀""啧啧""哈哈"等口头禅。

请基于以下八字信息，**首先只提供**：

亲切地问候求测者，可以根据他们的八字或出生日期开个小玩笑
1. 八字总评：以诙谐的方式点评命局整体特点，用生动比喻说明此八字的基本特质
2. 五行简述：简单介绍五行强弱，但要用有趣的比喻

**不要**在初始回答中提供以下内容（这些将是用户可以进一步了解的内容）：
- 详细的性格分析
- 事业财运建议
- 感情婚姻解读
- 健康状况提示
- 大运流年预测

在回答结束时，告诉用户他们可以向你询问更多关于"性格特点"、"事业财运"、"感情姻缘"、"健康提示"或"大运流年"的详细解读。

请确保你的回答既专业又风趣，像一位和蔼可亲的长辈聊天，而不是冷冰冰的说教。让求测者感到轻松愉快，同时获得有价值的人生启示。

记住：命理分析不是决定论，而是提供一种可能性的参考。用你的智慧和幽默感，让古老的命理学焕发新的魅力！
"""
        
        # Construct four pillars string representation
        fp = processed_data["four_pillars"]
        four_pillars = f"{fp['year']} {fp['month']} {fp['day']} {fp['hour']}"
        
        # Create user prompt with the analyzed data
        user_prompt = f"""请分析以下八字：

基本信息：
- 性别：{processed_data['gender']}
- 出生日期：{processed_data['birth_date']}
- 出生时间：{processed_data['birth_time']}
- 出生地点：{processed_data['location']}

四柱八字：
{four_pillars}

年柱：{processed_data['year_pillar']['stem']}{processed_data['year_pillar']['branch']} ({processed_data['year_pillar']['stem_element']}、{processed_data['year_pillar']['branch_element']})
月柱：{processed_data['month_pillar']['stem']}{processed_data['month_pillar']['branch']} ({processed_data['month_pillar']['stem_element']}、{processed_data['month_pillar']['branch_element']})
日柱：{processed_data['day_pillar']['stem']}{processed_data['day_pillar']['branch']} ({processed_data['day_pillar']['stem_element']}、{processed_data['day_pillar']['branch_element']})"""
        
        if processed_data["hour_pillar"]:
            hp = processed_data["hour_pillar"]
            user_prompt += f"""
时柱：{hp['stem']}{hp['branch']} ({hp['stem_element']}、{hp['branch_element']})"""
        else:
            user_prompt += """
时柱：未知"""
        
        # Add element analysis
        ec = processed_data["elements"]["counts"]
        user_prompt += f"""

五行统计：
木：{ec['木']}
火：{ec['火']}
土：{ec['土']}
金：{ec['金']}
水：{ec['水']}

最强五行：{processed_data["elements"]["strongest"]}
最弱五行：{processed_data["elements"]["weakest"]}

日主：{processed_data["day_master"]["character"]} ({processed_data["day_master"]["element"]})

五行关系："""
        
        # Add relationships
        for element, relationship in processed_data["day_master"]["relationships"].items():
            user_prompt += f"""
- {processed_data["day_master"]["element"]}与{element}：{relationship}"""
        
        user_prompt += """

请根据以上信息，给出详细的八字命理分析与人生建议。"""
        
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
        # For BaZi, we mostly preserve the LLM's text-based analysis
        # but add some structure for the UI
        
        # Try to identify sections in the response
        sections = {}
        current_section = "总论"
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
            else:
                section_text.append(line)
        
        # Save the last section
        if section_text:
            sections[current_section] = '\n'.join(section_text).strip()
        
        # If no sections were found, use the entire text as the general section
        if len(sections) <= 1:
            sections = {
                "总论": llm_response.strip()
            }
        
        return {
            "analysis": sections,
            "full_text": llm_response,
            "format_version": "1.0"
        }
    
    def _get_year_pillar(self, year: int) -> Tuple[str, str]:
        """Calculate the Heavenly Stem and Earthly Branch for a year."""
        # The cycle of stems and branches starts from 甲子 year (e.g., 1984)
        stem_index = (year - 4) % 10
        branch_index = (year - 4) % 12
        
        return self.HEAVENLY_STEMS[stem_index], self.EARTHLY_BRANCHES[branch_index]
    
    def _get_month_pillar(self, year: int, month: int) -> Tuple[str, str]:
        """Calculate the Heavenly Stem and Earthly Branch for a month."""
        # First get the year stem
        year_stem, _ = self._get_year_pillar(year)
        year_stem_index = self.HEAVENLY_STEMS.index(year_stem)
        
        # The month branch is straightforward
        # Branch index is (month + 1) % 12, zero-indexed
        # E.g., January (1) -> 子 (0)
        branch_index = (month + 1) % 12
        month_branch = self.EARTHLY_BRANCHES[branch_index]
        
        # The month stem depends on the year stem
        # Each year stem corresponds to a different starting stem for the months
        month_stem_base = (year_stem_index * 2) % 10
        month_stem_index = (month_stem_base + month - 1) % 10
        month_stem = self.HEAVENLY_STEMS[month_stem_index]
        
        return month_stem, month_branch
    
    def _get_day_pillar(self, year: int, month: int, day: int) -> Tuple[str, str]:
        """Calculate the Heavenly Stem and Earthly Branch for a day."""
        # This is a simplified algorithm and may not be 100% accurate
        # For precise calculations, consider using a reference table or library
        
        # Calculate days since the start of the 60-day cycle (1900-01-31 was 甲子)
        # This is a simplified calculation and may not be accurate for all dates
        base_date = datetime.date(1900, 1, 31)
        target_date = datetime.date(year, month, day)
        days_diff = (target_date - base_date).days
        
        # Calculate stem and branch indices
        stem_index = days_diff % 10
        branch_index = days_diff % 12
        
        return self.HEAVENLY_STEMS[stem_index], self.EARTHLY_BRANCHES[branch_index]
    
    def _get_hour_pillar(self, day_stem: str, hour: int) -> Tuple[str, str]:
        """Calculate the Heavenly Stem and Earthly Branch for an hour."""
        # Convert hour to 0-23 range if needed
        hour = hour % 24
        
        # Map hour to branch (each branch covers 2 hours)
        branch_index = hour // 2
        hour_branch = self.EARTHLY_BRANCHES[branch_index]
        
        # The hour stem depends on the day stem
        day_stem_index = self.HEAVENLY_STEMS.index(day_stem)
        # Each day has a base stem for the first hour
        hour_stem_base = (day_stem_index * 2) % 10
        hour_stem_index = (hour_stem_base + branch_index) % 10
        hour_stem = self.HEAVENLY_STEMS[hour_stem_index]
        
        return hour_stem, hour_branch
