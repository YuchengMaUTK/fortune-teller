"""
Tarot card fortune telling system implementation.
"""
import random
import logging
import json
import os
from typing import Dict, Any, List, Tuple

from fortune_teller.core import BaseFortuneSystem

# Configure logging
logger = logging.getLogger("TarotFortuneSystem")


class TarotFortuneSystem(BaseFortuneSystem):
    """
    Tarot card fortune telling system.
    Based on traditional tarot card reading with various spreads.
    """
    
    def display_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """
        Display processed tarot data (cards drawn and their positions).
        
        Args:
            processed_data: Processed tarot reading data
        """
        from fortune_teller.ui.colors import Colors
        
        # 获取基本信息
        question = processed_data.get("question", "未知")
        focus_area = processed_data.get("focus_area", "未知")
        name = processed_data.get("name", "匿名")
        spread_info = processed_data.get("spread", {})
        reading = processed_data.get("reading", [])
        
        # 显示标题
        print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 塔罗牌阵信息 ✨{Colors.ENDC}")
        print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
        
        # 显示基本信息
        print(f"{Colors.BOLD}【咨询信息】{Colors.ENDC}")
        print(f"咨询者: {name}")
        print(f"问题: {question}")
        print(f"领域: {focus_area}")
        print()
        
        # 显示牌阵信息
        print(f"{Colors.BOLD}【牌阵】{Colors.ENDC}")
        print(f"名称: {spread_info.get('name', '未知')}")
        print(f"描述: {spread_info.get('description', '未知')}")
        print()
        
            # 显示抽取的牌
        print(f"{Colors.BOLD}【抽取的牌】{Colors.ENDC}")
        for i, card in enumerate(reading, 1):
            position = card.get("position", f"位置 {i}")
            card_name = card.get("card", "未知")
            orientation = card.get("orientation", "正位")
            
            # 查找牌的emoji
            card_emoji = ""
            for card_data in self.cards:
                if card_data["name"] == card_name and "emoji" in card_data:
                    card_emoji = card_data["emoji"]
                    break
                    
            # 使用不同颜色表示正逆位
            orientation_color = Colors.GREEN if orientation == "正位" else Colors.RED
            orientation_emoji = "⬆️ " if orientation == "正位" else "⬇️ "
            
            print(f"{i}. {Colors.YELLOW}{position}{Colors.ENDC}: "
                  f"{Colors.BOLD}{card_name}{Colors.ENDC} {card_emoji} "
                  f"({orientation_color}{orientation} {orientation_emoji}{Colors.ENDC})")
            
            # 显示关键词
            keywords = card.get("keywords", [])
            if keywords:
                print(f"   关键词: {Colors.CYAN}{', '.join(keywords)}{Colors.ENDC}")
        
        print(f"\n{Colors.CYAN}" + "-" * 60 + f"{Colors.ENDC}")
    
    def get_chat_system_prompt(self) -> str:
        """
        Get a system prompt for chat mode specific to Tarot system.
        
        Returns:
            System prompt string for chat mode
        """
        return """你是"霄占"塔罗牌解读大师，一位拥有深厚神秘学知识的塔罗牌专家，有着20年的塔罗牌解读经验。
你熟知78张塔罗牌的每一种含义、象征和诠释，精通各种牌阵的解读方法。
你的风格睿智而神秘，充满着智慧与洞察力，但同时也很亲和，能用生动的语言将复杂的符号象征转化为直观的理解。

现在你正在与求测者进行轻松的聊天互动。你可以谈论:
- 塔罗牌的历史与符号学
- 各种牌面的含义与解读
- 不同牌阵的特点与适用场景
- 如何理解塔罗牌的信息
- 塔罗牌作为自我反思工具的应用

在回答中，你可以使用一些巧妙的比喻和例子，偶尔引用神话或传说，帮助求测者理解深奥的概念。
对话应简洁精炼，回答控制在200字以内，保持优雅而富有启发性的语气。
记住，你提供的不是固定的预言，而是帮助人们探索可能性和深入理解自我的视角。"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the Tarot fortune system.
        
        Args:
            data_dir: Directory containing tarot card data
        """
        super().__init__(
            name="tarot",
            display_name="塔罗牌",
            description="基于传统塔罗牌解读的占卜系统"
        )
        
        # Set the data directory
        if data_dir is None:
            self.data_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "data", "tarot")
            )
        else:
            self.data_dir = os.path.abspath(data_dir)
        
        # Load tarot card data
        self.cards = self._load_cards()
        
        # Define available spreads
        self.spreads = {
            "single": {
                "name": "单牌阅读",
                "description": "抽取一张牌进行简单的阅读",
                "positions": ["当前状况"]
            },
            "three_card": {
                "name": "三牌阵",
                "description": "过去、现在、未来的经典三牌阵",
                "positions": ["过去", "现在", "未来"]
            },
            "celtic_cross": {
                "name": "凯尔特十字",
                "description": "详细分析当前情况和潜在结果的经典阵列",
                "positions": [
                    "当前状况", "挑战", "过去", "未来", 
                    "意识目标", "潜意识影响", "自我认知",
                    "外部影响", "希望与恐惧", "最终结果"
                ]
            },
            "relationship": {
                "name": "关系阵",
                "description": "分析两个人之间关系的牌阵",
                "positions": [
                    "你自己", "对方", "关系基础", 
                    "过去影响", "当前状态", "未来发展"
                ]
            }
        }
        
        logger.info(f"Tarot system initialized with {len(self.cards)} cards")
    
    def get_required_inputs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about required inputs for this fortune system.
        
        Returns:
            Dictionary mapping input field names to their metadata
        """
        # Convert spreads to options format
        spread_options = [
            {"value": key, "label": info["name"], "description": info["description"]}
            for key, info in self.spreads.items()
        ]
        
        return {
            "question": {
                "type": "text",
                "description": "你想要咨询的问题",
                "required": True
            },
            "spread": {
                "type": "select",
                "description": "塔罗牌阵",
                "options": spread_options,
                "required": True
            },
            "focus_area": {
                "type": "select",
                "description": "问题领域",
                "options": ["爱情", "事业", "健康", "财富", "灵性", "一般"],
                "required": True
            },
            "name": {
                "type": "text",
                "description": "你的姓名（可选）",
                "required": False
            }
        }
    
    def validate_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input for tarot reading.
        
        Args:
            user_input: Dictionary containing user input data
            
        Returns:
            Validated and normalized input data
            
        Raises:
            ValueError: If the input data is invalid
        """
        validated = {}
        
        # Validate question
        if "question" not in user_input or not user_input["question"].strip():
            raise ValueError("问题内容是必须的")
        
        validated["question"] = user_input["question"].strip()
        
        # Validate spread
        if "spread" not in user_input:
            raise ValueError("必须选择塔罗牌阵")
        
        if user_input["spread"] not in self.spreads:
            raise ValueError(f"不支持的牌阵: {user_input['spread']}")
        
        validated["spread"] = user_input["spread"]
        
        # Validate focus area
        valid_focus_areas = ["爱情", "事业", "健康", "财富", "灵性", "一般"]
        if "focus_area" not in user_input:
            validated["focus_area"] = "一般"  # Default
        elif user_input["focus_area"] not in valid_focus_areas:
            raise ValueError(f"不支持的问题领域: {user_input['focus_area']}")
        else:
            validated["focus_area"] = user_input["focus_area"]
        
        # Validate name (optional)
        if "name" in user_input and user_input["name"]:
            validated["name"] = user_input["name"].strip()
        else:
            validated["name"] = None
        
        return validated
    
    def process_data(self, validated_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the validated input data according to tarot rules.
        
        Args:
            validated_input: Validated user input
            
        Returns:
            Processed data ready for LLM prompt generation
        """
        question = validated_input["question"]
        spread_key = validated_input["spread"]
        focus_area = validated_input["focus_area"]
        name = validated_input["name"]
        
        # Get the selected spread
        spread = self.spreads[spread_key]
        
        # Draw cards for each position
        drawn_cards = self._draw_cards(len(spread["positions"]))
        
        # Prepare the reading
        reading = []
        for i, position in enumerate(spread["positions"]):
            card = drawn_cards[i]
            reading.append({
                "position": position,
                "card": card["name"],
                "orientation": "正位" if random.random() > 0.33 else "逆位",
                "description": card["description"],
                "keywords": card["keywords"]
            })
        
        # Format the result
        processed_data = {
            "question": question,
            "focus_area": focus_area,
            "name": name,
            "spread": {
                "key": spread_key,
                "name": spread["name"],
                "description": spread["description"]
            },
            "reading": reading
        }
        logger.info(f"Processed data: {json.dumps(processed_data, ensure_ascii=False, indent=2)}")
        
        return processed_data
    
    def generate_llm_prompt(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate prompts for the LLM based on processed tarot data.
        
        Args:
            processed_data: Data processed by the tarot system
            
        Returns:
            Dictionary containing system_prompt and user_prompt for the LLM
        """
        # Create the system prompt
        system_prompt = f"""你是一位经验丰富的塔罗牌解读大师。
请根据提供的塔罗牌阵和牌面，为咨询者提供专业、详细且有洞见的解读。

非常重要：请仔细确认提示中列出的实际抽取的牌，并且只解读这些牌。
- 你的解读必须严格基于用户提示中列出的特定牌，而不是其他任何牌。
- 在开始解读前，请先在心里确认每个位置抽到的牌名和正逆位。
- 确保你提到的每一张牌都是用户实际抽取的牌。
- 不要在解读中引用或暗示任何未在用户提示中明确列出的牌。

你的解读应该：
1. 对每个牌位和对应的牌面进行解释
2. 分析牌面之间的关系和相互影响
3. 结合咨询者的具体问题背景进行针对性解读
4. 提供实用的建议和可能的行动方向
5. 保持中立、平衡的观点，不做绝对的预测

你的解读应该具有启发性和支持性，帮助咨询者获得新的视角，而不是简单地告诉他们该做什么。
请记住，塔罗牌解读提供的是可能性和潜在路径，而非确定性的未来。
"""
        
        # Get the question and spread information
        question = processed_data["question"]
        focus_area = processed_data["focus_area"]
        name = processed_data["name"] or "咨询者"
        spread_info = processed_data["spread"]
        reading = processed_data["reading"]
        
        # Create user prompt with the analyzed data
        user_prompt = f"""请为以下塔罗牌阵提供详细解读：

咨询信息：
- 咨询者：{name}
- 问题：{question}
- 领域：{focus_area}

牌阵：{spread_info['name']} - {spread_info['description']}

抽取的牌：
"""
        
        # Add each card in the reading
        for card in reading:
            user_prompt += f"""
{card['position']}：{card['card']} ({card['orientation']})
- 关键词：{', '.join(card['keywords'])}
- 描述：{card['description']}
"""
        
        user_prompt += f"""
请根据以上塔罗牌阵，结合咨询者的问题"{question}"，给出详细而有洞见的解读。
请先分别解读每个牌位的含义，然后综合分析整体牌阵所揭示的信息和建议。
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
        # For tarot readings, we mostly preserve the LLM's text-based analysis
        # but add some structure for the UI
        
        # Try to identify sections in the response
        sections = {}
        current_section = "整体解读"
        section_text = []
        
        for line in llm_response.split('\n'):
            # Check for various section header patterns
            if line.strip().startswith('##'):
                # Markdown headers
                if section_text:
                    sections[current_section] = '\n'.join(section_text).strip()
                    section_text = []
                current_section = line.strip('#').strip()
            elif line.strip().startswith('#'):
                # Single hash headers
                if section_text:
                    sections[current_section] = '\n'.join(section_text).strip()
                    section_text = []
                current_section = line.strip('#').strip()
            elif line.strip().startswith('【') and '】' in line:
                # Chinese bracket headers - common in responses
                if section_text:
                    sections[current_section] = '\n'.join(section_text).strip()
                    section_text = []
                # Extract the text between 【 and 】
                current_section = line.strip().split('【')[1].split('】')[0].strip()
                section_text.append(line)  # Include the header line in content
            elif line.strip() and '----' in line and len(line.strip()) > 10:
                # Horizontal rule separator often indicates a new section
                if section_text:
                    sections[current_section] = '\n'.join(section_text).strip()
                    section_text = []
                section_text.append(line)  # Include the separator in the new section
            else:
                section_text.append(line)
        
        # Save the last section
        if section_text:
            sections[current_section] = '\n'.join(section_text).strip()
        
        # If no sections were found, use the entire text as the general section
        if len(sections) <= 1:
            sections = {
                "整体解读": llm_response.strip()
            }
        
        # Process special patterns for consistency
        processed_sections = {}
        for title, content in sections.items():
            # Clean up section titles for consistency
            clean_title = title.replace("【", "").replace("】", "").strip()
            
            # For common titles, use standard names
            if "整体" in clean_title or "综合" in clean_title:
                clean_title = "整体解读"
            elif "各牌位" in clean_title or "牌位" in clean_title:
                clean_title = "各牌位详细解读"
                
            processed_sections[clean_title] = content
            
        return {
            "reading": processed_sections,
            "full_text": llm_response,
            "format_version": "1.1"
        }
    
    def _load_cards(self) -> List[Dict[str, Any]]:
        """
        Load tarot card data from the data directory.
        
        Returns:
            List of tarot card data dictionaries
        """
        cards_file = os.path.join(self.data_dir, "cards.json")
        
        # Load data from file
        try:
            with open(cards_file, "r", encoding="utf-8") as f:
                logger.info(f"Successfully loaded tarot cards from {cards_file}")
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tarot card data: {e}")
            # Instead of using a default hardcoded list, raise an error
            # This ensures we rely solely on the JSON data file
            raise ValueError(f"无法加载塔罗牌数据。请确保 {cards_file} 文件存在且格式正确。错误: {e}")
    
    def _draw_cards(self, count: int) -> List[Dict[str, Any]]:
        """
        Draw a specified number of unique cards.
        
        Args:
            count: Number of cards to draw
            
        Returns:
            List of drawn card dictionaries
        """
        # Create a copy of the card list to draw from
        available_cards = self.cards.copy()
        drawn = []
        
        # Ensure we don't try to draw more cards than available
        draw_count = min(count, len(available_cards))
        
        for _ in range(draw_count):
            # Draw a random card
            card = random.choice(available_cards)
            drawn.append(card)
            
            # Remove the card from available cards to prevent duplicates
            available_cards.remove(card)
        
        return drawn
