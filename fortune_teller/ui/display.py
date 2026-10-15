"""CLI screens and input collection built on the shared Rich renderer."""
import datetime
from typing import Any, Dict, List

from rich.table import Table
from rich.text import Text

from .keyboard_input import ask_text, pick_from_list
from .rendering import (display_chart, get_console, heading, markdown, message,
                        stream_markdown, welcome)


def print_welcome_screen():
    welcome()


def print_llm_info(config: Dict[str, Any]):
    names = {"aws_bedrock": "AWS Bedrock", "openai": "OpenAI", "anthropic": "Anthropic",
             "deepseek": "DeepSeek", "mock": "模拟模式"}
    provider = config.get("provider", "未知")
    message(f"模型 · {names.get(provider, provider)} / {config.get('model', '未知')}", "accent")
    if provider == "mock":
        message("离线演示模式 · 输出为模拟解读", "warning")
    else:
        # Configuration alone cannot prove connectivity; the real request does.
        message("模型已配置 · 生成解读时连接服务", "muted")


def print_available_systems(systems: List[Dict[str, Any]]):
    table = Table(title="可用的占卜系统", border_style="border")
    table.add_column("系统", style="title")
    table.add_column("名称")
    table.add_column("简介")
    for system in systems:
        table.add_row(Text(system['name']), Text(system['display_name']), Text(system['description']))
    get_console().print(table)


def display_eight_characters(processed_data):
    display_chart("bazi", processed_data)


def print_reading_result(result: Dict[str, Any], output_path=None):
    heading("命理解读")
    text = result.get("full_text")
    if text is not None:
        markdown(text)
    else:
        for section, content in result.get("reading", result.get("analysis", {})).items():
            heading(section)
            markdown(str(content))
    _completion(text or "", output_path)


def _completion(text, output_path=None):
    if not text.strip():
        message("未收到解读内容，请检查模型连接。", "warning")
    elif text.lstrip().startswith(("Error:", "Error during", "Error generating")):
        message("解读未完成，请检查模型连接。", "error")
    else:
        message("✓ 解读生成完成！", "success")
        if output_path:
            message(f"✓ 结果已保存到: {output_path}", "muted")


def print_reading_result_streaming(result_generator, output_path=None, start_time=None, pending_animation=None):
    text = stream_markdown(result_generator, "✨ 正在生成解读 ✨", pending_animation, start_time)
    _completion(text, output_path)
    return text


def print_followup_result(topic, content):
    heading(f"{topic}详解")
    markdown(content)


def print_followup_result_streaming(topic, result_generator, pending_animation=None):
    return stream_markdown(result_generator, f"{topic}详解", pending_animation)


def display_topic_menu(valid_topics):
    heading("您想深入了解哪个方面？")
    for index, topic in enumerate(valid_topics, 1):
        message(f"{index}. {topic}", "accent")
    message("0. 返回主菜单")


def get_user_inputs(fortune_system):
    inputs = {}
    heading(f"请输入{fortune_system.display_name}所需的信息")
    for name, info in fortune_system.get_required_inputs().items():
        required = info.get("required", False)
        description = info.get("description", name)
        kind = info.get("type", "text")
        if kind == "select" and "options" in info:
            options = info["options"]
            labels = [f"{o['label']} — {o['description']}" if isinstance(o, dict) else str(o) for o in options]
            while True:
                index = pick_from_list(labels, title=description)
                if index is not None:
                    chosen = options[index]
                    value = chosen["value"] if isinstance(chosen, dict) else chosen
                    break
                if not required:
                    value = None
                    break
                message(f"{description} 为必填，请选择一项", "warning")
        else:
            label = description + (" (必填)" if required else " (选填，Enter 跳过)")
            validator = None
            if kind in ("date", "time"):
                fmt = "%Y-%m-%d" if kind == "date" else "%H:%M"
                def validator(raw, fmt=fmt):
                    try:
                        datetime.datetime.strptime(raw, fmt)
                        return True
                    except ValueError:
                        return "请输入有效的日期 (YYYY-MM-DD)" if fmt == "%Y-%m-%d" else "请输入有效的时间 (HH:MM)"
            value = ask_text(label, required=required, validate=validator)
            if value and kind == "date":
                value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            elif value and kind == "time":
                value = datetime.datetime.strptime(value, "%H:%M").time()
        if value or required:
            inputs[name] = value
    return inputs
