"""
Color utilities for terminal output
"""

import sys
import os
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""

    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"


class ColorScheme:
    """Color scheme for different output elements"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and self._supports_color()

    @staticmethod
    def _supports_color() -> bool:
        """Check if the terminal supports color"""
        # Check if output is redirected
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        # Check environment variables
        if os.getenv("NO_COLOR"):
            return False

        if os.getenv("FORCE_COLOR"):
            return True

        # Check TERM variable
        term = os.getenv("TERM", "")
        if term in ("dumb", ""):
            return False

        # Windows support
        if sys.platform == "win32":
            # Enable ANSI support on Windows 10+
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False

        return True

    def _colorize(self, text: str, *codes: str) -> str:
        """Apply color codes to text"""
        if not self.enabled:
            return text
        return "".join(codes) + text + Colors.RESET

    # Header styles
    def header(self, text: str) -> str:
        """Main header style"""
        return self._colorize(text, Colors.BOLD, Colors.BRIGHT_CYAN)

    def subheader(self, text: str) -> str:
        """Subheader style"""
        return self._colorize(text, Colors.BOLD, Colors.BRIGHT_BLUE)

    def section(self, text: str) -> str:
        """Section header style"""
        return self._colorize(text, Colors.BOLD, Colors.CYAN)

    # File/directory styles
    def directory(self, text: str) -> str:
        """Directory name style"""
        return self._colorize(text, Colors.BOLD, Colors.BLUE)

    def file_logged(self, text: str) -> str:
        """Logged file style"""
        return self._colorize(text, Colors.GREEN)

    def file_skipped(self, text: str) -> str:
        """Skipped file style"""
        return self._colorize(text, Colors.DIM, Colors.BRIGHT_BLACK)

    # Status styles
    def success(self, text: str) -> str:
        """Success message style"""
        return self._colorize(text, Colors.BOLD, Colors.GREEN)

    def warning(self, text: str) -> str:
        """Warning message style"""
        return self._colorize(text, Colors.BOLD, Colors.YELLOW)

    def error(self, text: str) -> str:
        """Error message style"""
        return self._colorize(text, Colors.BOLD, Colors.RED)

    def info(self, text: str) -> str:
        """Info message style"""
        return self._colorize(text, Colors.CYAN)

    # Marker styles
    def marker_logged(self, text: str) -> str:
        """Logged marker style"""
        return self._colorize(text, Colors.BOLD, Colors.BRIGHT_GREEN)

    def marker_skipped(self, text: str) -> str:
        """Skipped marker style"""
        return self._colorize(text, Colors.BOLD, Colors.BRIGHT_RED)

    # Code/content styles
    def filepath(self, text: str) -> str:
        """File path style"""
        return self._colorize(text, Colors.BOLD, Colors.MAGENTA)

    def line_number(self, text: str) -> str:
        """Line number style"""
        return self._colorize(text, Colors.DIM, Colors.YELLOW)

    def separator(self, text: str) -> str:
        """Separator line style"""
        return self._colorize(text, Colors.DIM, Colors.BRIGHT_BLACK)

    def code_content(self, text: str) -> str:
        """Code content style - gray/dimmed"""
        return self._colorize(text, Colors.BRIGHT_BLACK)

    # Statistics styles
    def stat_label(self, text: str) -> str:
        """Statistics label style"""
        return self._colorize(text, Colors.BOLD, Colors.WHITE)

    def stat_value(self, text: str) -> str:
        """Statistics value style"""
        return self._colorize(text, Colors.BOLD, Colors.BRIGHT_YELLOW)

    # Legend styles
    def legend(self, text: str) -> str:
        """Legend text style"""
        return self._colorize(text, Colors.ITALIC, Colors.BRIGHT_BLACK)


def get_color_scheme(enabled: Optional[bool] = None) -> ColorScheme:
    """Get a color scheme instance

    Args:
        enabled: Force enable/disable colors. If None, auto-detect.
    """
    if enabled is None:
        return ColorScheme()
    return ColorScheme(enabled=enabled)
