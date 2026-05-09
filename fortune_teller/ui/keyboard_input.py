"""
Keyboard Input Handler - Arrow key navigation for menus
"""

import sys
import termios
import tty
from typing import List, Optional
from .colors import Colors


class KeyboardMenu:
    """Interactive keyboard menu with arrow key navigation"""
    
    def __init__(self, options: List[str], title: str = "", selected_index: int = 0):
        self.options = options
        self.title = title
        self.selected_index = selected_index
        self.max_index = len(options) - 1
    
    def _get_key(self) -> str:
        """Get a single keypress"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            
            # Handle arrow keys (escape sequences)
            if key == '\x1b':  # ESC sequence
                key += sys.stdin.read(2)
                
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return key
    
    # Lines rendered below the last option: blank line + hint line.
    _LINES_BELOW_OPTIONS = 2

    def _display_menu(self):
        """Render (or update) the menu inline at the cursor's current position.

        First call prints title / options / hint from the current line and
        leaves the cursor below the hint. Subsequent calls move the cursor
        back up to the options block, redraw each option (with \\033[K to
        clear leftover characters), then move back down so the cursor stays
        just past the hint line. This lets the menu coexist with whatever
        was printed above it (e.g. a streamed reading).
        """
        if not hasattr(self, "_menu_displayed"):
            if self.title:
                print(f"{Colors.BOLD}{Colors.YELLOW}{self.title}{Colors.ENDC}")
                print()
            for i, option in enumerate(self.options):
                if i == self.selected_index:
                    print(f"{Colors.BG_BLUE}{Colors.WHITE}► {option}{Colors.ENDC}")
                else:
                    print(f"  {option}")
            print()
            print(f"{Colors.CYAN}Use ↑↓ arrow keys to navigate, Enter to select, 'q' to quit{Colors.ENDC}")
            self._menu_displayed = True
        else:
            lines_up = len(self.options) + self._LINES_BELOW_OPTIONS
            print(f"\033[{lines_up}A", end="")
            for i, option in enumerate(self.options):
                # \r: column 0; \033[K: clear to end of line so wider old text
                # doesn't leave stray characters.
                if i == self.selected_index:
                    print(f"\r{Colors.BG_BLUE}{Colors.WHITE}► {option}{Colors.ENDC}\033[K")
                else:
                    print(f"\r  {option}\033[K")
            print(f"\033[{self._LINES_BELOW_OPTIONS}B", end="")

        sys.stdout.flush()

    def show(self) -> Optional[int]:
        """Show menu and return selected index, None if quit."""
        try:
            while True:
                self._display_menu()
                key = self._get_key()

                if key == "\x1b[A":  # Up arrow
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == "\x1b[B":  # Down arrow
                    self.selected_index = min(self.max_index, self.selected_index + 1)
                elif key in ("\r", "\n"):
                    return self.selected_index
                elif key.lower() == "q":
                    return None
                elif key == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt
        finally:
            # Ensure next output lands on a fresh line, not on top of the menu.
            print()
            sys.stdout.flush()


def pick_from_list(
    options: List[str],
    title: str = "",
    default_index: int = 0,
) -> Optional[int]:
    """Pick an option from a list. Returns chosen index, or None if cancelled.

    Uses arrow-key navigation when stdin is a TTY; falls back to a numbered
    prompt otherwise (so pytest, pipes, and CI work).
    """
    if sys.stdin.isatty():
        try:
            return KeyboardMenu(options, title=title, selected_index=default_index).show()
        except (OSError, termios.error):
            pass  # fall through to numeric prompt

    if title:
        print(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.ENDC}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
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
        print(f"{Colors.RED}无效输入，请重试{Colors.ENDC}")


def select_language() -> Optional[str]:
    """Language selection with arrow keys"""
    from ..i18n import t
    
    options = [
        f"🇺🇸 {t('language_english', 'en')}",
        f"🇨🇳 {t('language_chinese', 'zh')}"
    ]
    
    try:
        menu = KeyboardMenu(
            options=options,
            title=f"{t('language_select', 'en')} / {t('language_select', 'zh')}:",
            selected_index=0
        )
        
        result = menu.show()
        if result is not None:
            return "en" if result == 0 else "zh"
        return None
    except (ImportError, OSError, KeyboardInterrupt):
        # Fallback to simple input if keyboard navigation fails
        print(f"{t('language_select', 'en')} / {t('language_select', 'zh')}:")
        print(f"1. 🇺🇸 {t('language_english', 'en')}")
        print(f"2. 🇨🇳 {t('language_chinese', 'zh')}")
        
        try:
            choice = input("Select (1/2): ").strip()
            return "en" if choice == "1" else "zh" if choice == "2" else None
        except (EOFError, KeyboardInterrupt):
            return None


def select_gender(language: str = "zh") -> Optional[str]:
    """Gender selection with arrow keys"""
    from ..i18n import t
    
    options = [
        f"👨 {t('gender_male', language)}",
        f"👩 {t('gender_female', language)}"
    ]
    
    menu = KeyboardMenu(
        options=options,
        title=t('input_gender', language),
        selected_index=0
    )
    
    try:
        result = menu.show()
        if result is not None:
            return t('gender_male', 'zh') if result == 0 else t('gender_female', 'zh')
        return None
    except KeyboardInterrupt:
        return None


def select_tarot_spread(language: str = "zh") -> Optional[str]:
    """Tarot spread selection with arrow keys"""
    from ..i18n import t
    
    options = [
        f"🃏 {t('tarot_spread_single', language)}",
        f"🔮 {t('tarot_spread_three', language)}",
        f"✨ {t('tarot_spread_celtic', language)}",
        f"💕 {t('tarot_spread_relationship', language)}"
    ]
    
    menu = KeyboardMenu(
        options=options,
        title="请选择塔罗牌阵：" if language == "zh" else "Please select tarot spread:",
        selected_index=0
    )
    
    try:
        result = menu.show()
        if result is not None:
            spread_types = ["single", "three_card", "celtic_cross", "relationship"]
            return spread_types[result]
        return None
    except KeyboardInterrupt:
        return None


def select_fortune_system(language: str = "zh") -> Optional[str]:
    """Fortune system selection with arrow keys"""
    from ..i18n import t
    
    options = [
        f"🀄 {t('system_bazi', language)} - {t('system_bazi_desc', language)}",
        f"🃏 {t('system_tarot', language)} - {t('system_tarot_desc', language)}",
        f"⭐ {t('system_zodiac', language)} - {t('system_zodiac_desc', language)}"
    ]
    
    menu = KeyboardMenu(
        options=options,
        title=f"✨ {t('system_select', language)} ✨",
        selected_index=0
    )
    
    try:
        result = menu.show()
        if result is not None:
            systems = ["bazi", "tarot", "zodiac"]
            return systems[result]
        return None
    except KeyboardInterrupt:
        return None
