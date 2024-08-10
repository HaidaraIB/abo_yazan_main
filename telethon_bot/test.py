# from pyrogram import Client

# Client(
#     name="session",
#     api_id=23346530,
#     api_hash="4c2b3eedba39494c2c7685b4fbf3006d",
#     phone_number="+96181532982",
# ).start()

from telethon import TelegramClient
import os

from dotenv import load_dotenv
load_dotenv()

client = TelegramClient(
    session="/home/haidara/to_deliver1/telethon_bot/telethon_session.session",
    api_hash=os.getenv("API_HASH"),
    api_id=int(os.getenv("API_ID"))
).start(phone=os.getenv("PHONE"))

async def test():
    async with client:
        e = await client.get_entity(-1001771915378)
        print(e.stringify())


client.loop.run_until_complete(test())