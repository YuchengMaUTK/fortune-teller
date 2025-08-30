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
    
    def _display_menu(self):
        """Display the menu with current selection highlighted"""
        if not hasattr(self, '_menu_displayed'):
            # First time display - clear screen and show full menu
            print('\033[2J\033[H', end='')
            
            if self.title:
                print(f"{Colors.BOLD}{Colors.YELLOW}{self.title}{Colors.ENDC}")
                print()
            
            # Store the starting line for options
            self._options_start_line = 3 if self.title else 1
            
            # Display all options initially
            for i, option in enumerate(self.options):
                if i == self.selected_index:
                    print(f"{Colors.BG_BLUE}{Colors.WHITE}► {option}{Colors.ENDC}")
                else:
                    print(f"  {option}")
            
            print(f"\n{Colors.CYAN}Use ↑↓ arrow keys to navigate, Enter to select, 'q' to quit{Colors.ENDC}")
            self._menu_displayed = True
        else:
            # Update mode - only redraw the options that changed
            for i, option in enumerate(self.options):
                # Move cursor to this option's line
                line_num = self._options_start_line + i
                print(f'\033[{line_num}H', end='')
                
                if i == self.selected_index:
                    print(f"{Colors.BG_BLUE}{Colors.WHITE}► {option}{Colors.ENDC}\033[K")  # \033[K clears to end of line
                else:
                    print(f"  {option}\033[K")
        
        # Flush output for immediate display
        import sys
        sys.stdout.flush()
    
    def show(self) -> Optional[int]:
        """Show menu and return selected index, None if quit"""
        while True:
            self._display_menu()
            
            key = self._get_key()
            
            if key == '\x1b[A':  # Up arrow
                self.selected_index = max(0, self.selected_index - 1)
            elif key == '\x1b[B':  # Down arrow
                self.selected_index = min(self.max_index, self.selected_index + 1)
            elif key == '\r' or key == '\n':  # Enter
                return self.selected_index
            elif key.lower() == 'q':  # Quit
                return None
            elif key == '\x03':  # Ctrl+C
                raise KeyboardInterrupt


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
