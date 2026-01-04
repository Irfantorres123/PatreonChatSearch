"""
Interactive CLI for browsing and searching Patreon channels.
Provides a command-line interface with rich features for exploring channel messages.
"""

from typing import Dict, Any, List, Optional, Literal, Set
from dataclasses import dataclass, field
import shlex
from datetime import datetime

from .search import MessageSearcher, SearchResult
from .pagination import ChannelPaginator, MultiChannelPaginator
from .logger import get_logger
from .colors import Colors, print_separator, print_header

logger = get_logger()


@dataclass
class DisplayConfig:
    """Configuration for displaying search results and messages."""
    show_user_id: bool = False
    show_channel_id: bool = False
    show_message_id: bool = False
    show_date: bool = True
    show_full_text: bool = False
    max_text_length: int = 200
    results_per_page: int = 10
    date_format: str = "%b %d, %Y at %I:%M %p"

    # Field visibility
    visible_fields: Set[str] = field(default_factory=lambda: {
        'user_name', 'channel_name', 'text', 'date'
    })

    def __str__(self) -> str:
        """Return formatted configuration display."""
        from colorama import Fore
        separator = Colors.colorize("=" * 80, Fore.CYAN)

        lines = []
        lines.append(separator)
        lines.append(f"{Colors.header('DISPLAY CONFIGURATION')}")
        lines.append(separator)
        lines.append(f"{Colors.info('show_user_id:')}       {Colors.value(str(self.show_user_id))}")
        lines.append(f"{Colors.info('show_channel_id:')}    {Colors.value(str(self.show_channel_id))}")
        lines.append(f"{Colors.info('show_message_id:')}    {Colors.value(str(self.show_message_id))}")
        lines.append(f"{Colors.info('show_date:')}          {Colors.value(str(self.show_date))}")
        lines.append(f"{Colors.info('show_full_text:')}     {Colors.value(str(self.show_full_text))}")
        lines.append(f"{Colors.info('max_text_length:')}    {Colors.value(str(self.max_text_length))}")
        lines.append(f"{Colors.info('results_per_page:')}   {Colors.value(str(self.results_per_page))}")
        lines.append(f"{Colors.info('visible_fields:')}     {Colors.value(', '.join(sorted(self.visible_fields)))}")
        lines.append(separator)
        lines.append("")
        lines.append(f"{Colors.muted('Use')} {Colors.command('set <key> <value>')} {Colors.muted('to change settings')}")
        return '\n'.join(lines)


