"""
Main entry point for the Patreon Channel Search tool.
This is a simple demonstration of fetching and displaying channels.
"""

from dotenv import load_dotenv
from src.config import StreamAPIConfig
from src.clients import StreamChatClient


def main():
    """Main execution function."""
    # Load environment variables from .env file
    load_dotenv()

    # Configuration will automatically load from environment variables
    config = StreamAPIConfig()

    # Use context manager to ensure proper cleanup
    with StreamChatClient(config) as client:
        try:
            print("Fetching channels...")
            channels_data = client.get_channels()

            # Pretty print the response
            print("\nResponse received successfully!")
            print(f"Number of channels: {len(channels_data.get('channels', []))}")

            # Display channel details
            for idx, channel_wrapper in enumerate(channels_data.get('channels', []), 1):
                # The actual channel data is nested inside a 'channel' key
                channel = channel_wrapper.get('channel', {})

                print(f"\nChannel {idx}:")
                print(f"  Name: {channel.get('name', 'N/A')}")
                print(f"  Type: {channel.get('type')}")
                print(f"  ID: {channel.get('id')}")
                print(f"  CID: {channel.get('cid')}")
                print(f"  Member count: {channel.get('member_count', 'N/A')}")
                print(f"  Campaign ID: {channel.get('campaign_id', 'N/A')}")
                if 'last_message_at' in channel:
                    print(f"  Last message: {channel['last_message_at']}")
                if 'emoji' in channel:
                    print(f"  Emoji: {channel['emoji']}")

        except Exception as e:
            print(f"Failed to fetch channels: {e}")


if __name__ == "__main__":
    main()
