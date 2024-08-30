from telegram import Update, Chat, InlineKeyboardMarkup

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import asyncio
import re
import os
from custom_filters import User
from common import (
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
    build_user_keyboard,
    edit_message_text,
    insert_into_remote_db,
    update_into_remote_db,
    get_from_remote_db,
)
from user.send_id.common import extract_important_info
from start import start_command
from PyroClientSingleton import PyroClientSingleton
from DB import DB

GET_ID = range(1)


async def send_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        await update.callback_query.edit_message_text(
            text="أرسل الآيدي",
            reply_markup=InlineKeyboardMarkup(back_to_user_home_page_button),
        )
        return GET_ID


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
        if not rcvd.text or "not found" in rcvd.text:
            await wait_message.edit_text(
                text=(
                    "عذراً لم يتم العثور على حسابك"
                    " يرجى التأكد من تسجيلك عن طريق الرابط"
                    " . او التأكد من كتابتك للـid"
                    " بشكل صحيح ، ثم إعاده المحاولة من جديد."
                ),
                reply_markup=build_user_keyboard(),
            )
            return ConversationHandler.END

        stored_id = DB.get_ids(i=i)
        if "ACCOUNT CLOSED" in rcvd.text:
            is_closed = True
        else:
            is_closed = False
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
        remote_data = get_from_remote_db(trader_id=data[0])
        if remote_data:
            update_into_remote_db(data=data, is_closed=int(is_closed))
        else:
            insert_into_remote_db(data=data, is_closed=int(is_closed))

        if float(data[5]) == 0 and not is_closed:
            await wait_message.edit_text(
                text="تم التأكد من تسجيلك يرجى ايداع 10دولار في الحساب لإكمال شروطك .ثم إعادة إرسال  الـid هنا .ليتم إضافتك إلى جروب vip .",
                reply_markup=build_user_keyboard(),
            )
        elif is_closed:
            await wait_message.edit_text(
                text="هذا الحساب مغلق",
                reply_markup=build_user_keyboard(),
            )

        else:
            await wait_message.edit_text(
                text=(
                    "تم تأكيد تسجيلك للحساب اضغط على هذا الرابط للدخول إلى قناه  الـVIP\n"
                    "----------------------------------------------------------------\n"
                    "https://t.me/+c33u4mRoV6A5ZGZk\n"
                    "بالتوفيق للجميع اخوكم ابو يزن 🫡"
                )
            )
            await update.message.reply_text(
                text="القائمة الرئيسية🔝",
                reply_markup=build_user_keyboard(),
            )
        return ConversationHandler.END


send_id_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(send_id, "^send id$"),
    ],
    states={
        GET_ID: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=get_id,
            ),
        ],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
    ],
)