class InteractiveCLI:
    """Interactive command-line interface for browsing channels and messages."""

    def __init__(self, channels_data: Dict[str, Any], client: Any) -> None:
        """
        Initialize the interactive CLI.

        Args:
            channels_data: Initial channel data from API
            client: StreamChatClient instance for fetching more data
        """
        logger.info("Initializing InteractiveCLI")
        logger.debug(f"Channels data has {len(channels_data.get('channels', []))} channels")

        self.channels_data: Dict[str, Any] = channels_data
        self.client: Any = client
        self.searcher: MessageSearcher = MessageSearcher(channels_data)
        self.multi_paginator: MultiChannelPaginator = MultiChannelPaginator(client)

        self.current_channel: Optional[Dict[str, Any]] = None
        self.current_channel_index: int = 0
        self.last_search_results: List[SearchResult] = []
        self.current_page: int = 1

        self.display_config: DisplayConfig = DisplayConfig()

        logger.info("InteractiveCLI initialized successfully")

        # Command registry
        self.commands: Dict[str, tuple] = {
            'help': (self.cmd_help, 'Show available commands'),
            'list': (self.cmd_list_channels, 'List all channels'),
            'select': (self.cmd_select_channel, 'Select a channel by index or name'),
            'show': (self.cmd_show_channel, 'Show current channel details'),
            'messages': (self.cmd_show_messages, 'Show messages from current channel'),
            'search': (self.cmd_search, 'Search messages'),
            'next': (self.cmd_next_page, 'Go to next page of results'),
            'prev': (self.cmd_prev_page, 'Go to previous page of results'),
            'page': (self.cmd_goto_page, 'Go to specific page number'),
            'fetch': (self.cmd_fetch_more, 'Fetch more messages from current channel'),
            'config': (self.cmd_show_config, 'Show display configuration'),
            'set': (self.cmd_set_config, 'Set display configuration'),
            'fields': (self.cmd_show_fields, 'Show available fields'),
            'clear': (self.cmd_clear_screen, 'Clear screen'),
            'stats': (self.cmd_show_stats, 'Show statistics'),
            'quit': (self.cmd_quit, 'Exit the CLI'),
            'exit': (self.cmd_quit, 'Exit the CLI'),
        }

        self.running: bool = True

    def run(self) -> None:
        """Start the interactive CLI loop."""
        self.print_welcome()

        while self.running:
            try:
                command_line = input("\n> ").strip()
                if not command_line:
                    continue

                self.execute_command(command_line)

            except KeyboardInterrupt:
                print(f"\n\n{Colors.info('Use')} {Colors.command('quit')} {Colors.info('or')} {Colors.command('exit')} {Colors.info('to exit the CLI.')}")
            except EOFError:
                break
            except Exception as e:
                print(Colors.error(f"Error: {e}"))

    def execute_command(self, command_line: str) -> None:
        """Parse and execute a command."""
        logger.debug(f"Executing command: {command_line}")

        try:
            parts = shlex.split(command_line)
        except ValueError as e:
            logger.error(f"Invalid command syntax: {e}")
            print(Colors.error(f"Invalid command syntax: {e}"))
            return

        if not parts:
            return

        cmd_name = parts[0].lower()
        args = parts[1:]

        logger.info(f"Command: {cmd_name}, Args: {args}")

        if cmd_name in self.commands:
            handler, _ = self.commands[cmd_name]
            try:
                handler(args)
                logger.debug(f"Command '{cmd_name}' executed successfully")
            except Exception as e:
                logger.exception(f"Error executing command '{cmd_name}': {e}")
                print(Colors.error(f"Error executing command: {e}"))
        else:
            logger.warning(f"Unknown command: {cmd_name}")
            print(Colors.error(f"Unknown command: {cmd_name}"))
            print(f"{Colors.info('Type')} {Colors.command('help')} {Colors.info('for available commands.')}")

    # ========== Command Handlers ==========

    def cmd_help(self, args: List[str]) -> None:
        """Show help information."""
        print()
        print_header("AVAILABLE COMMANDS")

        categories = {
            'Navigation': ['list', 'select', 'show', 'next', 'prev', 'page'],
            'Viewing': ['messages', 'stats', 'fields'],
            'Search': ['search'],
            'Data': ['fetch'],
            'Configuration': ['config', 'set'],
            'System': ['help', 'clear', 'quit', 'exit']
        }

        for category, cmds in categories.items():
            print(f"\n{Colors.header(category)}:")
            for cmd in cmds:
                if cmd in self.commands:
                    _, desc = self.commands[cmd]
                    print(f"  {Colors.command(cmd):25} - {desc}")

        print()
        print_separator()
        print(Colors.header("EXAMPLES:"))
        examples = [
            ("list", "Show all channels"),
            ("select 1", "Select first channel"),
            ('select "Easy Investing"', "Select channel by name"),
            ("messages 20", "Show 20 messages"),
            ('search "NVIDIA"', "Search for keyword"),
            ("search --user Chris", "Search by username"),
            ('search --case "VRT"', "Case-sensitive search"),
            ("fetch 100", "Fetch 100 more messages"),
            ("set show_full_text true", "Show full message text"),
            ("set results_per_page 20", "Show 20 results per page"),
            ("fields add message_id", "Show message IDs"),
            ("fields remove date", "Hide dates"),
        ]
        for cmd, desc in examples:
            print(f"  {Colors.command(cmd):35} - {Colors.muted(desc)}")
        print_separator()

    def cmd_list_channels(self, args: List[str]) -> None:
        """List all available channels."""
        channels = self.channels_data.get('channels', [])

        print()
        print(f"{Colors.header('#'):<5} {Colors.header('Channel Name'):<50} {Colors.header('Type'):<35} {Colors.header('Members'):<10}")
        print_separator("-")

        for idx, channel_wrapper in enumerate(channels, 1):
            channel = channel_wrapper.get('channel', {})
            name = channel.get('name', 'Unknown')
            ch_type = channel.get('type', 'unknown')
            member_count = channel.get('member_count', 'N/A')

            # Truncate long names
            if len(name) > 37:
                name = name[:34] + "..."

            idx_str = Colors.value(str(idx))
            name_str = Colors.channel(name)
            type_str = Colors.muted(ch_type)
            members_str = Colors.info(str(member_count))

            print(f"{idx_str:<14} {name_str:<50} {type_str:<45} {members_str:<20}")

        print(f"\n{Colors.success('Total channels:')} {Colors.value(str(len(channels)))}")

    def cmd_select_channel(self, args: List[str]) -> None:
        """Select a channel by index or name."""
        logger.info(f"cmd_select_channel called with args: {args}")

        if not args:
            print(f"{Colors.warning('Usage:')} {Colors.command('select <index|name>')}")
            return

        channels = self.channels_data.get('channels', [])
        logger.debug(f"Total channels available: {len(channels)}")

        # Try to parse as index
        try:
            index = int(args[0])
            logger.debug(f"Attempting to select channel by index: {index}")

            if 1 <= index <= len(channels):
                self.current_channel_index = index - 1
                self.current_channel = channels[self.current_channel_index].get('channel', {})
                self.current_page = 1

                # Clear last search results when changing channels
                self.last_search_results = []

                channel_name = self.current_channel.get('name', 'Unknown')
                channel_cid = self.current_channel.get('cid', 'N/A')
                messages_count = len(channels[self.current_channel_index].get('messages', []))

                logger.info(f"Selected channel: {channel_name} (CID: {channel_cid}), {messages_count} messages loaded")

                print(f"\n{Colors.success('[OK] Selected channel:')} {Colors.channel(channel_name)}")
                self.cmd_show_channel([])
            else:
                logger.warning(f"Invalid channel index: {index}, must be between 1 and {len(channels)}")
                print(Colors.error(f"[X] Invalid index. Must be between 1 and {len(channels)}"))
        except ValueError:
            # Search by name
            search_name = ' '.join(args).lower()
            logger.debug(f"Searching for channel by name: {search_name}")

            for idx, channel_wrapper in enumerate(channels):
                channel = channel_wrapper.get('channel', {})
                if search_name in channel.get('name', '').lower():
                    self.current_channel_index = idx
                    self.current_channel = channel
                    self.current_page = 1
                    self.last_search_results = []

                    channel_name = channel.get('name', 'Unknown')
                    logger.info(f"Found and selected channel: {channel_name} at index {idx}")

                    print(f"\n{Colors.success('[OK] Selected channel:')} {Colors.channel(channel_name)}")
                    self.cmd_show_channel([])
                    return

            logger.warning(f"No channel found matching: {search_name}")
            print(Colors.error(f"[X] No channel found matching: {' '.join(args)}"))

    def cmd_show_channel(self, args: List[str]) -> None:
        """Show details of the current channel."""
        if not self.current_channel:
            print(Colors.warning("[!] No channel selected. Use 'select <index>' first."))
            return

        ch = self.current_channel
        print()
        print_separator()
        print(Colors.header(f"Channel: {ch.get('name', 'Unknown')}"))
        print_separator()
        print(f"{Colors.info('Type:')}          {Colors.value(ch.get('type', 'N/A'))}")
        print(f"{Colors.info('ID:')}            {Colors.muted(ch.get('id', 'N/A'))}")
        print(f"{Colors.info('CID:')}           {Colors.muted(ch.get('cid', 'N/A'))}")
        print(f"{Colors.info('Members:')}       {Colors.highlight(str(ch.get('member_count', 'N/A')))}")
        print(f"{Colors.info('Campaign ID:')}   {Colors.value(ch.get('campaign_id', 'N/A'))}")
        if ch.get('emoji'):
            print(f"{Colors.info('Emoji:')}         {ch['emoji']}")
        if ch.get('last_message_at'):
            print(f"{Colors.info('Last Message:')}  {Colors.date(ch['last_message_at'])}")

        # Count messages
        channels = self.channels_data.get('channels', [])
        if self.current_channel_index < len(channels):
            messages = channels[self.current_channel_index].get('messages', [])
            print(f"{Colors.info('Messages:')}      {Colors.success(str(len(messages)))} loaded")

        print_separator()

    def cmd_show_messages(self, args: List[str], skip_auto_jump: bool = False) -> None:
        """Show messages from the current channel."""
        logger.info(f"cmd_show_messages called with args: {args}, skip_auto_jump: {skip_auto_jump}")

        if not self.current_channel:
            logger.warning("No channel selected")
            print(Colors.warning("[!] No channel selected. Use 'select <index>' first."))
            return

        # Get limit from args
        limit = self.display_config.results_per_page
        if args:
            try:
                limit = int(args[0])
                logger.debug(f"Using custom limit: {limit}")
            except ValueError:
                logger.error(f"Invalid limit argument: {args[0]}")
                print(Colors.error(f"Invalid limit: {args[0]}"))
                return

        channels = self.channels_data.get('channels', [])
        logger.debug(f"Total channels in data: {len(channels)}, current index: {self.current_channel_index}")

        if self.current_channel_index >= len(channels):
            logger.error(f"Channel index {self.current_channel_index} out of range")
            print(Colors.error("Channel data not found."))
            return

        # Get messages (oldest first in original order)
        messages = channels[self.current_channel_index].get('messages', [])
        total_messages = len(messages)
        logger.info(f"Channel has {total_messages} messages loaded, showing page {self.current_page}")

        if not messages:
            logger.warning("No messages in channel")
            print(Colors.warning("No messages in this channel."))
            return

        # Calculate total pages
        total_pages = (total_messages + limit - 1) // limit

        # If this is the first time viewing (page 1), jump to last page (newest messages)
        if self.current_page == 1 and not skip_auto_jump:
            self.current_page = total_pages
            logger.info(f"First view - jumping to last page {total_pages} (newest messages)")

        # Paginate (page 1 = oldest, last page = newest)
        start_idx = (self.current_page - 1) * limit
        end_idx = min(start_idx + limit, total_messages)
        page_messages = messages[start_idx:end_idx]

        logger.debug(f"Pagination: start={start_idx}, end={end_idx}, page_messages_count={len(page_messages)}, total_pages={total_pages}")

        print()
        print_separator()
        channel_name = self.current_channel.get('name', 'Unknown')
        print(f"{Colors.header('Messages from:')} {Colors.channel(channel_name)}")
        print(f"{Colors.info('Page')} {Colors.highlight(str(self.current_page))} {Colors.muted('|')} {Colors.info('Showing')} {Colors.value(f'{start_idx + 1}-{end_idx}')} {Colors.info('of')} {Colors.value(str(total_messages))}")
        print_separator()
        print()

        # Display messages (oldest to newest within the page, with correct indices)
        for i, msg in enumerate(page_messages):
            actual_index = start_idx + i + 1
            self._display_message(msg, actual_index)

        logger.info(f"Total pages: {total_pages}, current page: {self.current_page}")
        print(f"\n{Colors.info('Page')} {Colors.highlight(str(self.current_page))} {Colors.info('of')} {Colors.value(str(total_pages))}")
        print(f"{Colors.muted('Use')} {Colors.command('next')}{Colors.muted(',')} {Colors.command('prev')}{Colors.muted(', or')} {Colors.command('page <num>')} {Colors.muted('to navigate.')}")

    def cmd_search(self, args: List[str]) -> None:
        """Search messages with various options."""
        if not args:
            print(f"\n{Colors.warning('Usage:')} {Colors.command('search <keyword> [options]')}")
            print(f"\n{Colors.header('Options:')}")
            print(f"  {Colors.command('--user <name>')}      {Colors.muted('Search by username only')}")
            print(f"  {Colors.command('--case')}             {Colors.muted('Case-sensitive search')}")
            print(f"  {Colors.command('--text-only')}        {Colors.muted('Search text only (not usernames)')}")
            print(f"  {Colors.command('--user-only')}        {Colors.muted('Search usernames only (not text)')}")
            return

        # Parse arguments
        keyword = None
        search_user = None
        case_sensitive = False
        search_text = True
        search_usernames = True

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '--user':
                if i + 1 < len(args):
                    search_user = args[i + 1]
                    i += 2
                else:
                    print(Colors.error("--user requires a value"))
                    return
            elif arg == '--case':
                case_sensitive = True
                i += 1
            elif arg == '--text-only':
                search_usernames = False
                i += 1
            elif arg == '--user-only':
                search_text = False
                i += 1
            else:
                keyword = arg
                i += 1

        if search_user:
            # Search by user
            self.last_search_results = self.searcher.search_by_user(
                search_user,
                case_sensitive=case_sensitive
            )
            print(f"\n{Colors.info('Searching for user:')} {Colors.username(search_user)}")
        elif keyword:
            # Search by keyword
            self.last_search_results = self.searcher.search(
                keyword,
                search_text=search_text,
                search_usernames=search_usernames,
                case_sensitive=case_sensitive
            )
            print(f"\n{Colors.info('Searching for:')} {Colors.highlight(keyword)}")
        else:
            print(Colors.error("Please provide a search keyword or --user option"))
            return

        self.current_page = 1
        self._display_search_results()

    def cmd_next_page(self, args: List[str]) -> None:
        """Go to the next page."""
        logger.info(f"cmd_next_page called, current_page={self.current_page}")
        logger.debug(f"Has search results: {bool(self.last_search_results)}, count={len(self.last_search_results)}")

        if self.last_search_results:
            total_pages = (len(self.last_search_results) + self.display_config.results_per_page - 1) // self.display_config.results_per_page
            logger.debug(f"Total search result pages: {total_pages}")

            if self.current_page < total_pages:
                self.current_page += 1
                logger.info(f"Moving to page {self.current_page}")
                self._display_search_results()
            else:
                logger.info("Already on last page of search results")
                print(Colors.warning("Already on the last page."))
        else:
            # No search results - check if we're viewing messages
            if self.current_channel:
                logger.info("No search results, checking if viewing messages in channel")
                channels = self.channels_data.get('channels', [])
                if self.current_channel_index < len(channels):
                    messages = channels[self.current_channel_index].get('messages', [])
                    total_pages = (len(messages) + self.display_config.results_per_page - 1) // self.display_config.results_per_page
                    logger.debug(f"Channel has {len(messages)} messages, {total_pages} pages")

                    if self.current_page < total_pages:
                        self.current_page += 1
                        logger.info(f"Moving to message page {self.current_page}")
                        self.cmd_show_messages([], skip_auto_jump=True)
                    else:
                        logger.info("Already on last page of messages")
                        print(Colors.warning("Already on the last page."))
                else:
                    logger.warning("Channel index out of range")
                    print(Colors.error("No search results to paginate."))
            else:
                logger.warning("No search results and no channel selected")
                print(Colors.error("No search results to paginate."))

    def cmd_prev_page(self, args: List[str]) -> None:
        """Go to the previous page."""
        logger.info(f"cmd_prev_page called, current_page={self.current_page}")
        logger.debug(f"Has search results: {bool(self.last_search_results)}")

        if self.last_search_results:
            if self.current_page > 1:
                self.current_page -= 1
                logger.info(f"Moving to page {self.current_page}")
                self._display_search_results()
            else:
                logger.info("Already on first page of search results")
                print(Colors.warning("Already on the first page."))
        else:
            # No search results - check if we're viewing messages
            if self.current_channel:
                logger.info("No search results, checking if viewing messages in channel")
                if self.current_page > 1:
                    self.current_page -= 1
                    logger.info(f"Moving to message page {self.current_page}")
                    self.cmd_show_messages([], skip_auto_jump=True)
                else:
                    logger.info("Already on first page of messages")
                    print(Colors.warning("Already on the first page."))
                    print(f"{Colors.info('Use')} {Colors.command('fetch <limit>')} {Colors.info('to load more messages from the server.')}")
            else:
                logger.warning("No search results and no channel selected")
                print(Colors.error("No search results to paginate."))

    def cmd_goto_page(self, args: List[str]) -> None:
        """Go to a specific page number."""
        if not args:
            print(f"{Colors.warning('Usage:')} {Colors.command('page <number>')}")
            return

        try:
            page_num = int(args[0])
            if self.last_search_results:
                total_pages = (len(self.last_search_results) + self.display_config.results_per_page - 1) // self.display_config.results_per_page
                if 1 <= page_num <= total_pages:
                    self.current_page = page_num
                    self._display_search_results()
                else:
                    print(Colors.error(f"Invalid page number. Must be between 1 and {total_pages}"))
            else:
                print(Colors.error("No search results to paginate."))
        except ValueError:
            print(Colors.error(f"Invalid page number: {args[0]}"))

    def cmd_fetch_more(self, args: List[str]) -> None:
        """Fetch more messages from the current channel."""
        logger.info(f"cmd_fetch_more called with args: {args}")

        if not self.current_channel:
            logger.warning("No channel selected for fetch")
            print(Colors.error("No channel selected. Use 'select <index>' first."))
            return

        limit = 50
        if args:
            try:
                limit = int(args[0])
                logger.debug(f"Using custom fetch limit: {limit}")
            except ValueError:
                logger.error(f"Invalid fetch limit: {args[0]}")
                print(Colors.error(f"Invalid limit: {args[0]}"))
                return

        cid = self.current_channel.get('cid')
        if not cid:
            logger.error("Channel CID not found")
            print(Colors.error("Channel CID not found."))
            return

        logger.info(f"Fetching up to {limit} messages from channel CID: {cid}")
        print(f"{Colors.info('Fetching')} {Colors.highlight(str(limit))} {Colors.info('more messages...')}")

        try:
            # Get current message count before fetching
            channels = self.channels_data.get('channels', [])
            old_count = len(channels[self.current_channel_index].get('messages', [])) if self.current_channel_index < len(channels) else 0
            logger.debug(f"Current message count before fetch: {old_count}")

            paginator = self.multi_paginator.get_paginator(cid)
            logger.debug(f"Got paginator for CID: {cid}")

            new_messages = paginator.fetch_all(page_size=50, max_messages=limit)
            logger.info(f"Fetched {len(new_messages)} messages from API")

            # Update channels_data
            if self.current_channel_index < len(channels):
                channels[self.current_channel_index]['messages'] = new_messages
                logger.debug(f"Updated channel {self.current_channel_index} with {len(new_messages)} messages")

            # Refresh searcher
            self.searcher = MessageSearcher(self.channels_data)
            logger.debug("Refreshed MessageSearcher with new data")

            print(f"{Colors.success('[OK] Fetched')} {Colors.highlight(str(len(new_messages)))} {Colors.info('messages total')} {Colors.muted(f'(had {old_count} before)')}")
            logger.info(f"Fetch complete: {old_count} -> {len(new_messages)} messages")
        except Exception as e:
            logger.exception(f"Error fetching messages: {e}")
            print(Colors.error(f"Error fetching messages: {e}"))

    def cmd_show_config(self, args: List[str]) -> None:
        """Show current display configuration."""
        print(f"\n{self.display_config}")

    def cmd_set_config(self, args: List[str]) -> None:
        """Set a configuration value."""
        if len(args) < 2:
            print(f"{Colors.warning('Usage:')} {Colors.command('set <key> <value>')}")
            print(f"{Colors.info('Example:')} {Colors.command('set show_full_text true')}")
            print(f"          {Colors.command('set results_per_page 20')}")
            return

        key = args[0]
        value = args[1]

        # Boolean values
        if key in ['show_user_id', 'show_channel_id', 'show_message_id', 'show_date', 'show_full_text']:
            bool_val = value.lower() in ['true', '1', 'yes', 'on']
            setattr(self.display_config, key, bool_val)
            print(f"{Colors.success('[OK] Set')} {Colors.info(key)} = {Colors.value(str(bool_val))}")

        # Integer values
        elif key in ['max_text_length', 'results_per_page']:
            try:
                int_val = int(value)
                setattr(self.display_config, key, int_val)
                print(f"{Colors.success('[OK] Set')} {Colors.info(key)} = {Colors.value(str(int_val))}")
            except ValueError:
                print(Colors.error(f"Invalid integer value: {value}"))

        else:
            print(Colors.error(f"Unknown configuration key: {key}"))

    def cmd_show_fields(self, args: List[str]) -> None:
        """Manage visible fields."""
        if not args:
            print(f"\n{Colors.header('Available fields:')}")
            all_fields = ['user_name', 'user_id', 'channel_name', 'channel_id',
                         'message_id', 'text', 'date', 'matched_field']
            print("  " + Colors.muted(", ".join(all_fields)))
            print(f"\n{Colors.info('Currently visible:')} {Colors.value(', '.join(sorted(self.display_config.visible_fields)))}")
            print(f"\n{Colors.header('Usage:')}")
            print(f"  {Colors.command('fields add <field>')}    {Colors.muted('- Add a field to display')}")
            print(f"  {Colors.command('fields remove <field>')} {Colors.muted('- Remove a field from display')}")
            return

        action = args[0].lower()
        if len(args) < 2:
            print(f"{Colors.warning('Usage:')} {Colors.command('fields <add|remove> <field>')}")
            return

        field = args[1]

        if action == 'add':
            self.display_config.visible_fields.add(field)
            print(f"{Colors.success('[OK] Added field:')} {Colors.value(field)}")
        elif action == 'remove':
            self.display_config.visible_fields.discard(field)
            print(f"{Colors.success('[OK] Removed field:')} {Colors.value(field)}")
        else:
            print(Colors.error(f"Unknown action: {action}. Use 'add' or 'remove'"))

    def cmd_clear_screen(self, args: List[str]) -> None:
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def cmd_show_stats(self, args: List[str]) -> None:
        """Show statistics."""
        print()
        print_separator()
        print(Colors.header("STATISTICS".center(80)))
        print_separator()
        print(f"{Colors.info('Total Channels:')}        {Colors.value(str(self.searcher.get_channel_count()))}")
        print(f"{Colors.info('Total Messages:')}        {Colors.value(str(self.searcher.get_total_message_count()))}")
        if self.current_channel:
            print(f"{Colors.info('Current Channel:')}       {Colors.channel(self.current_channel.get('name', 'Unknown'))}")
        if self.last_search_results:
            print(f"{Colors.info('Last Search Results:')}   {Colors.highlight(str(len(self.last_search_results)))}")
        print_separator()

    def cmd_quit(self, args: List[str]) -> None:
        """Exit the CLI."""
        print(f"\n{Colors.success('Goodbye!')}")
        self.running = False

    # ========== Helper Methods ==========

    def _format_human_date(self, created_at: str) -> str:
        """Format date in human-friendly format (today, yesterday, or date)."""
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            local_dt = dt.astimezone()
            now = datetime.now(local_dt.tzinfo)

            # Calculate days difference
            days_diff = (now.date() - local_dt.date()).days

            if days_diff == 0:
                # Today - show time only
                return f"Today {local_dt.strftime('%I:%M %p')}"
            elif days_diff == 1:
                # Yesterday
                return f"Yesterday {local_dt.strftime('%I:%M %p')}"
            elif days_diff < 7:
                # Within last week - show day name
                return local_dt.strftime('%a %I:%M %p')
            else:
                # Older - show date without year
                return local_dt.strftime('%b %d, %I:%M %p')
        except:
            return created_at

    def _display_message(self, msg: Dict[str, Any], index: int) -> None:
        """Display a single message."""
        user = msg.get('user', {})
        user_name = user.get('name', 'Unknown')
        text = msg.get('text', '')
        created_at = msg.get('created_at', '')

        # Format date
        date_str = ''
        if self.display_config.show_date and created_at:
            date_str = self._format_human_date(created_at)

        # Truncate text
        if not self.display_config.show_full_text and len(text) > self.display_config.max_text_length:
            text = text[:self.display_config.max_text_length] + "..."

        # Display: [index] username [date]
        print(f"{Colors.muted(f'[{index}]')} {Colors.username(user_name)}", end='')
        if date_str:
            print(f" {Colors.muted(f'[{date_str}]')}", end='')
        print(":")
        print(f"  {text}")

        if self.display_config.show_message_id:
            print(f"  {Colors.muted('ID:')} {Colors.muted(msg.get('id', 'N/A'))}")

        print()

    def _display_search_results(self) -> None:
        """Display paginated search results."""
        if not self.last_search_results:
            print(Colors.warning("No results found."))
            return

        # Paginate
        start_idx = (self.current_page - 1) * self.display_config.results_per_page
        end_idx = start_idx + self.display_config.results_per_page
        page_results = self.last_search_results[start_idx:end_idx]

        total_pages = (len(self.last_search_results) + self.display_config.results_per_page - 1) // self.display_config.results_per_page

        print()
        print_separator()
        print(f"{Colors.header('Search Results:')} {Colors.highlight(str(len(self.last_search_results)))} {Colors.info('total')}")
        print(f"{Colors.info('Page')} {Colors.highlight(str(self.current_page))} {Colors.info('of')} {Colors.value(str(total_pages))} {Colors.muted('|')} {Colors.info('Showing')} {Colors.value(f'{start_idx + 1}-{min(end_idx, len(self.last_search_results))}')}")
        print_separator()
        print()

        for idx, result in enumerate(page_results, start_idx + 1):
            self._display_search_result(result, idx)

        print(f"\n{Colors.info('Page')} {Colors.highlight(str(self.current_page))} {Colors.info('of')} {Colors.value(str(total_pages))}")
        print(f"{Colors.muted('Use')} {Colors.command('next')}{Colors.muted(',')} {Colors.command('prev')}{Colors.muted(', or')} {Colors.command('page <num>')} {Colors.muted('to navigate.')}")

    def _display_search_result(self, result: SearchResult, index: int) -> None:
        """Display a single search result."""
        fields = self.display_config.visible_fields

        # Display: [index] username [date] in 'channel'
        print(f"{Colors.muted(f'[{index}]')} ", end='')

        if 'user_name' in fields:
            print(f"{Colors.username(result.user_name)}", end='')

        if 'user_id' in fields and self.display_config.show_user_id:
            print(f" {Colors.muted(f'(ID: {result.user_id})')}", end='')

        if 'date' in fields and self.display_config.show_date:
            print(f" {Colors.muted(f'[{result.format_date()}]')}", end='')

        if 'channel_name' in fields:
            channel_with_quotes = f"'{result.channel_name}'"
            print(f" {Colors.info('in')} {Colors.channel(channel_with_quotes)}", end='')

        if 'matched_field' in fields:
            print(f" {Colors.muted(f'[matched: {result.matched_field}]')}", end='')

        print(":")  # End line with colon

        if 'text' in fields:
            text = result.text
            if not self.display_config.show_full_text and len(text) > self.display_config.max_text_length:
                text = text[:self.display_config.max_text_length] + "..."
            print(f"  {text}")

        if 'message_id' in fields and self.display_config.show_message_id:
            print(f"  {Colors.muted('Message ID:')} {Colors.muted(result.message_id)}")

        print()

    def print_welcome(self) -> None:
        """Print welcome message."""
        print()
        print_header("PATREON CHANNEL BROWSER")
        print(f"\n{Colors.success('[OK] Loaded')} {Colors.highlight(str(self.searcher.get_channel_count()))} {Colors.info('channels')} with {Colors.highlight(str(self.searcher.get_total_message_count()))} {Colors.info('messages')}")
        print(f"\n{Colors.info('>')} Type {Colors.command('help')} for available commands")
        print(f"{Colors.info('>')} Type {Colors.command('list')} to see all channels")
        print(f"{Colors.info('>')} Type {Colors.command('quit')} or {Colors.command('exit')} to exit")
        print_separator()


def start_interactive_cli(channels_data: Dict[str, Any], client: Any) -> None:
    """
    Start the interactive CLI.

    Args:
        channels_data: Initial channel data from API
        client: StreamChatClient instance
    """
    cli = InteractiveCLI(channels_data, client)
    cli.run()
