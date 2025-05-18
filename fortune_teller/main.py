#!/usr/bin/env python3
"""
霄占 (Fortune Teller) - Main Application

A Python-based multi-system fortune telling application using LLMs.
"""
import os
import sys
import argparse
import logging
import json
import traceback
import time
import datetime
from typing import Dict, Any, List, Optional

# 静默所有第三方库的日志，将它们仅输出到文件
# 这段代码必须在导入任何其他库之前执行
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fortune_teller.log')
    ]
)

# 移除所有已存在的根日志处理器，防止输出到控制台
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
root_logger.addHandler(logging.FileHandler('fortune_teller.log'))

# 特别处理常见的噪音库
for logger_name in ["boto3", "botocore", "urllib3", "s3transfer", 
                   "boto3.resources", "botocore.credentials"]:
    specific_logger = logging.getLogger(logger_name)
    specific_logger.setLevel(logging.ERROR)  # 只显示错误级别日志
    specific_logger.propagate = False  # 不向上传播日志

from fortune_teller.core import BaseFortuneSystem, PluginManager, LLMConnector, ConfigManager
from fortune_teller.ui.colors import Colors
from fortune_teller.ui.display import (
    print_welcome_screen, print_llm_info, print_available_systems,
    get_user_inputs, display_eight_characters,
    print_reading_result, print_reading_result_streaming,
    print_followup_result, display_topic_menu,
    print_followup_result_streaming
)
from fortune_teller.ui.animation import LoadingAnimation

# 应用专用的日志配置
logger = logging.getLogger("FortuneTeller")


