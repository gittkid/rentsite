"""
Тесты для моделей
"""

import pytest
from app import create_app, db
from app.models import User, TelegramUser, Category, Tool, Service
from datetime import datetime
import uuid

@pytest.fixture
def app():
    """Создание тестового приложения"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Тестовый клиент"""
    return app.test_client()

def test_user_creation(app):
    """Тест создания пользователя"""
    with app.app_context():
        user = User(
            phone="+79001234567",
            name="Тест Пользователь",
            email="test@example.com"
        )
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.phone == "+79001234567"
        assert user.name == "Тест Пользователь"

def test_telegram_user_creation(app):
    """Тест создания Telegram пользователя"""
    with app.app_context():
        telegram_user = TelegramUser(
            telegram_id=123456789,
            username="test_user",
            first_name="Тест",
            last_name="Пользователь"
        )
        db.session.add(telegram_user)
        db.session.commit()
        
        assert telegram_user.id is not None
        assert telegram_user.telegram_id == 123456789
        assert telegram_user.username == "test_user"

def test_category_creation(app):
    """Тест создания категории"""
    with app.app_context():
        category = Category(
            name="Электроинструменты",
            description="Профессиональные электроинструменты",
            image_url="category.jpg"
        )
        db.session.add(category)
        db.session.commit()
        
        assert category.id is not None
        assert category.name == "Электроинструменты"
        assert category.is_active == True

def test_tool_creation(app):
    """Тест создания инструмента"""
    with app.app_context():
        # Создаем категорию
        category = Category(name="Электроинструменты")
        db.session.add(category)
        db.session.commit()
        
        # Создаем инструмент
        tool = Tool(
            category_id=category.id,
            name="Дрель Makita",
            model="HP1631K",
            description="Профессиональная дрель",
            price_per_day=500.00,
            deposit=5000.00
        )
        db.session.add(tool)
        db.session.commit()
        
        assert tool.id is not None
        assert tool.name == "Дрель Makita"
        assert tool.price_per_day == 500.00
        assert tool.category.name == "Электроинструменты"

def test_service_creation(app):
    """Тест создания услуги"""
    with app.app_context():
        service = Service(
            name="Доставка",
            description="Доставка инструментов",
            price_per_day=300.00
        )
        db.session.add(service)
        db.session.commit()
        
        assert service.id is not None
        assert service.name == "Доставка"
        assert service.price_per_day == 300.00 