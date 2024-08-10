from telegram import InlineKeyboardButton
from DB import DB
from common import back_to_admin_home_page_button, back_to_user_home_page_button


def build_questions_keyboard(op: str, role: str = "admin"):
    qs = DB.get_all_question()
    if not qs:
        return []
    qs_keyboard = [
        [InlineKeyboardButton(text=str(q["question"]), callback_data=op + str(q["id"]))]
        for q in qs
    ]
    if role=="admin":
        qs_keyboard.append(
            [
                InlineKeyboardButton(
                    text="الرجوع🔙", callback_data="back to question settings"
                )
            ]
        )
        qs_keyboard.append(back_to_admin_home_page_button[0])
    else:
        qs_keyboard.append(back_to_user_home_page_button[0])

    return qs_keyboard