class FortuneTeller:
    """Main Fortune Teller application class."""
    
    def __init__(self, config_file: str = None):
        """
        Initialize the Fortune Teller application.
        
        Args:
            config_file: Path to configuration file
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_file)
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager()
        
        # Initialize LLM connector
        llm_config = self.config_manager.get_config("llm")
        self.llm_connector = LLMConnector(llm_config)
        
        # Load plugins
        self.load_plugins()
        
        # Cache for processed data (used for follow-up questions)
        self._last_processed_data = {}
        
        logger.info("Fortune Teller initialized")
    
    def load_plugins(self) -> None:
        """Load and initialize fortune telling plugins."""
        num_loaded = self.plugin_manager.load_all_plugins()
        logger.info(f"Loaded {num_loaded} fortune telling plugins")
    
    def get_available_systems(self) -> List[Dict[str, Any]]:
        """
        Get a list of available fortune telling systems.
        
        Returns:
            List of fortune system information dictionaries
        """
        return self.plugin_manager.get_plugin_info_list()
    
    def perform_reading(
        self, 
        system_name: str, 
        inputs: Dict[str, Any],
        processed_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform a fortune telling reading.
        
        Args:
            system_name: Name of the fortune telling system to use
            inputs: User input data for the fortune system
            processed_data: Optional pre-processed data (to avoid re-processing)
            
        Returns:
            Reading results and metadata
            
        Raises:
            ValueError: If system is not found or inputs are invalid
        """
        # Get the requested fortune system
        fortune_system = self.plugin_manager.get_plugin(system_name)
        if not fortune_system:
            raise ValueError(f"未找到占卜系统: {system_name}")
        
        try:
            # Use provided processed data if available, otherwise process the inputs
            if processed_data is None:
                # Validate inputs
                validated_inputs = fortune_system.validate_input(inputs)
                
                # Process the data
                processed_data = fortune_system.process_data(validated_inputs)
            else:
                # If processed_data is provided, we use that directly
                validated_inputs = inputs
            
            # Save processed data for follow-up questions
            self._last_processed_data = {
                "system_name": system_name,
                "processed_data": processed_data,
                "inputs": validated_inputs
            }
            
            # Generate LLM prompts
            prompts = fortune_system.generate_llm_prompt(processed_data)
            
            # Get LLM response
            llm_response, metadata = self.llm_connector.generate_response(
                prompts["system_prompt"],
                prompts["user_prompt"]
            )
            
            # Format the result
            result = fortune_system.format_result(llm_response)
            
            # Add metadata to the result
            result["metadata"] = {
                "system_name": system_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "llm_metadata": metadata,
                "inputs": {k: str(v) for k, v in inputs.items()}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing reading: {e}")
            raise ValueError(f"解读错误: {str(e)}")
    
    def perform_followup_reading(
        self, 
        topic: str
    ) -> Dict[str, Any]:
        """
        Perform a follow-up reading on a specific topic.
        
        Args:
            topic: The specific topic to ask about (e.g., "性格特点", "事业财运")
            
        Returns:
            Follow-up reading results
            
        Raises:
            ValueError: If there's no previous reading or if the topic is invalid
        """
        if not self._last_processed_data:
            raise ValueError("请先进行主要解读，然后再询问具体方面。")
        
        system_name = self._last_processed_data["system_name"]
        processed_data = self._last_processed_data["processed_data"]
        
        # Get the fortune system
        fortune_system = self.plugin_manager.get_plugin(system_name)
        if not fortune_system:
            raise ValueError(f"未找到占卜系统: {system_name}")
        
        # Define system-specific topics and prompts
        if system_name == "bazi":
            valid_topics = {
                "🧠 性格命格": "请详细分析此八字主人的性格特点、才能倾向和行为模式，使用生动有趣的比喻和例子。",
                "💼 事业财运": "请详细分析此八字主人的事业发展、适合行业和财富机遇，用风趣幽默的方式给出具体建议。", 
                "❤️ 婚姻情感": "请详细分析此八字主人的感情状况、婚姻倾向和桃花运势，以诙谐但不油腻的方式提供见解。",
                "🧘 健康寿元": "请详细分析此八字主人的健康状况、潜在问题和养生建议，用轻松方式点出需要注意的地方。",
                "🔄 流年大运": "请详细分析此八字主人近期和未来的运势变化、关键时间点，神秘而又不失风趣地展望未来。"
            }
        elif system_name == "tarot":
            valid_topics = {
                "🌟 核心启示": "请详细分析此塔罗牌阵的核心信息和主要启示，用深入而通俗的语言揭示关键洞见。",
                "🚶 当前处境": "请详细分析求测者目前所处的状况、面临的环境和心理状态，用生动的比喻帮助理解。", 
                "🧭 阻碍与助力": "请详细分析求测者当前面临的挑战和可利用的资源，提供创造性的思路和实用建议。",
                "🛤️ 潜在路径": "请详细分析求测者可能的发展方向和选择建议，以温和但明确的方式指出各种可能性。",
                "💫 精神成长": "请详细分析求测者的内在成长和个人转变的机会，用启发性的方式鼓励自我探索。"
            }
        elif system_name == "zodiac":
            valid_topics = {
                "🪐 星盘解析": "请详细分析这份星盘的整体特点、行星角度及主要影响，用清晰易懂的方式解释复杂的星象关系。",
                "🌠 宫位能量": "请详细分析星盘中重要宫位的能量分布和影响，特别关注上升、中天、下降和天底宫。", 
                "🔄 当前行运": "请详细分析当前行星运行对求测者的影响，指出关键的行星相位和过境现象。",
                "🌈 元素平衡": "请详细分析星盘中的元素与能量分布，说明火、土、风、水四元素的平衡状态与缺失情况。",
                "✨ 星座年运": "请详细预测未来一年内的星象变化及其对求测者的影响，用鼓舞人心的方式展望未来机遇。"
            }
        else:
            # Default topics for any other system or fallback
            valid_topics = {
                "性格特点": "请详细分析此命盘主人的性格特点、才能倾向和行为模式，使用生动有趣的比喻和例子。",
                "事业财运": "请详细分析此命盘主人的事业发展、适合行业和财富机遇，用风趣幽默的方式给出具体建议。", 
                "感情姻缘": "请详细分析此命盘主人的感情状况、婚姻倾向和桃花运势，以诙谐但不油腻的方式提供见解。",
                "健康提示": "请详细分析此命盘主人的健康状况、潜在问题和养生建议，用轻松方式点出需要注意的地方。",
                "大运流年": "请详细分析此命盘主人近期和未来的运势变化、关键时间点，神秘而又不失风趣地展望未来。"
            }

        # Clean topic name (remove emoji if present)
        clean_topic = topic
        if any(emoji in topic for emoji in ["🧠", "💼", "❤️", "🧘", "🔄", "🌟", "🚶", "🧭", "🛤️", "💫", "🪐", "🌠", "🌈", "✨", "💬"]):
            clean_topic = topic[2:].strip()  # Remove emoji and whitespace
            
        if topic not in valid_topics:
            topics_str = "、".join(list(valid_topics.keys()))
            raise ValueError(f"请选择有效的解读主题: {topics_str}")
            
        try:
            # Create a system prompt for the follow-up based on the system type
            if system_name == "bazi":
                system_prompt = f"""你是"霄占"，一位来自中国的八字命理学大师，已有30年的占卜经验，性格风趣幽默又不失智慧。
你刚刚为求测者提供了基本的八字命理分析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[topic]}

请确保你的回答既专业又风趣，像一位和蔼可亲的长辈聊天，而不是冷冰冰的说教。让求测者感到轻松愉快，同时获得有价值的人生启示。

你的分析应既有专业水准，又富含情趣价值，可以巧妙地引用一些谚语、典故或生活小故事来帮助理解。
"""
            elif system_name == "tarot":
                system_prompt = f"""你是"霄占"，一位精通塔罗牌解读的大师，拥有深厚的神秘学知识和20年的塔罗牌解读经验。
你刚刚为求测者提供了基本的塔罗牌阵解析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[topic]}

你的风格睿智而神秘，充满着智慧与洞察力，但同时也很亲和，能用生动的语言将复杂的符号象征转化为直观的理解。

你的解读应当既有专业深度，又有灵性启发，可以适当引用一些神话、传说或象征学知识来丰富分析。
"""
            elif system_name == "zodiac":
                system_prompt = f"""你是"霄占"，一位精通西方占星学的专家，有着丰富的占星咨询经验。
你刚刚为求测者提供了基本的星盘分析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[topic]}

你的风格既有专业深度，又不乏幽默感，能够用生动的比喻和实例解释复杂的星象。你既尊重占星学的传统知识，
又不会完全决定论，而是强调每个人都有自由意志来选择如何应对星象影响。

你的解读应当平衡、客观，避免过于绝对化的预测。提供实用的建议和观点，帮助咨询者更好地理解自己和当前的能量影响。
"""
            else:
                # Default generic prompt
                system_prompt = f"""你是"霄占"，一位来自中国的命理学大师，已有30年的占卜经验，性格风趣幽默又不失智慧。
你刚刚为求测者提供了基本的命理分析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[topic]}

请确保你的回答既专业又风趣，像一位和蔼可亲的长辈聊天，而不是冷冰冰的说教。让求测者感到轻松愉快，同时获得有价值的人生启示。

你的分析应既有专业水准，又富含情趣价值，可以巧妙地引用一些谚语、典故或生活小故事来帮助理解。
"""
            
            # Create a user prompt with the processed data and topic based on the system type
            if system_name == "bazi":
                user_prompt = f"""基于刚才的八字分析，请详细解读"{clean_topic}"方面的信息。

四柱八字：
{processed_data["four_pillars"]["year"]} {processed_data["four_pillars"]["month"]} {processed_data["four_pillars"]["day"]} {processed_data["four_pillars"]["hour"]}

性别: {processed_data["gender"]}
出生日期: {processed_data["birth_date"]}
出生时间: {processed_data["birth_time"]}

日主: {processed_data["day_master"]["character"]} ({processed_data["day_master"]["element"]})
最强五行: {processed_data["elements"]["strongest"]}
最弱五行: {processed_data["elements"]["weakest"]}

请提供详细而有趣的"{clean_topic}"分析。"""
            elif system_name == "tarot":
                # Reconstruct tarot reading summary from processed data
                card_info = ""
                if "reading" in processed_data:
                    for i, card in enumerate(processed_data["reading"], 1):
                        position = card.get("position", f"位置{i}")
                        card_name = card.get("card", "")
                        orientation = card.get("orientation", "")
                        card_info += f"{position}: {card_name} ({orientation})\n"
                
                user_prompt = f"""基于刚才的塔罗牌阵分析，请详细解读"{clean_topic}"方面的信息。

塔罗牌阵：{processed_data.get("spread", {}).get("name", "未知牌阵")}
问题：{processed_data.get("question", "未知")}
领域：{processed_data.get("focus_area", "未知")}

抽取的牌：
{card_info}

请提供详细而有深度的"{clean_topic}"分析。"""
            elif system_name == "zodiac":
                # Construct zodiac reading summary from processed data
                sign_info = processed_data.get("zodiac_sign", {})
                
                user_prompt = f"""基于刚才的星盘分析，请详细解读"{clean_topic}"方面的信息。

太阳星座：{sign_info.get("name", "未知")} ({sign_info.get("english", "Unknown")})
月亮星座：{processed_data.get("moon_sign", "未知")}
上升星座：{processed_data.get("rising_sign", "未知")}

元素：{sign_info.get("element", "未知")}
品质：{sign_info.get("quality", "未知")}
主宰星：{sign_info.get("ruler", "未知")}

关注领域：{processed_data.get("question_area", "未知")}

请提供详细而有洞见的"{clean_topic}"分析。"""
            else:
                # Generic prompt as fallback
                user_prompt = f"""基于刚才的命理分析，请详细解读"{clean_topic}"方面的信息。
                
请提供详细而有专业的"{clean_topic}"分析。"""
            
            # Get LLM response for the follow-up
            llm_response, metadata = self.llm_connector.generate_response(
                system_prompt,
                user_prompt
            )
            
            # Format the result for the follow-up
            result = {
                "analysis": {
                    topic.replace("🧠 ", "").replace("💼 ", "").replace("❤️ ", "").replace("🧘 ", "").replace("🔄 ", "")
                    .replace("🌟 ", "").replace("🚶 ", "").replace("🧭 ", "").replace("🛤️ ", "").replace("💫 ", "")
                    .replace("🪐 ", "").replace("🌠 ", "").replace("🌈 ", "").replace("✨ ", "").replace("💬 ", "")
                    .strip(): llm_response.strip()
                },
                "full_text": llm_response,
                "format_version": "1.0",
                "metadata": {
                    "system_name": system_name,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "topic": topic
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"错误生成'{topic}'的解读: {e}")
            raise ValueError(f"解读错误: {str(e)}")
    
    def save_reading(self, reading: Dict[str, Any], filename: str = None) -> str:
        """
        Save a reading to a file.
        
        Args:
            reading: Reading data to save
            filename: Filename to save to, or None for automatic name
            
        Returns:
            Path of the saved file
        """
        if not filename:
            # Generate a filename based on the system and timestamp
            system = reading["metadata"]["system_name"]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reading_{system}_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Save the reading
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(reading, f, ensure_ascii=False, indent=2)
        
        return os.path.abspath(filename)


def run_interactive_menu(fortune_teller, args):
    """
    Run the interactive command-line interface.
    
    Args:
        fortune_teller: FortuneTeller instance
        args: Parsed command-line arguments
    """
    try:
        first_run = True  # 添加标志位控制欢迎画面显示
        
        while True:  # Main loop to allow returning to the main menu
            # 仅在首次运行时显示欢迎画面
            if first_run:
                print_welcome_screen()
                first_run = False  # 重置标志位
            else:
                # 显示简化的标题，而不是完整的欢迎画面
                print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 霄占命理系统 ✨{Colors.ENDC}")
                print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}")
        
            
            # Get available systems
            available_systems = fortune_teller.get_available_systems()
            if not available_systems:
                print(f"{Colors.RED}错误: 没有找到可用的占卜系统{Colors.ENDC}")
                return
            
            # Select a system
            system = None
            if args.system:
                # Find the specified system
                for sys in available_systems:
                    if sys["name"] == args.system:
                        system = fortune_teller.plugin_manager.get_plugin(args.system)
                        break
                
                if not system:
                    print(f"错误: 未找到占卜系统 '{args.system}'")
                    print_available_systems(available_systems)
                    return
            else:
                # Let the user choose a system
                print_available_systems(available_systems)
                while True:
                    try:
                        choice = int(input("请选择一个占卜系统 (输入序号): "))
                        if 1 <= choice <= len(available_systems):
                            system_info = available_systems[choice - 1]
                            system = fortune_teller.plugin_manager.get_plugin(system_info["name"])
                            break
                        else:
                            print(f"请输入1到{len(available_systems)}之间的数字")
                    except ValueError:
                        print("请输入有效的数字")
            
            # Get user inputs for the selected system
            inputs = get_user_inputs(system)
            
            # Process the user input to get the processed data
            try:
                validated_inputs = system.validate_input(inputs)
                processed_data = system.process_data(validated_inputs)
                
                # Display the processed data using the system-specific display method
                system.display_processed_data(processed_data)
                
                # Store the processed data in the fortune teller's cache to prevent re-drawing cards
                # This is crucial for tarot readings to ensure consistency between displayed and interpreted cards
                fortune_teller._last_processed_data = {
                    "system_name": system.name,
                    "processed_data": processed_data,
                    "inputs": validated_inputs
                }
                
                # Confirm to proceed
                input(f"\n{Colors.CYAN}按回车键继续生成详细解读...{Colors.ENDC}")
                
            except Exception as e:
                print(f"{Colors.RED}处理数据时出错: {str(e)}{Colors.ENDC}")
                continue  # Return to the main menu instead of exiting
            
            # Generate LLM prompts from the stored processed data
            prompts = system.generate_llm_prompt(processed_data)
            
            # Save the result if output specified
            output_path = None
            if args.output:
                # Create empty result structure to be populated
                empty_result = {
                    "metadata": {
                        "system_name": system.name,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "inputs": {k: str(v) for k, v in inputs.items()}
                    }
                }
                output_path = fortune_teller.save_reading(empty_result, args.output)
            
            # Show loading animation for non-streaming mode
            animation = LoadingAnimation("正在连接大语言模型，解析命理")
            animation.start()

            try:
                # Define handlers for streaming and non-streaming responses
                def handle_streaming(response_generator, start_time):
                    """流式输出处理函数"""
                    nonlocal animation
                    # Stop animation before streaming output begins
                    animation.stop()
                    
                    return print_reading_result_streaming(
                        response_generator, 
                        output_path,
                        start_time=start_time
                    )
                
                def handle_standard(response, metadata):
                    """标准输出处理函数"""
                    nonlocal animation, system
                    # Format the result
                    result = system.format_result(response)
                    
                    # Add metadata to the result
                    result["metadata"] = {
                        "system_name": system.name,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "llm_metadata": metadata,
                        "inputs": {k: str(v) for k, v in inputs.items()}
                    }
                    
                    # Stop the loading animation
                    animation.stop()
                    
                    # Save the result if output specified
                    nonlocal output_path
                    if args.output:
                        output_path = fortune_teller.save_reading(result, args.output)
                    
                    # Display the result using standard method
                    print_reading_result(result, output_path)
                    return response
                
                # Use unified API for response generation
                complete_response = fortune_teller.llm_connector.generate_best_response(
                    prompts["system_prompt"],
                    prompts["user_prompt"],
                    streaming_handler=handle_streaming,
                    non_streaming_handler=handle_standard
                )
                
                # Interactive followup menu
                if not run_followup_menu(fortune_teller):
                    break  # Exit if user doesn't want to return to main menu
                
            except KeyboardInterrupt:
                # Handle user interruption
                animation.stop()
                print(f"\n\n{Colors.RED}已取消解读生成。{Colors.ENDC}")
                continue  # Return to the main menu
                
            except Exception as e:
                animation.stop()
                print(f"{Colors.RED}解读出错: {str(e)}{Colors.ENDC}")
                continue  # Return to the main menu
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}感谢使用霄占命理系统，再见！{Colors.ENDC}")
        return
        
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()


