import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка токена бота из .env файла
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен бота не найден в .env файле")

# Список администраторов (указываем ID)
ADMINS = {int(admin_id) for admin_id in os.getenv("ADMINS", "").split(",") if admin_id.isdigit()}

# Загрузка списка пользователей из файла
def load_users():
    try:
        with open("users.txt", "r") as file:
            return [int(line.strip()) for line in file if line.strip().isdigit()]
    except FileNotFoundError:
        logger.warning("Файл users.txt не найден. Список пользователей пуст.")
        return []

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Флаг для отслеживания состояния рассылки
active_sending = {}

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет прав для управления рассылкой.")
        return
    active_sending[message.from_user.id] = True
    await message.answer("Отправьте сообщение, и оно будет разослано.")

# Отправка сообщений пользователям
async def send_message_to_users(message: Message, users):
    media_methods = {
        'photo': bot.send_photo,
        'video': bot.send_video,
        'document': bot.send_document,
        'audio': bot.send_audio,
        'voice': bot.send_voice
    }
    
    for recipient_id in users:
        try:
            media_type = next((key for key in media_methods if getattr(message, key, None)), None)
            if media_type:
                await media_methods[media_type](recipient_id, getattr(message, media_type).file_id, caption=message.caption)
            else:
                await bot.send_message(recipient_id, message.text)
            logger.info(f"Сообщение отправлено пользователю {recipient_id}")
        except Exception as e:
            logger.warning(f"Ошибка при отправке пользователю {recipient_id}: {e}")

# Обработчик сообщений
@dp.message()
async def broadcast_message(message: Message):
    if message.from_user.id not in ADMINS or not active_sending.get(message.from_user.id, False):
        return
    users = load_users()
    if not users:
        await message.answer("Список пользователей пуст.")
        return
    await send_message_to_users(message, users)
    active_sending[message.from_user.id] = False
    await message.answer("Сообщение разослано!")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

