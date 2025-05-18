"""
Display functions for the Fortune Teller command-line application.
"""
import datetime
import sys
import logging
import time
import re
from typing import Dict, Any, List, Generator

from fortune_teller.ui.colors import Colors, ELEMENT_COLORS
from fortune_teller.core import BaseFortuneSystem

def print_welcome_screen():
    """Display a welcome screen with ASCII art and information."""
    # Chinese art title for 霄占
    xiao_zhan_ascii = """
    ██╗  ██╗██╗ █████╗  ██████╗      ███████╗██╗  ██╗ █████╗ ███╗   ██╗
    ╚██╗██╔╝██║██╔══██╗██╔═══██╗     ╚══███╔╝██║  ██║██╔══██╗████╗  ██║
     ╚███╔╝ ██║███████║██║   ██║       ███╔╝ ███████║███████║██╔██╗ ██║
     ██╔██╗ ██║██╔══██║██║   ██║      ███╔╝  ██╔══██║██╔══██║██║╚██╗██║
    ██╔╝ ██╗██║██║  ██║╚██████╔╝     ███████╗██║  ██║██║  ██║██║ ╚████║
    ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝      ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
    """
    
    print(f"{Colors.CYAN}{xiao_zhan_ascii}{Colors.ENDC}")
    
    print(f"{Colors.BOLD}欢迎使用 {Colors.YELLOW}霄占 (Fortune Teller){Colors.ENDC}{Colors.BOLD} 命理解析系统{Colors.ENDC}")
    print(f"{Colors.CYAN}✨ 古今命理，尽在掌握 ✨{Colors.ENDC}")
    print("\n" + "=" * 80 + "\n")


def print_llm_info(config: Dict[str, Any]):
    """
    Print information about the current LLM model.
    
    Args:
        config: LLM configuration dictionary
    """
    provider = config.get("provider", "未知")
    model = config.get("model", "未知")
    
    if provider == "mock":
        provider_name = "模拟模式"
        model_name = "测试模型"
        status = f"{Colors.YELLOW}⚠️ 当前为测试模式，解读结果不具参考价值{Colors.ENDC}"
    elif provider == "aws_bedrock":
        provider_name = "AWS Bedrock"
        model_name = model
        status = f"{Colors.GREEN}✓ 大语言模型已连接，系统准备就绪{Colors.ENDC}"
    elif provider == "openai":
        provider_name = "OpenAI"
        model_name = model
        status = f"{Colors.GREEN}✓ 大语言模型已连接，系统准备就绪{Colors.ENDC}"
    elif provider == "anthropic":
        provider_name = "Anthropic"
        model_name = model
        status = f"{Colors.GREEN}✓ 大语言模型已连接，系统准备就绪{Colors.ENDC}"
    else:
        provider_name = provider
        model_name = model
        status = f"{Colors.YELLOW}? 未知状态{Colors.ENDC}"
    
    print(f"🧠 当前使用的大语言模型: {Colors.GREEN}{provider_name} ({model_name}){Colors.ENDC}")
    print(f"📡 连接状态: {status}")
    print("\n" + "=" * 80)


def print_available_systems(systems: List[Dict[str, Any]]) -> None:
    """
    Print information about available fortune telling systems.
    
    Args:
        systems: List of fortune system information dictionaries
    """
    print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 可用的占卜系统 ✨{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "-" * 60 + f"{Colors.ENDC}")
    
    # 为不同的占卜系统添加独特的图标
    system_icons = {
        "bazi": "🀄",  
        "tarot": "🃏",
        "zodiac": "⭐",
    }
    
    for i, system in enumerate(systems, 1):
        system_name = system['name']
        icon = system_icons.get(system_name, "📜")
        
        print(f"{Colors.GREEN}{i}.{Colors.ENDC} {Colors.BOLD}{icon} {system['display_name']}{Colors.ENDC} ({system_name})")
        print(f"   {Colors.CYAN}描述:{Colors.ENDC} {system['description']}")
        print(f"{Colors.CYAN}" + "-" * 40 + f"{Colors.ENDC}")


