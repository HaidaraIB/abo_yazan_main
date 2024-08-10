from telegram import (
    Update,
)

from telegram import Chat
from telegram.ext.filters import (
    UpdateFilter
)
from DB import DB

class User(UpdateFilter):
    def filter(self, update: Update):
        user = DB.get_user(user_id=update.effective_user.id)
        result = DB.get_admin_ids()
        admin_ids = [id[0] for id in result]
        return update.effective_user.id not in admin_ids