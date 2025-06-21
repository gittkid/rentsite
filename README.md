# Makita Rental Flask Application

Веб-приложение для аренды инструментов Makita с интеграцией Telegram-бота.

## Описание

Это Flask-приложение предоставляет полный функционал для аренды инструментов:
- Каталог инструментов и услуг
- Система корзины и заказов
- Интеграция с Telegram-ботом
- Система доставки
- Административная панель

## Технологии

- **Backend**: Flask 3.1.1, SQLAlchemy 2.0.41
- **База данных**: PostgreSQL
- **Telegram Bot**: aiogram 3.20.0
- **Кэширование**: Redis
- **Развертывание**: Gunicorn

## Структура проекта

```
makita_rental_flask/
├── app/
│   ├── __init__.py          # Инициализация Flask приложения
│   ├── config.py            # Конфигурация
│   ├── models/              # Модели базы данных
│   │   ├── __init__.py
│   │   ├── user.py          # Пользователи
│   │   ├── category.py      # Категории
│   │   ├── tool.py          # Инструменты
│   │   ├── service.py       # Услуги
│   │   ├── cart.py          # Корзина
│   │   ├── order.py         # Заказы
│   │   └── delivery.py      # Доставка
│   ├── main/                # Основные страницы
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── bot/                 # Telegram бот
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── utils/
│   ├── static/              # Статические файлы
│   └── templates/           # Шаблоны
├── migrations/              # Миграции базы данных
├── tests/                   # Тесты
├── requirements.txt         # Зависимости
├── run.py                   # Запуск приложения
└── README.md
```

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd makita_rental_flask
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте файл `env.example` в `.env` и настройте переменные:

```bash
cp env.example .env
```

Отредактируйте `.env` файл:

```env
# Flask настройки
FLASK_ENV=development
SECRET_KEY=AK2YSTRT-S2C_RANDMOSMONDNIDN-H&FUHJ*HGF656464GI-KEYSTP
PORT=5000

# База данных
DATABASE_URL=postgresql://rentuser:R2ntS2c@localhost:5432/rentdatadb
TEST_DATABASE_URL=postgresql://rentuser:R2ntS2c@localhost:5432/makita_rental_test

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=K2YSTRT-S2C_RANDMOBVKVT876875-H&FUHF656464GI-KEYSTP

# Telegram Bot
TELEGRAM_BOT_TOKEN=7563888297:AAFFamD36WBMnF7fvMkHD0fbcuKcCrbsJac
CHAT_ID=392458818
TELEGRAM_WEBHOOK_URL=https://renttap.aibotrade.ru/webhook/telegram

# Настройки приложения
ITEMS_PER_PAGE=12
MAX_CART_ITEMS=20
MAX_RENTAL_DAYS=10
DEFAULT_DELIVERY_FEE=600
MIN_ORDER_AMOUNT_FOR_FREE_DELIVERY=5000

# Логирование
LOG_LEVEL=INFO
```

### 5. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE rentdatadb;
CREATE USER rentuser WITH PASSWORD 'R2ntS2c';
GRANT ALL PRIVILEGES ON DATABASE rentdatadb TO rentuser;
```

### 6. Инициализация миграций

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Запуск приложения

```bash
python run.py
```

Приложение будет доступно по адресу: http://localhost:5000

## API Endpoints

### Основные страницы
- `GET /` - Главная страница
- `GET /catalog` - Каталог инструментов
- `GET /tool/<id>` - Страница инструмента
- `GET /services` - Страница услуг
- `GET /about` - О компании
- `GET /contact` - Контакты

### API
- `GET /api/cart` - Получить корзину
- `POST /api/cart/add` - Добавить в корзину
- `POST /api/cart/update` - Обновить корзину
- `DELETE /api/cart/remove/<id>` - Удалить из корзины
- `POST /api/orders` - Создать заказ
- `GET /api/orders/<id>` - Получить заказ
- `GET /api/search` - Поиск

## Telegram Bot

Бот интегрирован в приложение и предоставляет:
- Просмотр каталога
- Добавление в корзину
- Оформление заказов
- Отслеживание статуса заказа
- Уведомления

### Настройка бота

1. Бот уже создан с токеном: `7563888297:AAFFamD36WBMnF7fvMkHD0fbcuKcCrbsJac`
2. Webhook настроен на: `https://renttap.aibotrade.ru/webhook/telegram`
3. Chat ID: `392458818`

## Разработка

### Запуск в режиме разработки

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### Запуск тестов

```bash
pytest
```

### Форматирование кода

```bash
black .
flake8 .
```

## Развертывание

### Продакшн

1. Настройте переменные окружения для продакшена
2. Используйте Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

3. Настройте Nginx как reverse proxy
4. Настройте SSL сертификаты
5. Настройте webhook для Telegram бота

### Docker (опционально)

```bash
docker build -t makita-rental .
docker run -p 5000:5000 makita-rental
```

### Docker Compose (рекомендуется)

```bash
# Запуск всего стека
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Модели базы данных

### Основные сущности:
- **User** - Пользователи сайта
- **TelegramUser** - Пользователи Telegram
- **Category** - Категории инструментов
- **Tool** - Инструменты
- **Service** - Услуги
- **CartSession** - Сессии корзины
- **CartItem** - Элементы корзины
- **Order** - Заказы
- **OrderItem** - Элементы заказов
- **Delivery** - Доставка

## Домен и SSL

- **Домен**: renttap.aibotrade.ru
- **SSL**: Настроен в Nginx конфигурации
- **Webhook URL**: https://renttap.aibotrade.ru/webhook/telegram

## Лицензия

MIT License

## Поддержка

Для получения поддержки обращайтесь к разработчикам проекта. 