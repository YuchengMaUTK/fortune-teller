"""
塔罗牌智能体 - 使用MCP工具
"""

from .base_agent import BaseFortuneAgent, FortuneMessage, MessagePriority
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class TarotAgent(BaseFortuneAgent):
    """塔罗牌智能体 - 提供塔罗牌占卜服务"""
    
    def __init__(self, agent_name: str = "tarot_agent", config: Dict[str, Any] = None):
        super().__init__(agent_name, config)
        self.system_name = "tarot"
        self.display_name = "塔罗牌占卜师"
        self.description = "专业塔罗牌占卜，洞察人生奥秘"
    
    async def validate_input(self, message: FortuneMessage) -> Dict[str, Any]:
        """验证塔罗输入"""
        payload = message.payload or {}
        
        # 塔罗牌需要问题
        question = payload.get("question", "").strip()
        if not question:
            return {
                "valid": False,
                "error": "请输入您想要咨询的问题",
                "system": "tarot"
            }
        
        # 其他可选信息
        name = payload.get("name", "缘主")
        focus_area = payload.get("focus_area", "综合运势")
        spread_type = payload.get("spread_type", "three_card")
        
        return {
            "valid": True,
            "system": "tarot",
            "question": question,
            "name": name,
            "focus_area": focus_area,
            "spread_type": spread_type
        }
    
    async def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """处理塔罗数据 - 使用MCP工具抽卡"""
        question = validated_input["question"]
        name = validated_input["name"]
        focus_area = validated_input["focus_area"]
        spread_type = validated_input["spread_type"]
        
        # 定义牌阵配置
        spreads = {
            "single": {
                "name": "单牌阅读",
                "positions": ["当前状况"],
                "card_count": 1
            },
            "three_card": {
                "name": "三牌阵",
                "positions": ["过去", "现在", "未来"],
                "card_count": 3
            },
            "celtic_cross": {
                "name": "凯尔特十字",
                "positions": ["当前状况", "挑战", "远程过去", "近期过去", "可能结果", "近期未来", "你的方法", "外部影响", "希望与恐惧", "最终结果"],
                "card_count": 10
            },
            "relationship": {
                "name": "关系阵",
                "positions": ["你", "对方", "关系", "建议"],
                "card_count": 4
            }
        }
        
        spread_config = spreads.get(spread_type, spreads["single"])
        card_count = spread_config["card_count"]
        
        # 使用MCP管理器抽卡
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
        from mcp.mcp_manager import draw_tarot_cards
        
        draw_result = await draw_tarot_cards(card_count, allow_reversed=True)
        
        if draw_result.get("success", False):
            drawn_cards = draw_result["cards"]
        else:
            # 后备抽卡
            drawn_cards = [
                {"id": 0, "name": "愚者", "english": "The Fool", "emoji": "🃏", 
                 "suit": "Major Arcana", "reversed": False}
            ] * card_count
        
        return {
            "system": "tarot",
            "question": question,
            "name": name,
            "focus_area": focus_area,
            "spread_type": spread_type,
            "spread_config": spread_config,
            "drawn_cards": drawn_cards,
            "draw_timestamp": draw_result.get("timestamp", "")
        }
    
    async def generate_reading(self, processed_data: Dict[str, Any], language: str = "zh") -> Dict[str, Any]:
        """生成塔罗解读"""
        
        question = processed_data["question"]
        drawn_cards = processed_data["drawn_cards"]
        spread_config = processed_data["spread_config"]
        
        # 构建牌面信息
        cards_info = []
        for i, card in enumerate(drawn_cards):
            position = spread_config["positions"][i] if i < len(spread_config["positions"]) else f"位置{i+1}"
            reversed_text = "逆位" if card.get("reversed", False) else "正位"
            
            if language == "en":
                card_name = card.get("english", card.get("name", "Unknown"))
                reversed_text = "Reversed" if card.get("reversed", False) else "Upright"
            else:
                card_name = card.get("name", "未知")
            
            cards_info.append(f"{position}: {card_name} ({reversed_text}) {card.get('emoji', '')}")
        
        cards_text = "\n".join(cards_info)
        
        # 使用 LLM 工具生成解读
        llm_tool = await self.get_tool("llm_tool")
        
        if language == "en":
            system_prompt = "You are a professional tarot reader with 30 years of experience. You can provide deep and insightful tarot readings with warmth and wisdom. IMPORTANT: You must respond ONLY in English, never in Chinese."
            
            prompt = f"""
As a professional tarot reader, please provide a detailed tarot reading for the user.

Question: {question}
Spread: {spread_config['name']}

Cards drawn:
{cards_text}

Please provide a comprehensive tarot reading including:
1. 🃏 Card Analysis - Meaning of each card in its position
2. 🔮 Overall Message - The main theme and guidance
3. 💫 Practical Advice - Actionable insights for the querent
4. ✨ Future Outlook - What to expect moving forward

Please use an insightful, compassionate tone and provide meaningful guidance.

IMPORTANT: Respond ONLY in English. Do not use any Chinese characters.
"""
        else:
            system_prompt = "你是一位经验丰富的塔罗牌占卜师，拥有30年的塔罗解读经验，能够提供深刻而有帮助的塔罗指导。"
            
            prompt = f"""
作为专业的塔罗占卜师，请为用户提供详细的塔罗牌解读。

咨询问题：{question}
牌阵：{spread_config['name']}

抽到的牌：
{cards_text}

请提供专业的塔罗解读，包括：
1. 🃏 牌面分析 - 每张牌在其位置上的含义
2. 🔮 整体信息 - 主要主题和指导
3. 💫 实用建议 - 对求问者的可行性洞察
4. ✨ 未来展望 - 前进方向的预期

请用富有洞察力、充满同情心的语气，提供有意义的指导。
"""
        
        try:
            reading = await llm_tool.generate_response(
                system_prompt=system_prompt,
                user_prompt=prompt,
                language=language,
                stream=True  # 启用流式输出
            )
            
            return {
                "system": "tarot",
                "reading": reading,
                "drawn_cards": drawn_cards,
                "spread_config": spread_config,
                "question": question,
                "timestamp": self.get_current_time()
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # 后备解读
            if language == "en":
                fallback_reading = f"""🃏 Tarot Reading

Question: {question}
Spread: {spread_config['name']}

Cards Drawn:
{cards_text}

The cards reveal important insights about your situation. Each card carries a message that, when combined, provides guidance for your path forward.

✨ Trust in the wisdom of the cards and your own intuition as you navigate your journey."""
            else:
                fallback_reading = f"""🃏 塔罗牌解读

咨询问题：{question}
牌阵：{spread_config['name']}

抽到的牌：
{cards_text}

塔罗牌为您揭示了重要的洞察。每张牌都承载着信息，当它们结合在一起时，为您的前进道路提供指导。

✨ 相信塔罗牌的智慧和您自己的直觉，在人生旅程中前行。"""
            
            return {
                "system": "tarot",
                "reading": fallback_reading,
                "drawn_cards": drawn_cards,
                "spread_config": spread_config,
                "question": question,
                "timestamp": self.get_current_time()
            }
