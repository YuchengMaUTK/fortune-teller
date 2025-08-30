"""
星座占星智能体 - 完整实现
"""

from .base_agent import BaseFortuneAgent, FortuneMessage, MessagePriority
from typing import Dict, Any, List
import datetime
import logging

logger = logging.getLogger(__name__)


class ZodiacAgent(BaseFortuneAgent):
    """星座占星专业智能体 - 集成传统占星逻辑"""
    
    def __init__(self, agent_name: str = "zodiac_agent", config: Dict[str, Any] = None):
        super().__init__(agent_name, config)
        self.system_name = "zodiac"
        self.display_name = "星座占星"
        self.description = "西方占星学和十二星座分析"
        
        # 十二星座数据
        self.zodiac_signs = [
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
    
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """验证星座输入"""
        payload = message.payload or {}
        
        # 星座占星需要出生日期
        birth_date = payload.get("birth_date")
        name = payload.get("name", "")
        
        # 如果没有生辰信息，返回需要收集的信息
        if not birth_date:
            return {
                "valid": False,
                "system": "zodiac",
                "need_input": True,
                "missing_fields": {
                    "birth_date": "请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15)"
                },
                "current_data": {
                    "birth_date": birth_date,
                    "name": name
                }
            }
        
        # 验证日期格式
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError as e:
            return {
                "valid": False,
                "system": "zodiac", 
                "error": f"日期格式错误: {e}",
                "need_input": True
            }
        
        return {
            "valid": True,
            "system": "zodiac",
            "birth_date": birth_date,
            "name": name,
            "question": payload.get("question", "请为我分析星座运势")
        }
    
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理星座数据 - 使用MCP工具计算星座"""
        birth_date = validated_input["birth_date"]
        name = validated_input["name"]
        question = validated_input["question"]
        
        # 使用MCP工具计算星座
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
        from mcp.mcp_manager import convert_to_zodiac
        
        zodiac_result = await convert_to_zodiac(
            birth_date.year,
            birth_date.month, 
            birth_date.day
        )
        
        if zodiac_result.get("success", False):
            zodiac_sign = zodiac_result["zodiac_sign"]
            birth_info = zodiac_result["birth_info"]
            element_compatibility = zodiac_result["element_compatibility"]
            age = birth_info.get("age", 0)
        else:
            # 后备计算
            zodiac_sign = self._calculate_zodiac_sign(birth_date)
            today = datetime.date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            birth_info = {"age": age, "days_to_birthday": 0}
            element_compatibility = []
        
        return {
            "system": "zodiac",
            "birth_date": birth_date,
            "name": name,
            "question": question,
            "zodiac_sign": zodiac_sign,
            "age": age,
            "birth_info": birth_info,
            "element_compatibility": element_compatibility,
            "zodiac_data": zodiac_result if zodiac_result.get("success") else None
        }
    
    def _calculate_zodiac_sign(self, birth_date: datetime.date) -> Dict[str, Any]:
        """计算星座"""
        month = birth_date.month
        day = birth_date.day
        
        for sign in self.zodiac_signs:
            start_month, start_day = sign["start_date"]
            end_month, end_day = sign["end_date"]
            
            # 处理跨年的星座（摩羯座）
            if start_month > end_month:
                if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
                    return sign
            else:
                if (month == start_month and day >= start_day) or (month == end_month and day <= end_day) or (start_month < month < end_month):
                    return sign
        
        # 默认返回白羊座
        return self.zodiac_signs[0]
    
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """生成星座解读"""
        
        zodiac_sign = processed_data["zodiac_sign"]
        birth_date = processed_data["birth_date"]
        birth_info = processed_data.get("birth_info", {})
        
        # 构建星座信息 - 让LLM基于准确的星座数据进行深度解读
        zodiac_info = f"""
星座信息：
出生日期：{birth_date}
星座：{zodiac_sign['emoji']} {zodiac_sign['name']} ({zodiac_sign['english']})
元素：{zodiac_sign['element']} ({zodiac_sign.get('element_en', '')})
年龄：{birth_info.get('age', 0)}岁

问题：{processed_data.get('question', '综合运势分析')}
"""
        
        # 使用 LLM 工具生成解读
        llm_tool = await self.get_tool("llm_tool")
        
        # 根据语言选择系统提示词和用户提示词
        if language == "en":
            system_prompt = "You are a professional astrologer with 30 years of experience in Western astrology and zodiac signs. You can provide deep and helpful astrological guidance with warmth and wisdom. IMPORTANT: You must respond ONLY in English, never in Chinese."
            
            prompt = f"""
As a professional astrologer, please provide a detailed zodiac fortune analysis for the user.

User Information:
Name: {processed_data.get('name', 'Dear Friend')}

{zodiac_info}

Please provide a professional astrological analysis including:
1. ⭐ Zodiac Personality Traits
2. 🌟 Current Fortune Analysis  
3. 💫 Fortune in Different Areas (Career, Love, Health, Finance)
4. 🔮 Future Guidance and Suggestions
5. ✨ Lucky Elements and Precautions

Please use a warm, insightful tone and combine the characteristics of the zodiac sign to give constructive advice.

IMPORTANT: Respond ONLY in English. Do not use any Chinese characters.
"""
        else:
            system_prompt = "你是一位经验丰富的占星师，精通西方占星学和十二星座的特点，能够提供深刻而有帮助的星座运势指导。"
            
            prompt = f"""
作为专业的占星师，请为用户提供详细的星座运势分析。

用户信息：
姓名：{processed_data.get('name', '缘主')}

{zodiac_info}

请提供专业的星座分析，包括：
1. ⭐ 星座性格特点
2. 🌟 当前运势分析
3. 💫 各方面运势（事业、爱情、健康、财运）
4. 🔮 未来一段时间的建议
5. ✨ 幸运元素和注意事项

请用温和、富有洞察力的语气，结合星座的特点，给出有建设性的建议。
"""
        
        try:
            reading_text = await llm_tool.generate_response(
                system_prompt=system_prompt,
                user_prompt=prompt,
                language=language,
                stream=True  # 启用流式输出
            )
            
            return {
                "system": "zodiac",
                "reading": reading_text,
                "zodiac_sign": zodiac_sign,
                "birth_date": str(birth_date),
                "question": processed_data["question"],
                "timestamp": self.get_current_time()
            }
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # 后备解读
            fallback_reading = f"""⭐ 星座运势解读

【您的星座】{zodiac_sign['emoji']} {zodiac_sign['name']}

【星座特点】
{zodiac_sign['name']}是{zodiac_sign['element']}象{zodiac_sign['quality']}星座，守护星是{zodiac_sign['ruler']}。

【性格特点】
作为{zodiac_sign['name']}，您具有{zodiac_sign['element']}象星座的特质，性格中带有{zodiac_sign['quality']}的特点。

【运势建议】
根据您的星座特点，建议您发挥{zodiac_sign['element']}象星座的优势，在生活中保持{zodiac_sign['quality']}的态度。

✨ 愿星座的智慧为您指引方向！"""
            
            return {
                "system": "zodiac",
                "reading": fallback_reading,
                "zodiac_sign": zodiac_sign,
                "birth_date": str(birth_date),
                "question": processed_data["question"],
                "timestamp": self.get_current_time()
            }
