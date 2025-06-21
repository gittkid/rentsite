"""
Сервис для работы с пользователями
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import User, TelegramUser
from app import db


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def get_or_create_telegram_user(telegram_id: int, username: str = None, 
                                   first_name: str = None, last_name: str = None,
                                   language_code: str = None, is_bot: bool = False) -> Optional[TelegramUser]:
        """Получить или создать пользователя Telegram"""
        try:
            telegram_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
            
            if not telegram_user:
                telegram_user = TelegramUser(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code,
                    is_bot=is_bot,
                    created_at=datetime.utcnow()
                )
                db.session.add(telegram_user)
                db.session.commit()
                return telegram_user
            else:
                # Обновляем активность
                telegram_user.last_activity = datetime.utcnow()
                db.session.commit()
                return telegram_user
                
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка создания/обновления Telegram пользователя: {e}")
            return None
    
    @staticmethod
    def get_telegram_user_by_id(telegram_id: int) -> Optional[TelegramUser]:
        """Получить пользователя Telegram по ID"""
        try:
            return TelegramUser.query.filter_by(telegram_id=telegram_id).first()
        except Exception as e:
            print(f"Ошибка получения Telegram пользователя: {e}")
            return None
    
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[User]:
        """Получить пользователя по телефону"""
        try:
            return User.query.filter_by(phone=phone).first()
        except Exception as e:
            print(f"Ошибка получения пользователя по телефону: {e}")
            return None
    
    @staticmethod
    def create_user(phone: str, name: str, email: str = None) -> Optional[User]:
        """Создать нового пользователя"""
        try:
            user = User(
                phone=phone,
                name=name,
                email=email,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка создания пользователя: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> bool:
        """Обновить данные пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка обновления пользователя: {e}")
            return False
    
    @staticmethod
    def get_user_orders(user_id: str) -> List[Dict[str, Any]]:
        """Получить заказы пользователя"""
        try:
            user = User.query.get(user_id)
            if not user:
                return []
            
            return [order.to_dict() for order in user.orders]
        except Exception as e:
            print(f"Ошибка получения заказов пользователя: {e}")
            return []
    
    @staticmethod
    def get_telegram_user_orders(telegram_user_id: str) -> List[Dict[str, Any]]:
        """Получить заказы пользователя Telegram"""
        try:
            telegram_user = TelegramUser.query.get(telegram_user_id)
            if not telegram_user:
                return []
            
            return [order.to_dict() for order in telegram_user.orders]
        except Exception as e:
            print(f"Ошибка получения заказов Telegram пользователя: {e}")
            return []
    
    @staticmethod
    def link_telegram_to_user(telegram_id: int, phone: str) -> bool:
        """Связать Telegram пользователя с обычным пользователем"""
        try:
            telegram_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
            user = User.query.filter_by(phone=phone).first()
            
            if not telegram_user or not user:
                return False
            
            # Здесь можно добавить логику связывания
            # Например, создать связь через отдельную таблицу
            
            return True
        except Exception as e:
            print(f"Ошибка связывания пользователей: {e}")
            return False
    
    @staticmethod
    def get_active_users_count() -> int:
        """Получить количество активных пользователей"""
        try:
            return User.query.filter_by(is_active=True).count()
        except Exception as e:
            print(f"Ошибка подсчета активных пользователей: {e}")
            return 0
    
    @staticmethod
    def get_telegram_users_count() -> int:
        """Получить количество пользователей Telegram"""
        try:
            return TelegramUser.query.count()
        except Exception as e:
            print(f"Ошибка подсчета Telegram пользователей: {e}")
            return 0

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def create_telegram_user(telegram_id: int, user_data: Dict[str, Any]) -> TelegramUser:
        """Создать пользователя Telegram"""
        telegram_user = TelegramUser(
            telegram_id=telegram_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            phone=user_data.get('phone'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(telegram_user)
        db.session.commit()
        return telegram_user
    
    @staticmethod
    def update_telegram_user(telegram_id: int, user_data: Dict[str, Any]) -> Optional[TelegramUser]:
        """Обновить данные пользователя Telegram"""
        telegram_user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
        if not telegram_user:
            return None
        
        for key, value in user_data.items():
            if hasattr(telegram_user, key):
                setattr(telegram_user, key, value)
        
        telegram_user.updated_at = datetime.utcnow()
        db.session.commit()
        return telegram_user
    
    @staticmethod
    def get_user_stats() -> Dict[str, Any]:
        """Получить статистику пользователей"""
        total_users = User.query.count()
        total_telegram_users = TelegramUser.query.count()
        
        # Пользователи за последние 30 дней
        thirty_days_ago = datetime.utcnow() - datetime.timedelta(days=30)
        new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
        new_telegram_users = TelegramUser.query.filter(TelegramUser.created_at >= thirty_days_ago).count()
        
        return {
            'total_users': total_users,
            'total_telegram_users': total_telegram_users,
            'new_users_30_days': new_users,
            'new_telegram_users_30_days': new_telegram_users
        } 