"""
国际化智能体 - 多语言支持
"""

from .base_agent import BaseFortuneAgent, FortuneMessage, MessagePriority
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class I18nAgent(BaseFortuneAgent):
    """国际化智能体 - 提供多语言资源管理和动态语言切换"""
    
    def __init__(self, agent_name: str = "i18n_agent", config: Dict[str, Any] = None):
        super().__init__(agent_name, config)
        self.system_name = "i18n"
        self.display_name = "多语言支持"
        self.description = "提供多语言界面和内容本地化"
        
        # 支持的语言
        self.supported_languages = ["zh", "en"]
        self.default_language = "zh"
        
        # 多语言文本资源
        self.texts = {
            "zh": {
                # 系统通用
                "welcome_title": "欢迎使用 霄占 (Fortune Teller) 命理解析系统",
                "welcome_subtitle": "✨ 古今命理，尽在掌握 ✨",
                "session_id": "会话ID",
                "quit_message": "霄占系统已安全关闭。感谢使用！",
                
                # 主菜单
                "available_systems": "✨ 可用的占卜系统 ✨",
                "system_bazi": "八字命理",
                "system_tarot": "塔罗牌", 
                "system_zodiac": "星座占星",
                "desc_bazi": "传统中国八字命理，基于出生年、月、日、时分析命运",
                "desc_tarot": "基于传统塔罗牌解读的占卜系统",
                "desc_zodiac": "基于西方占星学和十二星座的命运分析",
                "menu_instruction": "请选择:\n• 输入数字 (1/2/3) 选择占卜系统\n• 或直接说 \"八字命理\"、\"塔罗牌\"、\"星座占星\"\n• 输入 \"quit\" 退出系统",
                
                # 输入提示
                "select_system": "请选择 (1/2/3): ",
                "birth_date": "出生日期: ",
                "birth_time": "出生时间: ",
                "gender": "性别: ",
                "your_question": "您的问题: ",
                "select_spread": "选择牌阵 (1-4): ",
                
                # 八字系统
                "bazi_selected": "🀄 已选择八字命理系统",
                "bazi_birth_date_prompt": "请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15):",
                "bazi_birth_time_prompt": "请输入您的出生时间 (格式: HH:MM，如 14:30):",
                "bazi_gender_prompt": "请输入您的性别 (男/女):",
                "bazi_result_title": "🔮 八字命理 解读结果",
                "bazi_pillars_info": "📊 四柱八字信息:",
                
                # 塔罗系统
                "tarot_selected": "🃏 已选择塔罗牌系统",
                "tarot_question_prompt": "请输入您想要咨询的问题 (如：我的事业发展如何？):",
                "tarot_spread_menu": """请选择塔罗牌阵：

1. 🃏 单牌阅读 - 抽取一张牌进行简单的阅读
2. 🔮 三牌阵 - 过去、现在、未来的经典三牌阵  
3. ✨ 凯尔特十字 - 详细分析当前情况和潜在结果的经典阵列
4. 💕 关系阵 - 分析两个人之间关系的牌阵

请选择 (1-4):""",
                "tarot_result_title": "🔮 塔罗占卜 解读结果",
                
                # 星座系统
                "zodiac_selected": "⭐ 已选择星座占星系统",
                "zodiac_birth_date_prompt": "请输入您的出生日期 (格式: YYYY-MM-DD，如 1990-01-15):",
                "zodiac_result_title": "🔮 星座占星 解读结果",
                
                # 聊天系统
                "chat_title": "💬 与霄占命理师继续对话",
                "chat_instructions": """• 直接输入问题开始聊天 (如：我的事业运势如何？)
• 输入 1/2/3 选择新的占卜系统
• 输入 'quit' 退出系统""",
                "chat_prompt": "💬 聊天或选择系统: ",
                "chat_continue": "💬 继续聊天: ",
                "fortune_master": "🧙‍♂️ 霄占命理师: ",
                
                # 错误信息
                "date_format_error": "❌ 日期格式不正确",
                "input_error": "❌ 输入格式不正确",
                "processing_error": "❌ 处理错误"
            },
            
            "en": {
                # 系统通用
                "welcome_title": "Welcome to Fortune Teller (霄占) Divination System",
                "welcome_subtitle": "✨ Ancient Wisdom at Your Fingertips ✨",
                "session_id": "Session ID",
                "quit_message": "Fortune Teller system closed safely. Thank you for using!",
                
                # 主菜单
                "available_systems": "✨ Available Fortune Systems ✨",
                "system_bazi": "BaZi Fortune",
                "system_tarot": "Tarot Cards",
                "system_zodiac": "Western Astrology", 
                "desc_bazi": "Traditional Chinese BaZi fortune telling based on birth year, month, day, and time",
                "desc_tarot": "Fortune telling system based on traditional tarot card readings",
                "desc_zodiac": "Fortune analysis based on Western astrology and zodiac signs",
                "menu_instruction": "Please choose:\n• Enter number (1/2/3) to select fortune system\n• Or directly say \"BaZi\", \"Tarot\", \"Astrology\"\n• Enter \"quit\" to exit system",
                
                # 输入提示
                "select_system": "Please select (1/2/3): ",
                "birth_date": "Birth date: ",
                "birth_time": "Birth time: ",
                "gender": "Gender: ",
                "your_question": "Your question: ",
                "select_spread": "Select spread (1-4): ",
                
                # 八字系统
                "bazi_selected": "🀄 BaZi Fortune System Selected",
                "bazi_birth_date_prompt": "Please enter your birth date (Format: YYYY-MM-DD, e.g. 1990-01-15):",
                "bazi_birth_time_prompt": "Please enter your birth time (Format: HH:MM, e.g. 14:30):",
                "bazi_gender_prompt": "Please enter your gender (Male/Female):",
                "bazi_result_title": "🔮 BaZi Fortune Reading Results",
                "bazi_pillars_info": "📊 Four Pillars Information:",
                
                # 塔罗系统
                "tarot_selected": "🃏 Tarot Card System Selected",
                "tarot_question_prompt": "Please enter your question (e.g.: How is my career development?):",
                "tarot_spread_menu": """Please select tarot spread:

1. 🃏 Single Card - Draw one card for simple reading
2. 🔮 Three Card Spread - Classic past, present, future spread
3. ✨ Celtic Cross - Detailed analysis of current situation and potential outcomes
4. 💕 Relationship Spread - Analyze relationship between two people

Please select (1-4):""",
                "tarot_result_title": "🔮 Tarot Reading Results",
                
                # 星座系统
                "zodiac_selected": "⭐ Western Astrology System Selected",
                "zodiac_birth_date_prompt": "Please enter your birth date (Format: YYYY-MM-DD, e.g. 1990-01-15):",
                "zodiac_result_title": "🔮 Astrology Reading Results",
                
                # 聊天系统
                "chat_title": "💬 Continue Conversation with Fortune Master",
                "chat_instructions": """• Enter questions directly to start chatting (e.g.: How is my career fortune?)
• Enter 1/2/3 to select new fortune system
• Enter 'quit' to exit system""",
                "chat_prompt": "💬 Chat or select system: ",
                "chat_continue": "💬 Continue chat: ",
                "fortune_master": "🧙‍♂️ Fortune Master: ",
                
                # 错误信息
                "date_format_error": "❌ Incorrect date format",
                "input_error": "❌ Incorrect input format", 
                "processing_error": "❌ Processing error"
            }
        }
    
    def get_text(self, key: str, language: str = "zh") -> str:
        """获取本地化文本"""
        if language not in self.supported_languages:
            language = self.default_language
        
        return self.texts.get(language, {}).get(key, key)
    
    def get_system_display_name(self, system: str, language: str = "zh") -> str:
        """获取系统显示名称"""
        system_map = {
            "bazi": self.get_text("system_bazi", language),
            "tarot": self.get_text("system_tarot", language), 
            "zodiac": self.get_text("system_zodiac", language)
        }
        return system_map.get(system, system)
    
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """验证国际化输入"""
        payload = message.payload or {}
        
        return {
            "valid": True,
            "system": "i18n"
        }
    
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理国际化数据"""
        return {
            "system": "i18n"
        }
    
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """生成国际化内容"""
        return {
            "system": "i18n",
            "language": language,
            "timestamp": self.get_current_time()
        }