def display_eight_characters(processed_data: Dict[str, Any]):
    """
    Display formatted eight characters and five elements info.
    
    Args:
        processed_data: Processed BaZi data dictionary
    """
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
        elements_line += f"{color}{element}{Colors.ENDC}: {count}  "
    print(elements_line)
    
    # 显示最强最弱五行
    print(f"最强五行: {ELEMENT_COLORS.get(strongest, Colors.ENDC)}{strongest}{Colors.ENDC}")
    print(f"最弱五行: {ELEMENT_COLORS.get(weakest, Colors.ENDC)}{weakest}{Colors.ENDC}")
    print()
    
    # 显示日主信息
    print(f"{Colors.BOLD}【日主】{Colors.ENDC}")
    print(f"日主: {ELEMENT_COLORS.get(day_master_element, Colors.ENDC)}{day_master}{Colors.ENDC} ({day_master_element})")
    
    # 显示五行关系
    print(f"{Colors.BOLD}【五行关系】{Colors.ENDC}")
    for element, relationship in relationships.items():
        print(f"{ELEMENT_COLORS.get(day_master_element, Colors.ENDC)}{day_master_element}{Colors.ENDC} 与 {ELEMENT_COLORS.get(element, Colors.ENDC)}{element}{Colors.ENDC}: {relationship}")
    
    print(f"\n{Colors.CYAN}" + "-" * 60 + f"{Colors.ENDC}")


