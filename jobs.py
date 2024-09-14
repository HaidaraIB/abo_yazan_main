from telegram.ext import ContextTypes
from DB import DB
from PyroClientSingleton import PyroClientSingleton
import asyncio
import random


async def edit_ids_info(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_ids()
    for i in ids:
        trader_id = i["id"]
        cpyro = PyroClientSingleton()
        await cpyro.send_message(
            chat_id=context.bot.username,
            text=trader_id,
        )
        await asyncio.sleep(random.randint(3, 10))

    context.job_queue.run_once(
        callback=edit_ids_info,
        when=30,
    )


async def check_remote_ids(context: ContextTypes.DEFAULT_TYPE):
    ids = DB.get_trader_ids_to_check()
    for i in ids:
        trader_id = i["trader_id"]
        cpyro = PyroClientSingleton()

        await cpyro.send_message(
            chat_id=-1002453670376,
            text=trader_id,
        )
        await cpyro.send_message(
            chat_id=context.bot.username,
            text=trader_id,
        )

        DB.delete_checked_remote_id(i=trader_id)
        await asyncio.sleep(1)

    context.job_queue.run_once(
        callback=check_remote_ids,
        when=30,
    )
