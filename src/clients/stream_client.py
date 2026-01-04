"""
Stream.io API Client
Handles all API communication with Stream.io chat API.
"""

import requests
from typing import Optional, Dict, Any, List, TYPE_CHECKING
if TYPE_CHECKING:
    from ..config.api_config import StreamAPIConfig


class StreamChatClient:
    """Client for interacting with Stream.io Chat API."""

    def __init__(self, config: "StreamAPIConfig") -> None:
        """
        Initialize the Stream Chat client.

        Args:
            config: StreamAPIConfig instance with API credentials
        """
        self.config: "StreamAPIConfig" = config
        self.session: requests.Session = requests.Session()
        self._setup_headers()

    def _setup_headers(self) -> None:
        """Configure session headers for API requests."""
        self.session.headers.update({
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "stream-auth-type": "jwt",
            "x-stream-client": "stream-chat-javascript-client-browser-8.40.9",
        })

        # Add authorization header if token is provided
        if self.config.authorization_token:
            self.session.headers["authorization"] = self.config.authorization_token

    def _build_query_params(self) -> Dict[str, str]:
        """Build query parameters for API requests."""
        params = {
            "user_id": self.config.user_id,
            "connection_id": self.config.connection_id,
            "api_key": self.config.api_key,
        }
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}

    def query_channel(
        self,
        channel_id: str,
        message_limit: int = 100,
        id_lt: Optional[str] = None,
        id_gt: Optional[str] = None,
        state: bool = True
    ) -> Dict[str, Any]:
        """
        Query a channel with message pagination support.

        Args:
            channel_id: The channel ID (CID) in format "type:id" (e.g., "community_chat_lounge:9f5dd52...")
            message_limit: Maximum number of messages to return (default: 100)
            id_lt: Fetch messages with ID less than this (for fetching older messages)
            id_gt: Fetch messages with ID greater than this (for fetching newer messages)
            state: Include channel state (default: True)

        Returns:
            JSON response from the API containing channel and messages

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        # Split channel_id into type and id
        parts = channel_id.split(':', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid channel_id format: {channel_id}. Expected 'type:id'")

        channel_type, channel_uuid = parts

        # Build the URL
        url = f"{self.config.base_url}/channels/{channel_type}/{channel_uuid}/query"

        # Build query parameters
        params = self._build_query_params()

        # Build the request payload
        payload = {
            "data": {},
            "state": state,
            "messages": {
                "limit": message_limit
            }
        }

        # Add pagination parameters if provided
        if id_lt:
            payload["messages"]["id_lt"] = id_lt
        if id_gt:
            payload["messages"]["id_gt"] = id_gt

        try:
            response = self.session.post(url, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying channel: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def get_channel_by_id(
        self,
        channel_id: str,
        message_limit: int = 30,
        state: bool = True,
        watch: bool = True,
        presence: bool = False,
        sort_field: str = "last_message_at",
        sort_direction: int = -1,
    ) -> Dict[str, Any]:
        """
        Fetch a single channel by its CID (Channel ID).

        Args:
            channel_id: The channel ID (CID) to fetch (e.g., "community_chat_lounge:9f5dd52653a4487a8966714b77e11aa7")
            message_limit: Maximum number of messages to return (default: 30)
            state: Include channel state (default: True)
            watch: Watch for changes (default: True)
            presence: Include presence information (default: False)
            sort_field: Field to sort messages by (default: "last_message_at")
            sort_direction: Sort direction, -1 for descending, 1 for ascending (default: -1)

        Returns:
            JSON response from the API containing channel data

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.config.base_url}/channels"

        # Build the request payload for a specific channel
        payload = {
            "filter_conditions": {
                "cid": {"$in": [channel_id]}
            },
            "sort": [
                {
                    "field": sort_field,
                    "direction": sort_direction
                }
            ],
            "state": state,
            "watch": watch,
            "presence": presence,
            "limit": message_limit
        }

        # Build query parameters
        params = self._build_query_params()

        try:
            response = self.session.post(url, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching channel: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def get_channels(
        self,
        channel_types: Optional[List[str]] = None,
        limit: int = 30,
        message_limit: int = 25,
        offset: int = 0,
        state: bool = True,
        watch: bool = True,
        presence: bool = False,
        sort_field: str = "last_message_at",
        sort_direction: int = -1,
    ) -> Dict[str, Any]:
        """
        Fetch channels from the Stream.io API.

        Args:
            channel_types: List of channel types to filter (e.g., ["community_chat_lounge", "public_readable_chat"])
            limit: Maximum number of channels to return (default: 30)
            message_limit: Maximum number of messages per channel (default: 25)
            offset: Offset for pagination (default: 0)
            state: Include channel state (default: True)
            watch: Watch for changes (default: True)
            presence: Include presence information (default: False)
            sort_field: Field to sort by (default: "last_message_at")
            sort_direction: Sort direction, -1 for descending, 1 for ascending (default: -1)

        Returns:
            JSON response from the API containing channel data

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.config.base_url}/channels"

        # Default channel types if not provided
        if channel_types is None:
            channel_types = ["community_chat_lounge", "public_readable_chat"]

        # Build the request payload
        payload = {
            "filter_conditions": {
                "$and": [
                    {"type": {"$in": channel_types}},
                    {"members": {"$in": [self.config.user_id]}}
                ]
            },
            "sort": [
                {
                    "field": sort_field,
                    "direction": sort_direction
                }
            ],
            "state": state,
            "watch": watch,
            "presence": presence,
            "limit": limit,
            "message_limit": message_limit,
            "offset": offset
        }

        # Build query parameters
        params = self._build_query_params()

        try:
            response = self.session.post(url, params=params, json=payload)
            response.raise_for_status()  # Raise exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching channels: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self) -> "StreamChatClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit."""
        del exc_type, exc_val, exc_tb  # Unused but required by protocol
        self.close()
        return False
