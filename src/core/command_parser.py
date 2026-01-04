"""
Command parsing utilities.
Separates argument parsing logic from command execution.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SearchOptions:
    """Parsed search command options."""
    keyword: Optional[str] = None
    user: Optional[str] = None
    case_sensitive: bool = False
    search_text: bool = True
    search_usernames: bool = True


class CommandParser:
    """Parses command arguments following Single Responsibility Principle."""

    @staticmethod
    def parse_int_arg(args: List[str], default: int, arg_name: str = "value") -> Tuple[int, Optional[str]]:
        """
        Parse an integer argument.

        Args:
            args: Argument list
            default: Default value if no args provided
            arg_name: Name of argument for error message

        Returns:
            Tuple of (parsed_value, error_message_or_none)
        """
        if not args:
            return default, None

        try:
            value = int(args[0])
            return value, None
        except ValueError:
            return default, f"Invalid {arg_name}: {args[0]}"

    @staticmethod
    def parse_bool_arg(value: str) -> bool:
        """
        Parse a boolean argument.

        Args:
            value: String value to parse

        Returns:
            Boolean value
        """
        return value.lower() in ['true', '1', 'yes', 'on']

    @staticmethod
    def parse_search_args(args: List[str]) -> Tuple[Optional[SearchOptions], Optional[str]]:
        """
        Parse search command arguments.

        Args:
            args: Argument list from search command

        Returns:
            Tuple of (SearchOptions_or_none, error_message_or_none)
        """
        if not args:
            return None, "No search query provided"

        options = SearchOptions()
        i = 0

        while i < len(args):
            arg = args[i]

            if arg == '--user':
                if i + 1 < len(args):
                    options.user = args[i + 1]
                    i += 2
                else:
                    return None, "--user requires a value"

            elif arg == '--case':
                options.case_sensitive = True
                i += 1

            elif arg == '--text-only':
                options.search_usernames = False
                i += 1

            elif arg == '--user-only':
                options.search_text = False
                i += 1

            else:
                # Assume it's the keyword
                if options.keyword is None:
                    options.keyword = arg
                i += 1

        return options, None

    @staticmethod
    def parse_fields_args(args: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse fields command arguments.

        Args:
            args: Argument list

        Returns:
            Tuple of (action, field_name, error_message)
        """
        if not args:
            return None, None, None

        action = args[0].lower()

        if len(args) < 2:
            if action in ['add', 'remove']:
                return None, None, f"Usage: fields <add|remove> <field>"
            return None, None, None

        field = args[1]

        if action not in ['add', 'remove']:
            return None, None, f"Unknown action: {action}. Use 'add' or 'remove'"

        return action, field, None

    @staticmethod
    def parse_set_config_args(args: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse set config command arguments.

        Args:
            args: Argument list

        Returns:
            Tuple of (key, value, error_message)
        """
        if len(args) < 2:
            return None, None, "Usage: set <key> <value>"

        return args[0], args[1], None
