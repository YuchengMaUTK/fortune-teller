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

# Five elements color mapping
ELEMENT_COLORS = {
    "木": Colors.GREEN,
    "火": Colors.RED,
    "土": Colors.YELLOW,
    "金": Colors.BOLD,
    "水": Colors.BLUE
}
