import sqlite3
import mysql.connector
import os
import re
from asyncio import Lock

import mysql.connector.abstracts
import mysql.connector.cursor

lock = Lock()


def connect_to_remote(func):
    def wrapper(*args, **kwargs):
        db = mysql.connector.connect(
            host=os.getenv("REMOTE_DB_HOST"),
            user=os.getenv("REMOTE_DB_USERNAME"),
            password=os.getenv("REMOTE_DB_PASSWORD"),
            database=os.getenv("REMOTE_DB_NAME"),
        )
        cr = db.cursor(dictionary=True)
        result = func(*args, **kwargs, cr=cr)
        db.commit()
        cr.close()
        db.close()
        if result:
            return result

    return wrapper


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

        CREATE TABLE IF NOT EXISTS ids (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            message_id INTEGER,
            message_text TEXT,
            is_closed BOOLEAN DEFAULT 0,
            store_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    @staticmethod
    @lock_and_release
    async def add_id(
        i: int,
        user_id: int,
        message_id: int,
        message_text: str,
        is_closed: bool,
        cr: sqlite3.Cursor = None,
    ):
        cr.execute(
            "INSERT INTO ids(id, user_id, message_id, message_text, is_closed) VALUES(?, ?, ?, ?, ?)",
            (i, user_id, message_id, message_text, is_closed),
        )

    @staticmethod
    @lock_and_release
    async def update_message_text(i: int, new_text: str, cr: sqlite3.Cursor = None):
        cr.execute("UPDATE ids SET message_text = ? WHERE id = ?", (new_text, i))

    @staticmethod
    @lock_and_release
    async def close_account(i: int, cr: sqlite3.Cursor = None):
        cr.execute("UPDATE ids SET is_closed = 1 WHERE id = ?", (i,))

    @staticmethod
    @connect_and_close
    def get_ids(i: int = None, cr: sqlite3.Cursor = None):
        if i:
            cr.execute("SELECT * FROM ids WHERE id = ?", (i,))
            return cr.fetchone()
        else:
            cr.execute("SELECT * FROM ids")
            return cr.fetchall()

    @staticmethod
    @connect_to_remote
    def insert_into_remote_db(
        data: list,
        is_closed: int,
        cr: mysql.connector.abstracts.MySQLCursorAbstract = None,
    ):
        cr.execute(
            f"""
            INSERT INTO transactions (
                `trader-id`,
                `country`,
                `registery-date`,
                `balance`,
                `deposits-count`,
                `deposits-sum`,
                `withdrawals-count`,
                `withdrawals-sum`,
                `turnover-clear`,
                `vol-share`,
                `is-closed`
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (*data, is_closed),
        )

    @staticmethod
    @connect_to_remote
    def update_into_remote_db(
        data: list,
        is_closed: int,
        cr: mysql.connector.abstracts.MySQLCursorAbstract = None,
    ):
        cr.execute(
            f"""
                UPDATE transactions SET
                    `balance` = %s,
                    `deposits-count` = %s,
                    `deposits-sum` = %s,
                    `withdrawals-count` = %s,
                    `withdrawals-sum` = %s,
                    `turnover-clear` = %s,
                    `vol-share` = %s,
                    `is-closed` = %s
                WHERE `trader-id` = %s;
            """,
            (*data[3:], is_closed, data[0]),
        )

    @staticmethod
    @connect_to_remote
    def get_from_remote_db(
        trader_id: int, cr: mysql.connector.abstracts.MySQLCursorAbstract = None
    ):
        cr.execute(
            f"""
                SELECT * FROM transactions
                WHERE `trader-id` = %s;
            """,
            (trader_id,),
        )

        return cr.fetchone()

    @staticmethod
    @connect_to_remote
    def get_trader_ids_to_check(
        cr: mysql.connector.abstracts.MySQLCursorAbstract = None,
    ):

        cr.execute(
            f"""
                SELECT * FROM traderstest
            """
        )

        return cr.fetchall()

    @staticmethod
    @connect_to_remote
    def delete_checked_remote_id(
        i: int, cr: mysql.connector.abstracts.MySQLCursorAbstract = None
    ):
        cr.execute(
            """
                DELETE FROM traderstest WHERE trader_id = %s
            """,
            (i,),
        )
