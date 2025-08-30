"""
ANSI color codes for terminal styling in the Fortune Teller application.
"""

class Colors:
    """ANSI color codes for terminal styling."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'
    
    # Background colors
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_RED = '\033[41m'
    BG_CYAN = '\033[46m'

# Five elements color mapping
ELEMENT_COLORS = {
    "木": Colors.GREEN,
    "火": Colors.RED,
    "土": Colors.YELLOW,
    "金": Colors.BOLD,
    "水": Colors.BLUE
}
