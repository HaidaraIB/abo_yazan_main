from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from admin.questions_settings.functions import build_questions_keyboard
from admin.questions_settings.question_settings import back_to_question_settings_handler
from common import (
    build_admin_keyboard,
    stringify_question,
    back_to_admin_home_page_handler,
)
from start import start_command
from custom_filters import *
from DB import DB

Q_TO_SHOW = range(1)


async def show_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_questions_keyboard("s")

        if not keyboard:
            await update.callback_query.answer("ليس لديك أسئلة بعد ❗️", show_alert=True)
            return ConversationHandler.END

        await update.callback_query.edit_message_text(
            text="اختر السؤال.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return Q_TO_SHOW


async def q_to_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        q_id = update.callback_query.data[1:]
        q = DB.get_question(q_id=q_id)
        await update.callback_query.edit_message_text(
            text=stringify_question(q), reply_markup=build_admin_keyboard()
        )
        return ConversationHandler.END


show_questions_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=show_questions, pattern="^show questions$")
    ],
    states={
        Q_TO_SHOW: [CallbackQueryHandler(q_to_show, "^s\d+$")],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        back_to_question_settings_handler,
    ],
)
