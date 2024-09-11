from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from common import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
    build_admin_keyboard,
)

from admin.questions_settings.question_settings import (
    back_to_question_settings_button,
    back_to_question_settings_handler,
)

from custom_filters import *
from start import start_command

from DB import DB

(Q, A) = range(2)


async def add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            back_to_question_settings_button,
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل نص السؤال❓",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return Q


async def get_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        context.user_data["q_to_add"] = update.message.text
        back_buttons = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to add question"
                )
            ],
            back_to_admin_home_page_button[0],
        ]
        await update.message.reply_text(
            text="أرسل الجواب❗️",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return A


back_to_add_question = add_question


async def get_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await DB.add_question(
            q=context.user_data["q_to_add"],
            a=update.message.text,
        )
        await update.message.reply_text(
            text="تمت إضافة السؤال بنجاح✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_question_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_question, "add question"),
    ],
    states={
        Q: [
            MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=get_q),
        ],
        A: [
            MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=get_a),
        ],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        back_to_question_settings_handler,
        CallbackQueryHandler(back_to_add_question, "^back to add question$"),
    ],
)
