"""
API маршруты для работы с данными
"""

from flask import request, jsonify, session, current_app
from app.api import bp
from app.models import (
    Tool, Service, CartSession, CartItem, Order, OrderItem,
    User, TelegramUser, Category
)
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.tool_service import ToolService
from app.services.user_service import UserService
from app import db
import uuid
from datetime import datetime

@bp.route('/tools', methods=['GET'])
def get_tools():
    """Получение списка инструментов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category_id = request.args.get('category_id')
        search = request.args.get('search')
        
        if search:
            result = ToolService.search_tools(search, page, per_page)
        elif category_id:
            result = ToolService.get_tools_by_category(category_id, page, per_page)
        else:
            result = ToolService.get_all_tools(page, per_page)
        
        return jsonify({
            'tools': [tool.to_dict() for tool in result['tools']],
            'page': result['current_page'],
            'total_pages': result['pages'],
            'has_next': result['has_next'],
            'has_prev': result['has_prev'],
            'total': result['total']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tools/<tool_id>', methods=['GET'])
def get_tool(tool_id):
    """Получение информации об инструменте"""
    try:
        tool = ToolService.get_tool_by_id(tool_id)
        
        if not tool:
            return jsonify({'error': 'Tool not found'}), 404
        
        return jsonify(tool.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Получение списка категорий"""
    try:
        categories = ToolService.get_categories()
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cart', methods=['GET'])
def get_cart():
    """Получить содержимое корзины"""
    try:
        session_id = session.get('cart_session_id')
        
        if not session_id:
            return jsonify({'items': [], 'total': 0, 'total_items': 0})
        
        items = CartService.get_cart_items(session_id)
        total = CartService.get_cart_total(session_id)
        
        return jsonify({
            'items': items,
            'total': total['total'],
            'subtotal': total['subtotal'],
            'delivery_fee': total['delivery_fee'],
            'total_items': total['items_count']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cart/count', methods=['GET'])
def get_cart_count():
    """Получить количество товаров в корзине"""
    try:
        session_id = session.get('cart_session_id')
        
        if not session_id:
            return jsonify({'count': 0})
        
        count = CartService.get_cart_count(session_id)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Добавить товар в корзину"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        item_type = data.get('item_type')  # 'tool' или 'service'
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        days = data.get('days', 1)
        
        if not item_type or not item_id:
            return jsonify({'error': 'Missing item_type or item_id'}), 400
        
        # Получаем или создаем сессию корзины
        session_id = session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['cart_session_id'] = session_id
        
        cart_item = CartService.add_item(session_id, item_type, item_id, quantity, days)
        
        if not cart_item:
            return jsonify({'error': 'Failed to add item to cart'}), 400
        
        return jsonify({
            'success': True, 
            'message': 'Item added to cart',
            'cart_count': CartService.get_cart_count(session_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cart/update', methods=['POST'])
def update_cart_item():
    """Обновить элемент корзины"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        days = data.get('days')
        
        if not item_id:
            return jsonify({'error': 'Missing item_id'}), 400
        
        cart_item = CartService.update_item(item_id, quantity, days)
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        return jsonify({'success': True, 'message': 'Cart updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cart/remove/<item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """Удалить товар из корзины"""
    try:
        success = CartService.remove_item(item_id)
        
        if not success:
            return jsonify({'error': 'Cart item not found'}), 404
        
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cart/clear', methods=['DELETE'])
def clear_cart():
    """Очистить корзину"""
    try:
        session_id = session.get('cart_session_id')
        
        if not session_id:
            return jsonify({'success': True, 'message': 'Cart is already empty'})
        
        success = CartService.clear_cart(session_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Cart cleared'})
        else:
            return jsonify({'error': 'Failed to clear cart'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/orders', methods=['POST'])
def create_order():
    """Создать заказ"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Получаем данные заказа
    customer_name = data.get('customer_name')
    customer_phone = data.get('customer_phone')
    customer_email = data.get('customer_email')
    delivery_address = data.get('delivery_address')
    delivery_date = data.get('delivery_date')
    delivery_time_slot = data.get('delivery_time_slot')
    comment = data.get('comment')
    payment_method = data.get('payment_method', 'cash')
    
    if not customer_name or not customer_phone:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Получаем корзину
    session_id = session.get('cart_session_id')
    if not session_id:
        return jsonify({'error': 'Cart is empty'}), 400
    
    cart_session = CartSession.query.filter_by(session_id=session_id).first()
    if not cart_session or not cart_session.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Создаем заказ
    order = Order(
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        delivery_address=delivery_address,
        delivery_date=datetime.fromisoformat(delivery_date) if delivery_date else None,
        delivery_time_slot=delivery_time_slot,
        comment=comment,
        payment_method=payment_method,
        total_amount=0  # Будет рассчитано ниже
    )
    
    db.session.add(order)
    db.session.flush()  # Получаем ID заказа
    
    # Создаем элементы заказа
    total_amount = 0
    for cart_item in cart_session.items:
        if cart_item.tool:
            price_per_day = cart_item.tool.price_per_day
            item_name = cart_item.tool.name
        elif cart_item.service:
            price_per_day = cart_item.service.price_per_day
            item_name = cart_item.service.name
        else:
            continue
        
        total_price = price_per_day * cart_item.days * cart_item.quantity
        total_amount += total_price
        
        order_item = OrderItem(
            order_id=order.id,
            tool_id=cart_item.tool_id,
            service_id=cart_item.service_id,
            quantity=cart_item.quantity,
            days=cart_item.days,
            price_per_day=price_per_day,
            total_price=total_price
        )
        db.session.add(order_item)
    
    order.total_amount = total_amount
    db.session.commit()
    
    # Очищаем корзину
    for item in cart_session.items:
        db.session.delete(item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'order_id': str(order.id),
        'total_amount': float(total_amount)
    })

@bp.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Получить информацию о заказе"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict())

@bp.route('/services/<service_id>', methods=['GET'])
def get_service(service_id):
    """Получить информацию об услуге"""
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    return jsonify(service.to_dict())

@bp.route('/search', methods=['GET'])
def search():
    """Поиск инструментов и услуг"""
    query = request.args.get('q', '')
    category_id = request.args.get('category_id')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Поиск инструментов
    tools_query = Tool.query.filter_by(is_available=True)
    if category_id:
        tools_query = tools_query.filter_by(category_id=category_id)
    
    tools = tools_query.filter(
        Tool.name.ilike(f'%{query}%') |
        Tool.model.ilike(f'%{query}%') |
        Tool.description.ilike(f'%{query}%')
    ).limit(limit).all()
    
    # Поиск услуг
    services_query = Service.query.filter_by(is_available=True)
    services = services_query.filter(
        Service.name.ilike(f'%{query}%') |
        Service.description.ilike(f'%{query}%')
    ).limit(limit).all()
    
    return jsonify({
        'tools': [tool.to_dict() for tool in tools],
        'services': [service.to_dict() for service in services]
    }) 