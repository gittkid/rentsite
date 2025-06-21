"""
Сервис для работы с Telegram ботом
"""

import requests
from typing import Dict, Any, Optional
from app import db
from app.models import Order, TelegramUser
from app.services.order_service import OrderService


class TelegramService:
    """Сервис для работы с Telegram ботом"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Отправить сообщение"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
            return False
    
    def send_notification(self, text: str) -> bool:
        """Отправить уведомление в основной чат"""
        return self.send_message(self.chat_id, text)
    
    def notify_new_order(self, order: Order) -> bool:
        """Уведомить о новом заказе"""
        text = f"""
🆕 <b>Новый заказ #{order.id}</b>

👤 <b>Клиент:</b> {order.user_name}
📞 <b>Телефон:</b> {order.user_phone}
📧 <b>Email:</b> {order.user_email or 'Не указан'}

📍 <b>Адрес доставки:</b>
{order.delivery_address}

📅 <b>Дата доставки:</b> {order.delivery_date.strftime('%d.%m.%Y') if order.delivery_date else 'Не указана'}
📅 <b>Дата возврата:</b> {order.return_date.strftime('%d.%m.%Y') if order.return_date else 'Не указана'}

💰 <b>Сумма заказа:</b> {order.total_amount} ₽

📋 <b>Товары:</b>
"""
        
        # Добавляем товары
        for item in order.items:
            if item.item_type == 'tool':
                text += f"🔧 {item.quantity}x {item.item.name} ({item.rental_days} дн.) - {item.total_price} ₽\n"
            else:
                text += f"🛠️ {item.quantity}x {item.item.name} - {item.total_price} ₽\n"
        
        return self.send_notification(text)
    
    def notify_order_status_change(self, order: Order, old_status: str) -> bool:
        """Уведомить об изменении статуса заказа"""
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'in_progress': '🚚',
            'delivered': '📦',
            'completed': '🎉',
            'cancelled': '❌'
        }
        
        emoji = status_emoji.get(order.status, '📋')
        
        text = f"""
{emoji} <b>Статус заказа #{order.id} изменен</b>

👤 <b>Клиент:</b> {order.user_name}
📞 <b>Телефон:</b> {order.user_phone}

🔄 <b>Статус:</b> {old_status} → {order.status}

💰 <b>Сумма:</b> {order.total_amount} ₽
"""
        
        return self.send_notification(text)
    
    def send_order_status_to_user(self, telegram_id: int, order: Order) -> bool:
        """Отправить статус заказа пользователю"""
        status_text = {
            'pending': '⏳ Ожидает подтверждения',
            'confirmed': '✅ Заказ подтвержден',
            'in_progress': '🚚 Заказ в обработке',
            'delivered': '📦 Заказ доставлен',
            'completed': '🎉 Заказ завершен',
            'cancelled': '❌ Заказ отменен'
        }
        
        text = f"""
📋 <b>Заказ #{order.id}</b>

{status_text.get(order.status, '📋 Неизвестный статус')}

💰 <b>Сумма:</b> {order.total_amount} ₽

📅 <b>Дата заказа:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
"""
        
        return self.send_message(str(telegram_id), text)
    
    def send_catalog_to_user(self, telegram_id: int, tools: list, page: int = 1, total_pages: int = 1) -> bool:
        """Отправить каталог пользователю"""
        text = f"🔧 <b>Каталог инструментов</b> (стр. {page}/{total_pages})\n\n"
        
        for tool in tools:
            text += f"🔧 <b>{tool.name}</b>\n"
            text += f"💰 {tool.price_per_day} ₽/день\n"
            text += f"📝 {tool.description[:100]}...\n\n"
        
        return self.send_message(str(telegram_id), text)
    
    def send_cart_to_user(self, telegram_id: int, cart_items: list, total: float) -> bool:
        """Отправить корзину пользователю"""
        if not cart_items:
            text = "🛒 <b>Корзина пуста</b>"
        else:
            text = "🛒 <b>Ваша корзина:</b>\n\n"
            
            for item in cart_items:
                if item['item_type'] == 'tool':
                    text += f"🔧 {item['quantity']}x {item['item_details']['name']}\n"
                    text += f"   {item['rental_days']} дн. × {item['item_details']['price_per_day']} ₽ = {item['item_details']['total_price']} ₽\n\n"
                else:
                    text += f"🛠️ {item['quantity']}x {item['item_details']['name']}\n"
                    text += f"   {item['item_details']['price']} ₽ = {item['item_details']['total_price']} ₽\n\n"
            
            text += f"💰 <b>Итого: {total} ₽</b>"
        
        return self.send_message(str(telegram_id), text)
    
    def send_help_message(self, telegram_id: int) -> bool:
        """Отправить справку пользователю"""
        text = """
🤖 <b>Помощь по боту</b>

📋 <b>Доступные команды:</b>
/start - Главное меню
/catalog - Каталог инструментов
/cart - Корзина
/orders - Мои заказы
/help - Эта справка

🔧 <b>Как заказать:</b>
1. Выберите инструмент в каталоге
2. Добавьте в корзину
3. Укажите количество дней аренды
4. Оформите заказ

📞 <b>Поддержка:</b>
По всем вопросам обращайтесь к менеджеру
"""
        
        return self.send_message(str(telegram_id), text) 