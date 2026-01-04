# Patreon Chat Scraper

A simple tool to scrape and search through Patreon community chat messages using the Stream.io API.

## Features

- Search by keyword in message text
- Search by username
- Case-sensitive and case-insensitive search
- Pagination support for large result sets
- Fetch messages from specific channels
- Interactive CLI for browsing channels and messages

## Quick Start

**Total setup time: ~2 minutes**

See **[QUICK_START.md](QUICK_START.md)** for the complete step-by-step guide.

### Summary

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get your Stream.io configuration (2 minutes):
   - Login to Patreon and go to the chat page
   - Open DevTools (F12) → Network tab
   - Filter for "channels"
   - Right-click the request → Copy as cURL (bash)
   - Paste into `extract_from_curl.py` (line 85)
   - Run: `python extract_from_curl.py`
   - Copy the output to `.env` file

3. Run the scraper:
   ```bash
   python main.py
   ```

## Usage

### Basic Search

The main script provides an interactive search interface:

```bash
python main.py
```

Follow the prompts to:
- Search by keyword
- Search by username
- Browse channels
- View messages with pagination

### Configuration

All configuration is stored in the `.env` file:

```bash
STREAM_API_KEY=ezwwjrd7jqah
STREAM_USER_ID=your_user_id
STREAM_AUTH_TOKEN=your_auth_token
STREAM_CONNECTION_ID=your_connection_id
```

Use `extract_from_curl.py` to automatically extract these values from a browser network request.

## Project Structure

```
patreon-scrape/
├── src/
│   ├── config/          # API configuration
│   ├── clients/         # Stream.io API client
│   └── core/            # Search and pagination logic
├── queries/             # Cached channel/message data
├── main.py              # Main entry point
├── extract_from_curl.py # Setup tool (extract config from cURL)
├── QUICK_START.md       # 2-minute setup guide
├── .env                 # Your configuration
├── .env.example         # Configuration template
└── requirements.txt     # Python dependencies
```

## How It Works

1. **Configuration Extraction**: The `extract_from_curl.py` script extracts your Stream.io API credentials from a browser network request
2. **API Client**: Connects to Stream.io's chat API using your credentials
3. **Data Fetching**: Retrieves channel and message data with pagination support
4. **Search**: Provides flexible search across all messages

## Troubleshooting

### Token Expired

If you get authentication errors, your token may have expired (~30 days). Simply repeat the setup process to get a fresh token:

```bash
python extract_from_curl.py
```

Copy the new values to your `.env` file.

### No Channels Found

Make sure:
- You copied the cURL command from the correct network request (filter for "channels")
- You're logged into Patreon in your browser
- The chat page fully loaded before copying the request

### Import Errors

Make sure you've installed all dependencies:

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.7+
- `requests` library
- `python-dotenv` library

## License

This is a personal project for educational purposes.
