"""
API Configuration Module
Manages configuration and credentials for Stream.io API.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class StreamAPIConfig:
    """Configuration for Stream.io API client."""
    base_url: str = "https://chat.stream-io-api.com"
    api_key: Optional[str] = None
    user_id: Optional[str] = None
    connection_id: Optional[str] = None
    authorization_token: Optional[str] = None

    def __post_init__(self) -> None:
        """Load configuration from environment variables if not provided."""
        self.api_key = self.api_key or os.getenv("STREAM_API_KEY")
        self.user_id = self.user_id or os.getenv("STREAM_USER_ID")
        self.connection_id = self.connection_id or os.getenv("STREAM_CONNECTION_ID")
        self.authorization_token = self.authorization_token or os.getenv("STREAM_AUTH_TOKEN")
