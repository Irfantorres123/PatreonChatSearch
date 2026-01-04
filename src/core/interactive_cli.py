"""
Refactored Interactive CLI with clean separation of concerns.
Follows Single Responsibility Principle and layered architecture.
"""

import shlex
from typing import Dict, Any, List

from .view_context import ViewContext, ViewMode
from .renderers import (
    DisplayConfig,
    MessageRenderer,
    SearchRenderer,
    ChannelRenderer
)
from .navigation import NavigationController
from .command_parser import CommandParser
from .search import MessageSearcher
from .pagination import MultiChannelPaginator
from .colors import Colors, print_separator, print_header
from .logger import get_logger

logger = get_logger()


class InteractiveCLI:
    """
    Interactive command-line interface for browsing channels and messages.
    Refactored to follow clean architecture principles.
    """

    def __init__(self, channels_data: Dict[str, Any], client: Any) -> None:
        """
        Initialize the interactive CLI.

        Args:
            channels_data: Initial channel data from API
            client: StreamChatClient instance for fetching more data
        """
        logger.info("Initializing InteractiveCLI v2")

        # Core dependencies
        self.client = client
        self.searcher = MessageSearcher(channels_data)
        self.multi_paginator = MultiChannelPaginator(client)

        # View management
        self.context = ViewContext(channels_data=channels_data)
        self.display_config = DisplayConfig()

        # Controllers and renderers
        self.navigation = NavigationController(self.display_config.results_per_page)
        self.message_renderer = MessageRenderer(self.display_config)
        self.search_renderer = SearchRenderer(self.display_config)

        # Parser
        self.parser = CommandParser()

        # State
        self.running = False

        # Command registry
        self.commands: Dict[str, tuple] = {
            'help': (self.cmd_help, 'Show available commands'),
            'list': (self.cmd_list_channels, 'List all channels'),
            'select': (self.cmd_select_channel, 'Select a channel by index or name'),
            'show': (self.cmd_show_channel, 'Show current channel details'),
            'messages': (self.cmd_show_messages, 'Show messages from current channel'),
            'search': (self.cmd_search, 'Search messages'),
            'next': (self.cmd_next_page, 'Go to next page'),
            'prev': (self.cmd_prev_page, 'Go to previous page'),
            'page': (self.cmd_goto_page, 'Go to specific page'),
            'fetch': (self.cmd_fetch_more, 'Fetch more messages from server'),
            'config': (self.cmd_show_config, 'Show display configuration'),
            'set': (self.cmd_set_config, 'Set configuration value'),
            'fields': (self.cmd_show_fields, 'Manage visible fields'),
            'stats': (self.cmd_show_stats, 'Show statistics'),
            'clear': (self.cmd_clear_screen, 'Clear screen'),
            'quit': (self.cmd_quit, 'Exit the CLI'),
            'exit': (self.cmd_quit, 'Exit the CLI'),
        }

        logger.info("InteractiveCLI v2 initialized successfully")

    def run(self) -> None:
        """Main CLI loop."""
        self.running = True
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
                logger.exception(f"Unexpected error: {e}")
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
        channels = self.context.channels_data.get('channels', [])
        ChannelRenderer.render_channel_list(channels)

    def cmd_select_channel(self, args: List[str]) -> None:
        """Select a channel by index or name."""
        logger.info(f"cmd_select_channel called with args: {args}")

        if not args:
            print(f"{Colors.warning('Usage:')} {Colors.command('select <index|name>')}")
            return

        channels = self.context.channels_data.get('channels', [])

        # Try to parse as index
        try:
            index = int(args[0])
            logger.debug(f"Attempting to select channel by index: {index}")

            if 1 <= index <= len(channels):
                channel = channels[index - 1].get('channel', {})
                self.context.select_channel(channel, index - 1)

                channel_name = channel.get('name', 'Unknown')
                logger.info(f"Selected channel: {channel_name}")

                print(f"\n{Colors.success('[OK] Selected channel:')} {Colors.channel(channel_name)}")
                self.cmd_show_channel([])
            else:
                logger.warning(f"Invalid channel index: {index}")
                print(Colors.error(f"[X] Invalid index. Must be between 1 and {len(channels)}"))

        except ValueError:
            # Search by name
            search_name = ' '.join(args).lower()
            logger.debug(f"Searching for channel by name: {search_name}")

            for idx, channel_wrapper in enumerate(channels):
                channel = channel_wrapper.get('channel', {})
                if search_name in channel.get('name', '').lower():
                    self.context.select_channel(channel, idx)

                    channel_name = channel.get('name', 'Unknown')
                    logger.info(f"Found and selected channel: {channel_name}")

                    print(f"\n{Colors.success('[OK] Selected channel:')} {Colors.channel(channel_name)}")
                    self.cmd_show_channel([])
                    return

            logger.warning(f"No channel found matching: {search_name}")
            print(Colors.error(f"[X] No channel found matching: {' '.join(args)}"))

    def cmd_show_channel(self, args: List[str]) -> None:
        """Show details of the current channel."""
        if not self.context.has_channel():
            print(Colors.warning("[!] No channel selected. Use 'select <index>' first."))
            return

        message_count = len(self.context.get_current_messages())
        ChannelRenderer.render_channel_details(self.context.current_channel, message_count)

    def cmd_show_messages(self, args: List[str]) -> None:
        """Show messages from the current channel."""
        logger.info(f"cmd_show_messages called with args: {args}")

        if not self.context.has_channel():
            print(Colors.warning("[!] No channel selected. Use 'select <index>' first."))
            return

        # Parse limit
        limit, error = self.parser.parse_int_arg(
            args,
            self.display_config.results_per_page,
            "limit"
        )
        if error:
            print(Colors.error(error))
            return

        # Update items per page if custom limit provided
        if args:
            self.navigation.set_items_per_page(limit)

        messages = self.context.get_current_messages()
        if not messages:
            print(Colors.warning("No messages in this channel."))
            return

        # Determine if this is first view (auto-jump to newest)
        auto_jump = not self.context.messages_viewed

        # Mark messages as viewed and switch to messages mode
        self.context.messages_viewed = True
        self.context.mode = ViewMode.MESSAGES

        # Paginate
        result = self.navigation.paginate_messages(
            messages,
            self.context.current_page,
            auto_jump_to_last=auto_jump
        )

        # Update context page
        self.context.current_page = result.current_page

        # Render
        channel_name = self.context.current_channel.get('name', 'Unknown')
        self.message_renderer.render_message_list(
            result.items,
            channel_name,
            result.current_page,
            result.total_pages,
            result.start_idx,
            result.end_idx,
            result.total_items
        )

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

        # Parse search options
        options, error = self.parser.parse_search_args(args)
        if error:
            print(Colors.error(error))
            return

        # Execute search
        if options.user:
            results = self.searcher.search_by_user(
                options.user,
                case_sensitive=options.case_sensitive
            )
            print(f"\n{Colors.info('Searching for user:')} {Colors.username(options.user)}")
        elif options.keyword:
            results = self.searcher.search(
                options.keyword,
                search_text=options.search_text,
                search_usernames=options.search_usernames,
                case_sensitive=options.case_sensitive
            )
            print(f"\n{Colors.info('Searching for:')} {Colors.highlight(options.keyword)}")
        else:
            print(Colors.error("Please provide a search keyword or --user option"))
            return

        # Update context
        self.context.set_search_results(results)

        # Display results
        self._display_current_view()

    def cmd_next_page(self, args: List[str]) -> None:
        """Go to the next page."""
        new_page, message = self.navigation.next_page(self.context)

        if message:
            print(Colors.warning(message))
        else:
            self.context.current_page = new_page
            self._display_current_view()

    def cmd_prev_page(self, args: List[str]) -> None:
        """Go to the previous page."""
        new_page, message = self.navigation.prev_page(self.context)

        if message:
            if "first page" in message:
                print(Colors.warning("Already on the first page."))
                if self.context.is_viewing_messages():
                    print(f"{Colors.info('Use')} {Colors.command('fetch <limit>')} {Colors.info('to load more messages from the server.')}")
            else:
                print(Colors.warning(message))
        else:
            self.context.current_page = new_page
            self._display_current_view()

    def cmd_goto_page(self, args: List[str]) -> None:
        """Go to a specific page number."""
        if not args:
            print(f"{Colors.warning('Usage:')} {Colors.command('page <number>')}")
            return

        page_num, error = self.parser.parse_int_arg(args, 1, "page number")
        if error:
            print(Colors.error(error))
            return

        new_page, message = self.navigation.goto_page(self.context, page_num)

        if message:
            print(Colors.error(message))
        else:
            self.context.current_page = new_page
            self._display_current_view()

    def cmd_fetch_more(self, args: List[str]) -> None:
        """Fetch more messages from the current channel."""
        logger.info(f"cmd_fetch_more called with args: {args}")

        if not self.context.has_channel():
            print(Colors.error("No channel selected. Use 'select <index>' first."))
            return

        limit, error = self.parser.parse_int_arg(args, 50, "limit")
        if error:
            print(Colors.error(error))
            return

        cid = self.context.current_channel.get('cid')
        if not cid:
            print(Colors.error("Channel CID not found."))
            return

        logger.info(f"Fetching up to {limit} messages from channel CID: {cid}")
        print(f"{Colors.info('Fetching')} {Colors.highlight(str(limit))} {Colors.info('more messages...')}")

        try:
            old_messages = self.context.get_current_messages()
            old_count = len(old_messages)

            paginator = self.multi_paginator.get_paginator(cid)

            # If we have existing messages, set the paginator state to continue from the oldest message
            if old_messages:
                # Find the oldest message ID to continue pagination from
                oldest_msg = min(old_messages, key=lambda m: m.get('created_at', ''))
                paginator.state.last_message_id = oldest_msg.get('id')
                paginator.state.has_more = True  # Re-enable fetching

            # Fetch more messages (continuing from where we left off)
            new_messages = paginator.fetch_all(page_size=100, max_messages=limit)

            # Merge old and new messages, deduplicate, and sort
            all_messages = old_messages + new_messages

            # Deduplicate by message ID
            seen_ids = set()
            unique_messages = []
            for msg in all_messages:
                msg_id = msg.get('id')
                if msg_id and msg_id not in seen_ids:
                    seen_ids.add(msg_id)
                    unique_messages.append(msg)

            # Sort by created_at (oldest first)
            unique_messages.sort(key=lambda msg: msg.get('created_at', ''))

            # Update context
            self.context.update_channel_messages(unique_messages)

            # Refresh searcher
            self.searcher = MessageSearcher(self.context.channels_data)

            fetched_count = len(unique_messages) - old_count
            print(f"{Colors.success('[OK] Fetched')} {Colors.highlight(str(fetched_count))} {Colors.info('new messages')} {Colors.muted(f'(total: {len(unique_messages)})')}")
            logger.info(f"Fetch complete: {old_count} -> {len(unique_messages)} messages")

        except Exception as e:
            logger.exception(f"Error fetching messages: {e}")
            print(Colors.error(f"Error fetching messages: {e}"))

    def cmd_show_config(self, args: List[str]) -> None:
        """Show current display configuration."""
        print(f"\n{self.display_config}")

    def cmd_set_config(self, args: List[str]) -> None:
        """Set a configuration value."""
        key, value, error = self.parser.parse_set_config_args(args)

        if error:
            print(f"{Colors.warning(error)}")
            print(f"{Colors.info('Example:')} {Colors.command('set show_full_text true')}")
            print(f"          {Colors.command('set results_per_page 20')}")
            return

        # Boolean values
        if key in ['show_user_id', 'show_channel_id', 'show_message_id', 'show_date', 'show_full_text']:
            bool_val = self.parser.parse_bool_arg(value)
            setattr(self.display_config, key, bool_val)
            print(f"{Colors.success('[OK] Set')} {Colors.info(key)} = {Colors.value(str(bool_val))}")

        # Integer values
        elif key in ['max_text_length', 'results_per_page']:
            try:
                int_val = int(value)
                setattr(self.display_config, key, int_val)
                # Update navigation controller
                if key == 'results_per_page':
                    self.navigation.set_items_per_page(int_val)
                print(f"{Colors.success('[OK] Set')} {Colors.info(key)} = {Colors.value(str(int_val))}")
            except ValueError:
                print(Colors.error(f"Invalid integer value: {value}"))

        else:
            print(Colors.error(f"Unknown configuration key: {key}"))

    def cmd_show_fields(self, args: List[str]) -> None:
        """Manage visible fields."""
        action, field, error = self.parser.parse_fields_args(args)

        if error:
            print(f"{Colors.warning(error)}")
            return

        if not action:
            # Show help
            print(f"\n{Colors.header('Available fields:')}")
            all_fields = ['user_name', 'user_id', 'channel_name', 'channel_id',
                         'message_id', 'text', 'date', 'matched_field']
            print("  " + Colors.muted(", ".join(all_fields)))
            print(f"\n{Colors.info('Currently visible:')} {Colors.value(', '.join(sorted(self.display_config.visible_fields)))}")
            print(f"\n{Colors.header('Usage:')}")
            print(f"  {Colors.command('fields add <field>')}    {Colors.muted('- Add a field to display')}")
            print(f"  {Colors.command('fields remove <field>')} {Colors.muted('- Remove a field from display')}")
            return

        if action == 'add':
            self.display_config.visible_fields.add(field)
            print(f"{Colors.success('[OK] Added field:')} {Colors.value(field)}")
        elif action == 'remove':
            self.display_config.visible_fields.discard(field)
            print(f"{Colors.success('[OK] Removed field:')} {Colors.value(field)}")

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
        if self.context.has_channel():
            print(f"{Colors.info('Current Channel:')}       {Colors.channel(self.context.current_channel.get('name', 'Unknown'))}")
        if self.context.search_results:
            print(f"{Colors.info('Last Search Results:')}   {Colors.highlight(str(len(self.context.search_results)))}")
        print_separator()

    def cmd_quit(self, args: List[str]) -> None:
        """Exit the CLI."""
        print(f"\n{Colors.success('Goodbye!')}")
        self.running = False

    # ========== Helper Methods ==========

    def _display_current_view(self) -> None:
        """Display the current view based on context mode."""
        if self.context.is_viewing_search():
            self._display_search_results()
        elif self.context.is_viewing_messages():
            self.cmd_show_messages([])

    def _display_search_results(self) -> None:
        """Display paginated search results."""
        if not self.context.search_results:
            print(Colors.warning("No results found."))
            return

        result = self.navigation.paginate_search_results(
            self.context.search_results,
            self.context.current_page
        )

        self.search_renderer.render_search_results(
            result.items,
            result.current_page,
            result.total_pages,
            result.start_idx,
            result.end_idx
        )

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
