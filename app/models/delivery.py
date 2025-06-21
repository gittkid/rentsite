"""
Модели доставки
"""

import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Numeric, ForeignKey, BigInteger, Enum, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app import db

class DeliveryStatus(enum.Enum):
    """Статусы доставки"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeliveryType(enum.Enum):
    """Типы доставки"""
    DELIVERY = "delivery"
    PICKUP = "pickup"
    RETURN = "return"

class TimeSlot(enum.Enum):
    """Временные слоты доставки"""
    MORNING = "09:00-12:00"
    AFTERNOON = "12:00-15:00"
    EVENING = "15:00-18:00"

class DeliveryZone(db.Model):
    """Модель зоны доставки"""
    __tablename__ = 'delivery_zones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    delivery_fee = Column(Numeric(10, 2), default=0)
    min_order_amount = Column(Numeric(10, 2), default=0)
    delivery_time_hours = Column(Integer, default=24)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    deliveries = relationship('Delivery', back_populates='zone')
    
    def __repr__(self):
        return f'<DeliveryZone {self.name}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'delivery_fee': float(self.delivery_fee) if self.delivery_fee else 0,
            'min_order_amount': float(self.min_order_amount) if self.min_order_amount else 0,
            'delivery_time_hours': self.delivery_time_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Delivery(db.Model):
    """Модель доставки"""
    __tablename__ = 'deliveries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey('delivery_zones.id'), nullable=True)
    
    delivery_type = Column(Enum(DeliveryType), default=DeliveryType.DELIVERY)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.SCHEDULED)
    
    scheduled_date = Column(DateTime, nullable=False)
    scheduled_time_slot = Column(Enum(TimeSlot), nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    
    delivery_address = Column(Text, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100), nullable=True)
    
    driver_name = Column(String(100), nullable=True)
    driver_phone = Column(String(20), nullable=True)
    vehicle_info = Column(String(200), nullable=True)
    
    delivery_fee = Column(Numeric(10, 2), default=0)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    order = relationship('Order', back_populates='deliveries')
    zone = relationship('DeliveryZone', back_populates='deliveries')
    
    def __repr__(self):
        return f'<Delivery {self.id} - {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'zone_id': str(self.zone_id) if self.zone_id else None,
            'delivery_type': self.delivery_type.value,
            'status': self.status.value,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time_slot': self.scheduled_time_slot.value if self.scheduled_time_slot else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'delivery_address': self.delivery_address,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'vehicle_info': self.vehicle_info,
            'delivery_fee': float(self.delivery_fee) if self.delivery_fee else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'zone': self.zone.to_dict() if self.zone else None
        }

class DeliverySchedule(db.Model):
    """Модель расписания доставки"""
    __tablename__ = 'delivery_schedules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False)
    time_slot = Column(Enum(TimeSlot), nullable=False)
    max_deliveries = Column(Integer, default=10)
    current_deliveries = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeliverySchedule {self.date.date()} {self.time_slot.value}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'date': self.date.isoformat() if self.date else None,
            'time_slot': self.time_slot.value if self.time_slot else None,
            'max_deliveries': self.max_deliveries,
            'current_deliveries': self.current_deliveries,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def available_slots(self):
        """Количество доступных слотов"""
        return max(0, self.max_deliveries - self.current_deliveries) 