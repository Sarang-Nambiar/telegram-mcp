from mcp.server.fastmcp import FastMCP
from telethon.hints import TotalList
import traceback
from tools.telegram_tools import (
    ensure_client_connection,
    client,
    find_id_from_name,
    LIMIT_MESSAGES
)
from typing import List, Dict, Union
import logging

# TODO:
# Test out the resource feature in MCP
# List out all the names and then find the right person
# Make a prompt template to claude which would only give suggestions based on the tools we have and it should be able to send telegram messages with a compatible markdown syntax. https://docs.telethon.dev/en/v2/concepts/messages.html 
# Reading messages, maybe start with giving info on top k messages. 
# Then move on to reading unread messages if any. If none, then LLM should say that
# Deletion of chats, messages, groups.
# Deletion of specific messages, "maybe delete the 5th latest message".
# Edit the latest message or any message to something else

mcp = FastMCP("telegram-mcp")

# Read only resources
@mcp.resource("resource://telegram/user/conversations")
async def list_all_conversations() -> TotalList:
    """
    Lists all the open conversations had by the client.
    """
    await ensure_client_connection()
    dialogs = await client.get_dialogs(limit=50) # Limiting to 50 dialogs to preserve context window
    return dialogs

@mcp.tool()
async def send_message(name: str, message: str) -> str:
    """
    Send a message to a particular user on telegram with an active chat.
    """
    await ensure_client_connection()
    try:
        convo_id = await find_id_from_name(name)
        if convo_id is None:
            return f"Failed to send message to {name}: No active chat found."
        
        await client.send_message(convo_id, message)
        return f"Successfully sent message to {name}"
    except Exception as e:
        logging.error("The following exception occurred while trying to send a message:")
        traceback.print_exc()
        return "Failed to send message due to some error"

@mcp.tool()
async def read_message(name: str, latest_k: int=1) -> Union[str, List[Dict[str, str]]]:
    """
    Function to read telegram messages from an active chat.
    
    name: The name of the person who's messages are to be read.
    latest_k: The number of messages to be read in the chat starting from the latest one.
    """
    await ensure_client_connection()
    if latest_k > LIMIT_MESSAGES: # Limit on the number of messages that can be retrieved
        print(f"The number of messages to be read exceeds the limit: {LIMIT_MESSAGES}. Hence, the number of messages to be read is reset to {LIMIT_MESSAGES}")
    
    latest_k = min(latest_k, LIMIT_MESSAGES)
    try:
        convo_id = await find_id_from_name(name)
        if convo_id is None:
            return f"Failed to read message from {name}: No active chat found."
        
        msgs = await client.get_messages(convo_id, limit=latest_k)
        res = []
        for msg in msgs:
            if not msg:
                logging.error("Empty message found. Skipping.")
                continue

            sender = msg.sender.username # Fetching the sender of that particular message.
            if not sender:
                sender = 'me'

            res.append({sender : msg.message}) 
        return res
    
    except Exception as e:
        err_msg = str(e)
        logging.error("Something went wrong during reading:")
        traceback.print_exc()
        return f"Failed to send message due to error: {err_msg}"