"""
Модели инструментов
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app import db

class Tool(db.Model):
    """Модель инструмента"""
    __tablename__ = 'tools'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=False)
    name = Column(String(200), nullable=False)
    model = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    price_per_day = Column(Numeric(10, 2), nullable=False)
    deposit = Column(Numeric(10, 2), nullable=False)
    is_popular = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=1)
    available_quantity = Column(Integer, default=1)  # Количество доступных для аренды
    condition = Column(String(50), default='excellent')  # Состояние инструмента
    location = Column(String(200), nullable=True)  # Место хранения
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    category = relationship('Category', back_populates='tools')
    characteristics = relationship('ToolCharacteristic', back_populates='tool', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='tool')
    order_items = relationship('OrderItem', back_populates='tool')
    
    def __repr__(self):
        return f'<Tool {self.name} {self.model}>'
    
    @property
    def is_in_stock(self):
        """Проверяет, есть ли инструмент в наличии"""
        return self.available_quantity > 0 and self.is_available
    
    @property
    def full_name(self):
        """Полное название инструмента"""
        return f"{self.name} {self.model}"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'category_id': str(self.category_id),
            'category_name': self.category.name if self.category else None,
            'name': self.name,
            'model': self.model,
            'full_name': self.full_name,
            'description': self.description,
            'image_url': self.image_url,
            'price_per_day': float(self.price_per_day) if self.price_per_day else 0,
            'deposit': float(self.deposit) if self.deposit else 0,
            'is_popular': self.is_popular,
            'is_available': self.is_available,
            'is_in_stock': self.is_in_stock,
            'stock_quantity': self.stock_quantity,
            'available_quantity': self.available_quantity,
            'condition': self.condition,
            'location': self.location,
            'characteristics': [char.to_dict() for char in self.characteristics],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ToolCharacteristic(db.Model):
    """Модель характеристики инструмента"""
    __tablename__ = 'tool_characteristics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey('tools.id'), nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)
    
    # Связи
    tool = relationship('Tool', back_populates='characteristics')
    
    def __repr__(self):
        return f'<ToolCharacteristic {self.name}: {self.value}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'tool_id': str(self.tool_id),
            'name': self.name,
            'value': self.value,
            'sort_order': self.sort_order
        } 