#!/bin/bash

# Скрипт развертывания Makita Rental на VPS

set -e

echo "🚀 Начинаем развертывание Makita Rental..."

# Проверяем наличие необходимых переменных
if [ -z "$SECRET_KEY" ]; then
    echo "❌ Ошибка: SECRET_KEY не установлен"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ Ошибка: JWT_SECRET_KEY не установлен"
    exit 1
fi

# Обновляем систему
echo "📦 Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем зависимости..."
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl wget

# Создаем пользователя для приложения
echo "👤 Создаем пользователя приложения..."
sudo useradd -m -s /bin/bash makita_app || true

# Клонируем репозиторий
echo "📥 Клонируем репозиторий..."
cd /home/makita_app
sudo -u makita_app git clone https://github.com/gittkid/rentsite.git app
cd app

# Создаем виртуальное окружение
echo "🐍 Создаем виртуальное окружение..."
sudo -u makita_app python3 -m venv venv
sudo -u makita_app venv/bin/pip install --upgrade pip
sudo -u makita_app venv/bin/pip install -r requirements.txt

# Настраиваем базу данных
echo "🗄️ Настраиваем базу данных..."
sudo -u postgres psql -c "CREATE DATABASE rentdatadb;" || true
sudo -u postgres psql -c "CREATE USER rentuser WITH PASSWORD 'R2ntS2c';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rentdatadb TO rentuser;" || true

# Создаем файл переменных окружения
echo "⚙️ Создаем конфигурацию..."
sudo -u makita_app cp env.production.example .env
sudo -u makita_app sed -i "s/ВАШ_СЕКРЕТНЫЙ_КЛЮЧ_ДЛЯ_ПРОДАКШЕНА/$SECRET_KEY/g" .env
sudo -u makita_app sed -i "s/ВАШ_JWT_СЕКРЕТНЫЙ_КЛЮЧ_ДЛЯ_ПРОДАКШЕНА/$JWT_SECRET_KEY/g" .env

# Инициализируем базу данных
echo "🗃️ Инициализируем базу данных..."
sudo -u makita_app venv/bin/flask db upgrade

# Настраиваем systemd сервис
echo "🔧 Настраиваем systemd сервис..."
sudo tee /etc/systemd/system/makita-rental.service > /dev/null <<EOF
[Unit]
Description=Makita Rental Flask Application
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=makita_app
WorkingDirectory=/home/makita_app/app
Environment=PATH=/home/makita_app/app/venv/bin
ExecStart=/home/makita_app/app/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Настраиваем Nginx
echo "🌐 Настраиваем Nginx..."
sudo tee /etc/nginx/sites-available/makita-rental > /dev/null <<EOF
server {
    listen 80;
    server_name 88.151.114.49;

    location /static/ {
        alias /home/makita_app/app/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /webhook/telegram {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активируем сайт
sudo ln -sf /etc/nginx/sites-available/makita-rental /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Запускаем сервисы
echo "🚀 Запускаем сервисы..."
sudo systemctl daemon-reload
sudo systemctl enable makita-rental
sudo systemctl start makita-rental
sudo systemctl restart nginx
sudo systemctl restart redis

# Проверяем статус
echo "✅ Проверяем статус сервисов..."
sudo systemctl status makita-rental --no-pager
sudo systemctl status nginx --no-pager

echo "🎉 Развертывание завершено!"
echo "🌐 Приложение доступно по адресу: http://88.151.114.49"
echo "📝 Логи приложения: sudo journalctl -u makita-rental -f" 