from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)

from custom_filters import User
from common import stringify_question, check_if_user_member

from admin.questions_settings.functions import build_questions_keyboard

from DB import DB


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):

        # member = await check_if_user_member(update=update, context=context)
        # if not member:
        #     return
        
        keyboard = build_questions_keyboard(op="faq", role="user")
        if not keyboard:
            await update.callback_query.answer(
                "ليس هناك أسئلة شائعة ❗️", show_alert=True
            )
            return
        await update.callback_query.edit_message_text(
            text="اضغط على السؤال لعرضه مع الإجابة عليه👇🏻",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def q_to_show_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):

        # member = await check_if_user_member(update=update, context=context)
        # if not member:
        #     return
        
        q_id = int(update.callback_query.data[3:])
        q = DB.get_question(q_id=q_id)
        try:
            await update.callback_query.edit_message_text(
                text=stringify_question(q),
                reply_markup=InlineKeyboardMarkup(
                    build_questions_keyboard(op="faq", role="user")
                ),
            )
        except:
            pass


faq_handler = CallbackQueryHandler(faq, "^faq$")
q_to_show_user_handler = CallbackQueryHandler(q_to_show_user, "^faq\d+$")
