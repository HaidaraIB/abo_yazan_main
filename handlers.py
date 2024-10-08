from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    Application,
    PicklePersistence,
    InvalidCallbackData,
    Defaults,
)
from telegram.constants import ParseMode
from start import start_command, inits
from jobs import edit_ids_info, check_remote_ids
from common import (
    back_to_admin_home_page_handler,
    invalid_callback_data,
    error_handler,
    create_folders,
)
from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *
from admin.questions_settings import *
from send_id.send_id import send_id_handler
import os
from DB import DB
from PyroClientSingleton import PyroClientSingleton


def main():
    create_folders()
    DB.creat_tables()
    defaults = Defaults(parse_mode=ParseMode.HTML)
    my_persistence = PicklePersistence(filepath="data/persistence", single_file=False)
    app = (
        Application.builder()
        .token(os.getenv("BOT_TOKEN"))
        .post_init(inits)
        .persistence(persistence=my_persistence)
        .defaults(defaults)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )
    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    # QUESTIONS SETTINGS
    app.add_handler(question_settings_handler)
    app.add_handler(add_question_handler)
    app.add_handler(remove_question_handler)
    app.add_handler(update_question_handler)
    app.add_handler(show_questions_handler)

    app.add_handler(broadcast_message_handler)

    # app.add_handler(check_joined_handler)

    app.add_handler(ban_unban_user_handler)

    # # FAQ
    # app.add_handler(faq_handler)
    # app.add_handler(q_to_show_user_handler)

    # JOIN CHANNELS
    # app.add_handler(join_vip_handler)
    # app.add_handler(join_edu_handler)

    # SEND ID
    app.add_handler(send_id_handler)

    app.add_handler(start_command)
    # app.add_handler(find_id_handler)
    # app.add_handler(hide_ids_keyboard_handler)
    # app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    app.job_queue.run_once(callback=edit_ids_info, when=10)
    app.job_queue.run_once(callback=check_remote_ids, when=10)

    try:
        PyroClientSingleton().start()
    except ConnectionError:
        pass

    app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

    try:
        PyroClientSingleton().stop()
    except ConnectionError:
        pass
