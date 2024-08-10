from telegram import (
    Update,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler
)

from custom_filters import *

back_to_question_settings_button = [
    InlineKeyboardButton(text="الرجوع🔙", callback_data="back to questions settings")
]

question_settings_keyboard = [
    [InlineKeyboardButton(text="إضافة سؤال➕", callback_data="add question"),
     InlineKeyboardButton(text="حذف سؤال✖️", callback_data="remove question"),
     InlineKeyboardButton(text="تعديل سؤال➗", callback_data="update question")],
     [InlineKeyboardButton(text="عرض الأسئلة➿", callback_data="show questions")],
     back_to_question_settings_button,
]

async def question_settings(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="إعدادات الأسئلة، اختر ماذا تريد أن تفعل؟",
            reply_markup=InlineKeyboardMarkup(question_settings_keyboard)
        )

back_to_question_settings = question_settings

back_to_question_settings_handler = CallbackQueryHandler(back_to_question_settings, "^back to questions settings$")
question_settings_handler = CallbackQueryHandler(question_settings, "^questions settings$")
