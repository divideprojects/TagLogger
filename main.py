import os
import re

from pyrogram import Client, filters, idle
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

if os.environ.get("HEROKU"):
    API_ID = os.environ.get("API_ID")
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    SESSION = os.environ.get("SESSION")
    GROUP = os.environ.get("GROUP_ID")
else:
    from config import API_HASH, API_ID, BOT_TOKEN, GROUP, SESSION

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client(SESSION, api_id=API_ID, api_hash=API_HASH)


@user.on_message(filters.mentioned & filters.incoming)
async def alert(_, m: Message):
    if m.sender_chat:
        button_s = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Anonymous Admin", callback_data="nuthing")],
                [InlineKeyboardButton(text="📩 Message", url=m.link)],
            ],
        )

        await bot.send_message(GROUP, m.text, reply_markup=button_s)
        m.continue_propagation()
        return

    if m.from_user.is_bot:
        m.continue_propagation()
        return

    if not m:
        m.continue_propagation()
        return

    if m.from_user.last_name:
        name = f"{m.from_user.first_name} {m.from_user.last_name}"
    else:
        name = m.from_user.first_name

    if m.from_user.username:
        button_s = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=name,
                        url=f"https://t.me/{m.from_user.username}",
                    ),
                ],
                [InlineKeyboardButton(text=m.chat.title, url=m.link)],
            ],
        )
    else:
        button_s = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=name,
                        callback_data=f"user({m.from_user.id})",
                    ),
                ],
                [InlineKeyboardButton(text=m.chat.title, url=m.link)],
            ],
        )

    if m.media:
        if m.photo:
            _f = await m.photo.download(f"{m.chat.id}_{m.message_id}")
            await bot.send_photo(GROUP, _f, reply_markup=button_s)
            os.remove(_f)
        elif m.sticker:
            await bot.send_sticker(GROUP, m.sticker.file_id, reply_markup=button_s)
            os.remove(_f)
        elif m.animation:
            _f = await m.animation.download(f"{m.chat.id}_{m.message_id}")
            await bot.send_animation(GROUP, _f, reply_markup=button_s)
            os.remove(_f)
        elif m.document:
            _f = await m.document.download(f"{m.chat.id}_{m.message_id}")
            await bot.send_document(GROUP, _f, reply_markup=button_s)
            os.remove(_f)
        else:
            await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)
    elif m.text:
        await bot.send_message(GROUP, m.text, reply_markup=button_s)
    else:
        await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)

    m.continue_propagation()
    return


@bot.on_callback_query(filters.regex("^user.*"))
async def privacy(_, q: CallbackQuery):
    old = q.message.text or None
    if match := re.match(r"user\((.+?)\)", q.data):
        user_id = int(match[1])

    try:
        user = await q.message._client.get_users(user_id)
        if old != None:
            new = f"{old}\n\nUser: {user.mention} [`{user.id}`]"
            await q.message.edit_text(new)
        else:
            await q.message.reply_text("User: {user.mention} [`{user.id}`]")
        return
    except:
        if old != None:
            await q.message.edit_text(f"{old}\n\nFrom User ID: `{user_id}`")
        else:
            await q.message.reply_text(f"From User ID: `{user_id}`")


@bot.on_callback_query(filters.regex("^nuthing.*"))
async def privacy(_, __):
    return None


async def _run():
    if not API_ID:
        raise NameError("API_ID is Required to Run the Bot")

    if not API_HASH:
        raise NameError("API_HASH is Required to Run the Bot")

    if not GROUP:
        raise NameError("GROUP_ID is Required to Run the Bot")

    if not BOT_TOKEN:
        raise NameError("BOT_TOKEN is Required to Run the Bot")

    if not SESSION:
        raise NameError("SESSION is Required to Run the Bot")

    await bot.start()
    bot_info = await bot.get_me()

    await user.start()
    user_info = await user.get_me()

    FULL_INFO = (
        f"[INFO] - SUCCESSFULLY STARTED BOT {bot_info.username}\n"
        f"[INFO] - SUCCESSFULLY STARTED USER SESSION {user_info.username}"
    )
    print(FULL_INFO)

    await idle()


if __name__ == "__main__":
    user.loop.run_until_complete(_run())
