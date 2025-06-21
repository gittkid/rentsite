"""
Запуск Telegram-бота
"""

import os
import sys
from dotenv import load_dotenv

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

# Импортируем и запускаем бота
from bot import run_bot

if __name__ == '__main__':
    print("🤖 Запуск Telegram-бота Makita Rental...")
    run_bot() 