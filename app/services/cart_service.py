"""
Сервис для работы с корзиной
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import CartSession, CartItem, Tool, Service
from app import db


class CartService:
    """Сервис для работы с корзиной"""
    
    @staticmethod
    def get_or_create_session(session_id: str, user_id: Optional[str] = None, telegram_user_id: Optional[str] = None) -> CartSession:
        """Получить или создать сессию корзины"""
        session = CartSession.query.filter_by(session_id=session_id).first()
        
        if not session:
            session = CartSession(
                session_id=session_id,
                user_id=user_id,
                telegram_user_id=telegram_user_id,
                created_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
        
        return session
    
    @staticmethod
    def add_item(session_id: str, item_type: str, item_id: str, 
                 quantity: int = 1, days: int = 1) -> Optional[CartItem]:
        """Добавить товар в корзину"""
        try:
            cart_session = CartService.get_or_create_session(session_id)
            
            # Проверяем существование товара
            if item_type == 'tool':
                item = Tool.query.get(item_id)
                if not item or not item.is_in_stock:
                    return None
            elif item_type == 'service':
                item = Service.query.get(item_id)
                if not item or not item.is_available:
                    return None
            else:
                return None
            
            # Проверяем, есть ли уже такой товар в корзине
            existing_item = None
            if item_type == 'tool':
                existing_item = CartItem.query.filter_by(
                    cart_session_id=cart_session.id,
                    tool_id=item_id
                ).first()
            elif item_type == 'service':
                existing_item = CartItem.query.filter_by(
                    cart_session_id=cart_session.id,
                    service_id=item_id
                ).first()
            
            if existing_item:
                existing_item.quantity += quantity
                existing_item.days = max(existing_item.days, days)
                existing_item.cart_session.updated_at = datetime.utcnow()
                db.session.commit()
                return existing_item
            
            # Создаем новый элемент корзины
            cart_item_data = {
                'cart_session_id': cart_session.id,
                'quantity': quantity,
                'days': days,
                'created_at': datetime.utcnow()
            }
            
            if item_type == 'tool':
                cart_item_data['tool_id'] = item_id
            elif item_type == 'service':
                cart_item_data['service_id'] = item_id
            
            cart_item = CartItem(**cart_item_data)
            cart_session.updated_at = datetime.utcnow()
            
            db.session.add(cart_item)
            db.session.commit()
            return cart_item
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка добавления в корзину: {e}")
            return None
    
    @staticmethod
    def update_item(item_id: str, quantity: Optional[int] = None, days: Optional[int] = None) -> Optional[CartItem]:
        """Обновить товар в корзине"""
        try:
            cart_item = CartItem.query.get(item_id)
            if not cart_item:
                return None
            
            if quantity is not None and quantity > 0:
                cart_item.quantity = quantity
            if days is not None and days > 0:
                cart_item.days = days
            
            cart_item.cart_session.updated_at = datetime.utcnow()
            db.session.commit()
            return cart_item
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка обновления корзины: {e}")
            return None
    
    @staticmethod
    def remove_item(item_id: str) -> bool:
        """Удалить товар из корзины"""
        try:
            cart_item = CartItem.query.get(item_id)
            if not cart_item:
                return False
            
            cart_session = cart_item.cart_session
            db.session.delete(cart_item)
            cart_session.updated_at = datetime.utcnow()
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка удаления из корзины: {e}")
            return False
    
    @staticmethod
    def get_cart_items(session_id: str) -> List[Dict[str, Any]]:
        """Получить все товары в корзине с деталями"""
        try:
            cart_session = CartSession.query.filter_by(session_id=session_id).first()
            if not cart_session:
                return []
            
            return [item.to_dict() for item in cart_session.items]
            
        except Exception as e:
            print(f"Ошибка получения корзины: {e}")
            return []
    
    @staticmethod
    def get_cart_total(session_id: str) -> Dict[str, float]:
        """Получить общую сумму корзины"""
        try:
            items = CartService.get_cart_items(session_id)
            
            subtotal = sum(item.get('total_price', 0) for item in items)
            
            # Расчет доставки (можно вынести в конфигурацию)
            delivery_fee = 600 if subtotal < 5000 else 0
            
            return {
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'total': subtotal + delivery_fee,
                'items_count': len(items)
            }
            
        except Exception as e:
            print(f"Ошибка расчета корзины: {e}")
            return {
                'subtotal': 0,
                'delivery_fee': 0,
                'total': 0,
                'items_count': 0
            }
    
    @staticmethod
    def clear_cart(session_id: str) -> bool:
        """Очистить корзину"""
        try:
            cart_session = CartSession.query.filter_by(session_id=session_id).first()
            if not cart_session:
                return False
            
            for item in cart_session.items:
                db.session.delete(item)
            
            cart_session.updated_at = datetime.utcnow()
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка очистки корзины: {e}")
            return False
    
    @staticmethod
    def merge_carts(session_id: str, user_id: str) -> bool:
        """Объединить корзину сессии с корзиной пользователя"""
        try:
            session_cart = CartSession.query.filter_by(session_id=session_id).first()
            user_cart = CartSession.query.filter_by(user_id=user_id).first()
            
            if not session_cart:
                return False
            
            if not user_cart:
                # Если у пользователя нет корзины, просто привязываем сессию
                session_cart.user_id = user_id
                db.session.commit()
                return True
            
            # Объединяем товары
            for session_item in session_cart.items:
                existing_item = None
                
                if session_item.tool_id:
                    existing_item = CartItem.query.filter_by(
                        cart_session_id=user_cart.id,
                        tool_id=session_item.tool_id
                    ).first()
                elif session_item.service_id:
                    existing_item = CartItem.query.filter_by(
                        cart_session_id=user_cart.id,
                        service_id=session_item.service_id
                    ).first()
                
                if existing_item:
                    existing_item.quantity += session_item.quantity
                    existing_item.days = max(existing_item.days, session_item.days)
                    db.session.delete(session_item)
                else:
                    session_item.cart_session_id = user_cart.id
            
            db.session.delete(session_cart)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка объединения корзин: {e}")
            return False
    
    @staticmethod
    def get_cart_count(session_id: str) -> int:
        """Получить количество товаров в корзине"""
        try:
            cart_session = CartSession.query.filter_by(session_id=session_id).first()
            if not cart_session:
                return 0
            
            return sum(item.quantity for item in cart_session.items)
            
        except Exception as e:
            print(f"Ошибка подсчета корзины: {e}")
            return 0 