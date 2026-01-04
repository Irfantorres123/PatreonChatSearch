"""
Example demonstrating pagination for fetching messages from channels.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from src.config import StreamAPIConfig
from src.clients import StreamChatClient
from src.core import ChannelPaginator, MultiChannelPaginator, MessageSearcher


def example_single_channel_pagination():
    """Example: Paginate through a single channel."""
    print("=" * 80)
    print("Example 1: Single Channel Pagination")
    print("=" * 80)

    load_dotenv()
    config = StreamAPIConfig()

    with StreamChatClient(config) as client:
        # First, get the list of channels to find a channel ID
        print("\nFetching available channels...")
        channels_response = client.get_channels(message_limit=5)
        channels = channels_response.get('channels', [])

        if not channels:
            print("No channels found.")
            return

        # Get the first channel's ID
        first_channel = channels[0].get('channel', {})
        channel_id = first_channel.get('cid')
        channel_name = first_channel.get('name', 'Unknown')

        print(f"\nSelected channel: {channel_name}")
        print(f"Channel ID: {channel_id}")

        # Create paginator for this channel
        paginator = ChannelPaginator(client, channel_id)

        # Example 1a: Fetch first page
        print("\n--- Fetching first page (30 messages) ---")
        response = paginator.fetch_page(page_size=30)
        messages = response.get('channels', [{}])[0].get('messages', [])
        print(f"Fetched {len(messages)} messages")
        print(f"Total fetched so far: {paginator.state.total_fetched}")

        # Example 1b: Fetch all messages (up to 100)
        print("\n--- Fetching up to 100 messages total ---")
        paginator.reset()  # Reset state
        all_messages = paginator.fetch_all(page_size=30, max_messages=100)
        print(f"Fetched {len(all_messages)} messages total")

        # Display first few messages
        print("\nFirst 3 messages:")
        for idx, msg in enumerate(all_messages[:3], 1):
            user = msg.get('user', {})
            text = msg.get('text', '')[:50]
            print(f"  {idx}. {user.get('name', 'Unknown')}: {text}...")

        # Example 1c: Use iterator for memory efficiency
        print("\n--- Using iterator (fetch messages one at a time) ---")
        paginator.reset()
        count = 0
        for message in paginator.fetch_iterator(page_size=30, max_messages=10):
            count += 1
            user = message.get('user', {})
            print(f"  Message {count}: {user.get('name', 'Unknown')}")

        # Get channel info
        channel_info = paginator.get_channel_info()
        print(f"\nChannel info: {channel_info.get('name')} - {channel_info.get('member_count')} members")


def example_multi_channel_pagination():
    """Example: Paginate through multiple channels."""
    print("\n" + "=" * 80)
    print("Example 2: Multi-Channel Pagination")
    print("=" * 80)

    load_dotenv()
    config = StreamAPIConfig()

    with StreamChatClient(config) as client:
        # Get list of channels
        print("\nFetching available channels...")
        channels_response = client.get_channels(message_limit=5)
        channels = channels_response.get('channels', [])

        # Extract channel IDs
        channel_ids = [
            ch.get('channel', {}).get('cid')
            for ch in channels[:3]  # First 3 channels
            if ch.get('channel', {}).get('cid')
        ]

        if not channel_ids:
            print("No channels found.")
            return

        print(f"\nFetching from {len(channel_ids)} channels...")

        # Create multi-channel paginator
        multi_paginator = MultiChannelPaginator(client)

        # Fetch 50 messages from each channel
        results = multi_paginator.fetch_from_all_channels(
            channel_ids=channel_ids,
            page_size=30,
            max_messages_per_channel=50
        )

        # Display results
        for channel_id, messages in results.items():
            paginator = multi_paginator.get_paginator(channel_id)
            channel_info = paginator.get_channel_info()
            channel_name = channel_info.get('name', 'Unknown') if channel_info else 'Unknown'
            print(f"\n{channel_name}: {len(messages)} messages fetched")


def example_search_with_pagination():
    """Example: Search across paginated messages."""
    print("\n" + "=" * 80)
    print("Example 3: Search with Pagination")
    print("=" * 80)

    load_dotenv()
    config = StreamAPIConfig()

    with StreamChatClient(config) as client:
        # Get channels
        print("\nFetching channels...")
        channels_response = client.get_channels(message_limit=5)
        channels = channels_response.get('channels', [])

        if not channels:
            print("No channels found.")
            return

        # Get first channel
        first_channel = channels[0].get('channel', {})
        channel_id = first_channel.get('cid')
        channel_name = first_channel.get('name', 'Unknown')

        print(f"\nFetching more messages from: {channel_name}")

        # Paginate to get more messages
        paginator = ChannelPaginator(client, channel_id)
        all_messages = paginator.fetch_all(page_size=50, max_messages=200)

        print(f"Fetched {len(all_messages)} messages")

        # Build a mock channels_data structure for the searcher
        channels_data = {
            'channels': [{
                'channel': first_channel,
                'messages': all_messages
            }]
        }

        # Now search through the paginated messages
        searcher = MessageSearcher(channels_data)
        print(f"\nSearching for 'NVIDIA' in {len(all_messages)} messages...")
        results = searcher.search('NVIDIA')

        print(f"Found {len(results)} results")
        searcher.print_search_results(results, max_display=3)


def main():
    """Run all examples."""
    print("\nPagination Examples\n")

    try:
        example_single_channel_pagination()
        example_multi_channel_pagination()
        example_search_with_pagination()

        print("\n" + "=" * 80)
        print("All examples completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
