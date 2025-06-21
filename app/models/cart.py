"""
Модели корзины
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app import db

class CartSession(db.Model):
    """Модель сессии корзины"""
    __tablename__ = 'cart_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    telegram_user_id = Column(UUID(as_uuid=True), ForeignKey('telegram_users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user = relationship('User', back_populates='cart_sessions')
    telegram_user = relationship('TelegramUser', back_populates='cart_sessions')
    items = relationship('CartItem', back_populates='cart_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CartSession {self.session_id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'session_id': self.session_id,
            'user_id': str(self.user_id) if self.user_id else None,
            'telegram_user_id': str(self.telegram_user_id) if self.telegram_user_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items],
            'total_items': len(self.items),
            'total_amount': sum(item.total_price for item in self.items)
        }

class CartItem(db.Model):
    """Модель элемента корзины"""
    __tablename__ = 'cart_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_session_id = Column(UUID(as_uuid=True), ForeignKey('cart_sessions.id'), nullable=False)
    tool_id = Column(UUID(as_uuid=True), ForeignKey('tools.id'), nullable=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey('services.id'), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    days = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ограничение: должен быть либо tool_id, либо service_id, но не оба
    __table_args__ = (
        CheckConstraint(
            '(tool_id IS NOT NULL AND service_id IS NULL) OR (tool_id IS NULL AND service_id IS NOT NULL)',
            name='check_tool_or_service'
        ),
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        CheckConstraint('days > 0', name='check_positive_days'),
    )
    
    # Связи
    cart_session = relationship('CartSession', back_populates='items')
    tool = relationship('Tool', back_populates='cart_items')
    service = relationship('Service', back_populates='cart_items')
    
    def __repr__(self):
        if self.tool:
            return f'<CartItem Tool: {self.tool.name} x{self.quantity} ({self.days} дн.)>'
        elif self.service:
            return f'<CartItem Service: {self.service.name} x{self.quantity} ({self.days} дн.)>'
        return f'<CartItem {self.id}>'
    
    @property
    def item_name(self):
        """Название товара"""
        if self.tool:
            return self.tool.name
        elif self.service:
            return self.service.name
        return "Неизвестный товар"
    
    @property
    def item_type(self):
        """Тип товара"""
        if self.tool:
            return 'tool'
        elif self.service:
            return 'service'
        return None
    
    @property
    def price_per_day(self):
        """Цена за день"""
        if self.tool:
            return float(self.tool.price_per_day)
        elif self.service:
            return float(self.service.price_per_day)
        return 0
    
    @property
    def total_price(self):
        """Общая стоимость"""
        return self.price_per_day * self.days * self.quantity
    
    def to_dict(self):
        item_data = {
            'id': str(self.id),
            'cart_session_id': str(self.cart_session_id),
            'quantity': self.quantity,
            'days': self.days,
            'item_type': self.item_type,
            'item_name': self.item_name,
            'price_per_day': self.price_per_day,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if self.tool:
            item_data.update({
                'item': self.tool.to_dict()
            })
        elif self.service:
            item_data.update({
                'item': self.service.to_dict()
            })
        
        return item_data 