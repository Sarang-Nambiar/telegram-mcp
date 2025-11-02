from mcp.server.fastmcp import FastMCP
from telethon import TelegramClient
import dotenv
import os
import sys
from telethon.hints import TotalList
import traceback
import asyncio
dotenv.load_dotenv()

mcp = FastMCP("telegram-mcp")

# What you need to fix:
# The current client is disconnected when the some of the mcp functions are called
# What you need to ensure is that the client is connected when the mcp resource or tool is called and then disconnected either when the server is stopped or when the function ends. Although opening multiple connections could increase latency so the other approach is kind of better

TELE_APP_ID = os.getenv('TELE_APP_ID', None)
TELE_HASH = os.getenv('TELE_HASH', None)

if not TELE_APP_ID or not TELE_HASH:
    print("Unable to retrieve the telegram hash or app id.")
    sys.exit(1)

# Needs access to the user's phone number and login otp
# and an existing telegram account.
client = TelegramClient('anon', TELE_APP_ID, TELE_HASH)

_client_started = False
_connection_lock = asyncio.Lock()

async def ensure_client_connection():
    """
    Ensures the client is connected. Uses a lock to prevent race conditions.
    """
    global _client_started
    async with _connection_lock:
        if not _client_started:
            await client.start()
            _client_started = True

# Read only resources
@mcp.resource("resource://telegram/user/conversations")
async def list_all_conversations() -> TotalList:
    """
    Lists all the open conversations had by the client
    """
    await ensure_client_connection()
    dialogs = await client.get_dialogs(limit=50) # Limiting to 50 dialogs to preserve context window
    return dialogs

@mcp.tool()
async def find_id_from_name(name: str) -> int|None:
    """
    Finds the id of the person provided their name from the open conversations
    """
    await ensure_client_connection()
    async for dialog in client.iter_dialogs():
        if dialog.name == name:
            return dialog.id
    return None

@mcp.tool()
async def send_message(name: str, message: str) -> bool:
    """
    Send a message to a particular user on telegram
    """
    await ensure_client_connection()
    try:
        convo_id = await find_id_from_name(name)
        await client.send_message(convo_id, message)
        return True
    except Exception as e:
        print("The following exception occurred while trying to send a message")
        traceback.print_exc()
        return False

async def cleanup():
    """
    Disconnects the client when the MCP server shuts down
    """
    global _client_started
    if _client_started:
        await client.disconnect()
        _client_started = False
        print("Telegram client disconnected")

# async def main():
#     async for dialog in client.iter_dialogs():
#         print(dialog.name, 'has ID', dialog.id)

# with client:
#     # client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))
#     client.loop.run_until_complete(main())