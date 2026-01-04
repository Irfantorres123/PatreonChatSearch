"""
View context management for the interactive CLI.
Manages the current view state without coupling to specific display implementations.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from .search import SearchResult


class ViewMode(Enum):
    """Different view modes for the CLI."""
    CHANNEL_LIST = "channel_list"
    MESSAGES = "messages"
    SEARCH_RESULTS = "search_results"


@dataclass
class ViewContext:
    """
    Manages the current view state of the CLI.
    Replaces the modal state management scattered across InteractiveCLI.
    """

    # Current view mode
    mode: ViewMode = ViewMode.CHANNEL_LIST

    # Channel context
    current_channel: Optional[Dict[str, Any]] = None
    current_channel_index: int = 0
    channels_data: Optional[Dict[str, Any]] = None

    # Search context
    search_results: List[SearchResult] = None

    # Pagination context
    current_page: int = 1
    messages_viewed: bool = False  # Track if messages have been viewed for current channel

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.search_results is None:
            self.search_results = []
        if self.channels_data is None:
            self.channels_data = {'channels': []}

    def select_channel(self, channel: Dict[str, Any], index: int) -> None:
        """Select a channel and switch to messages view."""
        self.current_channel = channel
        self.current_channel_index = index
        self.mode = ViewMode.CHANNEL_LIST  # Don't auto-switch to MESSAGES mode
        self.current_page = 1
        self.search_results = []
        self.messages_viewed = False  # Reset when changing channels

    def set_search_results(self, results: List[SearchResult]) -> None:
        """Set search results and switch to search view."""
        self.search_results = results
        self.mode = ViewMode.SEARCH_RESULTS
        self.current_page = 1

    def clear_search(self) -> None:
        """Clear search results and return to previous view."""
        self.search_results = []
        if self.current_channel:
            self.mode = ViewMode.MESSAGES
        else:
            self.mode = ViewMode.CHANNEL_LIST

    def get_current_messages(self) -> List[Dict[str, Any]]:
        """Get messages from the current channel."""
        if not self.current_channel or not self.channels_data:
            return []

        channels = self.channels_data.get('channels', [])
        if self.current_channel_index >= len(channels):
            return []

        return channels[self.current_channel_index].get('messages', [])

    def update_channel_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Update messages for the current channel."""
        if not self.channels_data or self.current_channel_index < 0:
            return

        channels = self.channels_data.get('channels', [])
        if self.current_channel_index < len(channels):
            channels[self.current_channel_index]['messages'] = messages

    def is_viewing_messages(self) -> bool:
        """Check if currently viewing messages."""
        return self.mode == ViewMode.MESSAGES

    def is_viewing_search(self) -> bool:
        """Check if currently viewing search results."""
        return self.mode == ViewMode.SEARCH_RESULTS

    def has_channel(self) -> bool:
        """Check if a channel is selected."""
        return self.current_channel is not None
