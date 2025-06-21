"""
Сервис для работы с инструментами и категориями
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import or_
from datetime import datetime
from app.models import Tool, Category, Service, ToolCharacteristic
from app import db


class ToolService:
    """Сервис для работы с инструментами"""
    
    @staticmethod
    def get_all_tools(page: int = 1, per_page: int = 12) -> Dict[str, Any]:
        """Получить все инструменты с пагинацией"""
        try:
            query = Tool.query.filter_by(is_available=True).order_by(Tool.created_at.desc())
            
            # Пагинация
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'tools': pagination.items,
                'current_page': page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'total': pagination.total
            }
        except Exception as e:
            print(f"Ошибка получения инструментов: {e}")
            return {
                'tools': [],
                'current_page': 1,
                'pages': 0,
                'has_next': False,
                'has_prev': False,
                'total': 0
            }
    
    @staticmethod
    def get_tools_by_category(category_id: str, page: int = 1, per_page: int = 12) -> Dict[str, Any]:
        """Получить инструменты по категории"""
        try:
            query = Tool.query.filter_by(
                category_id=category_id,
                is_available=True
            ).order_by(Tool.created_at.desc())
            
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'tools': pagination.items,
                'current_page': page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'total': pagination.total
            }
        except Exception as e:
            print(f"Ошибка получения инструментов по категории: {e}")
            return {
                'tools': [],
                'current_page': 1,
                'pages': 0,
                'has_next': False,
                'has_prev': False,
                'total': 0
            }
    
    @staticmethod
    def search_tools(search_query: str, page: int = 1, per_page: int = 12) -> Dict[str, Any]:
        """Поиск инструментов"""
        try:
            query = Tool.query.filter(
                Tool.is_available == True,
                db.or_(
                    Tool.name.ilike(f'%{search_query}%'),
                    Tool.model.ilike(f'%{search_query}%'),
                    Tool.description.ilike(f'%{search_query}%')
                )
            ).order_by(Tool.created_at.desc())
            
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'tools': pagination.items,
                'current_page': page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'total': pagination.total
            }
        except Exception as e:
            print(f"Ошибка поиска инструментов: {e}")
            return {
                'tools': [],
                'current_page': 1,
                'pages': 0,
                'has_next': False,
                'has_prev': False,
                'total': 0
            }
    
    @staticmethod
    def get_tool_by_id(tool_id: str) -> Optional[Tool]:
        """Получить инструмент по ID"""
        try:
            return Tool.query.get(tool_id)
        except Exception as e:
            print(f"Ошибка получения инструмента: {e}")
            return None
    
    @staticmethod
    def get_popular_tools(limit: int = 8) -> List[Tool]:
        """Получить популярные инструменты"""
        try:
            return Tool.query.filter_by(
                is_popular=True,
                is_available=True
            ).limit(limit).all()
        except Exception as e:
            print(f"Ошибка получения популярных инструментов: {e}")
            return []
    
    @staticmethod
    def get_categories() -> List[Category]:
        """Получить все категории"""
        try:
            return Category.query.order_by(Category.sort_order, Category.name).all()
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []
    
    @staticmethod
    def get_category_by_id(category_id: str) -> Optional[Category]:
        """Получить категорию по ID"""
        try:
            return Category.query.get(category_id)
        except Exception as e:
            print(f"Ошибка получения категории: {e}")
            return None
    
    @staticmethod
    def get_services() -> List[Service]:
        """Получить все услуги"""
        try:
            return Service.query.filter_by(is_available=True).order_by(Service.name).all()
        except Exception as e:
            print(f"Ошибка получения услуг: {e}")
            return []
    
    @staticmethod
    def get_service_by_id(service_id: str) -> Optional[Service]:
        """Получить услугу по ID"""
        try:
            return Service.query.get(service_id)
        except Exception as e:
            print(f"Ошибка получения услуги: {e}")
            return None
    
    @staticmethod
    def update_tool_stock(tool_id: str, quantity: int) -> bool:
        """Обновить количество доступных инструментов"""
        try:
            tool = Tool.query.get(tool_id)
            if not tool:
                return False
            
            tool.available_quantity = max(0, tool.available_quantity - quantity)
            tool.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка обновления стока: {e}")
            return False
    
    @staticmethod
    def return_tool_stock(tool_id: str, quantity: int) -> bool:
        """Вернуть инструмент на склад"""
        try:
            tool = Tool.query.get(tool_id)
            if not tool:
                return False
            
            tool.available_quantity = min(tool.stock_quantity, tool.available_quantity + quantity)
            tool.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка возврата на склад: {e}")
            return False
    
    @staticmethod
    def get_featured_tools(limit: int = 6) -> List[Tool]:
        """Получить популярные инструменты"""
        return Tool.query.filter_by(is_active=True, is_featured=True).limit(limit).all()
    
    @staticmethod
    def get_new_tools(limit: int = 6) -> List[Tool]:
        """Получить новые инструменты"""
        return Tool.query.filter_by(is_active=True).order_by(Tool.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_tools_by_price_range(min_price: float, max_price: float, page: int = 1, per_page: int = 12) -> Dict[str, Any]:
        """Получить инструменты по диапазону цен"""
        tools = Tool.query.filter(
            Tool.is_active == True,
            Tool.price_per_day >= min_price,
            Tool.price_per_day <= max_price
        ).order_by(Tool.price_per_day).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'tools': tools.items,
            'total': tools.total,
            'pages': tools.pages,
            'current_page': tools.page,
            'has_next': tools.has_next,
            'has_prev': tools.has_prev,
            'min_price': min_price,
            'max_price': max_price
        }
    
    @staticmethod
    def get_tool_stats() -> Dict[str, Any]:
        """Получить статистику по инструментам"""
        total_tools = Tool.query.filter_by(is_active=True).count()
        total_categories = Category.query.filter_by(is_active=True).count()
        
        # Средняя цена
        avg_price = db.session.query(db.func.avg(Tool.price_per_day)).filter_by(is_active=True).scalar() or 0
        
        # Самый дорогой инструмент
        most_expensive = Tool.query.filter_by(is_active=True).order_by(Tool.price_per_day.desc()).first()
        
        # Самый дешевый инструмент
        cheapest = Tool.query.filter_by(is_active=True).order_by(Tool.price_per_day.asc()).first()
        
        return {
            'total_tools': total_tools,
            'total_categories': total_categories,
            'average_price': round(avg_price, 2),
            'most_expensive': most_expensive.name if most_expensive else None,
            'cheapest': cheapest.name if cheapest else None
        } 