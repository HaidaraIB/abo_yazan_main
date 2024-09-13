from telegram import Update, Chat
from telegram.ext import ContextTypes, MessageHandler, filters
import asyncio
import os
from custom_filters import User
from common import edit_message_text
from send_id.common import extract_important_info, stringify_id_info
from PyroClientSingleton import PyroClientSingleton
from DB import DB


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        wait_message = await update.message.reply_text(text="الرجاء الانتظار...")
        i = update.message.text
        cpyro = PyroClientSingleton()
        sent = await cpyro.send_message(
            chat_id="@QuotexPartnerBot",
            text=i,
        )
        await asyncio.sleep(2)
        rcvd = await cpyro.get_messages(
            chat_id="@QuotexPartnerBot",
            message_ids=sent.id + 1,
        )
        if (
            (not rcvd.text)
            or ("not found" in rcvd.text)
            or ("Trader #" not in rcvd.text)
        ):
            await wait_message.edit_text(
                text=(
                    "عذراً لم يتم العثور على حسابك"
                    " يرجى التأكد من تسجيلك عن طريق الرابط"
                    " . او التأكد من كتابتك للـid"
                    " بشكل صحيح ، ثم إعاده المحاولة من جديد."
                ),
            )
            return

        stored_id = DB.get_ids(i=i)
        is_closed = "ACCOUNT CLOSED" in rcvd.text
        data = extract_important_info(rcvd.text, is_closed=is_closed)
        if stored_id:
            if is_closed and not stored_id["is_closed"]:
                await DB.close_account(i=i)
            await DB.update_message_text(i=i, new_text="/".join(data))
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
                i=i,
                user_id=update.effective_user.id,
                message_id=msg.id,
                message_text="/".join(data) + (" ❌" if is_closed else ""),
                is_closed=is_closed,
            )
        remote_data = DB.get_from_remote_db(trader_id=data[0])
        if remote_data:
            DB.update_into_remote_db(data=data, is_closed=int(is_closed))
        else:
            DB.insert_into_remote_db(data=data, is_closed=int(is_closed))

        await update.message.reply_text(
            text=stringify_id_info(info=data, is_closed=is_closed)
        )


send_id_handler = MessageHandler(
    filters=filters.Regex("^\d+$"),
    callback=get_id,
)
