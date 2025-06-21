# 🚀 Развертывание Makita Rental на VPS

## 📋 Требования

- VPS с Debian 12 или Ubuntu 22.04
- Минимум 2GB RAM
- 20GB свободного места
- Root доступ или sudo права

## 🔧 Подготовка к развертыванию

### 1. Генерация секретных ключей

```bash
# Генерируем SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Генерируем JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Настройка переменных окружения

```bash
export SECRET_KEY="ваш_сгенерированный_secret_key"
export JWT_SECRET_KEY="ваш_сгенерированный_jwt_secret_key"
```

## 🚀 Автоматическое развертывание

### Вариант 1: Использование скрипта развертывания

```bash
# Клонируем репозиторий
git clone https://github.com/gittkid/rentsite.git
cd rentsite

# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем развертывание
./deploy.sh
```

### Вариант 2: Ручное развертывание

#### 1. Подключение к серверу
```bash
ssh userent@88.151.114.49
```

#### 2. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

#### 3. Установка зависимостей
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git
```

#### 4. Создание пользователя приложения
```bash
sudo useradd -m -s /bin/bash makita_app
```

#### 5. Клонирование репозитория
```bash
cd /home/makita_app
sudo -u makita_app git clone https://github.com/gittkid/rentsite.git app
cd app
```

#### 6. Создание виртуального окружения
```bash
sudo -u makita_app python3 -m venv venv
sudo -u makita_app venv/bin/pip install --upgrade pip
sudo -u makita_app venv/bin/pip install -r requirements.txt
```

#### 7. Настройка базы данных
```bash
sudo -u postgres psql -c "CREATE DATABASE rentdatadb;"
sudo -u postgres psql -c "CREATE USER rentuser WITH PASSWORD 'R2ntS2c';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rentdatadb TO rentuser;"
```

#### 8. Создание конфигурации
```bash
sudo -u makita_app cp env.production.example .env
# Отредактируйте .env файл с вашими секретными ключами
```

#### 9. Инициализация базы данных
```bash
sudo -u makita_app venv/bin/flask db upgrade
```

#### 10. Настройка systemd сервиса
```bash
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
```

#### 11. Настройка Nginx
```bash
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
```

#### 12. Активация сервисов
```bash
sudo ln -sf /etc/nginx/sites-available/makita-rental /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl enable makita-rental
sudo systemctl start makita-rental
sudo systemctl restart nginx
```

## 🔍 Проверка развертывания

### Проверка статуса сервисов
```bash
sudo systemctl status makita-rental
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

### Проверка логов
```bash
# Логи приложения
sudo journalctl -u makita-rental -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Проверка доступности
```bash
curl http://88.151.114.49
```

## 🔧 Управление приложением

### Перезапуск приложения
```bash
sudo systemctl restart makita-rental
```

### Обновление кода
```bash
cd /home/makita_app/app
sudo -u makita_app git pull
sudo -u makita_app venv/bin/pip install -r requirements.txt
sudo -u makita_app venv/bin/flask db upgrade
sudo systemctl restart makita-rental
```

### Просмотр логов
```bash
sudo journalctl -u makita-rental -f
```

## 🛡️ Безопасность

### Настройка firewall
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Настройка SSL (опционально)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Мониторинг

### Проверка ресурсов
```bash
htop
df -h
free -h
```

### Проверка процессов
```bash
ps aux | grep gunicorn
ps aux | grep nginx
```

## 🆘 Устранение неполадок

### Приложение не запускается
```bash
sudo systemctl status makita-rental
sudo journalctl -u makita-rental -n 50
```

### Проблемы с базой данных
```bash
sudo -u postgres psql -d rentdatadb -c "\dt"
```

### Проблемы с Nginx
```bash
sudo nginx -t
sudo systemctl status nginx
``` 