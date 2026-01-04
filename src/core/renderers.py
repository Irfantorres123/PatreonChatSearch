"""
Display renderers for different view types.
Separates display logic from business logic following Single Responsibility Principle.
"""

from typing import Dict, Any, List
from datetime import datetime

from .colors import Colors, print_separator
from .search import SearchResult


class DisplayConfig:
    """Configuration for display rendering."""

    def __init__(self):
        self.show_user_id: bool = False
        self.show_channel_id: bool = False
        self.show_message_id: bool = False
        self.show_date: bool = True
        self.show_full_text: bool = False
        self.max_text_length: int = 200
        self.results_per_page: int = 10
        self.visible_fields: set = {'user_name', 'channel_name', 'text', 'date'}

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


class DateFormatter:
    """Formats dates in human-friendly format."""

    @staticmethod
    def format_human_date(created_at: str) -> str:
        """
        Format date in human-friendly format (today, yesterday, or date).

        Args:
            created_at: ISO format datetime string

        Returns:
            Human-friendly date string
        """
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            local_dt = dt.astimezone()
            now = datetime.now(local_dt.tzinfo)

            days_diff = (now.date() - local_dt.date()).days

            if days_diff == 0:
                return f"Today {local_dt.strftime('%I:%M %p')}"
            elif days_diff == 1:
                return f"Yesterday {local_dt.strftime('%I:%M %p')}"
            elif days_diff < 7:
                return local_dt.strftime('%a %I:%M %p')
            else:
                return local_dt.strftime('%b %d, %I:%M %p')
        except:
            return created_at


class MessageRenderer:
    """Renders individual messages and message lists."""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.date_formatter = DateFormatter()

    def render_message(self, msg: Dict[str, Any], index: int) -> None:
        """
        Render a single message.

        Args:
            msg: Message dictionary
            index: Message index number
        """
        user = msg.get('user', {})
        user_name = user.get('name', 'Unknown')
        text = msg.get('text', '')
        created_at = msg.get('created_at', '')

        # Format date
        date_str = ''
        if self.config.show_date and created_at:
            date_str = self.date_formatter.format_human_date(created_at)

        # Truncate text
        if not self.config.show_full_text and len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length] + "..."

        # Display: [index] username [date]
        print(f"{Colors.muted(f'[{index}]')} {Colors.username(user_name)}", end='')
        if date_str:
            print(f" {Colors.muted(f'[{date_str}]')}", end='')
        print(":")
        print(f"  {text}")

        if self.config.show_message_id:
            print(f"  {Colors.muted('ID:')} {Colors.muted(msg.get('id', 'N/A'))}")

        print()

    def render_message_list(
        self,
        messages: List[Dict[str, Any]],
        channel_name: str,
        page: int,
        total_pages: int,
        start_idx: int,
        end_idx: int,
        total_messages: int
    ) -> None:
        """
        Render a paginated list of messages.

        Args:
            messages: List of message dictionaries for current page
            channel_name: Name of the channel
            page: Current page number
            total_pages: Total number of pages
            start_idx: Starting index (0-based)
            end_idx: Ending index (exclusive)
            total_messages: Total number of messages
        """
        print()
        print_separator()
        print(f"{Colors.header('Messages from:')} {Colors.channel(channel_name)}")
        print(f"{Colors.info('Page')} {Colors.highlight(str(page))} {Colors.muted('|')} {Colors.info('Showing')} {Colors.value(f'{start_idx + 1}-{end_idx}')} {Colors.info('of')} {Colors.value(str(total_messages))}")
        print_separator()
        print()

        # Display messages with correct indices
        for i, msg in enumerate(messages):
            actual_index = start_idx + i + 1
            self.render_message(msg, actual_index)

        print(f"\n{Colors.info('Page')} {Colors.highlight(str(page))} {Colors.info('of')} {Colors.value(str(total_pages))}")
        print(f"{Colors.muted('Use')} {Colors.command('next')}{Colors.muted(',')} {Colors.command('prev')}{Colors.muted(', or')} {Colors.command('page <num>')} {Colors.muted('to navigate.')}")


