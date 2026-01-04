"""
Pagination module for fetching messages from a single channel.
"""

from typing import Dict, Any, List, Optional, Iterator, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..clients.stream_client import StreamChatClient


@dataclass
class PaginationState:
    """Tracks pagination state for a channel."""
    channel_id: str
    total_fetched: int = 0
    last_message_id: Optional[str] = None
    has_more: bool = True


class ChannelPaginator:
    """
    Paginator for fetching messages from a single channel.

    Handles fetching messages in batches with automatic pagination.
    """

    def __init__(self, client: "StreamChatClient", channel_id: str) -> None:
        """
        Initialize the paginator.

        Args:
            client: StreamChatClient instance
            channel_id: The channel ID (CID) to paginate (e.g., "community_chat_lounge:9f5dd52...")
        """
        self.client: "StreamChatClient" = client
        self.channel_id: str = channel_id
        self.state: PaginationState = PaginationState(channel_id=channel_id)
        self.all_messages: List[Dict[str, Any]] = []
        self.channel_info: Optional[Dict[str, Any]] = None

    def fetch_page(
        self,
        page_size: int = 30,
        id_lt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch a single page of messages.

        Args:
            page_size: Number of messages to fetch (default: 30, max: 300)
            id_lt: Fetch messages with ID less than this (for pagination)

        Returns:
            API response containing channel and messages
        """
        # Use id_lt from state if not provided
        if id_lt is None and self.state.last_message_id is not None:
            id_lt = self.state.last_message_id

        # Call the query_channel API with pagination support
        response = self.client.query_channel(
            channel_id=self.channel_id,
            message_limit=page_size,
            id_lt=id_lt
        )

        # Extract channel and messages from the response structure
        channel = response.get('channel', {})
        messages = response.get('messages', [])

        # Store channel info on first fetch
        if self.channel_info is None:
            self.channel_info = channel

        # Update state - use the FIRST message's ID since messages are returned OLDEST-FIRST
        if messages:
            # Messages are returned oldest first, so we want the first (oldest) message ID for next pagination
            # Using id_lt with this ID will fetch even older messages
            self.state.last_message_id = messages[0].get('id')
            self.state.total_fetched += len(messages)

        # Check if there are more messages
        if len(messages) < page_size:
            self.state.has_more = False

        return response

    def fetch_all(
        self,
        page_size: int = 30,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all messages from the channel (or up to max_messages).

        Args:
            page_size: Number of messages to fetch per request
            max_messages: Maximum total messages to fetch (None = all)

        Returns:
            List of all message dictionaries sorted by created_at (oldest first), deduplicated by ID
        """
        self.all_messages = []
        messages_needed = max_messages
        last_message_id = None

        while self.state.has_more:
            # Determine how many to fetch this round
            fetch_size = page_size
            if messages_needed is not None:
                fetch_size = min(page_size, messages_needed - len(self.all_messages))
                if fetch_size <= 0:
                    break

            # Fetch page
            response = self.fetch_page(page_size=fetch_size)

            # Extract messages from the query_channel response
            messages = response.get('messages', [])

            if messages:
                # Check if we're getting the same messages (no progress)
                # This happens when we've reached the beginning of history
                # Since messages are oldest-first, check the first message ID
                current_first_id = messages[0].get('id')
                if current_first_id == last_message_id:
                    # No new messages, we've hit the end
                    break
                last_message_id = current_first_id

                self.all_messages.extend(messages)

            # Check if we're done
            if not self.state.has_more or len(messages) == 0:
                break

        # Deduplicate by message ID (in case of overlapping fetches)
        seen_ids = set()
        unique_messages = []
        for msg in self.all_messages:
            msg_id = msg.get('id')
            if msg_id and msg_id not in seen_ids:
                seen_ids.add(msg_id)
                unique_messages.append(msg)

        # Sort messages by created_at timestamp (oldest first)
        # This ensures consistent ordering regardless of fetch order
        unique_messages.sort(key=lambda msg: msg.get('created_at', ''))

        self.all_messages = unique_messages
        return self.all_messages

    def fetch_iterator(
        self,
        page_size: int = 30,
        max_messages: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Fetch messages as an iterator, yielding one message at a time.

        Args:
            page_size: Number of messages to fetch per request
            max_messages: Maximum total messages to fetch (None = all)

        Yields:
            Individual message dictionaries
        """
        total_yielded = 0

        while self.state.has_more:
            # Check if we've reached the limit
            if max_messages is not None and total_yielded >= max_messages:
                break

            # Fetch page
            response = self.fetch_page(page_size=page_size)

            # Extract and yield messages from query_channel response
            messages = response.get('messages', [])
            for message in messages:
                if max_messages is not None and total_yielded >= max_messages:
                    return
                yield message
                total_yielded += 1

            # Check if we're done
            if not self.state.has_more or len(messages) == 0:
                break

    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """
        Get channel information.

        Returns:
            Channel metadata dictionary, or None if not fetched yet
        """
        return self.channel_info

    def get_state(self) -> PaginationState:
        """Get current pagination state."""
        return self.state

    def reset(self) -> None:
        """Reset pagination state."""
        self.state = PaginationState(channel_id=self.channel_id)
        self.all_messages = []


class MultiChannelPaginator:
    """Paginator for multiple channels."""

    def __init__(self, client: "StreamChatClient") -> None:
        """
        Initialize the multi-channel paginator.

        Args:
            client: StreamChatClient instance
        """
        self.client: "StreamChatClient" = client
        self.paginators: Dict[str, ChannelPaginator] = {}

    def get_paginator(self, channel_id: str) -> ChannelPaginator:
        """
        Get or create a paginator for a specific channel.

        Args:
            channel_id: The channel ID (CID)

        Returns:
            ChannelPaginator instance for the channel
        """
        if channel_id not in self.paginators:
            self.paginators[channel_id] = ChannelPaginator(self.client, channel_id)
        return self.paginators[channel_id]

    def fetch_from_channel(
        self,
        channel_id: str,
        page_size: int = 30,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from a specific channel.

        Args:
            channel_id: The channel ID (CID)
            page_size: Number of messages to fetch per request
            max_messages: Maximum total messages to fetch

        Returns:
            List of message dictionaries
        """
        paginator = self.get_paginator(channel_id)
        return paginator.fetch_all(page_size=page_size, max_messages=max_messages)

    def fetch_from_all_channels(
        self,
        channel_ids: List[str],
        page_size: int = 30,
        max_messages_per_channel: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch messages from multiple channels.

        Args:
            channel_ids: List of channel IDs to fetch from
            page_size: Number of messages to fetch per request
            max_messages_per_channel: Maximum messages per channel

        Returns:
            Dictionary mapping channel_id to list of messages
        """
        results = {}
        for channel_id in channel_ids:
            messages = self.fetch_from_channel(
                channel_id=channel_id,
                page_size=page_size,
                max_messages=max_messages_per_channel
            )
            results[channel_id] = messages
        return results
