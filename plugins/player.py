"""
radioplayerv2.2, Telegram Voice Chat Bot
Copyright (c) 2021  green👑
"""

import os
import re
import asyncio
import subprocess
from signal import SIGINT
from youtube_dl import YoutubeDL
from config import Config
from pyrogram import Client, filters, emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from utils import mp, RADIO, USERNAME, FFMPEG_PROCESSES
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch


msg=Config.msg
playlist=Config.playlist
CHAT=Config.CHAT
ADMINS=Config.ADMINS
LOG_GROUP=Config.LOG_GROUP
RADIO_TITLE=Config.RADIO_TITLE
EDIT_TITLE=Config.EDIT_TITLE
ADMIN_ONLY=Config.ADMIN_ONLY
DURATION_LIMIT=Config.DURATION_LIMIT

async def is_admin(_, client, message: Message):
    admins = await mp.get_admins(CHAT)
    if message.from_user is None and message.sender_chat:
        return True
    if message.from_user.id in admins:
        return True
    else:
        return False

ADMINS_FILTER = filters.create(is_admin)



@Client.on_message(filters.command(["play", f"play@{USERNAME}"]) & (filters.chat(CHAT) | filters.private) | filters.audio & filters.private)
async def yplay(_, message: Message):
    if ADMIN_ONLY == "True":
        admins = await mp.get_admins(CHAT)
        if message.from_user.id not in admins:
            m=await message.reply_sticker(f"CAACAgUAAxkBAAECEkVg-AVwBlti3gbzIfeO21Q3wgS90wACIgADP4WmMVO8R-6oAxpDIAQ")
            await mp.delete(m)
            await mp.delete(message)
            return
    type=""
    yturl=""
    ysearch=""
    if message.audio:
        type="audio"
        m_audio = message
    elif message.reply_to_message and message.reply_to_message.audio:
        type="audio"
        m_audio = message.reply_to_message
    else:
        if message.reply_to_message:
            link=message.reply_to_message.text
            regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
            match = re.match(regex,link)
            if match:
                type="youtube"
                yturl=link
        elif " " in message.text:
            text = message.text.split(" ", 1)
            query = text[1]
            regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
            match = re.match(regex,query)
            if match:
                type="youtube"
                yturl=query
            else:
                type="query"
                ysearch=query
        else:
            d=await message.reply_text("❗️ __You Didn't Give Me Anything To Play, Send Me An Audio File or Reply /play To An Audio File!__")
            l=await message.reply_sticker("CAACAgIAAxkBAAKJImD4_eM7CRUcsBRFSxUiG-sShYHoAAIrAAOvxlEaRqWK_J559uAgBA")
            await mp.delete(l)
            await mp.delete(d)
            await mp.delete(message)
            return
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    group_call = mp.group_call
    if type=="audio":
        if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
            d=await message.reply_text(f"❌ __Audios Longer Than {DURATION_LIMIT} Minute(s) Aren't Allowed, The Provided Audio Is {round(m_audio.audio.duration/60)} Minute(s)!__")
            l=await message.reply_sticker(f"CAACAgIAAxkBAAKJH2D4_AIOSsdQQvGd4oURkJOTmCVuAAKfAAQ4oArNFf26LBCxFCAE")
            await mp.delete(l)
            await mp.delete(d)
            await mp.delete(message)
            return
        if playlist and playlist[-1][2] == m_audio.audio.file_id:
            d=await message.reply_text(f"{emoji.ROBOT} **Already Added To Playlist!**")
            await mp.delete(d)
            await mp.delete(message)
            return
        data={1:m_audio.audio.title, 2:m_audio.audio.file_id, 3:"telegram", 4:user}
        playlist.append(data)
        if len(playlist) == 1:
            m_status = await message.reply_text(
                f"**Loading...**"
            )
            l=await message.reply_sticker(f"CAACAgEAAxkBAAKJDGD46vznGAvLBlOQaG_59K5RlGsaAAIDCQAC43gEAAGmNc2l6ho94iAE")
            await mp.delete(l)
            await message.delete(message)
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
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
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][1]
            group_call.input_filename = os.path.join(
                _.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )
            await m_status.delete()
            print(f"- START PLAYING: {playlist[0][1]}")
        if not playlist:
            pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"
        else:   
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        if EDIT_TITLE:
            await mp.edit_title()
        if message.chat.type == "private":
            await message.reply_text(pl)        
        elif LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and message.chat.type == "supergroup":
            k=await message.reply_text(pl)
            await mp.delete(k)
        for track in playlist[:2]:
            await mp.download_audio(track)


    if type=="youtube" or type=="query":
        if type=="youtube":
            msg = await message.reply_text("**Loading...**")
            l=await message.reply_sticker(f"CAACAgEAAxkBAAKJHGD4-DVk4qBX51iFnDAtwIVJROFKAAL5CAAC43gEAAGJv7TJmwyJOiAE")
            await mp.delete(l)
            await message.delete(message)
            url=yturl
        elif type=="query":
            try:
                msg = await message.reply_text("**Loading...**")
                l=await message.reply_sticker(f"CAACAgEAAxkBAAKJE2D47TS-3U_RMUTmquyvX-0XncksAAL6CAAC43gEAAGV1HMXl9XkiSAE")
                await mp.delete(l)
                await message.delete(message)
                ytquery=ysearch
                results = YoutubeSearch(ytquery, max_results=1).to_dict()
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:40]
            except Exception as e:
                await msg.edit(
                    "**Literary Found Noting**!\nTry Searching On Inline 😉!"
                )
                l=await message.reply_sticker(f"CAACAgIAAxkBAAKJFmD47c3iAs2-7ylzj3grbqiab8J3AALOAAP3AsgPXJhH4MyrboogBA")
                await mp.delete(l)
                await message.delete(message)
                print(str(e))
                return
                await mp.delete(message)
                await mp.delete(msg)
        else:
            return
        ydl_opts = {
            "geo-bypass": True,
            "nocheckcertificate": True
        }
        ydl = YoutubeDL(ydl_opts)
        try:
            info = ydl.extract_info(url, False)
        except Exception as e:
            print(e)
            k=await msg.edit(
                f"❌ **YouTube Download Error!** \n\nError:- {e}"
                )
            print(str(e))
            await mp.delete(message)
            await mp.delete(k)
            return
        duration = round(info["duration"] / 60)
        title= info["title"]
        if int(duration) > DURATION_LIMIT:
            k=await message.reply_text(f"❌ __Videos Longer Than {DURATION_LIMIT} Minute(s) Aren't Allowed, The Provided Video Is {duration} Minute(s)!__")
            l=await message.reply_sticker(f"CAACAgIAAxkBAAKJH2D4_AIOSsdQQvGd4oURkJOTmCVuAAKfAAQ4oArNFf26LBCxFCAE")
            await mp.delete(l)
            await mp.delete(k)
            await mp.delete(message)
            return
        data={1:title, 2:url, 3:"youtube", 4:user}
        playlist.append(data)
        group_call = mp.group_call
        client = group_call.client
        if len(playlist) == 1:
            m_status = await msg.edit(
                f"Got it..."
            )
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
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
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][1]
            group_call.input_filename = os.path.join(
                client.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )
            await m_status.delete()
            print(f"- START PLAYING: {playlist[0][1]}")
        else:
            await msg.delete()
        if not playlist:
            pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
                for i, x in enumerate(playlist)
                ])
        if EDIT_TITLE:
            await mp.edit_title()
        if message.chat.type == "private":
            await message.reply_text(pl)
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and message.chat.type == "supergroup":
            k=await message.reply_text(pl)
            await mp.delete(k)
        for track in playlist[:2]:
            await mp.download_audio(track)
    await mp.delete(message)


