from telegram.ext import ContextTypes
from DB import DB
from PyroClientSingleton import PyroClientSingleton
import asyncio
from send_id.common import get_id_info


async def edit_ids_info(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_ids()
    for i in ids:
        await get_id_info(context=context, i=i["id"])
        await asyncio.sleep(5)

    context.job_queue.run_once(
        callback=edit_ids_info,
        when=30,
    )


async def check_remote_ids(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_trader_ids_to_check()
    for i in ids:
        trader_id = i["trader_id"]

        res = await get_id_info(context=context, i=trader_id)

        if res != "not found":
            await PyroClientSingleton().send_message(
                chat_id=-1002453670376,
                text=trader_id,
            )

        DB.delete_checked_remote_id(i=trader_id)
        await asyncio.sleep(1)

    context.job_queue.run_once(
        callback=check_remote_ids,
        when=5,
    )
