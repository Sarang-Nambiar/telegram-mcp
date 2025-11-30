# telegram-mcp

An MCP (Model Context Protocol) server for Telegram that enables AI assistants to interact with Telegram chats programmatically.

## Features

### Tools

#### Message Reading & Sending
- **`read_message`** - Read messages from an active chat with a user
  - Supports reading the latest K messages from a conversation
  - Automatically filters and formats message data
  - **Prompt Template**: `read_message_prompt()` - Guides conversation partner selection and message retrieval
  
- **`send_message`** - Send messages to a user on Telegram
  - Supports Telegram's markdown formatting (bold, italic, links, code blocks, etc.)
  - **Prompt Template**: `send_message_prompt()` - Handles fuzzy matching of usernames and user confirmation
  
- **`get_unread_count`** - Check unread message counts across active conversations
  - Retrieves unread counts from the top K chats
  - Returns aggregated unread message statistics
  - **Prompt Template**: `get_unread_count_prompt()` - Summarizes unread counts and suggests follow-up actions

#### Message Management
- **`delete_message`** - Delete messages from a conversation
  - Supports deleting single or multiple messages
  - Optional `remove_for_everyone` flag to delete for all chat participants
  - **Works independently** - Can search and delete messages without prior context
  - **Recommended usage**: Use after calling `read_message` when all messages are in context for precise deletion
  
- **`list_all_conversations`** - List all active conversations with the client

### Prompt Templates

This MCP server includes built-in prompt templates for seamless AI assistant integration:

- `send_message_prompt()` - Intelligently matches Telegram usernames and sends formatted messages
- `read_message_prompt()` - Retrieves and summarizes messages from specific conversations
- `get_unread_count_prompt()` - Analyzes unread messages and recommends next actions

These templates handle:
- Fuzzy username matching from open conversations
- User confirmation before executing actions
- Proper Telegram markdown formatting
- Natural language summarization of results

## Setup

### Requirements
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- An active Telegram account
- Telegram API credentials (App ID and Hash)

### Installation

1. Clone the repository
```bash
git clone https://github.com/Sarang-Nambiar/telegram-mcp.git
cd telegram-mcp
```
2. Create a virtual environment and install dependencies:
```bash
uv sync
```

### Configuration

1. Get your Telegram API credentials from [core.telegram.org](https://core.telegram.org/):
   - App ID
   - API Hash

2. Create a `.env` file in the project root:
```
TELE_APP_ID=your_app_id
TELE_HASH=your_api_hash
```

3. Then, run the server with the following command to log in:
```bash
uv run main.py
``` 
After a successful login, a file named `anon.session` will be created to store your session data.

## Usage
After logging in, add this repository as a custom MCP server in the MCP client application of your choice. For Claude Desktop, add the following to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "telegram-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/telegram-mcp",
        "main.py"
      ]
    }
  }
}
```
The guide to finding the location of claude_desktop_config.json can be found [here](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

## Configuration

### Limits

Adjust these constants in `tools/telegram_tools.py`:

- `LIMIT_MESSAGES` - Maximum number of messages to retrieve per request (default: 50)
- `LIMIT_DIALOGS` - Maximum number of active conversations to list (default: 50)

## Project Structure

```
telegram-mcp/
├── main.py                 # Entry point
├── server.py              # MCP server with tools and prompts
├── tools/
│   └── telegram_tools.py  # Telethon client utilities
├── utils/                 # Utility functions
├── pyproject.toml         # Project configuration
├── .env                   # Environment variables
└── README.md             # This file
```

## Notes

- All tools require an active Telegram connection
- The `delete_message` tool can work independently but is most effective when used after `read_message` to maintain context
- Message formatting follows Telegram's markdown style (bold, italic, links, code blocks, etc.)
- Rate limiting applies based on Telegram's API constraints
