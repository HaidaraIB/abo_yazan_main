from telegram import (
    Chat,
    Update,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

from common import (
    build_admin_keyboard,
    back_to_admin_home_page_handler,
)

from admin.questions_settings.functions import build_questions_keyboard
from admin.questions_settings.question_settings import back_to_question_settings_handler

from start import start_command

from DB import DB
from custom_filters.Admin import Admin

CHOOSE_Q_ID_TO_REMOVE = 0

async def remove_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_questions_keyboard('r')

        if not keyboard:
            await update.callback_query.answer("ليس لديك أسئلة بعد ❗️", show_alert=True)
            return ConversationHandler.END
        
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه السؤال الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_Q_ID_TO_REMOVE


async def choose_q_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        q_id = int(update.callback_query.data[1:])
        await DB.delete_question(q_id=q_id)
        await update.callback_query.answer(text="تمت إزالة السؤال بنجاح✅")
        keyboard = build_questions_keyboard('r')
        
        if not keyboard:
            await update.callback_query.edit_message_text(
                text="قمت بحذف آخر سؤال ولم يبق لديك أسئلة.",
                reply_markup=build_admin_keyboard(),
            )
            return ConversationHandler.END
        
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه السؤال الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_Q_ID_TO_REMOVE


remove_question_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=remove_question, pattern="^remove question$")
    ],
    states={
        CHOOSE_Q_ID_TO_REMOVE: [
            CallbackQueryHandler(choose_q_to_remove, "^r\d+$")
        ]
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        back_to_question_settings_handler,
    ],
)
