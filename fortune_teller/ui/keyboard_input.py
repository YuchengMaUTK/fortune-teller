"""Questionary menus with deterministic numbered input for non-TTY sessions."""
import os
import sys
from typing import List, Optional

import questionary
from rich.text import Text

from .rendering import get_console, message

STYLE = questionary.Style([
    ("qmark", "fg:#7dcfff bold"), ("question", "bold"),
    ("answer", "fg:#7dcfff"), ("pointer", "fg:#7dcfff bold"),
    ("highlighted", "fg:#7dcfff bold"), ("instruction", "fg:#9aa5b1"),
])


def _interactive():
    return sys.stdin.isatty() and sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


def pick_from_list(options: List[str], title: str = "", default_index: int = 0) -> Optional[int]:
    if not options:
        return None
    title = Text.from_ansi(title).plain
    options = [Text.from_ansi(str(option)).plain for option in options]
    if _interactive():
        try:
            prompt = questionary.select(
                title or "请选择", choices=[questionary.Choice(label, value=i) for i, label in enumerate(options)],
                default=max(0, min(default_index, len(options) - 1)), style=STYLE,
                instruction="↑↓ 选择 · Enter 确认 · q / Esc 返回", use_shortcuts=False,
                use_jk_keys=False,
            )
            # Bind q explicitly; it must not be captured by type-to-search.
            bindings = prompt.application.key_bindings
            @bindings.add('q', eager=True)
            @bindings.add('escape', eager=True)
            def cancel(event):
                event.app.exit(result=None)
            return prompt.unsafe_ask()
        except (OSError, EOFError):
            pass
    console = get_console()
    if title:
        console.print(Text(title, style="title"))
    for i, option in enumerate(options, 1):
        console.print(Text(f"  {i}. {option}"))
    while True:
        raw = input(f"请选择 (1-{len(options)}, q 退出): ").strip().lower()
        if raw in ("q", "quit", ""):
            return None
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        message("无效输入，请重试", "warning")


def ask_text(title: str, required=False, validate=None) -> str:
    """Use the same validators in Questionary and redirected-input sessions."""
    def check(value):
        if not value.strip():
            return "此字段为必填项" if required else True
        return validate(value) if validate else True
    if _interactive():
        result = questionary.text(Text.from_ansi(title).plain, validate=check, style=STYLE).ask()
        if result is None:
            raise KeyboardInterrupt
        return result
    while True:
        value = input(title + ": ")
        valid = check(value)
        if valid is True:
            return value
        message(str(valid), "warning")


class KeyboardMenu:
    """Retain the public interface for existing callers."""
    def __init__(self, options, title="", selected_index=0):
        self.options, self.title, self.selected_index = options, title, selected_index

    def show(self):
        return pick_from_list(self.options, self.title, self.selected_index)


def select_language() -> Optional[str]:
    index = pick_from_list(["English", "中文"], "Language / 语言")
    return ("en", "zh")[index] if index is not None else None


def select_gender(language="zh"):
    from ..i18n import t
    index = pick_from_list([t("gender_male", language), t("gender_female", language)], t("input_gender", language))
    return ("男", "女")[index] if index is not None else None


def select_tarot_spread(language="zh"):
    from ..i18n import t
    keys = ("single", "three", "celtic", "relationship")
    index = pick_from_list([t("tarot_spread_" + key, language) for key in keys],
                           "请选择塔罗牌阵" if language == "zh" else "Select a tarot spread")
    return ("single", "three_card", "celtic_cross", "relationship")[index] if index is not None else None


def select_fortune_system(language="zh"):
    from ..i18n import t
    modes = ("bazi", "tarot", "zodiac")
    index = pick_from_list([t("system_" + mode, language) for mode in modes], t("system_select", language))
    return modes[index] if index is not None else None
