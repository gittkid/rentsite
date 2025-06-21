"""
Inline клавиатуры для Telegram бота
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from app.models import Category, Tool, Service

def get_catalog_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """Клавиатура каталога категорий"""
    keyboard = []
    
    for category in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🔧 {category.name}",
                callback_data=f"category_{category.id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_tools_keyboard(tools: List, category_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура инструментов"""
    keyboard = []
    
    for tool in tools:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🔨 {tool.name} - {tool.price_per_day}₽/день",
                callback_data=f"tool_{tool.id}"
            )
        ])
    
    # Навигация
    nav_buttons = []
    if category_id:
        nav_buttons.append(InlineKeyboardButton(text="🔙 К категориям", callback_data="back_to_categories"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    
    keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_tool_detail_keyboard(tool_id: str) -> InlineKeyboardMarkup:
    """Клавиатура деталей инструмента"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 Добавить в корзину",
                callback_data=f"add_to_cart_tool_{tool_id}"
            )
        ],
        [
            InlineKeyboardButton(text="🔙 К инструментам", callback_data="back_to_tools"),
            InlineKeyboardButton(text="📋 Каталог", callback_data="back_to_categories")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_services_keyboard(services: List[Service]) -> InlineKeyboardMarkup:
    """Клавиатура услуг"""
    keyboard = []
    
    for service in services:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🛠️ {service.name} - {service.price_per_day}₽/день",
                callback_data=f"service_{service.id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_service_detail_keyboard(service_id: str) -> InlineKeyboardMarkup:
    """Клавиатура деталей услуги"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 Добавить в корзину",
                callback_data=f"add_to_cart_service_{service_id}"
            )
        ],
        [
            InlineKeyboardButton(text="🔙 К услугам", callback_data="back_to_services"),
            InlineKeyboardButton(text="📋 Каталог", callback_data="back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура корзины"""
    keyboard = [
        [
            InlineKeyboardButton(text="🛒 Очистить корзину", callback_data="clear_cart"),
            InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout")
        ],
        [
            InlineKeyboardButton(text="🔙 К каталогу", callback_data="back_to_main")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_quantity_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора количества"""
    keyboard = []
    
    # Кнопки количества
    row = []
    for i in range(1, 6):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"quantity_{i}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Дополнительные кнопки
    keyboard.append([
        InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_quantity")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_keyboard(action: str, item_id: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Да",
                callback_data=f"confirm_{action}_{item_id}"
            ),
            InlineKeyboardButton(
                text="❌ Нет",
                callback_data="cancel_confirm"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_order_status_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Клавиатура статуса заказа"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📋 Детали заказа",
                callback_data=f"order_details_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить заказ",
                callback_data=f"cancel_order_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_orders")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_orders_keyboard(orders: List) -> InlineKeyboardMarkup:
    """Клавиатура списка заказов"""
    keyboard = []
    
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'delivered': '🚚',
            'completed': '🎉',
            'cancelled': '❌'
        }.get(order.status.value, '📋')
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status_emoji} Заказ #{order.id[:8]} - {order.total_amount}₽",
                callback_data=f"order_{order.id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 