# Slack Thread Summarizer - Configuration Guide

## Features

### 1. Summary Formats
Users can choose how they want summaries formatted:
- **Bullets** (default): `• Point 1\n• Point 2\n...`
- **Numbered**: `1. Point 1\n2. Point 2\n...`
- **Paragraphs**: Full paragraph summaries
- **JSON**: Structured format with "point" and "explanation" fields

### 2. Summary Lengths
Summaries can be customized by length:
- **Brief**: 3 key points
- **Normal**: 5 key points (default)
- **Detailed**: 10 key points

### 3. Multi-Language Support
Summaries can be generated in multiple languages:
- **en**: English
- **tr**: Turkish
- **es**: Spanish
- **fr**: French
- **de**: German

### 4. Reaction Triggers
Different reactions trigger different default behaviors:
- **📝 memo**: Normal 5-point summary
- **📰 newspaper**: Detailed 10-point summary
- **📌 pushpin**: Brief 3-point summary

### 5. Message Filtering
Users can exclude certain message types:
- **Filter bots**: Skip messages from bot users
- **Filter system messages**: Skip channel join/leave events

### 6. User Preferences
Each user's preferences are stored in `user_preferences.json`:
```json
{
  "U123456789": {
    "default_format": "bullets",
    "default_length": "normal",
    "default_language": "en",
    "filter_bots": true,
    "filter_system": true
  }
}
```

## Commands

### `/summary-settings`
View your current summary preferences.

```
/summary-settings
```

Output:
```
Your Summary Settings:
• Format: bullets (bullets, numbered, paragraphs, json)
• Length: normal (brief, normal, detailed)
• Language: en (en, tr, es, fr, de)
• Filter bots: true
• Filter system messages: true
```

### `/summary-set <setting> <value>`
Update a specific setting.

Examples:
```
/summary-set format json
/summary-set length detailed
/summary-set language tr
/summary-set filter-bots false
/summary-set filter-system false
```

## How to Use

1. **React to a message** in a thread with one of the configured emojis:
   - 📝 for standard summary
   - 📰 for detailed summary
   - 📌 for brief summary

2. **Bot processes the thread** using your saved preferences

3. **Summary is posted** as a reply in the same thread

4. **Customize settings** anytime with `/summary-set` commands

## Environment Variables

Required in `.env` file:
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
CEREBRAS_API_KEY=csk-...
```

## Slack App Permissions

Ensure your Slack app has these permissions:
- `reactions:read` - Read reactions
- `chat:write` - Post messages
- `channels:history` - Read channel messages
- `commands` - Use slash commands

## Error Handling

- If no messages remain after filtering, the bot notifies the user
- If Cerebras API fails, the bot posts an error message to the thread
- All errors are logged for debugging

## File Storage

- `user_preferences.json`: Stores user configuration
- Created automatically on first run
- In production, consider using a database instead
