import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# Load .env file
load_dotenv()

# Initialize clients
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
cerebras_client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

# User preferences storage (in production, use a database)
USER_PREFERENCES_FILE = "user_preferences.json"


def load_user_preferences():
    """Load user preferences from JSON file."""
    if os.path.exists(USER_PREFERENCES_FILE):
        with open(USER_PREFERENCES_FILE, "r") as f:
            return json.load(f)
    return {}


def save_user_preferences(preferences):
    """Save user preferences to JSON file."""
    with open(USER_PREFERENCES_FILE, "w") as f:
        json.dump(preferences, f, indent=2)


def get_user_preference(user_id, key, default):
    """Get a specific user preference."""
    preferences = load_user_preferences()
    return preferences.get(user_id, {}).get(key, default)


def set_user_preference(user_id, key, value):
    """Set a user preference."""
    preferences = load_user_preferences()
    if user_id not in preferences:
        preferences[user_id] = {}
    preferences[user_id][key] = value
    save_user_preferences(preferences)


# Reaction to action mapping
REACTION_CONFIG = {
    "memo": {"action": "summary", "length": "normal", "description": "5-point summary"},
    "newspaper": {"action": "summary", "length": "detailed", "description": "10-point detailed summary"},
    "pushpin": {"action": "summary", "length": "brief", "description": "3-point brief summary"},
    "mag": {"action": "summary", "length": "normal", "description": "summary with analysis"},
}


def filter_messages(messages, user_id):
    """Filter messages based on user preferences."""
    filter_bots = get_user_preference(user_id, "filter_bots", True)
    filter_system = get_user_preference(user_id, "filter_system", True)
    
    filtered = []
    for msg in messages:
        # Skip bot messages if filter enabled
        if filter_bots and msg.get("bot_id"):
            continue
        # Skip system messages if filter enabled
        if filter_system and msg.get("subtype") in ["channel_join", "channel_leave", "bot_add", "bot_remove"]:
            continue
        # Skip empty messages
        if not msg.get("text"):
            continue
        filtered.append(msg)
    
    return filtered


def format_thread_text(messages):
    """Convert thread messages to readable text."""
    thread_text = ""
    for msg in messages:
        user = msg.get("user", "Unknown User")
        text = msg.get("text", "[Empty message or file]")
        thread_text += f"- {user}: {text}\n"
    return thread_text


def build_prompt(thread_text, summary_length, format_style, language, user_id):
    """Build the prompt for Cerebras based on user preferences."""
    length_config = {
        "brief": {"count": 3, "descriptor": "3-point"},
        "normal": {"count": 5, "descriptor": "5-point"},
        "detailed": {"count": 10, "descriptor": "10-point"},
    }
    
    config = length_config.get(summary_length, length_config["normal"])
    count = config["count"]
    
    format_instructions = {
        "bullets": f"Format as bullet points (exactly {count} points)",
        "numbered": f"Format as a numbered list (exactly {count} items)",
        "paragraphs": f"Format as {count} separate paragraphs",
        "json": f'Format as JSON array with {count} objects, each with "point" and "explanation" fields',
    }
    
    format_instruction = format_instructions.get(format_style, format_instructions["bullets"])
    
    lang_prefix = {
        "en": "English",
        "tr": "Turkish",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
    }
    
    language_name = lang_prefix.get(language, language)
    
    prompt = f"""Summarize the following Slack thread into exactly {count} key points.
{format_instruction}
Write the summary in {language_name}.
Keep each point clear, concise, and professional. Do not include introduction or conclusion text, only the {count} points.

Thread Content:
{thread_text}"""
    
    return prompt


def post_summary(client, channel_id, root_ts, summary, user_id, logger):
    """Post the summary to Slack."""
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=f"📝 *Thread Summary:*\n{summary}",
            thread_ts=root_ts
        )
        logger.info("Summary posted to Slack successfully!")
    except Exception as e:
        logger.error(f"Error posting summary: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text="Sorry, an error occurred while posting the summary. Please try again later.",
            thread_ts=root_ts
        )


