import sqlite3
import re
from asyncio import Lock

lock = Lock()


def lock_and_release(func):
    async def wrapper(*args, **kwargs):
        db = None
        cr = None
        try:
            await lock.acquire()
            db = sqlite3.connect("telethon_db.sqlite3")
            db.row_factory = sqlite3.Row
            cr = db.cursor()
            result = await func(*args, **kwargs, cr=cr)
            db.commit()
            if result:
                return result
        except sqlite3.Error as e:
            print(e)
        finally:
            cr.close()
            db.close()
            lock.release()

    return wrapper


def connect_and_close(func):
    def wrapper(*args, **kwargs):
        db = sqlite3.connect("telethon_db.sqlite3")
        db.row_factory = sqlite3.Row
        db.create_function("REGEXP", 2, regexp)
        cr = db.cursor()
        result = func(*args, **kwargs, cr=cr)
        cr.close()
        db.close()
        return result

    return wrapper


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


class TelethonDB:

    @staticmethod
    def creat_tables():
        db = sqlite3.connect("telethon_db.sqlite3")
        cr = db.cursor()
        script = f"""

        CREATE TABLE IF NOT EXISTS messages (
            from_message_id INTEGER,
            to_message_id INTEGER,
            from_channel_id INTEGER,
            to_channel_id INTEGER
        );


        """
        cr.executescript(script)

        db.commit()
        cr.close()
        db.close()


    @staticmethod
    @lock_and_release
    async def add_message(
        from_message_id: int,
        to_message_id: int,
        from_channel_id: int,
        to_channel_id: int,
        cr: sqlite3.Cursor = None,
    ):
        cr.execute(
            "INSERT OR IGNORE INTO messages VALUES(?, ?, ?, ?)",
            (
                from_message_id,
                to_message_id,
                from_channel_id,
                to_channel_id,
            ),
        )

    @staticmethod
    @connect_and_close
    def get_messages(
        from_message_id: int,
        from_channel_id: int,
        to_channel_id: int,
        cr: sqlite3.Cursor = None,
    ):
        cr.execute(
            "SELECT to_message_id FROM messages WHERE from_message_id = ? AND from_channel_id = ? AND to_channel_id = ?",
            (
                from_message_id,
                from_channel_id,
                to_channel_id,
            ),
        )
        return cr.fetchone()