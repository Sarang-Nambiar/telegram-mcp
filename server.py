from mcp.server.fastmcp import FastMCP
from telethon.hints import TotalList
import traceback
from tools.telegram_tools import (
    ensure_client_connection,
    client,
    find_id_from_name,
    filter_dialogs,
    LIMIT_MESSAGES,
    LIMIT_DIALOGS
)
from typing import List, Dict, Union
import logging

# TODO:
# List out all the names and then find the right person
# Reading messages, maybe start with giving info on top k messages. 
# Then move on to reading unread messages if any. If none, then LLM should say that
# Deletion of chats, messages, groups.
# Deletion of specific messages, "maybe delete the 5th latest message".
# Edit the latest message or any message to something else

mcp = FastMCP("telegram-mcp")

# Read only resources
@mcp.tool()
async def list_all_conversations() -> TotalList:
    """
    Lists all the open conversations had by the client.
    """
    await ensure_client_connection()
    dialogs = await client.get_dialogs(limit=LIMIT_DIALOGS) # Limiting to LIMIT_DIALOGS dialogs to preserve context window
    f_dialogs = filter_dialogs(dialogs)
    return f_dialogs

@mcp.tool()
async def send_message(name: str, message: str) -> str:
    """
    Send a message to a particular user on telegram with an active chat.
    
    name: The name of the person who's messages are to be read.
    message: The message to be sent to the user.
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

@mcp.tool()
async def get_unread_count(top_k:int) -> Union[str, Dict[str, int]]:
    """
    Function to report the number of unread messages from the top_k chats with unread messages.

    top_k: The top open chats to read unread messages from.
    """
    await ensure_client_connection()

    counts = {} # map of the username to the unread message count
    i = 0

    try:
        dialogs = await client.get_dialogs(limit=LIMIT_DIALOGS) # Limiting to LIMIT_DIALOGS dialogs to preserve context window

        for dialog in dialogs:
            if i == top_k:
                logging.info(f"Found {top_k} dialogs with unread messages.")
                break
            
            if dialog.is_user and dialog.unread_count != 0:
                logging.info(f'User {dialog.title} found with {dialog.unread_count}')
                counts[dialog.title] = dialog.unread_count
                i += 1
            
        return counts if counts else "No unread messages found."
        
    except Exception as e:
        err_msg = str(e)
        logging.error("Something went wrong when finding unread messages:")
        traceback.print_exc()
        return f"Failed to send message due to error: {err_msg}"

@mcp.prompt()
def send_message_prompt(telegram_username: str, message: str) -> str:
    """
    Prompt for sending a message on telegram.
    """
    return f"""
    Try finding a user with a Telegram username similar to {telegram_username} from the list of open conversations. 
    If there are multiple usernames which are similar, then confirm with the user on which one to pick,
    Else confirm whether the username which you found similar is the one that the user is intending to message.

    From the confirmed username, send the message {message} over to the user.
    
    When sending long messages or messages that require you to be expressive, use the below formatting style:
    *italic* and _italic_
    **bold** and __bold__
    # headings are underlined
    ~~strikethrough~~
    [inline URL](https://www.example.com/)
    [inline mention](tg://user?id=ab1234cd6789)
    custom emoji image with ![👍](tg://emoji?id=1234567890)
    `inline code`
    ```python
    multiline pre-formatted
    block with optional language
    ``` 
    """


# TODO: Write a prompt for reading a probably markdown formatting message from the telegram chat.
@mcp.prompt()
def read_message_prompt(telegram_username: str, top_k: int) -> str:
    """
    Prompt for sending a message on telegram.
    """
    return f"""
    Try finding a user with a Telegram username similar to {telegram_username} from the list of open conversations. 
    If there are multiple usernames which are similar, then confirm with the user on which one to pick,
    Else confirm whether the username which you found similar is the one that the user is trying to read the messages from.

    From the confirmed username, read {top_k} message(s) from the chat. 
    The message could be formatted with the following style:
    *italic* and _italic_
    **bold** and __bold__
    # headings are underlined
    ~~strikethrough~~
    [inline URL](https://www.example.com/)
    [inline mention](tg://user?id=ab1234cd6789)
    custom emoji image with ![👍](tg://emoji?id=1234567890)
    `inline code`
    ```python
    multiline pre-formatted
    block with optional language
    ```

    If the message(s) is short, output the exact message(s) from the chat. If not, output a summarized version of the message(s). 
    """

@mcp.prompt()
def get_unread_count_prompt(top_k: int) -> str:
    """
    Prompt for sending a message on telegram.
    """

    return f"""
    Find the count of the unread messages in the {top_k} open conversations that the user had. 

    The output from the execution of the function/tool would be a HashMap with the key being the username and the value being the count of the unread messages in that particular chat with that user. 

    Calculate the total number of unread messages for the user and list the count of the unread messages from the different usernames with the help of bullet points.
    
    If there are any unread messages, suggest further operations like reading those messages or sending a reply to the message.
    """