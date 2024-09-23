from telegram import Update, Chat, error
from telegram.ext import ContextTypes, MessageHandler, filters
import asyncio
import os
from custom_filters import User
from common import edit_message_text
from send_id.common import extract_important_info, stringify_id_info, get_id_info
from PyroClientSingleton import PyroClientSingleton
from DB import DB


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        try:
            wait_message = await update.message.reply_text(text="الرجاء الانتظار...")
        except error.RetryAfter as r:
            await asyncio.sleep(r.retry_after)
            wait_message = await update.message.reply_text(text="الرجاء الانتظار...")

        res = await get_id_info(
            context=context, i=update.message.text, user_id=update.effective_user.id
        )
        if res == "not found":
            await wait_message.edit_text(
                text=(
                    "عذراً لم يتم العثور على حسابك"
                    " يرجى التأكد من تسجيلك عن طريق الرابط"
                    " . او التأكد من كتابتك للـid"
                    " بشكل صحيح ، ثم إعاده المحاولة من جديد."
                ),
            )
            return

        try:
            await update.message.reply_text(
                text=stringify_id_info(info=res[0], is_closed=res[1])
            )
        except error.RetryAfter as r:
            await asyncio.sleep(r.retry_after)
            await update.message.reply_text(
                text=stringify_id_info(info=res[0], is_closed=res[1])
            )


send_id_handler = MessageHandler(
    filters=filters.Regex("^\d+$"),
    callback=get_id,
)
