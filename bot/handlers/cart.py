"""
Обработчики корзины для Telegram бота
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.inline import get_cart_keyboard, get_quantity_keyboard
from app.services.cart_service import CartService
from app.services.user_service import UserService
from app.services.tool_service import ToolService
import logging

logger = logging.getLogger(__name__)
router = Router()

async def show_user_cart(message: Message):
    """Показать корзину пользователя"""
    try:
        user = message.from_user
        telegram_user = UserService.get_telegram_user_by_id(user.id)
        
        if not telegram_user:
            await message.answer("Пожалуйста, начните с команды /start")
            return
        
        # Создаем сессию корзины для Telegram пользователя
        session_id = f"tg_{user.id}"
        cart_items = CartService.get_cart_items(session_id)
        cart_total = CartService.get_cart_total(session_id)
        
        if not cart_items:
            await message.answer(
                "🛒 Ваша корзина пуста\n\n"
                "Добавьте товары из каталога инструментов или услуг."
            )
            return
        
        # Формируем текст корзины
        cart_text = "🛒 Ваша корзина:\n\n"
        
        for item in cart_items:
            cart_text += f"• {item['item_name']}\n"
            cart_text += f"  Количество: {item['quantity']} шт.\n"
            cart_text += f"  Дней: {item['days']}\n"
            cart_text += f"  Цена: {item['total_price']} ₽\n\n"
        
        cart_text += f"💰 Итого: {cart_total['total']} ₽"
        
        if cart_total['delivery_fee'] > 0:
            cart_text += f"\n🚚 Доставка: {cart_total['delivery_fee']} ₽"
        
        await message.answer(
            cart_text,
            reply_markup=get_cart_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error showing cart: {e}")
        await message.answer("Произошла ошибка при загрузке корзины.")

@router.message(F.text == "🛒 Корзина")
async def cart_handler(message: Message):
    """Обработчик кнопки корзины"""
    await show_user_cart(message)

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart_handler(callback: CallbackQuery, state: FSMContext):
    """Добавить товар в корзину"""
    try:
        data = callback.data.split("_")
        item_type = data[3]  # tool или service
        item_id = data[4]
        
        # Сохраняем данные в состоянии
        await state.update_data(item_type=item_type, item_id=item_id)
        
        # Показываем выбор количества
        await callback.message.answer(
            "Выберите количество:",
            reply_markup=get_quantity_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in add to cart handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

@router.callback_query(F.data.startswith("quantity_"))
async def quantity_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора количества"""
    try:
        quantity = int(callback.data.split("_")[1])
        user_data = await state.get_data()
        
        item_type = user_data.get('item_type')
        item_id = user_data.get('item_id')
        
        if not item_type or not item_id:
            await callback.answer("Ошибка данных", show_alert=True)
            return
        
        # Добавляем в корзину
        session_id = f"tg_{callback.from_user.id}"
        cart_item = CartService.add_item(session_id, item_type, item_id, quantity, 1)
        
        if cart_item:
            await callback.message.answer(
                f"✅ Товар добавлен в корзину!\n"
                f"Количество: {quantity} шт."
            )
        else:
            await callback.message.answer("❌ Ошибка добавления в корзину")
        
        await callback.answer()
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in quantity handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    """Очистить корзину"""
    try:
        session_id = f"tg_{callback.from_user.id}"
        success = CartService.clear_cart(session_id)
        
        if success:
            await callback.message.edit_text("🛒 Корзина очищена")
        else:
            await callback.answer("Ошибка очистки корзины", show_alert=True)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

@router.callback_query(F.data == "checkout")
async def checkout_handler(callback: CallbackQuery, state: FSMContext):
    """Оформить заказ"""
    try:
        session_id = f"tg_{callback.from_user.id}"
        cart_items = CartService.get_cart_items(session_id)
        
        if not cart_items:
            await callback.answer("Корзина пуста", show_alert=True)
            return
        
        # Переходим к оформлению заказа
        await state.set_state("waiting_for_name")
        await callback.message.answer(
            "📝 Оформление заказа\n\n"
            "Введите ваше имя:"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in checkout handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router) 