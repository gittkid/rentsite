"""
Обработчики команды /start и главного меню
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_menu_keyboard
from bot.keyboards.inline import get_catalog_keyboard, get_services_keyboard
from app.models import TelegramUser, Category, Service
from app.services.user_service import UserService
from app.services.tool_service import ToolService
from app import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    try:
        user = message.from_user
        
        # Сохраняем или обновляем пользователя в БД
        telegram_user = UserService.get_or_create_telegram_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_bot=user.is_bot
        )
        
        if telegram_user:
            logger.info(f"Telegram user processed: {user.id}")
        
        # Приветственное сообщение
        welcome_text = f"""
🎉 Добро пожаловать в Makita Rental!

Мы предлагаем профессиональные инструменты Makita в аренду:
• 🔨 Электроинструменты
• 🛠️ Садовый инструмент  
• ⚡ Аккумуляторные инструменты
• 🏗️ Строительное оборудование

Выберите действие из меню ниже:
        """
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

@router.message(F.text == "📋 Каталог инструментов")
async def show_catalog(message: Message):
    """Показать каталог инструментов"""
    try:
        # Получаем категории
        categories = ToolService.get_categories()
        
        if not categories:
            await message.answer("😔 К сожалению, каталог временно недоступен.")
            return
        
        text = "🔧 Выберите категорию инструментов:"
        await message.answer(
            text,
            reply_markup=get_catalog_keyboard(categories)
        )
        
    except Exception as e:
        logger.error(f"Error showing catalog: {e}")
        await message.answer("Произошла ошибка при загрузке каталога.")

@router.message(F.text == "🛠️ Услуги")
async def show_services(message: Message):
    """Показать услуги"""
    try:
        # Получаем услуги
        services = ToolService.get_services()
        
        if not services:
            await message.answer("😔 К сожалению, услуги временно недоступны.")
            return
        
        text = "🛠️ Наши услуги:"
        await message.answer(
            text,
            reply_markup=get_services_keyboard(services)
        )
        
    except Exception as e:
        logger.error(f"Error showing services: {e}")
        await message.answer("Произошла ошибка при загрузке услуг.")

@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    """Показать корзину"""
    try:
        from bot.handlers.cart import show_user_cart
        await show_user_cart(message)
    except Exception as e:
        logger.error(f"Error showing cart: {e}")
        await message.answer("Произошла ошибка при загрузке корзины.")

@router.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    """Показать контакты"""
    contacts_text = """
📞 Контакты Makita Rental:

📱 Телефон: +7 (495) 123-45-67
📧 Email: info@makita-rental.ru
🌐 Сайт: https://makita-rental.ru

📍 Адрес: г. Москва, ул. Примерная, д. 123

🕒 Режим работы:
Пн-Пт: 9:00 - 18:00
Сб: 10:00 - 16:00
Вс: Выходной

🚚 Доставка по Москве и области
    """
    
    await message.answer(contacts_text)

@router.message(F.text == "ℹ️ О компании")
async def show_about(message: Message):
    """Показать информацию о компании"""
    about_text = """
🏢 О компании Makita Rental

Мы специализируемся на аренде профессионального инструмента Makita с 2010 года.

✅ Наши преимущества:
• Профессиональное оборудование
• Быстрая доставка
• Техническая поддержка
• Гибкие условия аренды
• Гарантия качества

🔧 В нашем парке более 500 единиц инструмента:
• Электроинструменты
• Садовый инструмент
• Строительное оборудование
• Аккумуляторные инструменты

💼 Работаем с частными лицами и организациями
    """
    
    await message.answer(about_text)

@router.message(F.text == "🔙 Главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await cmd_start(message, state)

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router) 