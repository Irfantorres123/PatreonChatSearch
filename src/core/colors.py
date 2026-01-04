"""
Terminal color utilities using colorama for cross-platform support.
"""

from colorama import Fore, Back, Style, init
from typing import Optional

# Initialize colorama for Windows support
init(autoreset=True)


class Colors:
    """Color codes and utility methods for terminal output."""

    # Foreground colors
    BLACK = Fore.BLACK
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE

    # Bright colors
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX
    BRIGHT_RED = Fore.LIGHTRED_EX
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX
    BRIGHT_BLUE = Fore.LIGHTBLUE_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_CYAN = Fore.LIGHTCYAN_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX

    # Background colors
    BG_BLACK = Back.BLACK
    BG_RED = Back.RED
    BG_GREEN = Back.GREEN
    BG_YELLOW = Back.YELLOW
    BG_BLUE = Back.BLUE
    BG_MAGENTA = Back.MAGENTA
    BG_CYAN = Back.CYAN
    BG_WHITE = Back.WHITE

    # Styles
    BOLD = Style.BRIGHT
    DIM = Style.DIM
    NORMAL = Style.NORMAL
    RESET = Style.RESET_ALL

    @staticmethod
    def colorize(text: str, color: str, bold: bool = False) -> str:
        """
        Colorize text with the specified color.

        Args:
            text: Text to colorize
            color: Color code
            bold: Whether to make text bold

        Returns:
            Colored text string
        """
        style = Style.BRIGHT if bold else ""
        return f"{style}{color}{text}{Style.RESET_ALL}"

    @staticmethod
    def success(text: str, bold: bool = False) -> str:
        """Green text for success messages."""
        return Colors.colorize(text, Fore.GREEN, bold)

    @staticmethod
    def error(text: str, bold: bool = True) -> str:
        """Red text for error messages."""
        return Colors.colorize(text, Fore.RED, bold)

    @staticmethod
    def warning(text: str, bold: bool = False) -> str:
        """Yellow text for warning messages."""
        return Colors.colorize(text, Fore.YELLOW, bold)

    @staticmethod
    def info(text: str, bold: bool = False) -> str:
        """Cyan text for info messages."""
        return Colors.colorize(text, Fore.CYAN, bold)

    @staticmethod
    def highlight(text: str, bold: bool = True) -> str:
        """Bright yellow text for highlighting."""
        return Colors.colorize(text, Fore.LIGHTYELLOW_EX, bold)

    @staticmethod
    def muted(text: str) -> str:
        """Dimmed text for less important info."""
        return f"{Style.DIM}{text}{Style.RESET_ALL}"

    @staticmethod
    def header(text: str) -> str:
        """Bright cyan bold text for headers."""
        return Colors.colorize(text, Fore.LIGHTCYAN_EX, bold=True)

    @staticmethod
    def command(text: str) -> str:
        """Magenta text for commands."""
        return Colors.colorize(text, Fore.MAGENTA, bold=False)

    @staticmethod
    def value(text: str) -> str:
        """Bright white text for values."""
        return Colors.colorize(text, Fore.LIGHTWHITE_EX, bold=False)

    @staticmethod
    def username(text: str) -> str:
        """Blue text for usernames."""
        return Colors.colorize(text, Fore.LIGHTBLUE_EX, bold=True)

    @staticmethod
    def channel(text: str) -> str:
        """Bright green text for channel names."""
        return Colors.colorize(text, Fore.LIGHTGREEN_EX, bold=True)

    @staticmethod
    def date(text: str) -> str:
        """Dimmed text for dates."""
        return Colors.muted(text)


def print_separator(char: str = "=", length: int = 80, color: Optional[str] = None) -> None:
    """
    Print a colored separator line.

    Args:
        char: Character to use for separator
        length: Length of separator
        color: Color to use (default: cyan)
    """
    separator = char * length
    if color:
        print(Colors.colorize(separator, color))
    else:
        print(Colors.colorize(separator, Fore.CYAN))


def print_header(text: str, char: str = "=", length: int = 80) -> None:
    """
    Print a colored header with separators.

    Args:
        text: Header text
        char: Character for separator
        length: Length of separator
    """
    print_separator(char, length, Fore.CYAN)
    print(Colors.header(text.center(length)))
    print_separator(char, length, Fore.CYAN)
