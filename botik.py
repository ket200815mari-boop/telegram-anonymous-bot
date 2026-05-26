import asyncio
import os
from threading import Thread

from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# =========================
# FLASK
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# =========================
# TELEGRAM BOT
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

message_links = {}

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "✉️ Оставьте свой запрос здесь. Администрация свяжется с вами в ближайшее время."
    )

@dp.message(F.from_user.id != OWNER_ID)
async def anonymous_message(message: Message):

    sent = await bot.send_message(
        OWNER_ID,
        f"📩 Новое сообщение\n\n"
        f"ID: {message.from_user.id}\n\n"
        f"{message.text or 'Медиа'}"
    )

    message_links[sent.message_id] = message.from_user.id

    await message.answer("✅ Ваш ответ записан.")

@dp.message(F.from_user.id == OWNER_ID)
async def owner_reply(message: Message):

    if not message.reply_to_message:
        return

    replied_id = message.reply_to_message.message_id

    if replied_id not in message_links:
        return

    user_id = message_links[replied_id]

    await bot.send_message(
        user_id,
        f"💬 Ответ владельца:\n\n{message.text}"
    )

async def start_bot():
    await dp.start_polling(bot)

# =========================
# START
# =========================

if __name__ == "__main__":

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    asyncio.run(start_bot())
