"""
radioplayerv2.2, Telegram Voice Chat Bot
Copyright (c) 2021 green👑
"""

from config import Config
from pyrogram import Client

REPLY_MESSAGE=Config.REPLY_MESSAGE

if REPLY_MESSAGE is not None:
    USER = Client(
        Config.SESSION,
        Config.API_ID,
        Config.API_HASH,
        plugins=dict(root="plugins.green")
        )
else:
    USER = Client(
        Config.SESSION,
        Config.API_ID,
        Config.API_HASH
        )
USER.start()
