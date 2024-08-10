from telegram import (
    Chat,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from common import (
    build_admin_keyboard,
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)

from start import start_command

import os
from DB import DB
from custom_filters.Admin import Admin

(NEW_ADMIN_ID, CHOOSE_ADMIN_ID_TO_REMOVE) = range(2)

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        admin_settings_keyboard = [
            [
                InlineKeyboardButton(text="إضافة آدمن➕", callback_data="add admin"),
                InlineKeyboardButton(text="حذف آدمن✖️", callback_data="remove admin"),
            ],
            [
                InlineKeyboardButton(
                    text="عرض آيديات الآدمنز الحاليين🆔", callback_data="show admins"
                )
            ],
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="إعدادات الآدمن🪄",
            reply_markup=InlineKeyboardMarkup(admin_settings_keyboard),
        )


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        back_button = [
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to admin settings"
                )
            ]
        ]
        await update.callback_query.edit_message_text(
            text="أرسل id المستخدم الذي تريد إضافته كآدمن.\nيمكنك معرفة الآيدي عن طريق كيبورد معرفة الآيديات، قم بالضغط على /start وإظهاره إن كان مخفياً.",
            reply_markup=InlineKeyboardMarkup(back_button),
        )
        return NEW_ADMIN_ID


async def new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await DB.add_new_admin(user_id=int(update.message.text))
        text = "تمت إضافة الآدمن بنجاح✅."
        await update.message.reply_text(text=text, reply_markup=build_admin_keyboard())
        return ConversationHandler.END


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        admins = DB.get_admin_ids()
        admin_ids_keyboard = [
            [InlineKeyboardButton(text=str(admin[0]), callback_data=str(admin[0]))]
            for admin in admins
        ]
        admin_ids_keyboard.append(
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to admin settings"
                )
            ]
        )
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه id الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )
        return CHOOSE_ADMIN_ID_TO_REMOVE


async def choose_admin_id_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        admin_id = int(update.callback_query.data)
        if admin_id == int(os.getenv("OWNER_ID")):
            await update.callback_query.answer(
                text="لا يمكنك إزالة مالك البوت من قائمة الآدمنز❗️"
            )
            return

        await DB.remove_admin(user_id=admin_id)
        await update.callback_query.answer(text="تمت إزالة الآدمن بنجاح✅")
        admins = DB.get_admin_ids()
        admin_ids_keyboard = [
            [InlineKeyboardButton(text=str(admin[0]), callback_data=str(admin[0]))]
            for admin in admins
        ]
        admin_ids_keyboard.append(
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to admin settings"
                )
            ]
        )
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه id الآدمن الذي تريد إزالته.",
            reply_markup=InlineKeyboardMarkup(admin_ids_keyboard),
        )

        return CHOOSE_ADMIN_ID_TO_REMOVE


async def back_to_admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        admin_settings_keyboard = [
            [
                InlineKeyboardButton(text="إضافة آدمن➕", callback_data="add admin"),
                InlineKeyboardButton(text="حذف آدمن✖️", callback_data="remove admin"),
            ],
            [
                InlineKeyboardButton(
                    text="عرض آيديات الآدمنز الحاليين🆔", callback_data="show admins"
                )
            ],
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="هل تريد:", reply_markup=InlineKeyboardMarkup(admin_settings_keyboard)
        )
        return ConversationHandler.END


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = DB.get_admin_ids()
    text = "آيديات الآدمنز الحاليين:\n\n"
    for admin in admins:
        if admin[0] == int(os.getenv("OWNER_ID")):
            text += "<code>" + str(admin[0]) + "</code>" + " <b>مالك البوت</b>\n"
            continue
        text += "<code>" + str(admin[0]) + "</code>" + "\n"
    text += "\nاختر ماذا تريد أن تفعل:"
    keyboard = build_admin_keyboard()
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
    )


admin_settings_handler = CallbackQueryHandler(admin_settings, "^admin settings$")

show_admins_handler = CallbackQueryHandler(
    callback=show_admins, pattern="^show admins$"
)

add_admin_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=add_admin, pattern="^add admin$")],
    states={
        NEW_ADMIN_ID: [
            MessageHandler(filters=filters.Regex("^\d+$"), callback=new_admin_id)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_admin_settings, pattern="^back to admin settings$"
        ),
        start_command,
        back_to_admin_home_page_handler,
    ],
)

remove_admin_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=remove_admin, pattern="^remove admin$")
    ],
    states={
        CHOOSE_ADMIN_ID_TO_REMOVE: [
            CallbackQueryHandler(choose_admin_id_to_remove, "^\d+$")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_admin_settings, pattern="^back to admin settings$"
        ),
        start_command,
        back_to_admin_home_page_handler,
    ],
)
