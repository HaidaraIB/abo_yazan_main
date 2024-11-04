import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

from telethon import events, TelegramClient, Button
from telethon.tl.patched import Message
import os
import asyncio
from telethon_db import TelethonDB

from dotenv import load_dotenv

load_dotenv()

FROM = [
    -1001820088359,
]

VIP_FROM = [
    -1001771915378,
]

TO = [
    -1002165082360,
]

VIP_TO = [
    -1002212821302,
    # -1002107793881,
]

# PUBLIC_CHANNEL = -1002107793881
PUBLIC_CHANNEL = 0

subs = [
    "Group rules:",
    "Promocode",
    "Perfect Sureshots",
    "Valuable Feedback",
]

TelethonDB.creat_tables()

client = TelegramClient(
    session="telethon_session",
    api_hash=os.getenv("API_HASH"),
    api_id=int(os.getenv("API_ID")),
).start(phone=os.getenv("PHONE"))


@client.on(events.NewMessage(chats=FROM + VIP_FROM))
@client.on(events.Album(chats=FROM + VIP_FROM))
async def get_post(event):
    gallery = getattr(event, "messages", None)
    if event.grouped_id and not gallery:
        return

    if event.chat_id == FROM[0]:
        await copy_messages(event, gallery, TO)
    elif all(sub not in event.message.text for sub in subs):
        await copy_messages(event, gallery, VIP_TO)

    raise events.StopPropagation


async def copy_messages(event, gallery, to):
    stored_msg = None
    if not event.grouped_id:
        message: Message = event.message
        # Single Photo
        if (message.photo and not message.web_preview) or message.video:
            for channel in to:
                if event.is_reply:
                    stored_msg = TelethonDB.get_messages(
                        from_message_id=message.reply_to_msg_id,
                        from_channel_id=event.chat_id,
                        to_channel_id=channel,
                    )
                if channel == PUBLIC_CHANNEL and "Profit" in message.text:
                    msg = await client.send_file(
                        channel,
                        caption=(
                            "ربح ✅✅✅\n"
                            "للإنظمام الى جروب الـvip 🔥\n\n"
                            "[TEAM ABO YAZAN](t.me/BOUCHA_A)"
                        ),
                        file=message.photo if message.photo else message.video,
                        reply_to=stored_msg[0] if stored_msg else None,
                    )
                elif channel != PUBLIC_CHANNEL:
                    msg = await client.send_file(
                        channel,
                        caption=message.text.replace(
                            "[🔗 REGISTER HERE ](https://bit.ly/QUOTEXVIP_MrSHEKO)\nCode : (MrSHEKO) 50% Deposit bounus",
                            "[🔗 REGISTER HEAR ](https://broker-qx.pro/sign-up/?lid=873616)\n(aboyazan)%كود بونص 50",
                        ),
                        file=message.photo if message.photo else message.video,
                        reply_to=stored_msg[0] if stored_msg else None,
                    )
                await TelethonDB.add_message(
                    from_message_id=message.id,
                    to_message_id=msg.id,
                    from_channel_id=event.chat_id,
                    to_channel_id=channel,
                )
        # Just Text
        else:
            for channel in to:
                if event.is_reply:
                    stored_msg = TelethonDB.get_messages(
                        from_message_id=message.reply_to_msg_id,
                        from_channel_id=event.chat_id,
                        to_channel_id=channel,
                    )
                if channel == PUBLIC_CHANNEL and "Open your Platform" in message.text:
                    msg = await client.send_message(
                        channel,
                        "نبدأ الجلسة على جروب الـvip 🔥",
                        reply_to=stored_msg[0] if stored_msg else None,
                    )
                elif channel != PUBLIC_CHANNEL:
                    msg = await client.send_message(
                        channel,
                        message.text.replace(
                            "[🔗 REGISTER HERE ](https://bit.ly/QUOTEXVIP_MrSHEKO)\nCode : (MrSHEKO) 50% Deposit bounus",
                            "[🔗 REGISTER HEAR ](https://broker-qx.pro/sign-up/?lid=873616)\n(aboyazan)%كود بونص 50",
                        ),
                        reply_to=stored_msg[0] if stored_msg else None,
                    )
                await TelethonDB.add_message(
                    from_message_id=message.id,
                    to_message_id=msg.id,
                    from_channel_id=event.chat_id,
                    to_channel_id=channel,
                )
    # Albums
    else:
        for channel in to:
            if channel == PUBLIC_CHANNEL:
                continue
            if event.is_reply:
                stored_msg = TelethonDB.get_messages(
                    from_message_id=gallery[0].reply_to_msg_id,
                    from_channel_id=event.chat_id,
                    to_channel_id=channel,
                )
            msg = await client.send_file(
                channel,
                gallery,
                caption=[
                    m.text.replace(
                        "[🔗 REGISTER HERE ](https://bit.ly/QUOTEXVIP_MrSHEKO)\nCode : (MrSHEKO) 50% Deposit bounus",
                        "[🔗 REGISTER HEAR ](https://broker-qx.pro/sign-up/?lid=873616)\n(aboyazan)%كود بونص 50",
                    )
                    for m in gallery
                ],
                reply_to=stored_msg[0] if stored_msg else None,
            )
            await TelethonDB.add_message(
                from_message_id=gallery[0].id,
                to_message_id=msg[0].id,
                from_channel_id=event.chat_id,
                to_channel_id=channel,
            )


async def request_updates(client):
    while True:
        await client.catch_up()
        await asyncio.sleep(5)


print("Running....")
client.loop.create_task(request_updates(client))
client.run_until_disconnected()
print("Stopping....")
