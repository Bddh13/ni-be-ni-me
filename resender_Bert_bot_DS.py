import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка токена бота из файла
def load_token():
    with open("resender_bert_bot_token.txt", "r") as file:
        return file.read().strip()

# Загрузка списка пользователей из файла
def load_users():
    with open("users.txt", "r") as file:
        return [int(line.strip()) for line in file if line.strip().isdigit()]

# Инициализация бота
TOKEN = load_token()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    users = load_users() 
    await message.answer("Привет! Что передать твоим преданным?")

# Обработчик сообщений
@dp.message()
async def broadcast_message(message: Message):
    logger.info(f"Получено сообщение для рассылки: {message.text}")
    users = load_users()
    logger.info(f"Загружены пользователи: {users}")
    for user_id in users:
        try:
            logger.info(f"Пытаюсь отправить сообщение пользователю {user_id}")
            await bot.send_message(user_id, message.text)
        except Exception as e:
            logger.warning(f"Ошибка при отправке пользователю {user_id}: {e}")
    await message.answer("Сообщение передано!")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
