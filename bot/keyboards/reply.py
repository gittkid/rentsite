"""
Reply клавиатуры для Telegram-бота
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню"""
    keyboard = [
        [
            KeyboardButton(text="📋 Каталог инструментов"),
            KeyboardButton(text="🛠️ Услуги")
        ],
        [
            KeyboardButton(text="🛒 Корзина"),
            KeyboardButton(text="📞 Контакты")
        ],
        [
            KeyboardButton(text="ℹ️ О компании")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_cart_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура корзины"""
    keyboard = [
        [
            KeyboardButton(text="📝 Оформить заказ"),
            KeyboardButton(text="🗑️ Очистить корзину")
        ],
        [
            KeyboardButton(text="🔙 Главное меню")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Управление корзиной"
    )

def get_order_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура заказа"""
    keyboard = [
        [
            KeyboardButton(text="✅ Подтвердить заказ"),
            KeyboardButton(text="❌ Отменить")
        ],
        [
            KeyboardButton(text="🔙 Главное меню")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Оформление заказа"
    )

def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    keyboard = [
        [
            KeyboardButton(text="🔙 Главное меню")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def get_remove_keyboard() -> ReplyKeyboardRemove:
    """Убрать клавиатуру"""
    return ReplyKeyboardRemove() 