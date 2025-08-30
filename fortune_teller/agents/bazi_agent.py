"""
八字命理智能体 - 完整实现
"""

from .base_agent import BaseFortuneAgent, FortuneMessage, MessagePriority
from typing import Dict, Any, Tuple
import datetime
import logging

logger = logging.getLogger(__name__)


class BaZiAgent(BaseFortuneAgent):
    """八字命理专业智能体 - 集成传统八字计算逻辑"""
    
    # 天干地支常量
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # 五行对应
    STEM_ELEMENTS = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
    }
    
    BRANCH_ELEMENTS = {
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
        "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    
    def __init__(self, agent_name: str = "bazi_agent", config: Dict[str, Any] = None):
        super().__init__(agent_name, config)
        self.system_name = "bazi"
        self.display_name = "八字命理"
        self.description = "传统中国八字命理分析"
    
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """验证八字输入 - 需要收集生辰信息"""
        payload = message.payload or {}
        
        # 检查是否已有完整的生辰信息
        birth_date = payload.get("birth_date")
        birth_time = payload.get("birth_time") 
        gender = payload.get("gender")
        name = payload.get("name", "")
        location = payload.get("location", "中国")
        
        # 如果缺少关键信息，返回需要收集的信息
        if not birth_date or not birth_time:
            return {
                "valid": False,
                "system": "bazi",
                "need_input": True,
                "missing_fields": {
                    "birth_date": "请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15)",
                    "birth_time": "请输入您的出生时间 (格式: HH:MM，如 14:30)",
                    "gender": "请输入您的性别 (男/女)",
                    "location": "请输入您的出生地点 (可选，默认中国)"
                },
                "current_data": {
                    "birth_date": birth_date,
                    "birth_time": birth_time,
                    "gender": gender,
                    "name": name,
                    "location": location
                }
            }
        
        # 验证日期格式
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
            if isinstance(birth_time, str):
                birth_time = datetime.datetime.strptime(birth_time, "%H:%M").time()
        except ValueError as e:
            return {
                "valid": False,
                "system": "bazi", 
                "error": f"日期时间格式错误: {e}",
                "need_input": True
            }
        
        return {
            "valid": True,
            "system": "bazi",
            "birth_date": birth_date,
            "birth_time": birth_time,
            "gender": gender or "未知",
            "name": name,
            "location": location,
            "question": payload.get("question", "请为我分析八字命理")
        }
    
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理八字数据 - 使用MCP工具计算四柱"""
        birth_date = validated_input["birth_date"]
        birth_time = validated_input["birth_time"]
        
        # 如果是字符串，转换为日期对象
        if isinstance(birth_date, str):
            birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
        
        # 解析时间
        hour = 12  # 默认中午
        if birth_time:
            if isinstance(birth_time, str):
                try:
                    time_parts = birth_time.split(":")
                    hour = int(time_parts[0])
                except:
                    hour = 12
            else:
                hour = birth_time.hour
        
        # 使用MCP管理器计算八字
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
        from mcp.mcp_manager import convert_to_bazi
        
        bazi_result = await convert_to_bazi(
            birth_date.year, 
            birth_date.month, 
            birth_date.day, 
            hour
        )
        
        if bazi_result.get("success", False):
            four_pillars = bazi_result["four_pillars"]
            five_elements = bazi_result["five_elements"]
            day_master = bazi_result["day_master"]
        else:
            # 后备计算使用原有方法
            year_stem, year_branch = self._get_year_pillar(birth_date.year)
            month_stem, month_branch = self._get_month_pillar(birth_date.year, birth_date.month)
            day_stem, day_branch = self._get_day_pillar(birth_date.year, birth_date.month, birth_date.day)
            
            if birth_time:
                hour_stem, hour_branch = self._get_hour_pillar(day_stem, hour)
            else:
                hour_stem, hour_branch = "未", "知"
            
            four_pillars = {
                "year": year_stem + year_branch,
                "month": month_stem + month_branch,
                "day": day_stem + day_branch,
                "hour": hour_stem + hour_branch
            }
            
            # 计算五行分布
            elements = []
            for char in [year_stem, year_branch, month_stem, month_branch, 
                        day_stem, day_branch, hour_stem, hour_branch]:
                if char in self.STEM_ELEMENTS:
                    elements.append(self.STEM_ELEMENTS[char])
                elif char in self.BRANCH_ELEMENTS:
                    elements.append(self.BRANCH_ELEMENTS[char])
            
            five_elements = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
            for element in elements:
                if element in five_elements:
                    five_elements[element] += 1
            
            day_master = day_stem
        
        return {
            "system": "bazi",
            "birth_date": birth_date,
            "birth_time": birth_time,
            "four_pillars": four_pillars,
            "five_elements": five_elements,
            "day_master": day_master,
            "bazi_data": bazi_result if bazi_result.get("success") else None
        }
    
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """生成八字解读"""
        
        # 构建详细的八字信息
        four_pillars = processed_data["four_pillars"]
        five_elements = processed_data["five_elements"]
        day_master = processed_data["day_master"]
        
        bazi_info = f"""
八字四柱：{four_pillars['year']} {four_pillars['month']} {four_pillars['day']} {four_pillars['hour']}
日主：{day_master}
五行分布：{five_elements}
"""
        
        # 使用 LLM 工具生成解读
        llm_tool = await self.get_tool("llm_tool")
        
        prompt = f"""
作为专业的八字命理师，请为用户提供详细的八字命理分析。

{bazi_info}

请提供专业的八字分析，包括：
1. 🀄 四柱八字解析
2. 🌟 日主性格特点  
3. 🔄 五行平衡分析
4. 💫 运势建议

请用温和、专业的语气，结合传统命理知识，给出有建设性的建议。
"""
        
        try:
            reading = await llm_tool.generate_response(
                system_prompt="你是一位经验丰富的八字命理师，精通传统命理学，能够根据生辰八字提供专业、准确的命理分析。",
                user_prompt=prompt,
                language=language,
                stream=True  # 启用流式输出
            )
            
            return {
                "system": "bazi",
                "reading": reading,
                "four_pillars": four_pillars,
                "five_elements": five_elements,
                "day_master": day_master,
                "timestamp": self.get_current_time()
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # 后备解读
            fallback_reading = f"""🀄 八字命理分析

【四柱八字】{four_pillars['year']} {four_pillars['month']} {four_pillars['day']} {four_pillars['hour']}

【日主分析】
您的日主为{day_master}，根据传统八字理论，您的命格显示出独特的特质。

【五行分布】
{' '.join([f'{k}:{v}个' for k, v in five_elements.items() if v > 0])}

【运势建议】
五行之间的平衡体现了您性格中的多面性。建议您在日常生活中注重内心平衡，顺应自然规律，必能趋吉避凶。

✨ 愿您前程似锦，好运常伴！"""
            
            return {
                "system": "bazi",
                "reading": fallback_reading,
                "four_pillars": four_pillars,
                "five_elements": five_elements,
                "day_master": day_master,
                "timestamp": self.get_current_time()
            }
