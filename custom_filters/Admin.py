from telegram import (
    Update
)

from telegram.ext.filters import (
    UpdateFilter,
)

from DB import DB


class Admin(UpdateFilter):
    def filter(self, update: Update):
        result = DB.get_admin_ids()
        admin_ids = [id[0] for id in result]

        return update.effective_user.id in admin_ids
