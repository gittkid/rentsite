"""
Модели пользователей
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app import db

class User(db.Model):
    """Модель пользователя сайта"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Связи
    orders = db.relationship('Order', back_populates='user')
    cart_sessions = db.relationship('CartSession', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.phone}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'phone': self.phone,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class TelegramUser(db.Model):
    """Модель Telegram пользователя"""
    __tablename__ = 'telegram_users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    orders = db.relationship('Order', back_populates='telegram_user')
    cart_sessions = db.relationship('CartSession', back_populates='telegram_user')
    
    def __repr__(self):
        return f'<TelegramUser {self.telegram_id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language_code': self.language_code,
            'is_bot': self.is_bot,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        } 