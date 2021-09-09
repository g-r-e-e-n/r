"""
radioplayerv2.2, Telegram Voice Chat Bot
Copyright (c) 2021  green👑
"""

import os
import time
import ffmpeg
import asyncio
import aiohttp
import requests
import youtube_dl
from pyrogram import Client, filters
from config import Config
from utils import USERNAME, mp
from youtube_search import YoutubeSearch

CHAT=Config.CHAT

## Extra Fns -------------------------------

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------------------------------

@Client.on_message(filters.command(["song", f"song@{USERNAME}"]) & (filters.chat(CHAT) | filters.private))
async def song(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    k=await message.reply_text("🔍 **Searching Song...**")
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "geo-bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        }
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count > 0:
                await time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            views = results[0]["views"]

            ## UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            # if time_to_seconds(duration) >= 1800:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            performer = f"[ᵍʳᵉᵉᶰ ᵐᵘˢᶤᶜ ʰᵒᵘˢᵉ]" 
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            await k.edit('❌ **Found Literary Noting! \nPlease Try Another Song or Use Correct Spelling.**')
            return
    except Exception as e:
        await k.edit(
            "❗ **Enter An Song Name!** \nFor Example: `/song Alone Marshmellow`"
        )
        print(str(e))
        return
    await k.edit("📥 **Downloading Song...**")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        cap = f'🏷 <b>Title:</b> <a href="{link}">{title}</a>\n⏳ <b>Duration:</b> <code>{duration}</code>\n👀 <b>Views:</b> <code>{views}</code>\n🎧 <b>Requested By:</b> {message.from_user.mention()} \n📤 <b>Uploaded By: ꧁☬𝓶𝓪𝓷𝓲☬꧂</b> 👑'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        await k.edit("📤 **Uploading Song...**")
        await message.reply_audio(audio_file, caption=cap, parse_mode='HTML', title=title, duration=dur, performer=performer, thumb=thumb_name)
        await mp.delete(k)
        await mp.delete(message)
    except Exception as e:
        await k.edit(f'❌ **An Error Occured!** \n\nError:- {e}')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
