import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = "8616847902:AAG-qSRjj1dtGsoHzM3WujL4LfisC0hHAD8"
OWNER_ID = 1413372081 # Telegram ID владельца

# =========================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# Хранилище соответствия сообщений
# message_id владельца -> user_id отправителя
message_links = {}


# =========================
# СТАРТ
# =========================

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "✉️ Привет.\n\n"
        "Оставьте здесь свой запрос .\n"
        "Администрация свяжется с вами в ближайшее время ."
    )


# =========================
# СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЕЙ
# =========================

@dp.message(F.from_user.id != OWNER_ID)
async def anonymous_message(message: Message):

    sender = message.from_user

    text = (
        "📩 <b>Новое анонимное сообщение</b>\n\n"
        f"👤 ID пользователя: <code>{sender.id}</code>\n\n"
    )

    if message.text:
        text += f"{message.text}"

        sent = await bot.send_message(
            OWNER_ID,
            text
        )

    else:
        sent = await bot.forward_message(
            OWNER_ID,
            message.chat.id,
            message.message_id
        )

    # Запоминаем кто отправил сообщение
    message_links[sent.message_id] = sender.id

    await message.answer("✅ Сообщение отправлено анонимно.")


# =========================
# ОТВЕТ ВЛАДЕЛЬЦА
# =========================

@dp.message(F.from_user.id == OWNER_ID)
async def owner_reply(message: Message):

    # Проверяем, ответил ли владелец реплаем
    if not message.reply_to_message:
        return

    replied_message_id = message.reply_to_message.message_id

    # Проверяем есть ли такой пользователь
    if replied_message_id not in message_links:
        return

    user_id = message_links[replied_message_id]

    try:
        if message.text:
            await bot.send_message(
                user_id,
                f"💬 <b>Ответ владельца:</b>\n\n{message.text}"
            )

        else:
            await bot.copy_message(
                user_id,
                OWNER_ID,
                message.message_id
            )

        await message.reply("✅ Ответ отправлен.")

    except Exception as e:
        await message.reply(f"Ошибка: {e}")


# =========================
# ЗАПУСК
# =========================

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
