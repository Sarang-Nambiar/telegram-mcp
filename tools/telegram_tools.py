import os
import sys
from telethon import TelegramClient
import dotenv
import asyncio

dotenv.load_dotenv()

TELE_APP_ID = os.getenv('TELE_APP_ID', None)
TELE_HASH = os.getenv('TELE_HASH', None)

if not TELE_APP_ID or not TELE_HASH:
    print("Unable to retrieve the telegram hash or app id.")
    sys.exit(1)

# Needs access to the user's phone number and login otp
# and an existing telegram account.
client = TelegramClient('anon', TELE_APP_ID, TELE_HASH)

# Utility functions
_client_started = False
_connection_lock = asyncio.Lock()

async def ensure_client_connection() -> None:
    """
    Ensures the client is connected. Uses a lock to prevent race conditions.
    """
    global _client_started
    async with _connection_lock:
        if not _client_started:
            await client.start()
            _client_started = True

async def find_id_from_name(name: str) -> int|None:
    """
    Finds the id of the person provided their name from the open conversations
    """
    await ensure_client_connection()
    async for dialog in client.iter_dialogs():
        if dialog.name == name:
            return dialog.id
    return None

async def cleanup():
    """
    Disconnects the client when the MCP server shuts down
    """
    global _client_started
    if _client_started:
        await client.disconnect()
        _client_started = False
        print("Telegram client disconnected")