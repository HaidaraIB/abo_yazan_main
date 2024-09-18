from pyrogram import Client
import os
import mysql.connector


class MySqlConnSingleton(Client):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:

            cls._instance = mysql.connector.connect(
                host=os.getenv("REMOTE_DB_HOST"),
                user=os.getenv("REMOTE_DB_USERNAME"),
                password=os.getenv("REMOTE_DB_PASSWORD"),
                database=os.getenv("REMOTE_DB_NAME"),
            )
        return cls._instance
