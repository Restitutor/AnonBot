# Anonymous Discord Forwarder Bot

## Overview

This Discord bot forwards direct messages to a designated channel, enabling centralized monitoring of DMs. It maintains message synchronization by updating forwarded messages when originals are edited or deleted.

### Key Features

- **DM Forwarding**: Automatically forwards all DMs to a specific channel
- **Message Sync**: Updates forwarded messages when originals are edited/deleted
- **Conversation Tracking**: Adds "New [PREFIX]:" header for conversations with 60+ minute gaps
- **Message Pairing**: Maintains mapping between original and forwarded messages

## Setup

### Prerequisites

- Python 3.10+
- Discord bot token
- Target guild and channel IDs

### Configuration

Create a `config.py` file with:

```python
TOKEN = "your_bot_token"
GUILD_ID = 123456789  # Server ID where bot operates
CHANNEL_ID = 987654321  # Target channel for forwarded messages
PREFIX = "DM"  # Prefix for new conversation headers
```

### Installation

```bash
uv install
uv run main.py
```

## Usage

### For End Users

- Send a DM to the bot user - it automatically forwards to the designated channel
- Edit/delete DMs - forwarded messages update accordingly
- Messages are marked with timestamps and conversation breaks

### For Administrators

Use `/toggle` slash command:

- `/toggle on` - Enable bot
- `/toggle off` - Disable bot (sends "disabled" reply to new DMs)

_Requires "Mute Members" permission_

## Technical Details

### Bot Configuration

```python
intents = discord.Intents.none()
intents.message_content = True
intents.guilds = True
intents.dm_messages = True
```

### Message Flow

1. **Incoming DM** → `on_text_message()`

   - Ignores bot messages and guild members
   - Checks conversation timing (60min threshold)
   - Adds prefix for new conversations
   - Forwards to target channel

2. **Message Edit** → `on_message_edit()`

   - Updates corresponding channel message
   - Preserves conversation prefix

3. **Message Delete** → `on_message_delete()`
   - Replaces content with "[Deleted]"
   - Removes from tracking dictionary

### Error Handling

- All event handlers wrapped in try/except blocks
- Logs exceptions via `logging` module

### Code Architecture

```
main.py
├── Bot initialization & configuration
├── Event handlers
│   ├── on_ready() - startup logging
│   ├── on_text_message() - DM forwarding
│   ├── on_message_edit() - sync edits
│   └── on_message_delete() - sync deletions
├── Slash commands
│   └── /toggle - admin control
└── Error handling & logging
```

### Dependencies

- `discord.py` - Discord API wrapper
- `datetime` - Timestamp handling
- `logging` - Error logging
- `config` - Bot configuration (custom module)

### Security Considerations

- Bot ignores all guild member messages (DM-only)
- Slash command restricted to admins
- No message content stored permanently
- AllowedMentions disabled to prevent ping spam
