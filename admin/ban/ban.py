from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from custom_filters import *
from DB import DB

from common import (
    build_admin_keyboard,
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)
from start import start_command

(
    USER_ID_TO_BAN_UNBAN,
    BAN_UNBAN_USER,
) = range(2)


async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        text = (
            "إرسل آيدي المستخدم الذي تريد حظره/فك الحظر عنه.\n\n"
            "يمكنك استخدام كيبورد معرفة الآيديات، قم بالضغط على /start وإظهاره إن كان مخفياً."
        )
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_to_admin_home_page_button),
        )
        return USER_ID_TO_BAN_UNBAN


async def user_id_to_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user = DB.get_user(user_id=int(update.message.text))
        if not user:
            await update.message.reply_text(
                text="لم يتم العثور على المستخدم، تأكد من الآيدي وأعد إرساله. ❌",
                reply_markup=InlineKeyboardMarkup(back_to_admin_home_page_button),
            )
            return
        if user["banned"]:
            ban_button = [
                InlineKeyboardButton(
                    text="فك الحظر 🔓", callback_data=f"unban {user['id']}"
                )
            ]
        else:
            ban_button = [
                InlineKeyboardButton(text="حظر 🔒", callback_data=f"ban {user['id']}")
            ]
        keyboard = [
            ban_button,
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to user id to ban unban"
                )
            ],
            back_to_admin_home_page_button[0],
        ]
        await update.message.reply_text(
            text="هل تريد.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return BAN_UNBAN_USER


back_to_user_id_to_ban_unban = ban_unban


async def ban_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await DB.set_banned(
            user_id=int(update.callback_query.data.split(" ")[-1]),
            banned=1 if update.callback_query.data.startswith("ban") else 0,
        )

        await update.callback_query.edit_message_text(
            text="تمت العملية بنجاح ✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


ban_unban_user_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            ban_unban,
            "^ban unban$",
        ),
    ],
    states={
        USER_ID_TO_BAN_UNBAN: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=user_id_to_ban_unban,
            )
        ],
        BAN_UNBAN_USER: [CallbackQueryHandler(ban_unban_user, "^ban \d+$|^unban \d+$")],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            back_to_user_id_to_ban_unban, "^back to user id to ban unban$"
        ),
    ],
)
