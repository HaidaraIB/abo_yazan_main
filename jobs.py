from telegram.ext import ContextTypes
from DB import DB
from PyroClientSingleton import PyroClientSingleton
import asyncio
import os
import random
from user.send_id.common import extract_important_info
from common import (
    edit_message_text,
    update_into_remote_db,
    get_from_remote_db,
    insert_into_remote_db,
)


async def edit_ids_info(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_ids()
    for i in ids:
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

        if (
            (str(i["id"]) not in rcvd.text)
            or (not rcvd.text)
            or ("not found" in rcvd.text)
        ):
            continue

        if "ACCOUNT CLOSED" in rcvd.text:
            is_closed = True
        else:
            is_closed = False

        important_info = extract_important_info(rcvd.text, is_closed=is_closed)

        if is_closed:
            stored_id = DB.get_ids(i=i["id"])
            if not stored_id["is_closed"]:
                await DB.close_account(i=i["id"])

        await edit_message_text(
            context=context,
            chat_id=int(os.getenv("IDS_CHANNEL_ID")),
            message_id=int(i["message_id"]),
            text="/".join(important_info) + (" ❌" if is_closed else ""),
        )
        await DB.update_message_text(i=i["id"], new_text="/".join(important_info))
        remote_data = get_from_remote_db(trader_id=i["id"])
        if remote_data:
            update_into_remote_db(data=important_info)
        else:
            insert_into_remote_db(data=important_info)
        await asyncio.sleep(random.randint(3, 10))

    context.job_queue.run_once(
        callback=edit_ids_info,
        when=600,
    )
