# Patreon Channel Message Search

A tool to search through Patreon community channel messages using the Stream.io API.

## Features

- **Interactive CLI Browser** - Full-featured command-line interface for browsing channels
- Search by keyword in message text
- Search by username
- Case-sensitive and case-insensitive search
- Pagination support for large result sets
- Fetch messages from specific channels with pagination
- Configurable display options (fields, text length, results per page)
- Channel navigation and exploration
- **Comprehensive Logging** - All operations logged to `logs/patreon_scrape.log` for debugging

## Project Structure

```
patreon-scrape/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── api_config.py          # API configuration and credentials
│   ├── clients/
│   │   ├── __init__.py
│   │   └── stream_client.py       # Stream.io API client
│   └── core/
│       ├── __init__.py
│       ├── search.py              # Search functionality
│       ├── pagination.py          # Pagination wrappers
│       └── interactive_cli.py     # Interactive CLI browser
├── examples/
│   ├── search_cli.py              # Command-line search interface
│   ├── search_example.py          # Search usage examples
│   └── pagination_example.py      # Pagination usage examples
├── browse.py                      # Interactive browser launcher
├── main.py                        # Simple demo script
├── .env                           # Configuration (credentials)
├── .env.example                   # Configuration template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your credentials in `.env`:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## Usage

### Interactive Browser (Recommended)

Launch the full-featured interactive CLI:
```bash
python browse.py
```

This provides a command-line interface where you can:
- Browse and select channels
- View messages with pagination
- Search with various options
- Fetch more messages on demand
- Configure display settings
- And much more!

**Example Session:**
```
> list                          # List all channels
> select 1                      # Select first channel
> show                          # Show channel details
> messages 20                   # Show 20 messages
> search "NVIDIA"               # Search for keyword
> search --user Chris           # Search by username
> fetch 100                     # Fetch 100 more messages
> set results_per_page 20       # Configure display
> help                          # Show all commands
```

### Quick Start

Run the demo script to fetch channels:
```bash
python main.py
```

### Command-Line Search

Direct command-line search without interactive mode:

```bash
# Search for a keyword
python examples/search_cli.py --keyword "NVIDIA"

# Search for messages from a specific user
python examples/search_cli.py --user "Chris"

# Case-sensitive search
python examples/search_cli.py --keyword "VRT" --case-sensitive

# Paginated results
python examples/search_cli.py --keyword "investing" --page-size 10 --page 1

# Show full message text (no truncation)
python examples/search_cli.py --keyword "options" --full-text
```

### Programmatic Usage

```python
from dotenv import load_dotenv
from src.config import StreamAPIConfig
from src.clients import StreamChatClient
from src.core import MessageSearcher

# Load configuration
load_dotenv()
config = StreamAPIConfig()

# Fetch channels
with StreamChatClient(config) as client:
    channels_data = client.get_channels()

# Create searcher
searcher = MessageSearcher(channels_data)

# Search for keyword
results = searcher.search("NVIDIA")

# Search by user
results = searcher.search_by_user("Chris")

# Paginated search
results = searcher.search("investing", page_size=10, page=1)

# Print results
searcher.print_search_results(results)
```

### Pagination

Fetch messages from a single channel in pages:

```python
from src.core import ChannelPaginator

paginator = ChannelPaginator(client, channel_id)

# Fetch one page at a time
response = paginator.fetch_page(page_size=50)

# Fetch all messages (or up to a limit)
all_messages = paginator.fetch_all(page_size=50, max_messages=500)

# Use iterator for memory efficiency
for message in paginator.fetch_iterator(page_size=50, max_messages=100):
    print(message['text'])
```

Fetch from multiple channels:

```python
from src.core import MultiChannelPaginator

multi_paginator = MultiChannelPaginator(client)

# Fetch from specific channels
results = multi_paginator.fetch_from_all_channels(
    channel_ids=['channel_id_1', 'channel_id_2'],
    page_size=50,
    max_messages_per_channel=200
)
```

## Architecture

### Modules

**`src/config`** - Configuration management
- `StreamAPIConfig` - Loads credentials from environment variables

**`src/clients`** - API clients
- `StreamChatClient` - Handles API communication with Stream.io

**`src/core`** - Core functionality
- `MessageSearcher` - Search through messages
- `SearchResult` - Search result data structure
- `ChannelPaginator` - Single channel pagination
- `MultiChannelPaginator` - Multi-channel pagination
- `PaginationState` - Pagination state tracking

**`examples`** - Example scripts and CLI tools
- `search_cli.py` - Command-line search interface
- `search_example.py` - Search usage examples
- `pagination_example.py` - Pagination usage examples

## Key Classes

**`StreamAPIConfig`** - Configuration management
- Loads credentials from environment variables
- Supports both `.env` file and system environment

**`StreamChatClient`** - API client
- Handles authentication and headers
- Fetches channel data with pagination support
- Context manager for proper resource cleanup

**`MessageSearcher`** - Search functionality
- Searches message text and usernames
- Supports case-sensitive/insensitive matching
- Pagination support
- Result formatting and display

**`SearchResult`** - Search result data structure
- Message content and metadata
- User information
- Channel information
- Human-readable date formatting

**`ChannelPaginator`** - Single channel pagination
- Fetch messages in pages
- Automatic state tracking
- Iterator support for memory efficiency

**`MultiChannelPaginator`** - Multi-channel pagination
- Manage multiple channel paginators
- Fetch from multiple channels
- Aggregate results

## Examples

See the `examples/` directory for detailed usage examples:

- **search_example.py** - Demonstrates various search scenarios
- **pagination_example.py** - Shows how to paginate through channel messages
- **search_cli.py** - Full-featured command-line interface

## Future Enhancements

- Date range filtering
- Regular expression support
- Export results to CSV/JSON
- Multi-keyword search (AND/OR logic)
- Search result highlighting
- Message threading support

## License

This is a personal project for educational purposes.
