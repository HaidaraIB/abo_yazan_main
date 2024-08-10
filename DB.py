import sqlite3
import os
import re
from asyncio import Lock

lock = Lock()


def lock_and_release(func):
    async def wrapper(*args, **kwargs):
        db = None
        cr = None
        try:
            await lock.acquire()
            db = sqlite3.connect(os.getenv("DB_PATH"))
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
        db = sqlite3.connect(os.getenv("DB_PATH"))
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


class DB:

    @staticmethod
    def creat_tables():
        db = sqlite3.connect(os.getenv("DB_PATH"))
        cr = db.cursor()
        script = f"""

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        );

        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY
        );

        """
        cr.executescript(script)

        db.commit()
        cr.close()
        db.close()

    @staticmethod
    @connect_and_close
    def check_admin(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute("SELECT * FROM admins WHERE id=?", (user_id,))
        return cr.fetchone()

    @staticmethod
    @connect_and_close
    def get_admin_ids(cr: sqlite3.Cursor = None):
        cr.execute("SELECT * FROM admins")
        return cr.fetchall()

    @staticmethod
    @lock_and_release
    async def add_new_user(
        user_id: int, username: str, name: str, cr: sqlite3.Cursor = None
    ):
        username = username if username else " "
        name = name if name else " "
        cr.execute(
            "INSERT OR IGNORE INTO users(id, username, name) VALUES(?, ?, ?)",
            (user_id, username, name),
        )

    @staticmethod
    @lock_and_release
    async def add_new_admin(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute("INSERT OR IGNORE INTO admins(id) VALUES(?)", (user_id,))

    @staticmethod
    @lock_and_release
    async def remove_admin(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute("DELETE FROM admins WHERE id = ?", (user_id,))

    @staticmethod
    @connect_and_close
    def get_user(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cr.fetchone()

    @staticmethod
    @connect_and_close
    def get_all_users(cr: sqlite3.Cursor = None):
        cr.execute("SELECT * FROM users")
        return cr.fetchall()

    @staticmethod
    @lock_and_release
    async def add_question(q: str, a: str, cr: sqlite3.Cursor = None):
        cr.execute(
            "INSERT OR IGNORE INTO questions(question, answer) VALUES(?, ?)",
            (q, a),
        )

    @staticmethod
    @lock_and_release
    async def delete_question(q_id: int, cr: sqlite3.Cursor = None):
        cr.execute(
            "DELETE FROM questions WHERE id = ?",
            (q_id,),
        )

    @staticmethod
    @lock_and_release
    async def update_question(
        q_id: int, new_q: str, new_a: str, cr: sqlite3.Cursor = None
    ):
        cr.execute(
            "UPDATE questions SET question = ?, answer = ? WHERE id = ?",
            (new_q, new_a, q_id),
        )

    @staticmethod
    @connect_and_close
    def get_question(q_id: int, cr: sqlite3.Cursor = None):
        cr.execute(
            "SELECT * FROM questions WHERE id = ?",
            (q_id,),
        )
        return cr.fetchone()

    @staticmethod
    @connect_and_close
    def get_all_question(cr: sqlite3.Cursor = None):
        cr.execute(
            "SELECT * FROM questions",
        )
        return cr.fetchall()