class SearchRenderer:
    """Renders search results."""

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.date_formatter = DateFormatter()

    def render_search_result(self, result: SearchResult, index: int) -> None:
        """
        Render a single search result.

        Args:
            result: SearchResult object
            index: Result index number
        """
        fields = self.config.visible_fields

        # Display: [index] username [date] in 'channel'
        print(f"{Colors.muted(f'[{index}]')} ", end='')

        if 'user_name' in fields:
            print(f"{Colors.username(result.user_name)}", end='')

        if 'user_id' in fields and self.config.show_user_id:
            print(f" {Colors.muted(f'(ID: {result.user_id})')}", end='')

        if 'date' in fields and self.config.show_date:
            print(f" {Colors.muted(f'[{result.format_date()}]')}", end='')

        if 'channel_name' in fields:
            channel_with_quotes = f"'{result.channel_name}'"
            print(f" {Colors.info('in')} {Colors.channel(channel_with_quotes)}", end='')

        if 'matched_field' in fields:
            print(f" {Colors.muted(f'[matched: {result.matched_field}]')}", end='')

        print(":")  # End line with colon

        if 'text' in fields:
            text = result.text
            if not self.config.show_full_text and len(text) > self.config.max_text_length:
                text = text[:self.config.max_text_length] + "..."
            print(f"  {text}")

        if 'message_id' in fields and self.config.show_message_id:
            print(f"  {Colors.muted('Message ID:')} {Colors.muted(result.message_id)}")

        print()

    def render_search_results(
        self,
        results: List[SearchResult],
        page: int,
        total_pages: int,
        start_idx: int,
        end_idx: int
    ) -> None:
        """
        Render a paginated list of search results.

        Args:
            results: List of SearchResult objects for current page
            page: Current page number
            total_pages: Total number of pages
            start_idx: Starting index (0-based)
            end_idx: Ending index (exclusive)
        """
        print()
        print_separator()
        print(f"{Colors.header('Search Results:')} {Colors.highlight(str(end_idx))} {Colors.info('total')}")
        print(f"{Colors.info('Page')} {Colors.highlight(str(page))} {Colors.info('of')} {Colors.value(str(total_pages))} {Colors.muted('|')} {Colors.info('Showing')} {Colors.value(f'{start_idx + 1}-{min(end_idx, len(results) + start_idx)}')}")
        print_separator()
        print()

        for idx, result in enumerate(results, start_idx + 1):
            self.render_search_result(result, idx)

        print(f"\n{Colors.info('Page')} {Colors.highlight(str(page))} {Colors.info('of')} {Colors.value(str(total_pages))}")
        print(f"{Colors.muted('Use')} {Colors.command('next')}{Colors.muted(',')} {Colors.command('prev')}{Colors.muted(', or')} {Colors.command('page <num>')} {Colors.muted('to navigate.')}")


class ChannelRenderer:
    """Renders channel information."""

    @staticmethod
    def render_channel_list(channels: List[Dict[str, Any]]) -> None:
        """
        Render a list of channels.

        Args:
            channels: List of channel wrapper dictionaries
        """
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

    @staticmethod
    def render_channel_details(channel: Dict[str, Any], message_count: int) -> None:
        """
        Render detailed information about a channel.

        Args:
            channel: Channel dictionary
            message_count: Number of loaded messages
        """
        print()
        print_separator()
        print(Colors.header(f"Channel: {channel.get('name', 'Unknown')}"))
        print_separator()
        print(f"{Colors.info('Type:')}          {Colors.value(channel.get('type', 'N/A'))}")
        print(f"{Colors.info('ID:')}            {Colors.muted(channel.get('id', 'N/A'))}")
        print(f"{Colors.info('CID:')}           {Colors.muted(channel.get('cid', 'N/A'))}")
        print(f"{Colors.info('Members:')}       {Colors.highlight(str(channel.get('member_count', 'N/A')))}")
        print(f"{Colors.info('Campaign ID:')}   {Colors.value(channel.get('campaign_id', 'N/A'))}")

        if channel.get('emoji'):
            print(f"{Colors.info('Emoji:')}         {channel['emoji']}")

        if channel.get('last_message_at'):
            date_str = DateFormatter.format_human_date(channel['last_message_at'])
            print(f"{Colors.info('Last Message:')}  {Colors.date(date_str)}")

        print(f"{Colors.info('Messages:')}      {Colors.success(str(message_count))} loaded")
        print_separator()
