"""
radioplayerv2.2, Telegram Voice Chat Bot
Copyright (c) 2021  green👑
"""

from pyrogram import Client, filters, emoji
from pyrogram.types import Message
from utils import mp, RADIO, USERNAME
from config import Config, STREAM

CHAT=Config.CHAT
ADMINS=Config.ADMINS


@Client.on_message(filters.command(["radio", f"radio@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT) | filters.private))
async def radio(client, message: Message):
    if 1 in RADIO:
        k=await message.reply_text(f"{emoji.ROBOT} **Please Stop Existing Radio Stream!**")
        await mp.delete(k)
        await message.delete()
        return
    await mp.start_radio()
    k=await message.reply_text(f"{emoji.CHECK_MARK_BUTTON} **Radio Stream Started :** \n<code>{STREAM}</code>")
    l=await message.reply_sticker(f"CAACAgIAAxkBAAKJBGD46GSfEz_B3CFAH-7abvHOTfXkAAItAANOXNIpkn2HNpmRcXQgBA")
    await mp.delete(k)
    await mp.delete(l)
    await mp.delete(message)

@Client.on_message(filters.command(["stopradio", f"stopradio@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT) | filters.private))
async def stop(_, message: Message):
    if 0 in RADIO:
        k=await message.reply_text(f"{emoji.ROBOT} **Please Start A Radio Stream First By /radio Command!**")
        await mp.delete(k)
        await mp.delete(message)
        return
    await mp.stop_radio()
    k=await message.reply_text(f"{emoji.CROSS_MARK_BUTTON} **Radio Stream Ended Successfully!**")
    l=await message.reply_sticker(f"CAACAgEAAxkBAAKI9WD44j5fhLG3rDHjXiUw81s9ASVBAAL9CAAC43gEAAGblj92tuxeQiAE")
    await mp.delete(l)
    await mp.delete(k)
    await mp.delete(message)
