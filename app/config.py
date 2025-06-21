"""
Конфигурация приложения
"""

import os
from datetime import timedelta

class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'AK2YSTRT-S2C_RANDMOSMONDNIDN-H&FUHJ*HGF656464GI-KEYSTP'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Настройки Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.environ.get('TELEGRAM_WEBHOOK_URL')
    CHAT_ID = os.environ.get('CHAT_ID')
    
    # Настройки Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Настройки JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'K2YSTRT-S2C_RANDMOBVKVT876875-H&FUHF656464GI-KEYSTP'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Настройки загрузки файлов
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Настройки пагинации
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 12))
    
    # Настройки корзины
    MAX_CART_ITEMS = int(os.environ.get('MAX_CART_ITEMS', 20))
    MAX_RENTAL_DAYS = int(os.environ.get('MAX_RENTAL_DAYS', 10))
    
    # Настройки доставки
    DEFAULT_DELIVERY_FEE = int(os.environ.get('DEFAULT_DELIVERY_FEE', 600))
    MIN_ORDER_AMOUNT_FOR_FREE_DELIVERY = int(os.environ.get('MIN_ORDER_AMOUNT_FOR_FREE_DELIVERY', 5000))
    
    # Логирование
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://rentuser:R2ntS2c@localhost:5432/rentdatadb'
    
    # Логирование
    LOG_LEVEL = 'DEBUG'
    
    # Настройки для разработки
    TELEGRAM_WEBHOOK_URL = None  # Отключаем webhook в разработке

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Логирование
    LOG_LEVEL = 'INFO'
    
    # Безопасность
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Настройки для продакшена
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required for production")

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://rentuser:R2ntS2c@localhost:5432/makita_rental_test'
    
    # Отключаем CSRF для тестов
    WTF_CSRF_ENABLED = False
    
    # Настройки для тестирования
    TELEGRAM_BOT_TOKEN = 'test_token'
    TELEGRAM_WEBHOOK_URL = None

# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 