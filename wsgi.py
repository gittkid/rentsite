"""
WSGI файл для продакшен развертывания
"""

import os
from app import create_app

# Создаем приложение в продакшен режиме
app = create_app('production')

if __name__ == "__main__":
    app.run() 