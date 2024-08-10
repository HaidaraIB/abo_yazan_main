from telegram import (
    Update,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)

from custom_filters import User
from common import back_to_user_home_page_button


async def join_edu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        text = (
            "💫⚜️شروط الانضمام لجروب VIP⚜️💫\n"
            "----------------------------------------------------------------\n"
            "1- حذف حسابك القديم\n"
            "----------------------------------------------------------------\n"
            "2- وإنشاء حساب جديد من هذا الرابط\n"
            "----------------------------------------------------------------\n"
            "https://broker-qx.pro/sign-up/?lid=788615\n"
            "----------------------------------------------------------------\n"
            "للحصول على بونص 50% 👈aboyazan\n"
            "----------------------------------------------------------------\n"
            "3- إيداع 10دولار\n"
            "----------------------------------------------------------------\n"
            "4- إرسال ID كتابه .\n"
            "----------------------------------------------------------------\n"
            "بالتوفيق للجميع 🫡\n"
        )
        send_id_button = [
            [
                InlineKeyboardButton(
                    text="(أرسل ID حسابك هنا كتابةً )", callback_data="send id"
                )
            ],
            back_to_user_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(send_id_button)
        )


join_edu_handler = CallbackQueryHandler(join_edu, "^join edu$")
