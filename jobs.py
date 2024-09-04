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
        trader_id = i["id"]
        cpyro = PyroClientSingleton()
        sent = await cpyro.send_message(
            chat_id="@QuotexPartnerBot",
            text=trader_id,
        )
        await asyncio.sleep(2)
        rcvd = await cpyro.get_messages(
            chat_id="@QuotexPartnerBot",
            message_ids=sent.id + 1,
        )

        if (
            (str(trader_id) not in rcvd.text)
            or (not rcvd.text)
            or ("not found" in rcvd.text)
        ):
            continue

        is_closed = "ACCOUNT CLOSED" in rcvd.text

        important_info = extract_important_info(rcvd.text, is_closed=is_closed)

        if is_closed:
            stored_id = DB.get_ids(i=trader_id)
            if not stored_id["is_closed"]:
                await DB.close_account(i=trader_id)

        remote_data = DB.get_from_remote_db(trader_id=trader_id)
        if remote_data:
            DB.update_into_remote_db(data=important_info, is_closed=int(is_closed))
        else:
            DB.insert_into_remote_db(data=important_info, is_closed=int(is_closed))
        await asyncio.sleep(random.randint(3, 10))

    context.job_queue.run_once(
        callback=check_remote_ids,
        when=30,
    )


async def check_remote_ids(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_trader_ids_to_check()
    for i in ids:
        trader_id = i["trader_id"]
        cpyro = PyroClientSingleton()
        sent = await cpyro.send_message(
            chat_id="@QuotexPartnerBot",
            text=trader_id,
        )
        await asyncio.sleep(2)
        rcvd = await cpyro.get_messages(
            chat_id="@QuotexPartnerBot",
            message_ids=sent.id + 1,
        )

        if (
            (str(trader_id) not in rcvd.text)
            or (not rcvd.text)
            or ("not found" in rcvd.text)
        ):
            continue

        is_closed = "ACCOUNT CLOSED" in rcvd.text

        data = extract_important_info(rcvd.text, is_closed=is_closed)

        stored_id = DB.get_ids(i=trader_id)
        if stored_id:
            if is_closed and not stored_id["is_closed"]:
                await DB.close_account(i=trader_id)
            await DB.update_message_text(i=trader_id, new_text="/".join(data))
            await edit_message_text(
                context=context,
                chat_id=int(os.getenv("IDS_CHANNEL_ID")),
                message_id=int(stored_id["message_id"]),
                text="/".join(data) + (" ❌" if is_closed else ""),
            )
        else:
            msg = await context.bot.send_message(
                chat_id=int(os.getenv("IDS_CHANNEL_ID")),
                text="/".join(data) + (" ❌" if is_closed else ""),
            )
            await DB.add_id(
                i=trader_id,
                user_id=0,  # we pass 0 because the trader-id is from the website
                message_id=msg.id,
                message_text="/".join(data) + (" ❌" if is_closed else ""),
                is_closed=is_closed,
            )

        remote_data = DB.get_from_remote_db(trader_id=trader_id)
        if remote_data:
            DB.update_into_remote_db(data=data, is_closed=int(is_closed))
        else:
            DB.insert_into_remote_db(data=data, is_closed=int(is_closed))

        DB.delete_checked_remote_id(i=trader_id)
        await asyncio.sleep(1)

    context.job_queue.run_once(
        callback=edit_ids_info,
        when=30,
    )
