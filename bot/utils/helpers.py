"""
Вспомогательные функции для Telegram бота
"""

import hashlib
from typing import Optional


def get_session_id(user_id: int) -> str:
    """Генерирует уникальный ID сессии для пользователя"""
    return hashlib.md5(f"user_{user_id}".encode()).hexdigest()[:16]


def get_user_info(user) -> dict:
    """Извлекает информацию о пользователе из объекта Telegram"""
    return {
        'telegram_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip()
    }


def parse_rental_days(text: str) -> Optional[int]:
    """Парсит количество дней аренды из текста"""
    try:
        # Ищем числа в тексте
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            days = int(numbers[0])
            return min(max(days, 1), 30)  # Ограничиваем от 1 до 30 дней
    except:
        pass
    return None


def parse_quantity(text: str) -> Optional[int]:
    """Парсит количество товаров из текста"""
    try:
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            quantity = int(numbers[0])
            return min(max(quantity, 1), 10)  # Ограничиваем от 1 до 10
    except:
        pass
    return None


def extract_phone_from_text(text: str) -> Optional[str]:
    """Извлекает номер телефона из текста"""
    import re
    # Паттерны для российских номеров
    patterns = [
        r'\+7\s?\(?(\d{3})\)?\s?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})',
        r'8\s?\(?(\d{3})\)?\s?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})',
        r'(\d{3})[-\s]?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 4:
                return f"+7{groups[0]}{groups[1]}{groups[2]}{groups[3]}"
            elif len(groups) == 3:
                return f"+7{groups[0]}{groups[1]}{groups[2]}"
    
    return None


def clean_text(text: str) -> str:
    """Очищает текст от лишних символов"""
    if not text:
        return ""
    
    # Убираем лишние пробелы
    text = ' '.join(text.split())
    
    # Убираем специальные символы в начале и конце
    text = text.strip('.,!?;:')
    
    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезает текст до указанной длины"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def format_duration(days: int) -> str:
    """Форматирует длительность аренды"""
    if days == 1:
        return "1 день"
    elif days < 5:
        return f"{days} дня"
    else:
        return f"{days} дней"


def get_emoji_for_category(category_name: str) -> str:
    """Возвращает эмодзи для категории"""
    emoji_map = {
        'дрели': '🔧',
        'шуруповерты': '🔧',
        'болгарки': '⚡',
        'перфораторы': '🔨',
        'пилы': '🪚',
        'шлифмашины': '🔧',
        'компрессоры': '💨',
        'генераторы': '⚡',
        'строительное оборудование': '🏗️',
        'садовый инструмент': '🌱',
        'электроинструмент': '🔌',
        'ручной инструмент': '🔧'
    }
    
    category_lower = category_name.lower()
    for key, emoji in emoji_map.items():
        if key in category_lower:
            return emoji
    
    return '🔧'  # По умолчанию


def get_status_emoji(status: str) -> str:
    """Возвращает эмодзи для статуса заказа"""
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'in_progress': '🚚',
        'delivered': '📦',
        'completed': '🎉',
        'cancelled': '❌'
    }
    return status_emoji.get(status, '📋') 