@Client.on_message(filters.command(["menu", f"menu@{USERNAME}"]) & (filters.chat(CHAT) | filters.private))
async def current(_, m: Message):
    if not playlist:
        l=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(l)
        await m.delete()
        return
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    if m.chat.type == "private":
        await m.reply_text(
            pl,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="replay"),
                        InlineKeyboardButton("⏸", callback_data="pause"),
                        InlineKeyboardButton("⏭", callback_data="next")
                    
                    ],

                ]
                )
        )
    else:
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await m.reply_text(
            pl,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄", callback_data="replay"),
                        InlineKeyboardButton("⏸", callback_data="pause"),
                        InlineKeyboardButton("⏭", callback_data="next")
                    
                    ],

                ]
                )
        )
    await mp.delete(m)


@Client.on_message(filters.command(["volume", f"volume@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def set_vol(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.ROBOT} **Didn't Joined Any Voice Chat!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if len(m.command) < 2:
        k=await m.reply_text(f"{emoji.ROBOT} **You Forgot To Pass Volume (0-200)!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_my_volume(int(m.command[1]))
    k=await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} **Volume Set To {m.command[1]}!**")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["next", f"next@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def skip_track(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        l=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(l)
        await m.delete()
        return
    if len(m.command) == 1:
        await mp.skip_current_playing()
        if not playlist:
            pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
        if m.chat.type == "private":
            await m.reply_text(pl)
        if LOG_GROUP:
            await mp.send_playlist()
        elif not LOG_GROUP and m.chat.type == "supergroup":
            k=await m.reply_text(pl)
            await mp.delete(k)
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            text = []
            for i in items:
                if 2 <= i <= (len(playlist) - 1):
                    audio = f"{playlist[i][1]}"
                    playlist.pop(i)
                    text.append(f"{emoji.WASTEBASKET} **Succesfully Skipped** - {i}. **{audio}**")
                else:
                    text.append(f"{emoji.CROSS_MARK} **Can't Skip First Two Song** - {i}")
            k=await m.reply_text("\n".join(text))
            await mp.delete(k)
            if not playlist:
                pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"
            else:
                pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
                    f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
                    for i, x in enumerate(playlist)
                    ])
            if m.chat.type == "private":
                await m.reply_text(pl)
            if LOG_GROUP:
                await mp.send_playlist()
            elif not LOG_GROUP and m.chat.type == "supergroup":
                k=await m.reply_text(pl)
                await mp.delete(k)
        except (ValueError, TypeError):
            k=await m.reply_text(f"{emoji.NO_ENTRY} **Invalid Input!**",
                                       disable_web_page_preview=True)
            await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["join", f"join@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def join_group_call(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgIAAxkBAAKJXGD5Ee5pyjFi2dvSX_Gx4rD2BzkwAALxAAP3AsgPpyvTEE4AAXhHIAQ")
        await mp.delete(k)
        await mp.delete(m)
        return
    await mp.start_call()
    chat = await client.get_chat(CHAT)
    k=await m.reply_sticker(f"CAACAgUAAxkBAAKJK2D5AS2zZbt1gTMq5aUivCNK-AjwAAKAAAM_haYxfMITnqDOPrIgBA")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["leave", f"leave@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def leave_voice_chat(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgIAAxkBAAKJLmD5Ag0_TnimUpsVE7O5oolzHUNkAAIiAAOvxlEa1hH3OwW9VWcgBA")
        await mp.delete(k)
        await mp.delete(m)
        return
    playlist.clear()
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.input_filename = ''
    await group_call.stop()
    k=await m.reply_sticker(f"CAACAgIAAxkBAAKJNGD5BN482rgvQnMTM3FhgBWJbj-CAAJWAANBtVYM1ZNlBU-tNFYgBA")
    await mp.delete(k)
    await mp.delete(m)



@Client.on_message(filters.command(["stop", f"stop@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def stop_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.stop_playout()
    k=await m.reply_sticker(f"CAACAgIAAxkBAAKJSmD5DqUFQzXWRQkAASRnTSsB0bDOlwACxQADR_sJDBAWmdq78XPaIAQ")
    playlist.clear()
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["replay", f"replay@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def restart_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    if not playlist:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    group_call.restart_playout()
    k=await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "**Playing From The Beginning!**"
    )
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["pause", f"pause@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def pause_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.pause_playout()
    k=await m.reply__sticker(f"CAACAgEAAxkBAAKJSWD5DqWSZ6pcvxub9sNSsqwPycj4AAIXCQAC43gEAAGYcjO94dFR7SAE",
                               quote=False)
    await mp.delete(k)
    await mp.delete(m)



@Client.on_message(filters.command(["resume", f"resume@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def resume_playing(_, m: Message):
    if not mp.group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.resume_playout()
    k=await m.reply_sticker(f"CAACAgIAAxkBAAKJKGD5AAHPYbzqx7Qu3HZeDb_JzHElMgACiA8AAlMr0EqExOGtL6VYTCAE",
                               quote=False)
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["clean", f"clean@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def clean_raw_pcm(client, m: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    all_fn: list[str] = os.listdir(download_dir)
    for track in playlist[:2]:
        track_fn = f"{track[1]}.raw"
        if track_fn in all_fn:
            all_fn.remove(track_fn)
    count = 0
    if all_fn:
        for fn in all_fn:
            if fn.endswith(".raw"):
                count += 1
                os.remove(os.path.join(download_dir, fn))
    l=await m.reply_sticker(f"CAACAgIAAxkBAAKJPGD5Cfc8JnzvP_tNq3a_jiT8WpE5AAIgDQACmVp5SESxkBA3MhjUIAQ")
    k=await m.reply_text(f"**Cleaned {count} Files!**")
    await mp.delete(l)
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["mute", f"mute@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def mute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    group_call.set_is_mute(True)
    k=await m.reply_sticker(f"CAACAgIAAxkBAAKJOmD5Cfee0AmrObSd4w6K8GMrFA34AAL6AAP0exkAAUhycRaDXHTIIAQ")
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["unmute", f"unmute@{USERNAME}"]) & ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def unmute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    group_call.set_is_mute(False)
    k=await m.reply_sticker(f"CAACAgEAAxkBAAKJO2D5CfcH0IVaNECqLQroXvcZYqQAAyAIAALjeAQAAcDFfL4jhrRgIAQ")
    await mp.delete(k)
    await mp.delete(m)

@Client.on_message(filters.command(["playlist", f"playlist@{USERNAME}"]) & (filters.chat(CHAT) | filters.private))
async def show_playlist(_, m: Message):
    if not playlist:
        k=await m.reply_sticker(f"CAACAgEAAxkBAAKJJWD4_wxgfuNqVyE9efCC-yJV30heAAIjCAAC43gEAAH524TTtdFddCAE")
        await mp.delete(k)
        await mp.delete(m)
        return
    else:
        pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join([
            f"**{i}**. **{x[1]}**\n  - **Requested By:** {x[4]}"
            for i, x in enumerate(playlist)
            ])
    if m.chat.type == "private":
        await m.reply_text(pl)
    else:
        if msg.get('playlist') is not None:
            await msg['playlist'].delete()
        msg['playlist'] = await m.reply_text(pl)
    await mp.delete(m)

admincmds=["join", "unmute", "mute", "leave", "clean", "pause", "resume", "stop", "next", "radio", "stopradio", "replay", "restart", "volume", "update", f"update@{USERNAME}",  f"volume@{USERNAME}", f"join@{USERNAME}", f"unmute@{USERNAME}", f"mute@{USERNAME}", f"leave@{USERNAME}", f"clean@{USERNAME}", f"pause@{USERNAME}", f"resume@{USERNAME}", f"stop@{USERNAME}", f"next@{USERNAME}", f"radio@{USERNAME}", f"stopradio@{USERNAME}", f"replay@{USERNAME}", f"restart@{USERNAME}"]

@Client.on_message(filters.command(admincmds) & ~ADMINS_FILTER & (filters.chat(CHAT) | filters.private))
async def notforu(_, m: Message):
    k=await m.reply_sticker("CAACAgUAAxkBAAKJN2D5BTDF8d2YXKpg0yTYQJEiUxJyAAJAAAM_haYxNGLffWPfP_wgBA")
    await mp.delete(k)
    await mp.delete(m)

allcmd = ["play", "menu", "playlist", "song", f"song@{USERNAME}", f"play@{USERNAME}", f"menu@{USERNAME}", f"playlist@{USERNAME}"] + admincmds

@Client.on_message(filters.command(allcmd) & filters.group & ~filters.chat(CHAT))
async def not_chat(_, m: Message):
    buttons = [
            [
                InlineKeyboardButton("꧁☬𝓶𝓪𝓷𝓲☬꧂"),
            ]
         ]
    k=await m.reply_text("<b>Sorry, You Can't Use This Bot In This Group!</b>", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
    await mp.delete(m)
