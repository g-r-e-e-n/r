"""
radioplayerv2.2, Telegram Voice Chat Bot
Copyright (c) 2021  greenπ
"""

import os
import sys
import asyncio
import subprocess
from signal import SIGINT
from pyrogram import Client, filters, emoji
from utils import USERNAME, FFMPEG_PROCESSES, mp
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

msg=Config.msg
CHAT=Config.CHAT
ADMINS=Config.ADMINS
playlist=Config.playlist

HOME_TEXT = "ππ» **Hi [{}](tg://user?id={})**,\n\nI'm **Radio Player V2.2** \nI Can Play Radio / Music / YouTube Live In Channel & Group 24x7 Nonstop.By κ§β¬πΆπͺπ·π²β¬κ§!"
HELP_TEXT = """
π§ --**Need Help ?**--

π·οΈ --**Common Commands**-- :

\u2022 `/play` - reply to an audio or youTube link to play it or use /play [song name]
\u2022 `/help` - shows help for commands
\u2022 `/song` [song name] - download the song as audio track
\u2022 `/menu` - shows playing time of current track
\u2022 `/playlist` - shows the current playlist with controls

π·οΈ --**Admin Commands**-- :

\u2022 `/radio` - start radio stream
\u2022 `/stopradio` - stop radio stream
\u2022 `/next` [n] - skip current or n where n >= 2
\u2022 `/join` - join the voice chat
\u2022 `/leave` - leave the voice chat
\u2022 `/stop` - stop playing music
\u2022 `/volume` - change volume (0-200)
\u2022 `/replay` - play from the beginning
\u2022 `/clean` - remove unused raw files
\u2022 `/pause` - pause playing music
\u2022 `/resume` - resume playing music
\u2022 `/mute` - mute the vc userbot
\u2022 `/unmute` - unmute the vc userbot
\u2022 `/restart` - restart the bot
\u2022 `/update` - update the bot to latest

Β© **Powered By** : 
**κ§β¬πΆπͺπ·π²β¬κ§** π
"""


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.from_user.id not in Config.ADMINS and query.data != "help":
        await query.answer(
            "You're Not Allowed π€£!",
            show_alert=True
            )
        return
    else:
        await query.answer()
    if query.data == "replay":
        group_call = mp.group_call
        if not playlist:
            return
        group_call.restart_playout()
        if not playlist:
            pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await query.edit_message_text(
                f"{pl}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("π", callback_data="replay"),
                            InlineKeyboardButton("βΈ", callback_data="pause"),
                            InlineKeyboardButton("β­", callback_data="next")
                            
                        ],
                    ]
                )
            )

    elif query.data == "pause":
        if not playlist:
            return
        else:
            mp.group_call.pause_playout()
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  **Requested By:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await query.edit_message_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} **Paused !**\n\n{pl}",
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("π", callback_data="replay"),
                            InlineKeyboardButton("βΆοΈ", callback_data="resume"),
                            InlineKeyboardButton("β­", callback_data="next")
                            
                        ],
                    ]
                )
            )

    elif query.data == "resume":   
        if not playlist:
            return
        else:
            mp.group_call.resume_playout()
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        await query.edit_message_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} **Resumed !**\n\n{pl}",
        reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("π", callback_data="replay"),
                            InlineKeyboardButton("βΈ", callback_data="pause"),
                            InlineKeyboardButton("β­", callback_data="next")
                            
                        ],
                    ]
                )
            )

    elif query.data=="next":   
        if not playlist:
            return
        else:
            await mp.skip_current_playing()
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        try:
            await query.edit_message_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} **Skipped !**\n\n{pl}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("π", callback_data="replay"),
                        InlineKeyboardButton("βΈ", callback_data="pause"),
                        InlineKeyboardButton("β­", callback_data="next")
                            
                    ],
                ]
            )
        )
        except:
            pass
    elif query.data=="help":
        buttons = [
            [
                InlineKeyboardButton("CLOSE π", callback_data="close"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(
            HELP_TEXT,
            reply_markup=reply_markup

        )

    elif query.data=="close":
        await query.message.delete()


@Client.on_message(filters.command(["start", f"start@{USERNAME}"]))
async def start(client, message):
    buttons = [
            [
                InlineKeyboardButton("HOW TO USE β", callback_data="help"),
            ]
            ]
    reply_markup = InlineKeyboardMarkup(buttons)
    m=await message.reply_photo(photo="https://telegra.ph/file/8f14823545ccefd8a158b.jpg", caption=HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)
    await mp.delete(m)
    await mp.delete(message)



@Client.on_message(filters.command(["help", f"help@{USERNAME}"]))
async def help(client, message):
    buttons = [
            [
                InlineKeyboardButton("CLOSE π", callback_data="close"),
            ]
            ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if msg.get('help') is not None:
        await msg['help'].delete()
    msg['help'] = await message.reply_photo(photo="https://telegra.ph/file/8f14823545ccefd8a158b.jpg", caption=HELP_TEXT, reply_markup=reply_markup)
    await mp.delete(message)

@Client.on_message(filters.command(["restart", f"restart@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT) | filters.private))
async def restart(client, message):
    m=await message.reply_sticker(f"CAACAgEAAxkBAAKInWD4Qc_nONV7824rezyHW5Kej2aEAAIcCQAC43gEAAH_gQf4a0ronSAE")
    await mp.delete(m)
    await mp.delete(message)
    process = FFMPEG_PROCESSES.get(CHAT)
    if process:
        try:
            process.send_signal(SIGINT)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            print(e)
            pass
        FFMPEG_PROCESSES[CHAT] = ""
    os.execl(sys.executable, sys.executable, *sys.argv)
