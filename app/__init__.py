"""
Инициализация Flask приложения
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Фабрика приложений Flask"""
    app = Flask(__name__)
    
    # Конфигурация
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Регистрация blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Импорт моделей для миграций
    from app.models import (
        User, TelegramUser, Category, Tool, ToolCharacteristic,
        Service, ServiceFeature, CartSession, CartItem,
        Order, OrderItem, OrderNotification, Delivery,
        DeliveryZone, DeliverySchedule
    )
    
    # Создание контекста приложения только для разработки
    if config_name == 'development':
        with app.app_context():
            # Создание таблиц только в режиме разработки
            db.create_all()
    
    return app 