"""
Example script demonstrating the search functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from src.config import StreamAPIConfig
from src.clients import StreamChatClient
from src.core import MessageSearcher, search_channels_interactive


def main():
    """Demonstrate search functionality."""
    # Load environment variables
    load_dotenv()

    # Initialize API client
    config = StreamAPIConfig()

    print("Fetching channels from Stream.io API...")
    with StreamChatClient(config) as client:
        channels_data = client.get_channels()

    print(f"Successfully fetched {len(channels_data.get('channels', []))} channel(s)")

    # Initialize searcher
    searcher = MessageSearcher(channels_data)

    print(f"\nStatistics:")
    print(f"  Total Channels: {searcher.get_channel_count()}")
    print(f"  Total Messages: {searcher.get_total_message_count()}")

    # Example 1: Search for a keyword in messages
    print("\n" + "=" * 80)
    print("Example 1: Search for 'NVIDIA' in messages")
    print("=" * 80)
    results = searcher.search("NVIDIA")
    searcher.print_search_results(results, max_display=5)

    # Example 2: Search for a specific user
    print("\n" + "=" * 80)
    print("Example 2: Search for messages from user 'Chris'")
    print("=" * 80)
    results = searcher.search_by_user("Chris")
    searcher.print_search_results(results, max_display=5)

    # Example 3: Case-sensitive search
    print("\n" + "=" * 80)
    print("Example 3: Case-sensitive search for 'VRT'")
    print("=" * 80)
    results = searcher.search("VRT", case_sensitive=True)
    searcher.print_search_results(results, max_display=5)

    # Example 4: Paginated search
    print("\n" + "=" * 80)
    print("Example 4: Paginated search - Page 1 of results for 'the'")
    print("=" * 80)
    results = searcher.search("the", page_size=5, page=1)
    searcher.print_search_results(results, show_full_text=False)

    # Example 5: Interactive search mode
    print("\n" + "=" * 80)
    print("Starting Interactive Search Mode")
    print("=" * 80)
    search_channels_interactive(channels_data)


if __name__ == "__main__":
    main()
