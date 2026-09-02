# Example Usage and Test Cases

## Test Scenario 1: Default Summary (📝)
**Setup:** User hasn't configured preferences
**Action:** User reacts with 📝 emoji to a thread message
**Expected:** 5-point bullet-point summary in English

## Test Scenario 2: Custom Format (Numbered)
**Setup:** User runs `/summary-set format numbered`
**Action:** User reacts with 📝 emoji
**Expected:** 5-point numbered summary instead of bullets

## Test Scenario 3: Different Language
**Setup:** 
- `/summary-set language tr` (Turkish)
- `/summary-set length brief` (3 points)
**Action:** User reacts with 📝 emoji to a thread
**Expected:** 3-point Turkish summary

## Test Scenario 4: Detailed Summary (📰)
**Setup:** Default settings
**Action:** User reacts with 📰 emoji (newspaper)
**Expected:** 10-point detailed summary

## Test Scenario 5: Brief Summary (📌)
**Setup:** Default settings
**Action:** User reacts with 📌 emoji (pushpin)
**Expected:** 3-point brief summary

## Test Scenario 6: JSON Format
**Setup:** `/summary-set format json`
**Action:** User reacts with 📝 emoji
**Expected:** JSON response with structured point and explanation fields

## Test Scenario 7: Bot Filtering
**Setup:** `/summary-set filter-bots true`
**Action:** Thread has both user and bot messages, react with 📝
**Expected:** Summary excludes bot messages

## Test Scenario 8: System Message Filtering
**Setup:** `/summary-set filter-system true`
**Action:** Thread has system messages (channel_join, etc.), react with 📝
**Expected:** Summary excludes system messages

## Test Scenario 9: View Settings
**Setup:** User has customized multiple settings
**Action:** User runs `/summary-settings`
**Expected:** Shows all current settings

## Test Scenario 10: Error Handling
**Setup:** Empty thread (all messages filtered out)
**Action:** User reacts with 📝 emoji
**Expected:** Bot posts message "No messages found to summarize after filtering."

## Sample User Preferences File

```json
{
  "U123456789": {
    "default_format": "numbered",
    "default_length": "detailed",
    "default_language": "tr",
    "filter_bots": true,
    "filter_system": true
  },
  "U987654321": {
    "default_format": "json",
    "default_length": "brief",
    "default_language": "en",
    "filter_bots": false,
    "filter_system": true
  }
}
```

## Running Tests

1. Set up your Slack workspace and bot tokens
2. Deploy the bot
3. Run through each scenario manually
4. Verify `user_preferences.json` is created and updated
5. Check logs for any errors
