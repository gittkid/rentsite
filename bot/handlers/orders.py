"""
Обработчики заказов
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.reply import get_order_keyboard, get_main_menu_keyboard
from bot.keyboards.inline import get_payment_keyboard
from app.models import Order, OrderItem, CartSession, TelegramUser
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = Router()

class OrderForm(StatesGroup):
    """Состояния оформления заказа"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_comment = State()
    waiting_for_payment = State()

@router.message(F.text == "📝 Оформить заказ")
async def start_order(message: Message, state: FSMContext):
    """Начать оформление заказа"""
    # Получаем пользователя
    telegram_user = TelegramUser.query.filter_by(telegram_id=message.from_user.id).first()
    if not telegram_user:
        await message.answer("Пользователь не найден")
        return
    
    # Проверяем корзину
    cart_session = CartSession.query.filter_by(telegram_user_id=telegram_user.id).first()
    if not cart_session or not cart_session.items:
        await message.answer("Корзина пуста! Добавьте товары для оформления заказа.")
        return
    
    # Начинаем оформление заказа
    await state.set_state(OrderForm.waiting_for_name)
    await message.answer(
        "📝 Оформление заказа\n\nВведите ваше имя:",
        reply_markup=get_order_keyboard()
    )

@router.message(OrderForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    await state.update_data(customer_name=message.text)
    await state.set_state(OrderForm.waiting_for_phone)
    await message.answer("📱 Введите ваш номер телефона:")

@router.message(OrderForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка телефона"""
    await state.update_data(customer_phone=message.text)
    await state.set_state(OrderForm.waiting_for_address)
    await message.answer("📍 Введите адрес доставки:")

@router.message(OrderForm.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """Обработка адреса"""
    await state.update_data(delivery_address=message.text)
    await state.set_state(OrderForm.waiting_for_date)
    await message.answer("📅 Введите желаемую дату доставки (ДД.ММ.ГГГГ):")

@router.message(OrderForm.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    """Обработка даты"""
    try:
        date_obj = datetime.strptime(message.text, "%d.%m.%Y")
        await state.update_data(delivery_date=date_obj)
        await state.set_state(OrderForm.waiting_for_time)
        await message.answer("🕒 Выберите время доставки:\n\n09:00-12:00\n12:00-15:00\n15:00-18:00")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")

@router.message(OrderForm.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Обработка времени"""
    time_slots = ["09:00-12:00", "12:00-15:00", "15:00-18:00"]
    if message.text in time_slots:
        await state.update_data(delivery_time_slot=message.text)
        await state.set_state(OrderForm.waiting_for_comment)
        await message.answer("💬 Введите комментарий к заказу (или отправьте '-' если комментария нет):")
    else:
        await message.answer("❌ Выберите одно из предложенных временных слотов")

@router.message(OrderForm.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    """Обработка комментария"""
    comment = message.text if message.text != "-" else None
    await state.update_data(comment=comment)
    await state.set_state(OrderForm.waiting_for_payment)
    
    # Показываем сводку заказа
    data = await state.get_data()
    summary = f"""
📋 Сводка заказа:

👤 Имя: {data['customer_name']}
📱 Телефон: {data['customer_phone']}
📍 Адрес: {data['delivery_address']}
📅 Дата: {data['delivery_date'].strftime('%d.%m.%Y')}
🕒 Время: {data['delivery_time_slot']}
💬 Комментарий: {data['comment'] or 'Нет'}

Выберите способ оплаты:
    """
    
    await message.answer(
        summary,
        reply_markup=get_payment_keyboard()
    )

@router.callback_query(F.data.startswith("payment:"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    """Обработка способа оплаты"""
    payment_method = callback.data.split(":")[1]
    
    # Получаем данные заказа
    data = await state.get_data()
    
    # Получаем пользователя и корзину
    telegram_user = TelegramUser.query.filter_by(telegram_id=callback.from_user.id).first()
    cart_session = CartSession.query.filter_by(telegram_user_id=telegram_user.id).first()
    
    if not cart_session or not cart_session.items:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    
    # Создаем заказ
    order = Order(
        telegram_user_id=telegram_user.id,
        telegram_chat_id=callback.message.chat.id,
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        delivery_address=data['delivery_address'],
        delivery_date=data['delivery_date'],
        delivery_time_slot=data['delivery_time_slot'],
        comment=data['comment'],
        payment_method=payment_method,
        total_amount=0  # Будет рассчитано ниже
    )
    
    db.session.add(order)
    db.session.flush()  # Получаем ID заказа
    
    # Создаем элементы заказа
    total_amount = 0
    for cart_item in cart_session.items:
        if cart_item.tool:
            price_per_day = cart_item.tool.price_per_day
        elif cart_item.service:
            price_per_day = cart_item.service.price_per_day
        else:
            continue
        
        total_price = price_per_day * cart_item.days * cart_item.quantity
        total_amount += total_price
        
        order_item = OrderItem(
            order_id=order.id,
            tool_id=cart_item.tool_id,
            service_id=cart_item.service_id,
            quantity=cart_item.quantity,
            days=cart_item.days,
            price_per_day=price_per_day,
            total_price=total_price
        )
        db.session.add(order_item)
    
    order.total_amount = total_amount
    db.session.commit()
    
    # Очищаем корзину
    for item in cart_session.items:
        db.session.delete(item)
    db.session.commit()
    
    # Отправляем подтверждение
    success_text = f"""
✅ Заказ успешно оформлен!

📋 Номер заказа: {order.id}
💰 Сумма: {total_amount}₽
💳 Способ оплаты: {'Карта' if payment_method == 'card' else 'Наличные'}

📞 Наш менеджер свяжется с вами в ближайшее время для подтверждения заказа.

Спасибо за выбор Makita Rental! 🎉
    """
    
    await callback.message.edit_text(success_text)
    await state.clear()

@router.callback_query(F.data == "back_to_order")
async def back_to_order(callback: CallbackQuery, state: FSMContext):
    """Вернуться к оформлению заказа"""
    await state.clear()
    await start_order(callback.message, state)

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router) 