def print_reading_result(result: Dict[str, Any], output_path: str = None):
    """
    Print the fortune reading result to the console.
    
    Args:
        result: Reading results dictionary
        output_path: Path where the result was saved (optional)
    """
    # Show success message
    print(f"\n{Colors.GREEN}✓ 解读生成完成！{Colors.ENDC}\n")
    
    # Show output path if provided
    if output_path:
        print(f"{Colors.GREEN}✓ 结果已保存到:{Colors.ENDC} {output_path}\n")
    
    # Display the result
    print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 命理解读结果 ✨{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
    
    # Print the formatted sections
    reading_sections = result.get("reading", result.get("analysis", {}))
    for section, content in reading_sections.items():
        print(f"{Colors.BOLD}{Colors.GREEN}【 {section} 】{Colors.ENDC}\n")
        print(f"{content}")
        print(f"\n{Colors.CYAN}" + "-" * 40 + f"{Colors.ENDC}\n")

def print_reading_result_streaming(result_generator: Generator[str, None, None], output_path: str = None, start_time: float = None) -> str:
    """
    Print the streaming fortune reading result to the console, displaying content as it arrives.
    
    Args:
        result_generator: Generator yielding text chunks of the fortune reading
        output_path: Path where the result will be saved (optional)
        start_time: Timestamp when the API call was initiated (for latency measurement)
        
    Returns:
        Complete response text (for potential saving or further processing)
    """
    # Setup logger for chunk tracking
    chunk_logger = logging.getLogger("StreamingChunks")
    chunk_logger.setLevel(logging.DEBUG)
    
    # Ensure we have a file handler for the chunk log
    if not chunk_logger.handlers:
        chunk_handler = logging.FileHandler('streaming_chunks.log')
        chunk_formatter = logging.Formatter('%(asctime)s - %(message)s')
        chunk_handler.setFormatter(chunk_formatter)
        chunk_logger.addHandler(chunk_handler)
    
    # Log start of streaming
    chunk_logger.info("=== START OF STREAMING SESSION ===")
    
    # Show preparing message
    print(f"\n{Colors.GREEN}✨ 正在生成解读，请稍候... ✨{Colors.ENDC}\n")
    
    # Display the result header
    print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
    
    # Collect the complete response while printing chunks
    complete_response = ""
    chunk_count = 0
    json_start_pattern = re.compile(r'^\s*\{')
    json_mode_detected = False
    
    # For measuring first chunk latency
    first_chunk_time = None
    
    try:
        for chunk in result_generator:
            # Record time of first non-empty chunk
            if chunk_count == 0 and start_time:
                first_chunk_time = time.time()
                latency = first_chunk_time - start_time
                chunk_logger.info(f"⏱️ 首个块延迟: {latency:.3f}秒")
                print(f"{Colors.CYAN}⏱️ 响应延迟: {latency:.3f}秒{Colors.ENDC}")
            
            chunk_count += 1
            
            # Skip empty chunks
            if not chunk or chunk.strip() == "":
                continue
                
            # Log each chunk with details
            chunk_repr = repr(chunk)
            chunk_logger.info(f"Chunk #{chunk_count} received | Length: {len(chunk)} | Content: {chunk_repr}")
            
            # Try to detect if we're receiving raw JSON and handle it appropriately
            if chunk_count <= 2 and json_start_pattern.match(chunk):
                json_mode_detected = True
                chunk_logger.warning("Detected JSON format in streaming output - will filter")
                # Don't print raw JSON to console
                complete_response += chunk
                continue
                
            # Skip chunks that look like JSON objects/fragments in JSON mode
            if json_mode_detected and (chunk.startswith('{') or chunk.startswith('"type":')):
                chunk_logger.info(f"Skipping JSON fragment: {chunk[:30]}...")
                complete_response += chunk
                continue
            
            # Strip any JSON formatting from text chunks
            clean_chunk = chunk
            
            # Print chunk and force flush to show immediately
            sys.stdout.write(clean_chunk)
            sys.stdout.flush()  # Flush buffer
            
            # Add to complete response
            complete_response += clean_chunk
            
            # Add delay to ensure terminal has time to update and create a smoother reading experience
            # This is especially important for terminals that may buffer output
            time.sleep(0.05)  # Increased from 0.01 for smoother output
            
            # Every few chunks, add a dummy flush/write to force update
            if chunk_count % 5 == 0:
                sys.stdout.write("")  # Write empty string to force update
                sys.stdout.flush()    # Additional flush
    except KeyboardInterrupt:
        # Handle user interruption
        print(f"\n\n{Colors.RED}解读生成已被中断{Colors.ENDC}")
    except Exception as e:
        # Handle errors
        print(f"\n\n{Colors.RED}解读生成出错: {e}{Colors.ENDC}")
    
    # Print footer
    print(f"\n\n{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}")
    
    # Show success message
    print(f"\n{Colors.GREEN}✓ 解读生成完成！{Colors.ENDC}")
    
    # Show output path if provided
    if output_path:
        print(f"{Colors.GREEN}✓ 结果已保存到:{Colors.ENDC} {output_path}")
    
    return complete_response


def print_followup_result(topic: str, content: str):
    """
    Print the followup reading result to the console.
    
    Args:
        topic: The topic of the followup reading
        content: The content of the followup reading
    """
    print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ {topic}详解 ✨{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
    
    print(content)
    print(f"\n{Colors.CYAN}" + "-" * 40 + f"{Colors.ENDC}\n")


def print_followup_result_streaming(topic: str, result_generator: Generator[str, None, None]) -> str:
    """
    Print the streaming followup reading result to the console.
    
    Args:
        topic: The topic of the followup reading
        result_generator: Generator yielding text chunks of the reading
        
    Returns:
        Complete response text
    """
    # Setup logger for chunk tracking
    chunk_logger = logging.getLogger("StreamingChunks")
    chunk_logger.setLevel(logging.DEBUG)
    
    # Ensure we have a file handler for the chunk log
    if not chunk_logger.handlers:
        chunk_handler = logging.FileHandler('streaming_chunks.log')
        chunk_formatter = logging.Formatter('%(asctime)s - %(message)s')
        chunk_handler.setFormatter(chunk_formatter)
        chunk_logger.addHandler(chunk_handler)
    
    # Log start of streaming
    chunk_logger.info(f"=== START OF STREAMING SESSION FOR TOPIC: {topic} ===")
    
    # Display header
    print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ {topic}详解 ✨{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "=" * 60 + f"{Colors.ENDC}\n")
    
    # Collect complete response while printing chunks
    complete_response = ""
    chunk_count = 0
    
    try:
        for chunk in result_generator:
            chunk_count += 1
            
            # Log each chunk with details
            chunk_repr = repr(chunk)
            chunk_logger.info(f"Topic '{topic}' Chunk #{chunk_count} | Length: {len(chunk)} | Content: {chunk_repr}")
            
            # Print chunk without newline and flush to show immediately
            sys.stdout.write(chunk)
            sys.stdout.flush()
            
            # Add to complete response
            complete_response += chunk
            
            # Add delay to ensure terminal has time to update and create a smoother reading experience
            time.sleep(0.05)  # Added delay for smoother output
    except KeyboardInterrupt:
        # Handle user interruption
        print(f"\n\n{Colors.RED}解读生成已被中断{Colors.ENDC}")
    except Exception as e:
        # Handle errors
        print(f"\n\n{Colors.RED}解读生成出错: {e}{Colors.ENDC}")
    
    # Print footer
    print(f"\n\n{Colors.CYAN}" + "-" * 40 + f"{Colors.ENDC}")
    
    return complete_response


def display_topic_menu(valid_topics: List[str]) -> None:
    """
    Display the interactive menu for selecting a topic to analyze further.
    
    Args:
        valid_topics: List of valid topic options
    """
    print(f"\n{Colors.BOLD}您想深入了解哪个方面?{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "-" * 40 + f"{Colors.ENDC}")
    
    # No need to add icons here as they're already in the topic names from the new system-specific topics
    for i, topic in enumerate(valid_topics, 1):
        print(f"{Colors.GREEN}{i}.{Colors.ENDC} {topic}")
    print(f"{Colors.GREEN}0.{Colors.ENDC} 🏠 返回主菜单")
    

def get_user_inputs(fortune_system: BaseFortuneSystem) -> Dict[str, Any]:
    """
    Get user inputs for a fortune system.
    
    Args:
        fortune_system: Fortune system to get inputs for
        
    Returns:
        Dictionary of user inputs
    """
    inputs = {}
    required_inputs = fortune_system.get_required_inputs()
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}✨ 请输入{fortune_system.display_name}所需的信息 ✨{Colors.ENDC}")
    print(f"{Colors.CYAN}" + "-" * 60 + f"{Colors.ENDC}\n")
    
    for name, input_info in required_inputs.items():
        required = input_info.get("required", False)
        description = input_info.get("description", name)
        input_type = input_info.get("type", "text")
        
        # Format the prompt
        prompt = f"{description}"
        if required:
            prompt += " (必填)"
        else:
            prompt += " (选填，按Enter跳过)"
        prompt += ": "
        
        # Get the input based on type
        if input_type == "select" and "options" in input_info:
            # For select type, show options
            print(f"\n{description}:")
            options = input_info["options"]
            for i, option in enumerate(options, 1):
                if isinstance(option, dict):
                    print(f"{i}. {option['label']} - {option['description']}")
                else:
                    print(f"{i}. {option}")
            
            while True:
                value = input(f"请选择一个选项 (1-{len(options)}): ")
                if not value and not required:
                    break
                
                try:
                    index = int(value) - 1
                    if 0 <= index < len(options):
                        if isinstance(options[index], dict):
                            value = options[index]["value"]
                        else:
                            value = options[index]
                        break
                    else:
                        print(f"请输入1到{len(options)}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
        elif input_type == "date":
            # Date input
            while True:
                value = input(prompt)
                if not value and not required:
                    break
                
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("请输入有效的日期格式 (YYYY-MM-DD)")
        
        elif input_type == "time":
            # Time input
            while True:
                value = input(prompt)
                if not value and not required:
                    break
                
                try:
                    value = datetime.datetime.strptime(value, "%H:%M").time()
                    break
                except ValueError:
                    print("请输入有效的时间格式 (HH:MM)")
        
        else:
            # Default text input
            value = input(prompt)
            if not value and required:
                while not value:
                    print("此字段为必填项，请输入有效值")
                    value = input(prompt)
        
        if value or required:
            inputs[name] = value
    
    return inputs
