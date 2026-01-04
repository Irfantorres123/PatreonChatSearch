# Quick Start Guide (2 Minutes!)

Get your Patreon chat scraper running in **2 simple steps**.

## Step 1: Copy Network Request (1 minute)

1. **Login** to Patreon in your browser
2. **Go to chat page** (https://www.patreon.com/messages)
3. Press **F12** (opens DevTools)
4. Click **Network** tab
5. In the filter box, type: `channels`
6. You'll see ONE request to `chat.stream-io-api.com`
7. **Right-click** on it → **Copy** → **Copy as cURL (bash)**

You should now have something like this copied:
```bash
curl 'https://chat.stream-io-api.com/channels?user_id=...&api_key=...' \
  -H 'authorization: eyJhbGci...' \
  ...
```

## Step 2: Extract & Run (1 minute)

1. Open `extract_from_curl.py` in Notepad
2. Find line 84: `CURL_COMMAND = """"""`
3. Paste your cURL command between the triple quotes
4. Save and run:
   ```bash
   python extract_from_curl.py
   ```
5. **Copy the output** (between the lines)
6. **Paste into `.env`** file
7. **Run the scraper**:
   ```bash
   python main.py
   ```

## That's It!

Total time: **~2 minutes**

## What You'll See

When you run `extract_from_curl.py`, you'll get:

```
================================================================================
RESULT - COPY THIS TO YOUR .env FILE
================================================================================

STREAM_API_KEY=ezwwjrd7jqah
STREAM_USER_ID=197857143
STREAM_AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
STREAM_CONNECTION_ID=694469dc-0a1d-26b3-0200-0000009c289e

# This config was extracted from your browser's Network tab
# If the auth token expires, just repeat the process to get a new one

================================================================================
[OK] Complete! Copy the lines above to your .env file and run: python main.py
================================================================================
```

Just copy everything from `STREAM_API_KEY` to `STREAM_CONNECTION_ID` and paste into `.env`!

## Visual Guide

```
Browser Network Tab → Copy as cURL → extract_from_curl.py → .env → main.py
     (1 click)           (Ctrl+C)        (paste & run)      (paste)  (run!)
```

## Troubleshooting

### "channels request not found"

Make sure:
- You're on the chat/messages page (not just logged in)
- The page has fully loaded
- You're looking in the **Network** tab, not Console

### "No cURL command provided"

Make sure you pasted the command between the `""""""` triple quotes on line 84.

### Token Expired?

Just repeat Step 1-2. Takes 2 minutes to get a fresh token.

---

**This is the simplest method!** All config values are in one network request.
