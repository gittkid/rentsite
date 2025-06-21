"""
Инициализация Telegram-бота
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'), parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Импорт обработчиков
from bot.handlers import start, catalog, cart, orders, common

# Регистрация обработчиков
def register_handlers():
    """Регистрация всех обработчиков"""
    start.register_handlers(dp)
    catalog.register_handlers(dp)
    cart.register_handlers(dp)
    orders.register_handlers(dp)
    common.register_handlers(dp)

async def on_startup(application: web.Application):
    """Действия при запуске приложения"""
    logger.info("Bot starting up...")
    
    # Регистрация обработчиков
    register_handlers()
    
    # Настройка webhook (если указан URL)
    webhook_url = os.getenv('TELEGRAM_WEBHOOK_URL')
    if webhook_url:
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.info("Running in polling mode")

async def on_shutdown(application: web.Application):
    """Действия при остановке приложения"""
    logger.info("Bot shutting down...")
    
    # Удаление webhook
    await bot.delete_webhook()
    
    # Закрытие сессии бота
    await bot.session.close()

def create_bot_app():
    """Создание aiohttp приложения для бота"""
    app = web.Application()
    
    # Настройка webhook handler
    webhook_path = "/webhook/telegram"
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_handler.register(app, path=webhook_path)
    
    # Настройка startup/shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    return app

async def start_polling():
    """Запуск бота в режиме polling"""
    logger.info("Starting bot in polling mode...")
    
    # Регистрация обработчиков
    register_handlers()
    
    # Запуск polling
    await dp.start_polling(bot)

def run_bot():
    """Запуск бота"""
    webhook_url = os.getenv('TELEGRAM_WEBHOOK_URL')
    
    if webhook_url:
        # Запуск webhook сервера
        app = create_bot_app()
        web.run_app(app, host='0.0.0.0', port=8000)
    else:
        # Запуск polling
        asyncio.run(start_polling())

if __name__ == '__main__':
    run_bot() 