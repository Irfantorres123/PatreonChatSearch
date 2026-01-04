"""
Command-line interface for searching channel messages.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
from dotenv import load_dotenv
from src.config import StreamAPIConfig
from src.clients import StreamChatClient
from src.core import MessageSearcher, search_channels_interactive


def main():
    """CLI entry point for channel message search."""
    parser = argparse.ArgumentParser(
        description="Search through Patreon channel messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python search_cli.py

  # Search for a keyword
  python search_cli.py --keyword "NVIDIA"

  # Search for a user
  python search_cli.py --user "Chris"

  # Case-sensitive search
  python search_cli.py --keyword "VRT" --case-sensitive

  # Paginated results
  python search_cli.py --keyword "investing" --page-size 10 --page 2

  # Search only in message text
  python search_cli.py --keyword "trading" --no-search-users

  # Show full message text
  python search_cli.py --keyword "options" --full-text
        """
    )

    parser.add_argument(
        '--keyword', '-k',
        type=str,
        help='Keyword to search for in messages and usernames'
    )

    parser.add_argument(
        '--user', '-u',
        type=str,
        help='Search for messages from a specific user'
    )

    parser.add_argument(
        '--case-sensitive', '-c',
        action='store_true',
        help='Perform case-sensitive search'
    )

    parser.add_argument(
        '--no-search-text',
        action='store_true',
        help='Do not search in message text'
    )

    parser.add_argument(
        '--no-search-users',
        action='store_true',
        help='Do not search in usernames'
    )

    parser.add_argument(
        '--page-size', '-s',
        type=int,
        help='Number of results per page'
    )

    parser.add_argument(
        '--page', '-p',
        type=int,
        default=1,
        help='Page number (default: 1)'
    )

    parser.add_argument(
        '--max-display', '-m',
        type=int,
        help='Maximum number of results to display'
    )

    parser.add_argument(
        '--full-text', '-f',
        action='store_true',
        help='Show full message text (do not truncate)'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive search mode'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Fetch channel data
    print("Fetching channels from Stream.io API...")
    config = StreamAPIConfig()

    with StreamChatClient(config) as client:
        channels_data = client.get_channels()

    print(f"✓ Fetched {len(channels_data.get('channels', []))} channel(s)\n")

    # Initialize searcher
    searcher = MessageSearcher(channels_data)

    # Interactive mode
    if args.interactive or (not args.keyword and not args.user):
        search_channels_interactive(channels_data)
        return

    # Perform search based on arguments
    if args.user:
        # Search by user
        results = searcher.search_by_user(
            username=args.user,
            case_sensitive=args.case_sensitive
        )
    elif args.keyword:
        # Search by keyword
        results = searcher.search(
            keyword=args.keyword,
            search_text=not args.no_search_text,
            search_usernames=not args.no_search_users,
            case_sensitive=args.case_sensitive,
            page_size=args.page_size,
            page=args.page
        )
    else:
        parser.print_help()
        return

    # Display results
    searcher.print_search_results(
        results,
        max_display=args.max_display,
        show_full_text=args.full_text
    )

    # Show pagination info
    if args.page_size:
        total_pages = (len(results) + args.page_size - 1) // args.page_size
        print(f"\nPage {args.page} of {total_pages}")


if __name__ == "__main__":
    main()
