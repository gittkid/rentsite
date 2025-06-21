"""
Обработчики каталога инструментов
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.inline import get_tools_keyboard, get_tool_detail_keyboard
from bot.keyboards.reply import get_main_menu_keyboard
from app.models import Category, Tool
from app import db
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith("category:"))
async def show_category_tools(callback: CallbackQuery, state: FSMContext):
    """Показать инструменты категории"""
    category_id = callback.data.split(":")[1]
    
    # Получаем категорию
    category = Category.query.get(category_id)
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return
    
    # Получаем инструменты категории
    tools = Tool.query.filter_by(
        category_id=category_id,
        is_available=True
    ).all()
    
    if not tools:
        await callback.answer("В этой категории пока нет инструментов", show_alert=True)
        return
    
    text = f"🔧 {category.name}\n\nВыберите инструмент:"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tools_keyboard(tools, category_id)
    )

@router.callback_query(F.data.startswith("tool:"))
async def show_tool_detail(callback: CallbackQuery, state: FSMContext):
    """Показать детальную информацию об инструменте"""
    tool_id = callback.data.split(":")[1]
    
    # Получаем инструмент
    tool = Tool.query.get(tool_id)
    if not tool:
        await callback.answer("Инструмент не найден", show_alert=True)
        return
    
    # Формируем описание
    text = f"""
🔨 <b>{tool.name}</b>
📋 Модель: {tool.model}
💰 Цена: {tool.price_per_day}₽/день
💳 Залог: {tool.deposit}₽
📦 В наличии: {tool.stock_quantity} шт.

📝 Описание:
{tool.description or 'Описание отсутствует'}

🔧 Характеристики:
"""
    
    # Добавляем характеристики
    if tool.characteristics:
        for char in tool.characteristics:
            text += f"• {char.name}: {char.value}\n"
    else:
        text += "Характеристики не указаны\n"
    
    text += f"\n📞 Для заказа: +7 (XXX) XXX-XX-XX"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tool_detail_keyboard(tool_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Вернуться к категориям"""
    # Получаем категории
    categories = Category.query.filter_by(is_active=True).all()
    
    if not categories:
        await callback.answer("Категории не найдены", show_alert=True)
        return
    
    text = "🔧 Выберите категорию инструментов:"
    
    from bot.keyboards.inline import get_catalog_keyboard
    await callback.message.edit_text(
        text,
        reply_markup=get_catalog_keyboard(categories)
    )

@router.callback_query(F.data == "back_to_tools")
async def back_to_tools(callback: CallbackQuery, state: FSMContext):
    """Вернуться к инструментам"""
    # Получаем последнюю категорию из состояния
    data = await state.get_data()
    category_id = data.get('last_category_id')
    
    if not category_id:
        await callback.answer("Категория не найдена", show_alert=True)
        return
    
    # Получаем инструменты
    tools = Tool.query.filter_by(
        category_id=category_id,
        is_available=True
    ).all()
    
    if not tools:
        await callback.answer("Инструменты не найдены", show_alert=True)
        return
    
    category = Category.query.get(category_id)
    text = f"🔧 {category.name}\n\nВыберите инструмент:"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_tools_keyboard(tools, category_id)
    )

@router.callback_query(F.data == "call_order")
async def call_order(callback: CallbackQuery):
    """Заказ по телефону"""
    text = """
📞 Заказ по телефону

Для оформления заказа позвоните нам:
📱 +7 (XXX) XXX-XX-XX

🕒 Режим работы:
Пн-Пт: 9:00 - 18:00
Сб: 10:00 - 16:00
Вс: Выходной

💬 Или напишите в WhatsApp: +7 (XXX) XXX-XX-XX
    """
    
    await callback.message.answer(text)

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router) 