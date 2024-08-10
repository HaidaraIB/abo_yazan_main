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
from custom_filters import User
from common import (
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
    cpyro,
    build_user_keyboard,
)
from start import start_command

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
        try:
            async with cpyro:
                sent = await cpyro.send_message(
                    chat_id="@QuotexPartnerBot",
                    text=i,
                )
                await asyncio.sleep(2)
                rcvd = await cpyro.get_messages(
                    chat_id="@QuotexPartnerBot",
                    message_ids=sent.id + 1,
                )
        except ConnectionError:
            sent = await cpyro.send_message(
                chat_id="@QuotexPartnerBot",
                text=i,
            )
            await asyncio.sleep(2)
            rcvd = await cpyro.get_messages(
                chat_id="@QuotexPartnerBot",
                message_ids=sent.id + 1,
            )
            await cpyro.disconnect()
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

        nums = re.findall(r"\d+\.?\d*", rcvd.text)

        if float(nums[6]) == 0:
            await wait_message.edit_text(
                text="تم التأكد من تسجيلك يرجى ايداع 10دولار في الحساب لإكمال شروطك .ثم إعادة إرسال  الـid هنا .ليتم إضافتك إلى جروب vip .",
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
