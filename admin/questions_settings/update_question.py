from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from admin.questions_settings.functions import build_questions_keyboard
from admin.questions_settings.question_settings import back_to_question_settings_handler
from custom_filters import *
from start import start_command
from DB import DB
from common import (
    build_back_button,
    build_admin_keyboard,
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)

(
    Q_TO_UPDATE,
    CHOOSE_UPDATE_QUESTION,
    UPDATE_Q,
) = range(3)

update_question_keyboard = [
    [InlineKeyboardButton(text="السؤال❓", callback_data="update question")],
    [InlineKeyboardButton(text="الجواب❗️", callback_data="update answer")],
    build_back_button("back to update question"),
    back_to_admin_home_page_button[0],
]


async def update_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_questions_keyboard("u")

        if not keyboard:
            await update.callback_query.answer("ليس لديك أسئلة بعد ❗️", show_alert=True)
            return ConversationHandler.END

        await update.callback_query.edit_message_text(
            text="اختر السؤال الذي تريد تعديله",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return Q_TO_UPDATE


async def q_to_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if not update.callback_query.data.startswith("back"):
            context.user_data["q_id_to_update"] = int(update.callback_query.data[1:])
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text="هل تريد تعديل؟",
            reply_markup=InlineKeyboardMarkup(update_question_keyboard),
        )
        return CHOOSE_UPDATE_QUESTION


back_to_update_question = update_question


async def choose_update_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        what_to_update = update.callback_query.data.split(" ")[-1]
        context.user_data["what_to_update"] = what_to_update
        back_buttons = [
            build_back_button("back to q to update"),
            back_to_admin_home_page_button[0],
        ]
        text = ""
        if what_to_update == "question":
            text = ("أرسل نص السؤال الجديد",)
        elif what_to_update == "answer":
            text = ("أرسل الجواب الجديد",)

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return UPDATE_Q


back_to_q_to_update = q_to_update


async def update_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        q = DB.get_question(q_id=context.user_data["q_id_to_update"])
        q[context.user_data["what_to_update"]] = update.message.text
        await DB.update_question(
            q_id=context.user_data["q_id_to_update"],
            new_q=q["question"],
            new_a=q["answer"],
        )
        await update.message.reply_text(
            text="تم التعديل بنجاح✅",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


update_question_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            update_question,
            "^update question$",
        ),
    ],
    states={
        Q_TO_UPDATE: [CallbackQueryHandler(q_to_update, "^q\d+$")],
        CHOOSE_UPDATE_QUESTION: [
            CallbackQueryHandler(
                choose_update_question, "^update ((question)|(answer))$"
            )
        ],
        UPDATE_Q: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND, callback=choose_update_question
            )
        ],
    },
    fallbacks=[
        start_command,
        back_to_admin_home_page_handler,
        back_to_question_settings_handler,
        CallbackQueryHandler(back_to_q_to_update, "^back to q to update$"),
        CallbackQueryHandler(back_to_update_question, "^back to update question$"),
    ],
)
