"""
Extract Stream.io configuration from a cURL command.

SIMPLEST METHOD: Just copy a network request as cURL!

1. Login to Patreon
2. Go to chat page
3. Open DevTools > Network tab
4. Search for "channels"
5. Right-click the request > Copy > Copy as cURL (bash)
6. Paste the entire cURL command into CURL_COMMAND below
7. Run this script
"""

import re
from typing import Optional, Dict


def extract_config_from_curl(curl_command: str) -> Optional[Dict[str, str]]:
    """
    Extract Stream.io configuration from a cURL command.

    The cURL command contains:
    - URL with user_id, connection_id, and api_key as query parameters
    - Authorization header with the JWT token

    Args:
        curl_command: Full cURL command copied from browser DevTools

    Returns:
        Dictionary with config values, or None if extraction failed
    """
    config = {}

    # Extract from URL query parameters
    # Pattern: ?user_id=123&connection_id=abc&api_key=xyz
    # Remove any trailing quotes or apostrophes
    user_id_match = re.search(r'[?&]user_id=([^&\s\'\"]+)', curl_command)
    connection_id_match = re.search(r'[?&]connection_id=([^&\s\'\"]+)', curl_command)
    api_key_match = re.search(r'[?&]api_key=([^&\s\'\"]+)', curl_command)

    if user_id_match:
        config['user_id'] = user_id_match.group(1).strip('\'"')
        print(f"  [OK] Found user_id: {config['user_id']}")
    else:
        print("  [X] user_id not found in URL")
        return None

    if connection_id_match:
        config['connection_id'] = connection_id_match.group(1).strip('\'"')
        print(f"  [OK] Found connection_id: {config['connection_id'][:20]}...")
    else:
        print("  [!] connection_id not found (optional, can be empty)")
        config['connection_id'] = ""

    if api_key_match:
        config['api_key'] = api_key_match.group(1).strip('\'"')
        print(f"  [OK] Found api_key: {config['api_key']}")
    else:
        print("  [!] api_key not found, using fallback: ezwwjrd7jqah")
        config['api_key'] = "ezwwjrd7jqah"

    # Extract authorization token from header
    # Pattern: -H 'authorization: eyJhbGci...'
    auth_match = re.search(r"-H ['\"]authorization:\s*([^'\"]+)['\"]", curl_command, re.IGNORECASE)
    if auth_match:
        config['auth_token'] = auth_match.group(1).strip()
        print(f"  [OK] Found auth_token: {config['auth_token'][:50]}...")
    else:
        print("  [X] authorization header not found")
        return None

    return config


def main():
    """Main entry point."""
    print()
    print("=" * 80)
    print("EXTRACT STREAM.IO CONFIG FROM cURL")
    print("=" * 80)
    print()

    # Paste your cURL command here (between the triple quotes)
    CURL_COMMAND = """"""

    if not CURL_COMMAND or len(CURL_COMMAND.strip()) < 50:
        print("[!] No cURL command provided.")
        print()
        print("INSTRUCTIONS:")
        print("  1. Login to Patreon and go to the chat page")
        print("  2. Open DevTools (F12) > Network tab")
        print("  3. In the filter box, type: channels")
        print("  4. You should see exactly ONE request to chat.stream-io-api.com")
        print("  5. Right-click on that request")
        print("  6. Select: Copy > Copy as cURL (bash)")
        print("  7. Paste the ENTIRE command into CURL_COMMAND = \"\"\"\"\"\" in this file")
        print("     (between the triple quotes on line 62)")
        print("  8. Run this script again: python extract_from_curl.py")
        print()
        print("The cURL command will look like:")
        print("  curl 'https://chat.stream-io-api.com/channels?user_id=...&api_key=...' \\")
        print("    -H 'authorization: eyJhbGci...' \\")
        print("    -H 'content-type: application/json' \\")
        print("    ...")
        print()
        return

    print("Extracting configuration from cURL command...")
    print()

    config = extract_config_from_curl(CURL_COMMAND)

    if not config:
        print()
        print("[X] Failed to extract configuration. Check the cURL command.")
        return

    print()
    print("=" * 80)
    print("RESULT - COPY THIS TO YOUR .env FILE")
    print("=" * 80)
    print()

    # Output in .env format
    print(f"STREAM_API_KEY={config['api_key']}")
    print(f"STREAM_USER_ID={config['user_id']}")
    print(f"STREAM_AUTH_TOKEN={config['auth_token']}")
    print(f"STREAM_CONNECTION_ID={config['connection_id']}")
    print()
    print("# This config was extracted from your browser's Network tab")
    print("# If the auth token expires, just repeat the process to get a new one")
    print()
    print("=" * 80)
    print("[OK] Complete! Copy the lines above to your .env file and run: python main.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
