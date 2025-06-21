"""
Модели услуг
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app import db

class Service(db.Model):
    """Модель услуги"""
    __tablename__ = 'services'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    price_per_day = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    duration_hours = Column(Integer, default=8)  # Продолжительность услуги в часах
    max_quantity = Column(Integer, default=10)  # Максимальное количество за раз
    service_type = Column(String(50), default='rental')  # Тип услуги: rental, delivery, setup
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    features = relationship('ServiceFeature', back_populates='service', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='service')
    order_items = relationship('OrderItem', back_populates='service')
    
    def __repr__(self):
        return f'<Service {self.name}>'
    
    @property
    def is_active(self):
        """Проверяет, активна ли услуга"""
        return self.is_available
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'price_per_day': float(self.price_per_day) if self.price_per_day else 0,
            'is_available': self.is_available,
            'is_active': self.is_active,
            'duration_hours': self.duration_hours,
            'max_quantity': self.max_quantity,
            'service_type': self.service_type,
            'features': [feature.to_dict() for feature in self.features],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ServiceFeature(db.Model):
    """Модель функции услуги"""
    __tablename__ = 'service_features'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey('services.id'), nullable=False)
    feature = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)
    
    # Связи
    service = relationship('Service', back_populates='features')
    
    def __repr__(self):
        return f'<ServiceFeature {self.feature}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'service_id': str(self.service_id),
            'feature': self.feature,
            'sort_order': self.sort_order
        } 