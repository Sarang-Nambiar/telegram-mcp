from mcp.server.fastmcp import FastMCP
from telethon.hints import TotalList
import traceback
from tools.telegram_tools import (
    ensure_client_connection,
    client,
    find_id_from_name
)

# TODO:
# Test out the resource feature in MCP
# Reading messages, maybe start with giving info on top k messages. 
# Then move on to reading unread messages if any. If none, then LLM should say that
# Deletion of chats, messages, groups.
# Deletion of specific messages, "maybe delete the 5th latest message".

mcp = FastMCP("telegram-mcp")

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

