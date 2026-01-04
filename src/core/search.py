"""
Channel Message Search Module
Provides search functionality for Stream.io chat messages.
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    """Represents a single search result from a message."""
    message_id: str
    text: str
    user_id: str
    user_name: str
    channel_id: str
    channel_name: str
    created_at: str
    matched_field: Literal['text', 'user_name']

    def format_date(self) -> str:
        """Format the ISO timestamp to a human-readable format."""
        try:
            # Parse ISO format: "2025-11-20T20:42:25.971701Z"
            dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            # Convert to local time
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
        except (ValueError, AttributeError):
            # Return original if parsing fails
            return self.created_at

    def __str__(self) -> str:
        """Format the search result for display."""
        return (
            f"[{self.format_date()}] {self.user_name} in '{self.channel_name}':\n"
            f"  {self.text[:100]}{'...' if len(self.text) > 100 else ''}\n"
            f"  (Matched: {self.matched_field})"
        )


class MessageSearcher:
    """Search through channel messages for keywords."""

    def __init__(self, channels_data: Dict[str, Any]) -> None:
        """
        Initialize the searcher with channel data.

        Args:
            channels_data: The JSON response from the get_channels API call
        """
        self.channels_data: Dict[str, Any] = channels_data
        self.channels: List[Dict[str, Any]] = channels_data.get('channels', [])

    def search(
        self,
        keyword: str,
        search_text: bool = True,
        search_usernames: bool = True,
        case_sensitive: bool = False,
        page_size: Optional[int] = None,
        page: int = 1
    ) -> List[SearchResult]:
        """
        Search for a keyword in messages and usernames.

        Args:
            keyword: The keyword to search for
            search_text: Whether to search in message text (default: True)
            search_usernames: Whether to search in usernames (default: True)
            case_sensitive: Whether the search should be case-sensitive (default: False)
            page_size: Number of results per page (None = all results)
            page: Page number (1-indexed)

        Returns:
            List of SearchResult objects matching the criteria
        """
        if not keyword:
            return []

        # Prepare keyword for comparison
        search_keyword = keyword if case_sensitive else keyword.lower()

        results = []

        # Iterate through all channels
        for channel_wrapper in self.channels:
            channel = channel_wrapper.get('channel', {})
            channel_id = channel.get('id', 'unknown')
            channel_name = channel.get('name', 'Unknown Channel')
            messages = channel_wrapper.get('messages', [])

            # Search through messages in this channel
            for message in messages:
                message_id = message.get('id', '')
                text = message.get('text', '')
                user = message.get('user', {})
                user_id = user.get('id', 'unknown')
                user_name = user.get('name', 'Unknown User')
                created_at = message.get('created_at', '')

                # Prepare fields for comparison
                compare_text = text if case_sensitive else text.lower()
                compare_username = user_name if case_sensitive else user_name.lower()

                # Check for matches
                matched = False
                matched_field = None

                if search_text and search_keyword in compare_text:
                    matched = True
                    matched_field = 'text'
                elif search_usernames and search_keyword in compare_username:
                    matched = True
                    matched_field = 'user_name'

                if matched:
                    results.append(SearchResult(
                        message_id=message_id,
                        text=text,
                        user_id=user_id,
                        user_name=user_name,
                        channel_id=channel_id,
                        channel_name=channel_name,
                        created_at=created_at,
                        matched_field=matched_field
                    ))

        # Apply pagination if requested
        if page_size is not None:
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            results = results[start_idx:end_idx]

        return results

    def search_by_user(self, username: str, case_sensitive: bool = False) -> List[SearchResult]:
        """
        Find all messages from a specific user.

        Args:
            username: The username to search for
            case_sensitive: Whether the search should be case-sensitive

        Returns:
            List of SearchResult objects from that user
        """
        return self.search(
            keyword=username,
            search_text=False,
            search_usernames=True,
            case_sensitive=case_sensitive
        )

    def get_total_message_count(self) -> int:
        """Get the total number of messages across all channels."""
        count = 0
        for channel_wrapper in self.channels:
            messages = channel_wrapper.get('messages', [])
            count += len(messages)
        return count

    def get_channel_count(self) -> int:
        """Get the total number of channels."""
        return len(self.channels)

    def print_search_results(
        self,
        results: List[SearchResult],
        max_display: Optional[int] = None,
        show_full_text: bool = False
    ) -> None:
        """
        Print search results in a readable format.

        Args:
            results: List of SearchResult objects
            max_display: Maximum number of results to display (None = all)
            show_full_text: Whether to show full message text or truncate
        """
        if not results:
            print("No results found.")
            return

        print(f"\nFound {len(results)} result(s):\n")
        print("=" * 80)

        display_count = len(results) if max_display is None else min(max_display, len(results))

        for idx, result in enumerate(results[:display_count], 1):
            print(f"\n[Result {idx}]")
            print(f"User: {result.user_name} (ID: {result.user_id})")
            print(f"Channel: {result.channel_name}")
            print(f"Date: {result.format_date()}")
            print(f"Matched: {result.matched_field}")
            print(f"Message:")

            if show_full_text:
                print(f"  {result.text}")
            else:
                # Truncate long messages
                max_len = 200
                if len(result.text) > max_len:
                    print(f"  {result.text[:max_len]}...")
                else:
                    print(f"  {result.text}")

            print("-" * 80)

        if max_display and len(results) > max_display:
            print(f"\n... and {len(results) - max_display} more result(s)")


def search_channels_interactive(channels_data: Dict[str, Any]) -> None:
    """
    Interactive search mode for exploring channel messages.

    Args:
        channels_data: The JSON response from the get_channels API call
    """
    searcher = MessageSearcher(channels_data)

    print(f"\nChannel Search Initialized")
    print(f"Channels: {searcher.get_channel_count()}")
    print(f"Total Messages: {searcher.get_total_message_count()}")
    print("\nSearch Options:")
    print("  - Enter a keyword to search")
    print("  - Type 'user:<username>' to search by username")
    print("  - Type 'quit' to exit")

    while True:
        print("\n" + "=" * 80)
        query = input("\nSearch: ").strip()

        if query.lower() == 'quit':
            print("Exiting search.")
            break

        if not query:
            continue

        # Check if searching by user
        if query.lower().startswith('user:'):
            username = query[5:].strip()
            results = searcher.search_by_user(username)
        else:
            results = searcher.search(query)

        searcher.print_search_results(results, max_display=10)
