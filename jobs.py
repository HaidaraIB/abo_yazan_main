from telegram.ext import ContextTypes
from DB import DB
from PyroClientSingleton import PyroClientSingleton
import asyncio
import os
import random
from user.send_id.common import extract_important_info
from common import edit_message_text


async def edit_ids_info(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_ids()
    for i in ids:
        if i["is_closed"]:
            continue
        cpyro = PyroClientSingleton()
        sent = await cpyro.send_message(
            chat_id="@QuotexPartnerBot",
            text=i["id"],
        )
        await asyncio.sleep(2)
        rcvd = await cpyro.get_messages(
            chat_id="@QuotexPartnerBot",
            message_ids=sent.id + 1,
        )
        if "ACCOUNT CLOSED" in rcvd.text:
            important_info = extract_important_info(rcvd.text, is_closed=True)
            await DB.close_account(i=i["id"])
            await edit_message_text(
                context=context,
                chat_id=int(os.getenv("IDS_CHANNEL_ID")),
                message_id=int(i["message_id"]),
                text=important_info + " ❌",
            )
            continue

        if (
            (str(i["id"]) not in rcvd.text)
            or (not rcvd.text)
            or ("not found" in rcvd.text)
        ):
            continue

        important_info = extract_important_info(rcvd.text, is_closed=False)
        await edit_message_text(
            context=context,
            chat_id=int(os.getenv("IDS_CHANNEL_ID")),
            message_id=int(i["message_id"]),
            text=important_info,
        )
        await asyncio.sleep(random.randint(3, 10))

    context.job_queue.run_once(
        callback=edit_ids_info,
        when=600,
    )
