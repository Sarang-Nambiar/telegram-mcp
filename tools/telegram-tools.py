from telethon import TelegramClient
import dotenv
import os
import sys
dotenv.load_dotenv()

TELE_APP_ID = os.getenv('TELE_APP_ID', None)
TELE_HASH = os.getenv('TELE_HASH', None)

if not TELE_APP_ID or not TELE_HASH:
    print("Unable to retrieve the telegram hash or app id.")
    sys.exit(1)

# Needs access to the user's phone number and login otp
# and an existing telegram account.
client = TelegramClient('anon', TELE_APP_ID, TELE_HASH)

with client:
    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))