def run_chat_mode(fortune_teller, system_name=None):
    """
    Run an interactive chat mode with the LLM as the fortune teller.
    
    Args:
        fortune_teller: FortuneTeller instance
        system_name: Optional name of the fortune system to use for chat
        
    Returns:
        True if user wants to return to main menu, False to exit
    """
    # Use the appropriate system based on what we're using
    if system_name:
        # Get the specific fortune system
        fortune_system = fortune_teller.plugin_manager.get_plugin(system_name)
        system_display_name = fortune_system.display_name
    elif fortune_teller._last_processed_data:
        # Use the last used system if available
        system_name = fortune_teller._last_processed_data["system_name"]
        fortune_system = fortune_teller.plugin_manager.get_plugin(system_name)
        system_display_name = fortune_system.display_name
    else:
        # Default to generic system
        fortune_system = None
        system_display_name = "命理师"
    
    # Display welcome message
    print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 与霄占{system_display_name}聊天 ✨{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
    print(f"您可以向霄占{system_display_name}询问任何关于命理、运势或生活的问题。")
    print(f"{system_display_name}将以灵活幽默的方式与您交流，分享智慧与见解。")
    print(f"输入 {Colors.GREEN}exit{Colors.ENDC} 或 {Colors.GREEN}退出{Colors.ENDC} 返回主菜单。\n")
    
    # Get system prompt from the fortune system or use default if not available
    if fortune_system:
        system_prompt = fortune_system.get_chat_system_prompt()
    else:
        system_prompt = """你是"霄占"命理大师，一位来自中国的命理学专家，已有30年的占卜经验，性格风趣幽默又不失智慧。
现在你正在与求测者进行轻松的聊天互动。你可以谈论命理学知识、回答关于运势的问题，
也可以聊一些日常话题，但始终保持着命理师的角色和视角。
用生动有趣的语言表达，偶尔引用古诗词或俏皮话，让谈话充满趣味性。
让求测者感觉是在和一位睿智而亲切的老朋友聊天。

对话应简洁精炼，回答控制在200字以内，保持幽默风趣的语气。
"""
    
    user_prompt = "请向用户打招呼，自我介绍，并询问他们想了解什么。"
    
    try:
        # Show loading animation
        animation = LoadingAnimation("霄占命理师正在沉思")
        animation.start()
        
        # Get initial greeting from LLM
        response, _ = fortune_teller.llm_connector.generate_response(system_prompt, user_prompt)
        
        # Stop animation
        animation.stop()
        
        # Display the greeting
        print(f"\n{Colors.GREEN}霄占: {Colors.ENDC}{response.strip()}\n")
        
        # Chat loop
        chat_context = []  # Store recent chat history
        while True:
            # Get user input
            user_input = input(f"{Colors.YELLOW}您: {Colors.ENDC}")
            
            # Check for exit command
            if user_input.lower().strip() in ["exit", "quit", "退出", "q"]:
                print(f"\n{Colors.CYAN}霄占命理师向您挥手告别，欢迎随时回来继续聊天！{Colors.ENDC}")
                return True
            
            if not user_input.strip():
                continue
            
            # Add to chat context
            chat_context.append(f"用户: {user_input}")
            
            # Limit context length
            if len(chat_context) > 5:
                chat_context = chat_context[-5:]
            
            # Create prompt with context
            context_prompt = "\n".join(chat_context)
            chat_prompt = f"""求测者刚刚说: "{user_input}"

基于以前的对话内容（如果有）：
{context_prompt}

请以霄占命理师的身份回应。记得保持幽默风趣，并控制回复在200字以内。"""
            
                
            try:
                # 定义聊天的处理函数
                def handle_chat_streaming(response_generator, start_time, thinking_anim):
                    """聊天流式输出处理函数"""
                    nonlocal animation, chat_context
                    # Stop main animation (the loading one)
                    animation.stop()
                    
                    # 显示流式结果并测量首个块延迟
                    complete_response = ""
                    chunk_count = 0
                    first_chunk_time = None
                    
                    for chunk in response_generator:
                        # 记录首个块时间
                        if chunk_count == 0:
                            # 停止思考动画，它会自动显示霄占: 前缀
                            thinking_anim.stop()
                            
                            first_chunk_time = time.time()
                            latency = first_chunk_time - start_time
                            logger.info(f"聊天首个块延迟: {latency:.3f}秒")
                        
                        # 跳过空块
                        if not chunk or chunk.strip() == "":
                            continue
                            
                        chunk_count += 1
                        
                        # 打印块并刷新
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                        
                        # 添加到完整响应
                        complete_response += chunk
                        
                        # 适当延迟以确保更流畅的阅读体验
                        time.sleep(0.05)  # 从0.01增加到0.05，使输出更平滑
                    
                    # 流式响应后添加换行
                    print("\n")
                    return complete_response
                
                def handle_chat_standard(response, metadata, thinking_anim):
                    """聊天标准输出处理函数"""
                    nonlocal animation
                    # 停止所有动画
                    animation.stop()
                    thinking_anim.stop()
                    
                    # 显示响应 (思考动画停止后会自动显示霄占: 前缀)
                    print(f"{response.strip()}\n")
                    return response
                
                # 在调用前导入并初始化思考动画
                from fortune_teller.ui.thinking_animation import ChatThinkingAnimation
                
                # 先完全停止主动画，确保它不再显示任何内容
                animation.stop()
                
                # 清除现有输出行，确保没有残留动画文本
                sys.stdout.write("\r" + " " * 60 + "\r") 
                sys.stdout.flush()
                
                # 等待一小段时间确保主动画完全停止
                time.sleep(0.1)
                
                # 显示即时反馈（在API调用前）
                thinking_animation = ChatThinkingAnimation(prefix="")
                print(f"\n{Colors.GREEN}霄占: {Colors.ENDC}", end="", flush=True)
                thinking_animation.start()
                
                # 使用统一的API生成响应
                response = fortune_teller.llm_connector.generate_best_response(
                    system_prompt, 
                    chat_prompt,
                    streaming_handler=lambda gen, st: handle_chat_streaming(gen, st, thinking_animation),
                    non_streaming_handler=lambda resp, meta: handle_chat_standard(resp, meta, thinking_animation)
                )
                
                # 将响应添加到聊天上下文
                chat_context.append(f"霄占: {response.strip()}")
                
            except Exception as e:
                animation.stop()
                print(f"\n{Colors.RED}霄占思考过度走神了: {e}{Colors.ENDC}")
                
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}霄占命理师向您挥手告别，欢迎随时回来继续聊天！{Colors.ENDC}")
        return True
    
    return True


