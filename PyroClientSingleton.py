from pyrogram import Client
import os


class PyroClientSingleton(Client):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:

            cls._instance = Client(
                name=os.getenv("SESSION"),
                api_id=int(os.getenv("API_ID")),
                api_hash=os.getenv("API_HASH"),
                phone_number=os.getenv("PHONE"),
            )
        return cls._instance
