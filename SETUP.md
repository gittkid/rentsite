# Инструкции по настройке и запуску

## Быстрый старт

### 1. Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository-url>
cd makita_rental_flask

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Создание базы данных PostgreSQL
sudo -u postgres psql
CREATE DATABASE rentdatadb;
CREATE USER rentuser WITH PASSWORD 'R2ntS2c';
GRANT ALL PRIVILEGES ON DATABASE rentdatadb TO rentuser;
\q
```

### 3. Настройка переменных окружения

```bash
# Копирование файла конфигурации
cp env.example .env

# Редактирование .env файла
nano .env
```

Содержимое `.env` файла:
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

### 4. Инициализация базы данных

```bash
# Инициализация миграций
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Запуск приложения

```bash
# Запуск Flask приложения
python run.py

# В отдельном терминале - запуск Telegram бота
python run_bot.py
```

## Запуск через Docker

### 1. Сборка и запуск

```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 2. Только база данных и Redis

```bash
# Запуск только базы данных и Redis
docker-compose up -d postgres redis

# Подключение к базе данных
docker exec -it makita_postgres psql -U rentuser -d rentdatadb
```

## Настройка Telegram бота

### 1. Создание бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Настройка webhook (для продакшена)

```bash
# Установка webhook
curl -X POST "https://api.telegram.org/bot7563888297:AAFFamD36WBMnF7fvMkHD0fbcuKcCrbsJac/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://aibotrade.ru/webhook/telegram"}'
```

### 3. Тестирование бота

```bash
# Запуск бота в режиме polling (для разработки)
python run_bot.py
```

## Структура проекта

```
makita_rental_flask/
├── app/                    # Flask приложение
│   ├── __init__.py        # Инициализация приложения
│   ├── config.py          # Конфигурация
│   ├── models/            # Модели базы данных
│   ├── main/              # Основные страницы
│   ├── api/               # API endpoints
│   └── static/            # Статические файлы
├── bot/                   # Telegram бот
│   ├── __init__.py        # Инициализация бота
│   ├── handlers/          # Обработчики сообщений
│   └── keyboards/         # Клавиатуры
├── migrations/            # Миграции базы данных
├── tests/                 # Тесты
├── requirements.txt       # Зависимости
├── run.py                 # Запуск Flask приложения
├── run_bot.py            # Запуск Telegram бота
├── Dockerfile            # Docker конфигурация
├── docker-compose.yml    # Docker Compose
└── README.md             # Документация
```

## API Endpoints

### Основные страницы
- `GET /` - Главная страница
- `GET /catalog` - Каталог инструментов
- `GET /tool/<id>` - Страница инструмента
- `GET /services` - Страница услуг

### API
- `GET /api/cart` - Получить корзину
- `POST /api/cart/add` - Добавить в корзину
- `POST /api/orders` - Создать заказ
- `GET /api/search` - Поиск

## Тестирование

```bash
# Запуск тестов
pytest

# Запуск с покрытием
pytest --cov=app

# Запуск линтера
flake8 app bot

# Форматирование кода
black app bot
```

## Развертывание в продакшене

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Настройка SSL

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d renttap.aibotrade.ru
```

### 3. Развертывание

```bash
# Клонирование проекта
git clone <repository-url>
cd makita_rental_flask

# Настройка переменных окружения
cp env.example .env
nano .env

# Запуск
docker-compose up -d
```

## Мониторинг и логи

```bash
# Просмотр логов приложения
docker-compose logs -f web

# Просмотр логов базы данных
docker-compose logs -f postgres

# Просмотр логов Nginx
docker-compose logs -f nginx
```

## Резервное копирование

```bash
# Создание резервной копии базы данных
docker exec makita_postgres pg_dump -U rentuser rentdatadb > backup.sql

# Восстановление из резервной копии
docker exec -i makita_postgres psql -U rentuser rentdatadb < backup.sql
```

## Устранение неполадок

### Проблемы с базой данных
```bash
# Проверка подключения
docker exec makita_postgres psql -U rentuser -d rentdatadb -c "SELECT 1;"

# Сброс миграций
flask db stamp head
flask db migrate
flask db upgrade
```

### Проблемы с Telegram ботом
```bash
# Проверка токена
curl "https://api.telegram.org/bot7563888297:AAFFamD36WBMnF7fvMkHD0fbcuKcCrbsJac/getMe"

# Удаление webhook
curl -X POST "https://api.telegram.org/bot7563888297:AAFFamD36WBMnF7fvMkHD0fbcuKcCrbsJac/deleteWebhook"
```

### Проблемы с Docker
```bash
# Пересборка контейнеров
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Очистка Docker
docker system prune -a
``` 