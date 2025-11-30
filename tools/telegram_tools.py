import logging
import os
import sys
import traceback
from typing import Any, Dict, List
from telethon import TelegramClient
import dotenv
import asyncio
from telethon.types import Dialog
dotenv.load_dotenv()

TELE_APP_ID = os.getenv('TELE_APP_ID', None)
TELE_HASH = os.getenv('TELE_HASH', None)
LIMIT_MESSAGES = 50 # Number of messages to be read/fetched
LIMIT_DIALOGS = 50 # Number of active conversations in telegram

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


async def find_msg_ids_from_msg(convo_id: int, message_texts: List[str]) -> List[int] | None:
    """
    Finds the message ids of the plain text messages

    convo_id: The open conversation from which the message id should be found.
    message_texts: Plain text messages from which the ids are to be found
    """
    await ensure_client_connection()
    res = []

    try:
        messages = await client.get_messages(convo_id, limit=LIMIT_MESSAGES)
        
        for text in message_texts:
            for msg in messages:
                if msg.message == text:
                    logging.info(f"Found the message '{text}'. Retrieving the id.")
                    res.append(msg.id)
                    break
            else:
                # Message could not be found, skip it
                logging.warning(f"Could not find '{text}' in the chat. Skipping.")

        return res
    
    except Exception as e:
        traceback.print_exc()
        logging.error("Something went wrong when trying to fetch the ids of the messages.")
        return None
        

async def find_id_from_name(name: str) -> int|None:
    """
    Finds the id of the person provided their name from the open conversations
    """
    await ensure_client_connection()
    async for dialog in client.iter_dialogs():
        if dialog.name == name:
            return dialog.id
    return None

def filter_dialogs(dialogs: List[Dialog]) -> List[Dict[str, Any]]:
    """
    Filter out unnecessary properties from the Dialog class
    """
    f_dialogs = []
    for dialog in dialogs:
        last_message = dialog.message
        f_dialog = {
            "username": dialog.title, # username or chatname
            "last_message": last_message.message,
            "last_message_date": last_message.date, 
            "chat_id": dialog.id,
            "is_user": dialog.is_user,
            "is_group": dialog.is_group,
            "is_channel": dialog.is_channel,
        }
        f_dialogs.append(f_dialog)
    return f_dialogs

async def cleanup() -> None:
    """
    Disconnects the client when the MCP server shuts down
    """
    global _client_started
    if _client_started:
        await client.disconnect()
        _client_started = False
        print("Telegram client disconnected")