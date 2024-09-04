from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Chat,
    error,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
)
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from telegram.constants import ChatType
from telegram.error import TimedOut, NetworkError
import os
import uuid
import traceback
import json
import mysql.connector
from custom_filters import User, Admin
from dotenv import load_dotenv

load_dotenv()

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def edit_message_text(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    text: str,
):
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except error.BadRequest as e:
        if "Message is not modified:" in e.message:
            pass
        else:
            write_error(
                f"{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}\n\n"
            )


def build_user_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="(للدخول إلى جروب VIP)", callback_data="join vip")],
        # [InlineKeyboardButton(text="الدخول القناه التعليميه", callback_data="join edu")],
        # [InlineKeyboardButton(text="الأسئلة الشائعة ⁉️", callback_data="faq")],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن⚙️🎛",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="حظر/فك حظر 🔓🔒",
                callback_data="ban unban",
            )
        ],
        [
            InlineKeyboardButton(
                text="إعدادات الأسئلة❓",
                callback_data="questions settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_button(data: str):
    return [InlineKeyboardButton(text="الرجوع🔙", callback_data=data)]


def callback_button_uuid_generator():
    return uuid.uuid4().hex


def stringify_question(q):
    return "السؤال:\n" f"{q['question']}\n\n" "الجواب:\n" f"{q['answer']}"


back_to_admin_home_page_button = [
    [
        InlineKeyboardButton(
            text="العودة إلى القائمة الرئيسية🔙",
            callback_data="back to admin home page",
        )
    ],
]

back_to_user_home_page_button = [
    [
        InlineKeyboardButton(
            text="الرجوع🔙",
            callback_data="back to user home page",
        )
    ],
]


async def back_to_user_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        await update.callback_query.edit_message_text(
            text="القائمة الرئيسية🔝", reply_markup=build_user_keyboard()
        )
        return ConversationHandler.END


async def back_to_admin_home_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="القائمة الرئيسية🔝", reply_markup=build_admin_keyboard()
        )
        return ConversationHandler.END


back_to_user_home_page_handler = CallbackQueryHandler(
    back_to_user_home_page, "^back to user home page$"
)
back_to_admin_home_page_handler = CallbackQueryHandler(
    back_to_admin_home_page, "^back to admin home page$"
)


request_buttons = [
    [
        KeyboardButton(
            text="معرفة id مستخدم🆔",
            request_users=KeyboardButtonRequestUsers(request_id=0, user_is_bot=False),
        ),
        KeyboardButton(
            text="معرفة id قناة📢",
            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=True),
        ),
    ],
    [
        KeyboardButton(
            text="معرفة id مجموعة👥",
            request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False),
        ),
        KeyboardButton(
            text="معرفة id بوت🤖",
            request_users=KeyboardButtonRequestUsers(request_id=3, user_is_bot=True),
        ),
    ],
]


def create_folders():
    os.makedirs("data", exist_ok=True)


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, (TimedOut, NetworkError)):
        return
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    try:
        error = (
            f"update = {json.dumps(update_str, indent=2, ensure_ascii=False)}\n\n"
            f"user_data = {str(context.user_data)}\n"
            f"chat_data = {str(context.chat_data)}\n\n"
            f"{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}\n\n"
        )

        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(error)
    except TypeError:
        error = (
            f"update = TypeError\n\n"
            f"user_data = {str(context.user_data)}\n"
            f"chat_data = {str(context.chat_data)}\n\n"
            f"{''.join(traceback.format_exception(None, context.error, context.error.__traceback__))}\n\n"
        )
        write_error(error=error)


def write_error(error: str):
    with open("errors.txt", "a", encoding="utf-8") as f:
        f.write(error + f"{'-'*100}\n\n\n")
