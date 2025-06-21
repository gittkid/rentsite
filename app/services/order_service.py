"""
Сервис для работы с заказами
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import Order, OrderItem, Delivery, CartSession, CartItem, OrderStatus, DeliveryStatus
from app.services.cart_service import CartService
from app import db


class OrderService:
    """Сервис для работы с заказами"""
    
    @staticmethod
    def create_order_from_cart(session_id: str, user_data: Dict[str, Any], 
                              user_id: Optional[str] = None, 
                              telegram_user_id: Optional[str] = None) -> Optional[Order]:
        """Создать заказ из корзины"""
        try:
            cart_items = CartService.get_cart_items(session_id)
            if not cart_items:
                return None
            
            cart_total = CartService.get_cart_total(session_id)
            
            # Создаем заказ
            order_data = {
                'user_id': user_id,
                'telegram_user_id': telegram_user_id,
                'customer_name': user_data.get('name'),
                'customer_phone': user_data.get('phone'),
                'customer_email': user_data.get('email'),
                'delivery_address': user_data.get('address'),
                'delivery_date': user_data.get('delivery_date'),
                'delivery_time_slot': user_data.get('delivery_time_slot'),
                'total_amount': cart_total['total'],
                'delivery_fee': cart_total['delivery_fee'],
                'comment': user_data.get('comment'),
                'payment_method': user_data.get('payment_method', 'cash'),
                'status': OrderStatus.PENDING,
                'created_at': datetime.utcnow()
            }
            
            order = Order(**order_data)
            db.session.add(order)
            db.session.flush()  # Получаем ID заказа
            
            # Создаем элементы заказа
            for cart_item in cart_items:
                order_item_data = {
                    'order_id': order.id,
                    'quantity': cart_item['quantity'],
                    'days': cart_item['days'],
                    'price_per_day': cart_item['price_per_day'],
                    'total_price': cart_item['total_price'],
                    'created_at': datetime.utcnow()
                }
                
                if cart_item['item_type'] == 'tool':
                    order_item_data['tool_id'] = cart_item['item']['id']
                elif cart_item['item_type'] == 'service':
                    order_item_data['service_id'] = cart_item['item']['id']
                
                order_item = OrderItem(**order_item_data)
                db.session.add(order_item)
            
            # Создаем доставку
            if user_data.get('delivery_date'):
                delivery_data = {
                    'order_id': order.id,
                    'delivery_address': user_data.get('address'),
                    'scheduled_date': user_data.get('delivery_date'),
                    'delivery_type': 'delivery',
                    'status': DeliveryStatus.SCHEDULED,
                    'customer_name': user_data.get('name'),
                    'customer_phone': user_data.get('phone'),
                    'customer_email': user_data.get('email'),
                    'delivery_fee': cart_total['delivery_fee'],
                    'created_at': datetime.utcnow()
                }
                
                delivery = Delivery(**delivery_data)
                db.session.add(delivery)
            
            # Очищаем корзину
            CartService.clear_cart(session_id)
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка создания заказа: {e}")
            return None
    
    @staticmethod
    def get_order(order_id: str) -> Optional[Order]:
        """Получить заказ по ID"""
        return Order.query.get(order_id)
    
    @staticmethod
    def get_user_orders(user_phone: str) -> List[Order]:
        """Получить заказы пользователя по телефону"""
        return Order.query.filter_by(customer_phone=user_phone).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_telegram_user_orders(telegram_user_id: str) -> List[Order]:
        """Получить заказы пользователя Telegram"""
        return Order.query.filter_by(telegram_user_id=telegram_user_id).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def update_order_status(order_id: str, status: str) -> Optional[Order]:
        """Обновить статус заказа"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return None
            
            old_status = order.status
            order.status = OrderStatus(status)
            order.updated_at = datetime.utcnow()
            
            # Обновляем статус доставки
            delivery = Delivery.query.filter_by(order_id=order_id).first()
            if delivery:
                if status == 'delivered':
                    delivery.status = DeliveryStatus.DELIVERED
                elif status == 'completed':
                    delivery.status = DeliveryStatus.DELIVERED
                elif status == 'cancelled':
                    delivery.status = DeliveryStatus.CANCELLED
                delivery.updated_at = datetime.utcnow()
            
            db.session.commit()
            return order
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка обновления статуса заказа: {e}")
            return None
    
    @staticmethod
    def get_order_details(order_id: str) -> Optional[Dict[str, Any]]:
        """Получить детали заказа"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return None
            
            return order.to_dict()
            
        except Exception as e:
            print(f"Ошибка получения деталей заказа: {e}")
            return None
    
    @staticmethod
    def get_orders_by_status(status: str) -> List[Order]:
        """Получить заказы по статусу"""
        try:
            return Order.query.filter_by(status=OrderStatus(status)).order_by(Order.created_at.desc()).all()
        except:
            return []
    
    @staticmethod
    def get_recent_orders(limit: int = 10) -> List[Order]:
        """Получить последние заказы"""
        return Order.query.order_by(Order.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def calculate_order_stats() -> Dict[str, Any]:
        """Рассчитать статистику заказов"""
        try:
            total_orders = Order.query.count()
            pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
            completed_orders = Order.query.filter_by(status=OrderStatus.COMPLETED).count()
            cancelled_orders = Order.query.filter_by(status=OrderStatus.CANCELLED).count()
            
            # Общая сумма заказов
            total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(status=OrderStatus.COMPLETED).scalar() or 0
            
            # Заказы за последние 30 дней
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_orders = Order.query.filter(Order.created_at >= thirty_days_ago).count()
            
            return {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'total_revenue': float(total_revenue),
                'recent_orders_30_days': recent_orders
            }
            
        except Exception as e:
            print(f"Ошибка расчета статистики: {e}")
            return {
                'total_orders': 0,
                'pending_orders': 0,
                'completed_orders': 0,
                'cancelled_orders': 0,
                'total_revenue': 0,
                'recent_orders_30_days': 0
            }
    
    @staticmethod
    def cancel_order(order_id: str, reason: str = None) -> bool:
        """Отменить заказ"""
        try:
            order = Order.query.get(order_id)
            if not order or order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
                return False
            
            order.status = OrderStatus.CANCELLED
            order.comment = f"Отменен: {reason}" if reason else "Отменен пользователем"
            order.updated_at = datetime.utcnow()
            
            # Обновляем статус доставки
            delivery = Delivery.query.filter_by(order_id=order_id).first()
            if delivery:
                delivery.status = DeliveryStatus.CANCELLED
                delivery.updated_at = datetime.utcnow()
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка отмены заказа: {e}")
            return False 