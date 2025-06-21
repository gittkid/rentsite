"""
Общие обработчики
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import get_main_menu_keyboard
from bot.keyboards.inline import get_services_keyboard
from app.models import Service
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    
    welcome_text = """
🎉 Главное меню Makita Rental!

Выберите действие:
    """
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    """Вернуться к услугам"""
    services = Service.query.filter_by(is_available=True).all()
    
    if not services:
        await callback.answer("Услуги недоступны", show_alert=True)
        return
    
    text = "🛠️ Наши услуги:"
    await callback.message.edit_text(
        text,
        reply_markup=get_services_keyboard(services)
    )

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отменить действие"""
    await state.clear()
    await callback.answer("Действие отменено")
    await back_to_main_menu(callback, state)

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда помощи"""
    help_text = """
🤖 Помощь по использованию бота

📋 Доступные команды:
/start - Главное меню
/help - Эта справка
/catalog - Каталог инструментов
/cart - Корзина
/contacts - Контакты

🔧 Как пользоваться:
1. Выберите категорию инструментов
2. Просмотрите доступные инструменты
3. Добавьте нужные в корзину
4. Оформите заказ

📞 Если у вас есть вопросы, звоните:
+7 (XXX) XXX-XX-XX

💬 Или пишите в WhatsApp:
+7 (XXX) XXX-XX-XX
    """
    
    await message.answer(help_text)

@router.message(Command("contacts"))
async def cmd_contacts(message: Message):
    """Команда контактов"""
    contacts_text = """
📞 Контакты Makita Rental:

📱 Телефон: +7 (XXX) XXX-XX-XX
📧 Email: info@makita-rental.ru
🌐 Сайт: https://makita-rental.ru

📍 Адрес: г. Москва, ул. Примерная, д. 123

🕒 Режим работы:
Пн-Пт: 9:00 - 18:00
Сб: 10:00 - 16:00
Вс: Выходной

🚚 Доставка по Москве и области

💬 WhatsApp: +7 (XXX) XXX-XX-XX
    """
    
    await message.answer(contacts_text)

@router.message(Command("catalog"))
async def cmd_catalog(message: Message):
    """Команда каталога"""
    from bot.handlers.start import show_catalog
    await show_catalog(message)

@router.message(Command("cart"))
async def cmd_cart(message: Message, state: FSMContext):
    """Команда корзины"""
    from bot.handlers.cart import show_cart
    await show_cart(message, state)

@router.message()
async def unknown_message(message: Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "❓ Не понимаю эту команду.\n\nИспользуйте /start для возврата в главное меню или /help для справки."
    )

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router) 