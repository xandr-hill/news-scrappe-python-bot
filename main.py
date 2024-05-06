# main.py
import re
import config
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, exceptions
from aiogram.filters import CommandStart, Command
from os import getenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token value from the environment variable
TOKEN = getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функція-обробник для команди /start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.reply("Привіт! Я бот для моніторингу новинних каналів. "
                        "Надішліть команду /monitor, щоб почати моніторинг.")

# Функція-обробник для команди /monitor
@dp.message(Command("monitor"))
async def monitor_handler(message: types.Message):
    # Get the channel IDs
    channel_ids = []
    for channel_name in config.NEWS_CHANNELS:
        # Отримати інформацію про канал за його ім'ям
        try:
            chat_info = await bot.get_chat(channel_name)
            channel_ids.append(chat_info.id)
        except exceptions.TelegramAPIError as e:
            # Обробити помилку, якщо канал не знайдено або він приватний
            print(f"Помилка: {e}")

    # Надати останні новини з кожного каналу
    await provide_latest_news(channel_ids, message)

    # Call the monitor_news_channels function with the channel IDs
    await monitor_news_channels(channel_ids, message)

async def provide_latest_news(channel_ids, message):
    for chat_id in channel_ids:
        # Отримати останні повідомлення з кожного каналу і надіслати їх користувачу
        try:
            latest_messages = await bot.get_chat_history(chat_id, limit=5)  # Задайте бажану кількість останніх повідомлень
            for message in latest_messages:
                await message.forward(message.chat.id)
        except exceptions.TelegramAPIError as e:
            print(f"Помилка: {e}")

async def monitor_news_channels(channel_ids, message, offset=None):
    while True:
        for chat_id in channel_ids:
            updates = await bot.get_updates(offset=offset, limit=10, timeout=None, allowed_updates=["message"])
            if not updates:
                break

            for update in updates:
                offset = update.update_id + 1
                if update.message and update.message.chat.id == chat_id:
                    await message.reply(update.message.text)
                    await asyncio.sleep(1)


@dp.message()
async def send_echo(message: types.Message):
    try:
        if message.text:
            # Обробляємо текст
            processed_text = re.sub(r'[^\w\s]', '', message.text.lower())

            if "славаукраїні" in processed_text or "слава україні" in processed_text:
                await message.answer(text="Героям слава!")
            elif "славанації" in processed_text or "слава нації" in processed_text:
                await message.answer(text="Смерть ворогам!")
            elif "путін" in processed_text:
                if "путін" == processed_text or processed_text.endswith("путін"):
                    await message.answer(text="Хуйло!")
                else:
                    await message.answer(text="путін - Хуйло!")
            else:
                await message.send_copy(chat_id=message.chat.id)

        elif message.sticker:
            await message.bot.send_sticker(
                chat_id=message.chat.id,
                sticker=message.sticker.file_id,
            )
        else:
            await message.send_copy(chat_id=message.chat.id)

    except TypeError:
        await message.reply(text="Я Вас не зрозумів, вибачте...")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