@app.event("reaction_added")
def handle_reaction(event, client, logger):
    """Handle reaction events and summarize threads."""
    reaction = event["reaction"]
    
    # Check if this reaction is configured
    if reaction not in REACTION_CONFIG:
        return
    
    user_id = event["user"]
    channel_id = event["item"]["channel"]
    message_ts = event["item"]["ts"]
    
    # Get the root message ts (handles replies in threads)
    root_ts = event["item"].get("thread_ts", message_ts)
    
    config = REACTION_CONFIG[reaction]
    length = get_user_preference(user_id, "default_length", config.get("length", "normal"))
    format_style = get_user_preference(user_id, "default_format", "bullets")
    language = get_user_preference(user_id, "default_language", "en")
    
    logger.info(f"📝 Reaction '{reaction}' captured! Channel: {channel_id}, User: {user_id}")
    
    try:
        # 1. Fetch thread messages
        result = client.conversations_replies(channel=channel_id, ts=root_ts)
        messages = result["messages"]
        
        # 2. Filter messages based on user preferences
        filtered_messages = filter_messages(messages, user_id)
        
        if not filtered_messages:
            client.chat_postMessage(
                channel=channel_id,
                text="No messages found to summarize after filtering.",
                thread_ts=root_ts
            )
            return
        
        # 3. Convert messages to text
        thread_text = format_thread_text(filtered_messages)
        
        # 4. Build prompt
        prompt = build_prompt(thread_text, length, format_style, language, user_id)
        
        logger.info("Sending summarization request to Cerebras...")
        
        # 5. Send to Cerebras
        response = cerebras_client.chat.completions.create(
            model="llama3.1-70b",
            messages=[
                {"role": "system", "content": "You are a Slack thread summarization assistant. Provide only the requested format with no additional commentary."},
                {"role": "user", "content": prompt}
            ],
        )
        
        summary = response.choices[0].message.content
        logger.info("Summary created successfully!")
        
        # 6. Post summary to Slack
        post_summary(client, channel_id, root_ts, summary, user_id, logger)
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text="Sorry, an error occurred while creating the summary. Please try again later.",
            thread_ts=root_ts
        )


@app.command("/summary-settings")
def handle_summary_settings(ack, body, client, logger):
    """Handle /summary-settings command to configure user preferences."""
    ack()
    
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    
    preferences = load_user_preferences().get(user_id, {})
    
    current_format = preferences.get("default_format", "bullets")
    current_length = preferences.get("default_length", "normal")
    current_language = preferences.get("default_language", "en")
    current_filter_bots = preferences.get("filter_bots", True)
    current_filter_system = preferences.get("filter_system", True)
    
    settings_text = f"""
*Your Summary Settings:*
• Format: `{current_format}` (bullets, numbered, paragraphs, json)
• Length: `{current_length}` (brief, normal, detailed)
• Language: `{current_language}` (en, tr, es, fr, de)
• Filter bots: `{current_filter_bots}`
• Filter system messages: `{current_filter_system}`

Use `/summary-set format <bullets|numbered|paragraphs|json>` to change format
Use `/summary-set length <brief|normal|detailed>` to change length
Use `/summary-set language <en|tr|es|fr|de>` to change language
Use `/summary-set filter-bots <true|false>` to toggle bot filtering
Use `/summary-set filter-system <true|false>` to toggle system message filtering

*Reaction Guide:*
• 📝 memo: Normal 5-point summary
• 📰 newspaper: Detailed 10-point summary
• 📌 pushpin: Brief 3-point summary
"""
    
    client.chat_postMessage(
        channel=channel_id,
        text=settings_text
    )
    
    logger.info(f"Settings displayed for user {user_id}")


@app.command("/summary-set")
def handle_summary_set(ack, body, client, logger):
    """Handle /summary-set command to update user preferences."""
    ack()
    
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    text = body.get("text", "").strip().split(" ", 1)
    
    if len(text) < 2:
        client.chat_postMessage(
            channel=channel_id,
            text="Usage: `/summary-set <setting> <value>`\nExample: `/summary-set format numbered`"
        )
        return
    
    setting, value = text[0], text[1]
    
    valid_formats = ["bullets", "numbered", "paragraphs", "json"]
    valid_lengths = ["brief", "normal", "detailed"]
    valid_languages = ["en", "tr", "es", "fr", "de"]
    
    if setting == "format":
        if value in valid_formats:
            set_user_preference(user_id, "default_format", value)
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Format updated to `{value}`"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Invalid format. Choose from: {', '.join(valid_formats)}"
            )
    
    elif setting == "length":
        if value in valid_lengths:
            set_user_preference(user_id, "default_length", value)
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Length updated to `{value}`"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Invalid length. Choose from: {', '.join(valid_lengths)}"
            )
    
    elif setting == "language":
        if value in valid_languages:
            set_user_preference(user_id, "default_language", value)
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Language updated to `{value}`"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Invalid language. Choose from: {', '.join(valid_languages)}"
            )
    
    elif setting == "filter-bots":
        if value.lower() in ["true", "false"]:
            bool_value = value.lower() == "true"
            set_user_preference(user_id, "filter_bots", bool_value)
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Bot filtering updated to `{bool_value}`"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Invalid value. Use `true` or `false`"
            )
    
    elif setting == "filter-system":
        if value.lower() in ["true", "false"]:
            bool_value = value.lower() == "true"
            set_user_preference(user_id, "filter_system", bool_value)
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ System message filtering updated to `{bool_value}`"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Invalid value. Use `true` or `false`"
            )
    
    else:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Unknown setting. Choose from: format, length, language, filter-bots, filter-system"
        )
    
    logger.info(f"Setting '{setting}' updated for user {user_id}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    app.logger.info("Bot starting... Ready!")
    handler.start()
