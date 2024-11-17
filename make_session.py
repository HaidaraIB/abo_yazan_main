from telethon import TelegramClient
import os

from dotenv import load_dotenv
load_dotenv()
from pyrogram import Client

client = Client(
    name="session",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    phone_number=os.getenv("PHONE"),
)

# client = TelegramClient(
#     session="session",
#    api_hash=os.getenv("API_HASH"),
#    api_id=int(os.getenv("API_ID"))
# )

async def test():
    await client.start()
    me = await client.get_me()
    print(me)
    await client.stop()


client.loop.run_until_complete(test())