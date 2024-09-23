import os
import mysql.connector


class MySqlConnSingleton:
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

    @classmethod
    def destroy(cls):
        if cls._instance:
            cls._instance.shutdown()
            cls._instance = None
