#    Tag Logger, A Telegram Bot to log when you were Mentioning
#    Copyright (C) 2021 Jayant Hegde Kageri.
#
#    This program is free software: you can redistribute it or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
from pyrogram import filters, Client, idle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
)

if os.environ.get("HEROKU"):
    API_ID = os.environ.get("API_ID")
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    SESSION = os.environ.get("SESSION")
    GROUP = os.environ.get("GROUP_ID")
else:
    from config import API_ID, API_HASH, BOT_TOKEN, SESSION, GROUP

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client(SESSION, api_id=API_ID, api_hash=API_HASH)


@user.on_message(filters.mentioned & filters.incoming)
async def alert(_, message: Message):
    if message.sender_chat:
        button_s = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Anonymous Admin", callback_data="nuthing")],
                [InlineKeyboardButton(text="📩 Message", url=message.link)],
            ]
        )

        await bot.send_message(GROUP, message.text, reply_markup=button_s)
        message.continue_propagation()
        return

    if message.from_user.is_bot:
        message.continue_propagation()
        return

    if not message:
        message.continue_propagation()
        return

    if message.from_user.last_name:
        name = message.from_user.first_name + " " + message.from_user.last_name
    else:
        name = message.from_user.first_name

    if message.from_user.username:
        button_s = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=name, url=f"https://t.me/{message.from_user.username}"
                    )
                ],
                [InlineKeyboardButton(text=message.chat.title, url=message.link)],
            ]
        )
    else:
        button_s = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=name, callback_data="user({})".format(message.from_user.id)
                    )
                ],
                [InlineKeyboardButton(text=message.chat.title, url=message.link)],
            ]
        )

    if message.media == True:
        if message.photo:
            await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)
            message.continue_propagation()
            return
        elif message.sticker:
            await bot.send_sticker(
                GROUP, message.sticker.file_id, reply_markup=button_s
            )
            message.continue_propagation()
            return

        elif message.animation:
            await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)
            message.continue_propagation()
            return

        elif message.document:
            await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)
            message.continue_propagation()
            return

        else:
            await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)
            message.continue_propagation()
            return

    if message.text:
        await bot.send_message(GROUP, message.text, reply_markup=button_s)
        message.continue_propagation()
        return

    else:
        await bot.send_message(GROUP, "Unsupported Message", reply_markup=button_s)
        message.continue_propagation()
        return


@bot.on_callback_query(filters.regex("^user.*"))
async def privacy(_, cb: CallbackQuery):
    if cb.message.text:
        old = cb.message.text
    else:
        old = None
    match = re.match(r"user\((.+?)\)", cb.data)
    if match:
        user_id = int(match.group(1))

    try:
        user = await cb.message._client.get_users(user_id)
        if old != None:
            new = old + f"\n\nUser: {user.mention} [`{user.id}`]"
            await cb.message.edit_text(new)
            return
        else:
            await cb.message.reply_text("User: {user.mention} [`{user.id}`]")
            return

    except:
        if old != None:
            await cb.message.edit_text(f"{old}\n\nFrom User ID: `{user_id}`")
        else:
            await cb.message.reply_text(f"From User ID: `{user_id}`")


@bot.on_callback_query(filters.regex("^nuthing.*"))
async def privacy(_, cb: CallbackQuery):
    if cb.from_user:
        return
    else:
        return


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
