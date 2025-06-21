"""
Маршруты для основных страниц
"""

from flask import render_template, request, jsonify, current_app
from app.main import bp
from app.models import Category, Tool, Service
from app import db
from sqlalchemy import or_

@bp.route('/')
def index():
    """Главная страница"""
    # Получаем популярные инструменты
    popular_tools = Tool.query.filter_by(is_popular=True, is_available=True).limit(6).all()
    
    # Получаем категории
    categories = Category.query.filter_by(is_active=True).all()
    
    # Получаем услуги
    services = Service.query.filter_by(is_available=True).limit(4).all()
    
    return render_template('index.html',
                         popular_tools=popular_tools,
                         categories=categories,
                         services=services)

@bp.route('/catalog')
def catalog():
    """Страница каталога"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=str)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')
    
    # Базовый запрос
    query = Tool.query.filter_by(is_available=True)
    
    # Фильтр по категории
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Поиск
    if search:
        search_filter = or_(
            Tool.name.ilike(f'%{search}%'),
            Tool.model.ilike(f'%{search}%'),
            Tool.description.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)
    
    # Сортировка
    if sort_by == 'price_asc':
        query = query.order_by(Tool.price_per_day.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Tool.price_per_day.desc())
    elif sort_by == 'name':
        query = query.order_by(Tool.name.asc())
    else:
        query = query.order_by(Tool.created_at.desc())
    
    # Пагинация
    per_page = current_app.config['ITEMS_PER_PAGE']
    tools = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Получаем категории для фильтра
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('catalog.html',
                         tools=tools,
                         categories=categories,
                         current_category=category_id,
                         search=search,
                         sort_by=sort_by)

@bp.route('/tool/<tool_id>')
def tool_detail(tool_id):
    """Страница инструмента"""
    tool = Tool.query.get_or_404(tool_id)
    
    # Получаем похожие инструменты
    similar_tools = Tool.query.filter(
        Tool.category_id == tool.category_id,
        Tool.id != tool.id,
        Tool.is_available == True
    ).limit(4).all()
    
    return render_template('tool_detail.html',
                         tool=tool,
                         similar_tools=similar_tools)

@bp.route('/services')
def services():
    """Страница услуг"""
    services = Service.query.filter_by(is_available=True).all()
    return render_template('services.html', services=services)

@bp.route('/service/<service_id>')
def service_detail(service_id):
    """Страница услуги"""
    service = Service.query.get_or_404(service_id)
    return render_template('service_detail.html', service=service)

@bp.route('/about')
def about():
    """Страница о компании"""
    return render_template('about.html')

@bp.route('/contact')
def contact():
    """Страница контактов"""
    return render_template('contact.html')

@bp.route('/delivery')
def delivery():
    """Страница доставки"""
    return render_template('delivery.html')

@bp.route('/terms')
def terms():
    """Условия аренды"""
    return render_template('terms.html')

@bp.route('/privacy')
def privacy():
    """Политика конфиденциальности"""
    return render_template('privacy.html')

# API маршруты для AJAX запросов
@bp.route('/api/categories')
def api_categories():
    """API для получения категорий"""
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([category.to_dict() for category in categories])

@bp.route('/api/tools')
def api_tools():
    """API для получения инструментов"""
    category_id = request.args.get('category_id')
    search = request.args.get('search', '')
    
    query = Tool.query.filter_by(is_available=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        search_filter = or_(
            Tool.name.ilike(f'%{search}%'),
            Tool.model.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)
    
    tools = query.limit(20).all()
    return jsonify([tool.to_dict() for tool in tools]) 