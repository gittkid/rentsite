"""
Модели заказов
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Numeric, ForeignKey, BigInteger, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app import db

class OrderStatus(enum.Enum):
    """Статусы заказа"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    """Способы оплаты"""
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"

class NotificationType(enum.Enum):
    """Типы уведомлений"""
    STATUS_CHANGE = "status_change"
    REMINDER = "reminder"
    DELIVERY = "delivery"

class Order(db.Model):
    """Модель заказа"""
    __tablename__ = 'orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    telegram_user_id = Column(UUID(as_uuid=True), ForeignKey('telegram_users.id'), nullable=True)
    telegram_chat_id = Column(BigInteger, nullable=True)
    telegram_message_id = Column(BigInteger, nullable=True)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    delivery_fee = Column(Numeric(10, 2), default=0)
    delivery_address = Column(Text, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    delivery_time_slot = Column(String(50), nullable=True)
    
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100), nullable=True)
    comment = Column(Text, nullable=True)
    
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user = relationship('User', back_populates='orders')
    telegram_user = relationship('TelegramUser', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    notifications = relationship('OrderNotification', back_populates='order', cascade='all, delete-orphan')
    deliveries = relationship('Delivery', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'telegram_user_id': str(self.telegram_user_id) if self.telegram_user_id else None,
            'telegram_chat_id': self.telegram_chat_id,
            'telegram_message_id': self.telegram_message_id,
            'status': self.status.value,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'delivery_fee': float(self.delivery_fee) if self.delivery_fee else 0,
            'delivery_address': self.delivery_address,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_time_slot': self.delivery_time_slot,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'comment': self.comment,
            'payment_method': self.payment_method.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    """Модель элемента заказа"""
    __tablename__ = 'order_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    tool_id = Column(UUID(as_uuid=True), ForeignKey('tools.id'), nullable=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey('services.id'), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    days = Column(Integer, default=1, nullable=False)
    price_per_day = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ограничение: должен быть либо tool_id, либо service_id, но не оба
    __table_args__ = (
        CheckConstraint(
            '(tool_id IS NOT NULL AND service_id IS NULL) OR (tool_id IS NULL AND service_id IS NOT NULL)',
            name='check_tool_or_service_order'
        ),
        CheckConstraint('quantity > 0', name='check_positive_quantity_order'),
        CheckConstraint('days > 0', name='check_positive_days_order'),
        CheckConstraint('price_per_day > 0', name='check_positive_price_order'),
        CheckConstraint('total_price > 0', name='check_positive_total_order'),
    )
    
    # Связи
    order = relationship('Order', back_populates='items')
    tool = relationship('Tool', back_populates='order_items')
    service = relationship('Service', back_populates='order_items')
    
    def __repr__(self):
        if self.tool:
            return f'<OrderItem Tool: {self.tool.name} x{self.quantity} ({self.days} дн.)>'
        elif self.service:
            return f'<OrderItem Service: {self.service.name} x{self.quantity} ({self.days} дн.)>'
        return f'<OrderItem {self.id}>'
    
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
    
    def to_dict(self):
        item_data = {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'quantity': self.quantity,
            'days': self.days,
            'price_per_day': float(self.price_per_day) if self.price_per_day else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'item_type': self.item_type,
            'item_name': self.item_name,
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

class OrderNotification(db.Model):
    """Модель уведомления о заказе"""
    __tablename__ = 'order_notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    telegram_message_id = Column(BigInteger, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    # Связи
    order = relationship('Order', back_populates='notifications')
    
    def __repr__(self):
        return f'<OrderNotification {self.notification_type.value} for Order {self.order_id}>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'order_id': str(self.order_id),
            'notification_type': self.notification_type.value,
            'telegram_message_id': self.telegram_message_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'is_read': self.is_read
        } 