def run_followup_menu(fortune_teller):
    """
    Run the interactive follow-up menu.
    
    Args:
        fortune_teller: FortuneTeller instance
        
    Returns:
        True if user wants to return to main menu, False to exit
    """
    while True:
        # Move topic generation inside loop to regenerate each time
        # Determine which system is being used
        if not fortune_teller._last_processed_data:
            # Fallback to generic topics if no previous reading
            valid_topics = ["性格特点", "事业财运", "感情姻缘", "健康提示", "大运流年", "与霄占聊天"]
        else:
            system_name = fortune_teller._last_processed_data["system_name"]
            
            if system_name == "bazi":
                valid_topics = [
                    "🧠 性格命格", "💼 事业财运", "❤️ 婚姻情感", 
                    "🧘 健康寿元", "🔄 流年大运"
                ]
            elif system_name == "tarot":
                valid_topics = [
                    "🌟 核心启示", "🚶 当前处境", "🧭 阻碍与助力", 
                    "🛤️ 潜在路径", "💫 精神成长"
                ]
            elif system_name == "zodiac":
                valid_topics = [
                    "🪐 星盘解析", "🌠 宫位能量", "🔄 当前行运", 
                    "🌈 元素平衡", "✨ 星座年运"
                ]
            else:
                # Fallback to generic topics
                valid_topics = ["性格特点", "事业财运", "感情姻缘", "健康提示", "大运流年"]
                
            # Always add chat option regardless of the system
            valid_topics.append("💬 与霄占聊天")
        
        # Display menu with freshly generated topics list
        display_topic_menu(valid_topics)
        
        try:
            choice = input(f"\n{Colors.BOLD}请选择 (0-{len(valid_topics)}): {Colors.ENDC}")
            if choice.strip() == "0" or choice.strip().lower() == "q":
                print(f"\n{Colors.YELLOW}✨ 解读完成，感谢您使用霄占命理系统! ✨{Colors.ENDC}")
                return True  # Return to main menu
            
            topic_index = int(choice) - 1
            if 0 <= topic_index < len(valid_topics):
                selected_topic = valid_topics[topic_index]
                
                # Special case for chat mode
                if "聊天" in selected_topic or "💬" in selected_topic:
                    return run_chat_mode(fortune_teller)
                
                # Show loading animation for regular topics
                animation = LoadingAnimation(f"正在深入分析「{selected_topic}」")
                animation.start()
                
                try:
                    # This is where we'll replace direct method call with streaming approach
                    # First, create system and user prompts
                    system_name = fortune_teller._last_processed_data["system_name"]
                    processed_data = fortune_teller._last_processed_data["processed_data"]
                    
                    # Get clean topic name (remove emoji if present)
                    clean_topic = selected_topic
                    if any(emoji in selected_topic for emoji in ["🧠", "💼", "❤️", "🧘", "🔄", "🌟", "🚶", "🧭", "🛤️", "💫", "🪐", "🌠", "🌈", "✨", "💬"]):
                        clean_topic = selected_topic[2:].strip()  # Remove emoji and whitespace
                    
                    # Define system-specific topics and prompts
                    if system_name == "bazi":
                        valid_topics = {
                            "🧠 性格命格": "请详细分析此八字主人的性格特点、才能倾向和行为模式，使用生动有趣的比喻和例子。",
                            "💼 事业财运": "请详细分析此八字主人的事业发展、适合行业和财富机遇，用风趣幽默的方式给出具体建议。", 
                            "❤️ 婚姻情感": "请详细分析此八字主人的感情状况、婚姻倾向和桃花运势，以诙谐但不油腻的方式提供见解。",
                            "🧘 健康寿元": "请详细分析此八字主人的健康状况、潜在问题和养生建议，用轻松方式点出需要注意的地方。",
                            "🔄 流年大运": "请详细分析此八字主人近期和未来的运势变化、关键时间点，神秘而又不失风趣地展望未来。"
                        }
                    elif system_name == "tarot":
                        valid_topics = {
                            "🌟 核心启示": "请详细分析此塔罗牌阵的核心信息和主要启示，用深入而通俗的语言揭示关键洞见。",
                            "🚶 当前处境": "请详细分析求测者目前所处的状况、面临的环境和心理状态，用生动的比喻帮助理解。", 
                            "🧭 阻碍与助力": "请详细分析求测者当前面临的挑战和可利用的资源，提供创造性的思路和实用建议。",
                            "🛤️ 潜在路径": "请详细分析求测者可能的发展方向和选择建议，以温和但明确的方式指出各种可能性。",
                            "💫 精神成长": "请详细分析求测者的内在成长和个人转变的机会，用启发性的方式鼓励自我探索。"
                        }
                    elif system_name == "zodiac":
                        valid_topics = {
                            "🪐 星盘解析": "请详细分析这份星盘的整体特点、行星角度及主要影响，用清晰易懂的方式解释复杂的星象关系。",
                            "🌠 宫位能量": "请详细分析星盘中重要宫位的能量分布和影响，特别关注上升、中天、下降和天底宫。", 
                            "🔄 当前行运": "请详细分析当前行星运行对求测者的影响，指出关键的行星相位和过境现象。",
                            "🌈 元素平衡": "请详细分析星盘中的元素与能量分布，说明火、土、风、水四元素的平衡状态与缺失情况。",
                            "✨ 星座年运": "请详细预测未来一年内的星象变化及其对求测者的影响，用鼓舞人心的方式展望未来机遇。"
                        }
                    else:
                        # Default topics for any other system or fallback
                        valid_topics = {
                            "性格特点": "请详细分析此命盘主人的性格特点、才能倾向和行为模式，使用生动有趣的比喻和例子。",
                            "事业财运": "请详细分析此命盘主人的事业发展、适合行业和财富机遇，用风趣幽默的方式给出具体建议。", 
                            "感情姻缘": "请详细分析此命盘主人的感情状况、婚姻倾向和桃花运势，以诙谐但不油腻的方式提供见解。",
                            "健康提示": "请详细分析此命盘主人的健康状况、潜在问题和养生建议，用轻松方式点出需要注意的地方。",
                            "大运流年": "请详细分析此命盘主人近期和未来的运势变化、关键时间点，神秘而又不失风趣地展望未来。"
                        }
                    
                    # Make sure the selected topic is in our topics dictionary to avoid KeyError
                    topic_description = ""
                    try:
                        topic_description = valid_topics.get(selected_topic, "")
                        logger.info(f"找到话题'{selected_topic}'的描述: {topic_description}")
                    except Exception as e:
                        logger.error(f"获取话题描述时出错: {e}", exc_info=True)
                        # Provide a generic description if we can't find one
                        topic_description = f"请详细分析{clean_topic}方面的信息，用清晰易懂的语言提供有见解的解读。"
                        
                    # Create system prompts for different fortune systems
                    if system_name == "bazi":
                        system_prompt = f"""你是"霄占"，一位来自中国的八字命理学大师，已有30年的占卜经验，性格风趣幽默又不失智慧。
你刚刚为求测者提供了基本的八字命理分析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{topic_description}

请确保你的回答既专业又风趣，像一位和蔼可亲的长辈聊天，而不是冷冰冰的说教。让求测者感到轻松愉快，同时获得有价值的人生启示。

你的分析应既有专业水准，又富含情趣价值，可以巧妙地引用一些谚语、典故或生活小故事来帮助理解。
"""
                    elif system_name == "tarot":
                        system_prompt = f"""你是"霄占"，一位精通塔罗牌解读的大师，拥有深厚的神秘学知识和20年的塔罗牌解读经验。
你刚刚为求测者提供了基本的塔罗牌阵解析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[selected_topic]}

你的风格睿智而神秘，充满着智慧与洞察力，但同时也很亲和，能用生动的语言将复杂的符号象征转化为直观的理解。

你的解读应当既有专业深度，又有灵性启发，可以适当引用一些神话、传说或象征学知识来丰富分析。
"""
                    elif system_name == "zodiac":
                        system_prompt = f"""你是"霄占"，一位精通西方占星学的专家，有着丰富的占星咨询经验。
你刚刚为求测者提供了基本的星盘分析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[selected_topic]}

你的风格既有专业深度，又不乏幽默感，能够用生动的比喻和实例解释复杂的星象。你既尊重占星学的传统知识，
又不会完全决定论，而是强调每个人都有自由意志来选择如何应对星象影响。

你的解读应当平衡、客观，避免过于绝对化的预测。提供实用的建议和观点，帮助咨询者更好地理解自己和当前的能量影响。
"""
                    else:
                        # Default generic prompt
                        system_prompt = f"""你是"霄占"，一位来自中国的命理学大师，已有30年的占卜经验，性格风趣幽默又不失智慧。
你刚刚为求测者提供了基本的命理分析。现在，求测者想了解更多关于"{clean_topic}"的详细信息。

请为求测者提供关于"{clean_topic}"的深入详尽的解读。{valid_topics[selected_topic]}

请确保你的回答既专业又风趣，像一位和蔼可亲的长辈聊天，而不是冷冰冰的说教。让求测者感到轻松愉快，同时获得有价值的人生启示。

你的分析应既有专业水准，又富含情趣价值，可以巧妙地引用一些谚语、典故或生活小故事来帮助理解。
"""
                    
                    # Create user prompts based on system type
                    if system_name == "bazi":
                        user_prompt = f"""基于刚才的八字分析，请详细解读"{clean_topic}"方面的信息。

四柱八字：
{processed_data["four_pillars"]["year"]} {processed_data["four_pillars"]["month"]} {processed_data["four_pillars"]["day"]} {processed_data["four_pillars"]["hour"]}

性别: {processed_data["gender"]}
出生日期: {processed_data["birth_date"]}
出生时间: {processed_data["birth_time"]}

日主: {processed_data["day_master"]["character"]} ({processed_data["day_master"]["element"]})
最强五行: {processed_data["elements"]["strongest"]}
最弱五行: {processed_data["elements"]["weakest"]}

请提供详细而有趣的"{clean_topic}"分析。"""
                    elif system_name == "tarot":
                        # Reconstruct tarot reading summary from processed data
                        card_info = ""
                        if "reading" in processed_data:
                            for i, card in enumerate(processed_data["reading"], 1):
                                position = card.get("position", f"位置{i}")
                                card_name = card.get("card", "")
                                orientation = card.get("orientation", "")
                                card_info += f"{position}: {card_name} ({orientation})\n"
                        
                        user_prompt = f"""基于刚才的塔罗牌阵分析，请详细解读"{clean_topic}"方面的信息。

塔罗牌阵：{processed_data.get("spread", {}).get("name", "未知牌阵")}
问题：{processed_data.get("question", "未知")}
领域：{processed_data.get("focus_area", "未知")}

抽取的牌：
{card_info}

请提供详细而有深度的"{clean_topic}"分析。"""
                    elif system_name == "zodiac":
                        # Construct zodiac reading summary from processed data
                        sign_info = processed_data.get("zodiac_sign", {})
                        
                        user_prompt = f"""基于刚才的星盘分析，请详细解读"{clean_topic}"方面的信息。

太阳星座：{sign_info.get("name", "未知")} ({sign_info.get("english", "Unknown")})
月亮星座：{processed_data.get("moon_sign", "未知")}
上升星座：{processed_data.get("rising_sign", "未知")}

元素：{sign_info.get("element", "未知")}
品质：{sign_info.get("quality", "未知")}
主宰星：{sign_info.get("ruler", "未知")}

关注领域：{processed_data.get("question_area", "未知")}

请提供详细而有洞见的"{clean_topic}"分析。"""
                    else:
                        # Generic prompt as fallback
                        user_prompt = f"""基于刚才的命理分析，请详细解读"{clean_topic}"方面的信息。
                        
请提供详细而有专业的"{clean_topic}"分析。"""
                    
                    def handle_followup_streaming(response_generator, start_time, thinking_anim=None):
                        """话题解读流式输出处理函数"""
                        nonlocal animation
                        # 停止主加载动画
                        animation.stop()
                        
                        # 如果有思考动画，停止它
                        if thinking_anim:
                            thinking_anim.stop()
                        
                        # 使用流式输出展示结果
                        return print_followup_result_streaming(
                            selected_topic,
                            response_generator
                        )
                    
                    def handle_followup_standard(response, metadata, thinking_anim=None):
                        """话题解读标准输出处理函数"""
                        nonlocal animation
                        
                        # 停止加载动画
                        animation.stop()
                        
                        # 如果有思考动画，也停止它
                        if thinking_anim:
                            thinking_anim.stop()
                        
                        # 使用标准方式显示结果
                        print_followup_result(selected_topic, response)
                        return response
                    
                    # Import and setup thinking animation
                    from fortune_teller.ui.thinking_animation import ChatThinkingAnimation
                    
                    # 先完全停止主动画，确保它不再显示任何内容
                    animation.stop()
                    
                    # 清除现有输出行，确保没有残留动画文本
                    sys.stdout.write("\r" + " " * 60 + "\r") 
                    sys.stdout.flush()
                    
                    # 等待一小段时间确保主动画完全停止
                    time.sleep(0.1)
                    
                    # 显示即时反馈（在API调用前）
                    thinking_animation = ChatThinkingAnimation(prefix="")
                    print(f"\n{Colors.GREEN}解读中: {Colors.ENDC}", end="", flush=True)
                    thinking_animation.start()
                    
                    # 使用统一的API生成响应
                    response = fortune_teller.llm_connector.generate_best_response(
                        system_prompt, 
                        user_prompt,
                        streaming_handler=lambda gen, st: handle_followup_streaming(gen, st, thinking_animation),
                        non_streaming_handler=lambda resp, meta: handle_followup_standard(resp, meta, thinking_animation)
                    )
                    
                except Exception as e:
                    animation.stop()
                    print(f"\n{Colors.RED}解读出错: {e}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}请输入有效的选项 (0-{len(valid_topics)}){Colors.ENDC}")
        except ValueError:
            print(f"{Colors.YELLOW}请输入有效的数字{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}✨ 已取消深入解读，感谢您使用霄占命理系统! ✨{Colors.ENDC}")
            return True  # Return to main menu
    
    return True


def main():
    """Main entry point for the Fortune Teller application."""
    parser = argparse.ArgumentParser(
        description="霄占 (Fortune Teller) - 基于LLM的多系统算命程序"
    )
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--list", action="store_true", help="列出可用的占卜系统")
    parser.add_argument("--system", help="使用指定的占卜系统")
    parser.add_argument("--output", help="输出结果文件路径")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    
    args = parser.parse_args()
    
    # Configure console logging if verbose mode is enabled
    if args.verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(console_handler)
    
    try:
        # Show initialization message
        print(f"{Colors.CYAN}正在初始化系统...{Colors.ENDC}")
        
        # Initialize the application
        fortune_teller = FortuneTeller(args.config)
        
        # Show LLM information
        llm_config = fortune_teller.config_manager.get_config("llm")
        print_llm_info(llm_config)
        
        if args.list:
            # Just list available systems and exit
            print_available_systems(fortune_teller.get_available_systems())
            return
        
        # Run the interactive menu
        run_interactive_menu(fortune_teller, args)
        
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
