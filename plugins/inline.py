"""
radioplayerv2.2, Telegram Voice Chat Bot
Copyright (c) 2021  green👑
"""

import asyncio
from pyrogram.handlers import InlineQueryHandler
from youtubesearchpython import VideosSearch
from utils import USERNAME
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, errors
from config import Config

REPLY_MESSAGE=Config.REPLY_MESSAGE
buttons = [
            [
                InlineKeyboardButton("❔ HOW TO USE ME ❔", callback_data="help"),
            ]
         ]


@Client.on_inline_query()
async def search(client, query):
    answers = []
    if query.query == "rasmikaamandhana":
        answers.append(
            InlineQueryResultArticle(
                title="player",
                thumb_url="https://telegra.ph/file/8f14823545ccefd8a158b.jpg",
                input_message_content=InputTextMessageContent(f"{REPLY_MESSAGE}\n\n<b>© Powered By : \n꧁☬𝓶𝓪𝓷𝓲☬꧂👑</b>", disable_web_page_preview=True),
                reply_markup=InlineKeyboardMarkup(buttons)
                )
            )
        await query.answer(results=answers, cache_time=0)
        return
    string = query.query.lower().strip().rstrip()
    if string == "":
        await client.answer_inline_query(
            query.id,
            results=answers,
            switch_pm_text=("Type An Song Name ?"),
            switch_pm_parameter="help",
            cache_time=0
        )
    else:
        videosSearch = VideosSearch(string.lower(), limit=50)
        for v in videosSearch.result()["result"]:
            answers.append(
                InlineQueryResultArticle(
                    title=v["title"],
                    description=("Duration: {} Views: {}").format(
                        v["duration"],
                        v["viewCount"]["short"]
                    ),
                    input_message_content=InputTextMessageContent(
                        "/play https://www.youtube.com/watch?v={}".format(
                            v["id"]
                        )
                    ),
                    thumb_url=v["thumbnails"][0]["url"]
                )
            )
        try:
            await query.answer(
                results=answers,
                cache_time=0
            )
        except errors.QueryIdInvalid:
            await query.answer(
                results=answers,
                cache_time=0,
                switch_pm_text=("Error: Search Timed Out!"),
                switch_pm_parameter="",
            )


__handlers__ = [
    [
        InlineQueryHandler(
            search
        )
    ]
]
