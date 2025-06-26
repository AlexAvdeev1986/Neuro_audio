# Полное руководство по развертыванию Neuro_audio на Ubuntu сервере

## 1. Подготовка сервера Ubuntu

```bash
```bash
## Полное руководство по развертыванию Neuro_audio на Ubuntu сервере
1. Подготовка сервера Ubuntu
Обновление системы
bash
sudo apt update && sudo apt upgrade -y

```bash
# Установка виртуального окружения
sudo apt install python3.10-venv
apt install python3-pip
sudo apt install git

```bash
# Клонируем репозиторий
git clone https://github.com/AlexAvdeev1986/neuroaudio.git

cd neuroaudio
python3 -m venv venv
source venv/bin/activate
```bash
# Для обработки аудио

sudo apt install -y ffmpeg

# Если проблеммы то
sudo apt install -y ffmpeg > /dev/null  

```bash
# Для Транскрибации аудиофайлов

pip install git+https://github.com/openai/whisper.git 

```bash

# устанавливаем зависимости
pip install -r requirements.txt
```bash

# Обновление системы
sudo apt update && sudo apt upgrade -y

### Установка Docker и Docker Compose
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка для применения изменений
sudo reboot
```

### Установка Nginx и Certbot
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

## 2. Структура проекта

Создайте структуру проекта:
```bash
mkdir -p /opt/neuroaudio
cd /opt/neuroaudio
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для временных файлов
RUN mkdir -p /tmp/audio_temp

# Порт для Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Запуск приложения
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
```

### requirements.txt
```txt
streamlit>=1.28.0
openai>=1.3.0
pydub>=0.25.1
python-dotenv>=1.0.0
requests>=2.31.0
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  neuroaudio:
    build: .
    container_name: neuroaudio_app
    restart: unless-stopped
    ports:
      - "127.0.0.1:8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./logs:/app/logs
      - /tmp/audio_temp:/tmp/audio_temp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 512M
```

### .env файл
```env
OPENAI_API_KEY=your_openai_api_key_here
```

```bash
## 4. Настройка Nginx

### /etc/nginx/sites-available/neuroaudio
```nginx
server {
    listen 80;
    server_name neuroaudio777.ddns.net;
    
    # Перенаправление HTTP на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name neuroaudio777.ddns.net;
    
    # SSL сертификаты (будут созданы Certbot)
    ssl_certificate /etc/letsencrypt/live/neuroaudio777.ddns.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/neuroaudio777.ddns.net/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Увеличение лимитов для загрузки файлов
    client_max_body_size 100M;
    client_body_timeout 120s;
    client_header_timeout 120s;
    
    # Proxy к Streamlit приложению
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Для WebSocket соединений Streamlit
        proxy_buffering off;
    }
    
    # Статические файлы Streamlit
    location ^~ /static {
        proxy_pass http://127.0.0.1:8501/static/;
    }
    
    # Health check
    location /_stcore/health {
        proxy_pass http://127.0.0.1:8501/_stcore/health;
        access_log off;
    }
}
```

## 5. Скрипты для управления

### start.sh
```bash
#!/bin/bash
cd /opt/neuroaudio

# Проверка .env файла
if [ ! -f .env ]; then
    echo "Ошибка: .env файл не найден!"
    exit 1
fi

# Запуск приложения
docker-compose up -d --build

echo "Neuroaudio запущен!"
echo "Проверить статус: docker-compose ps"
echo "Логи: docker-compose logs -f"
```

### stop.sh
```bash
#!/bin/bash
cd /opt/neuroaudio
docker-compose down
echo "Neuroaudio остановлен!"
```

### restart.sh
```bash
#!/bin/bash
cd /opt/neuroaudio
docker-compose down
docker-compose up -d --build
echo "Neuroaudio перезапущен!"
```

### update.sh
```bash
#!/bin/bash
cd /opt/neuroaudio

# Остановка приложения
docker-compose down

# Обновление кода (если используется git)
# git pull origin main

# Пересборка и запуск
docker-compose up -d --build

echo "Neuroaudio обновлен и перезапущен!"
```

## 6. Системный сервис (опционально)

### /etc/systemd/system/neuroaudio.service
```ini
[Unit]
Description=Neuroaudio Docker Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/neuroaudio
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

## 7. Пошаговая установка

### 1. Подготовка файлов
```bash
# Создание директории
sudo mkdir -p /opt/neuroaudio
sudo chown $USER:$USER /opt/neuroaudio
cd /opt/neuroaudio

# Копирование ваших файлов Python
# app.py, audio_utils.py, openai_utils.py, config.py

# Создание Dockerfile, docker-compose.yml, requirements.txt
# (используйте содержимое выше)

# Создание .env файла
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

### 2. Настройка прав доступа
```bash
chmod +x /opt/neuroaudio/*.sh
sudo chown -R $USER:$USER /opt/neuroaudio
```

### 3. Настройка Nginx
```bash
# Создание конфига Nginx
sudo cp /opt/neuroaudio/nginx.conf /etc/nginx/sites-available/neuroaudio
sudo ln -s /etc/nginx/sites-available/neuroaudio /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Проверка конфигурации
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx
```

### 4. Получение SSL сертификата
```bash
# Убедитесь, что домен neuroaudio777.ddns.net указывает на ваш сервер
sudo certbot --nginx -d neuroaudio777.ddns.net

# Настройка автообновления сертификата
sudo crontab -e
# Добавьте строку:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 5. Запуск приложения
```bash
cd /opt/neuroaudio
./start.sh
```

### 6. Включение автозапуска при перезагрузке
```bash
sudo systemctl enable neuroaudio
sudo systemctl start neuroaudio
```

## 8. Мониторинг и логи

### Проверка статуса
```bash
# Статус контейнеров
docker-compose ps

# Логи приложения
docker-compose logs -f neuroaudio

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Системные ресурсы
docker stats
```

### Настройка ротации логов
```bash
# /etc/logrotate.d/neuroaudio
/opt/neuroaudio/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    postrotate
        docker-compose -f /opt/neuroaudio/docker-compose.yml restart neuroaudio
    endscript
}
```

## 9. Бэкап и восстановление

### Скрипт бэкапа
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/neuroaudio"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап конфигурации
tar -czf $BACKUP_DIR/neuroaudio_config_$DATE.tar.gz \
    -C /opt/neuroaudio \
    --exclude=logs \
    .

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Бэкап создан: $BACKUP_DIR/neuroaudio_config_$DATE.tar.gz"
```

## 10. Безопасность

### Firewall настройки
```bash
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Fail2ban для защиты от брутфорса
```bash
sudo apt install fail2ban -y

# /etc/fail2ban/jail.local
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
```

## 11. Финальная проверка

После выполнения всех шагов:

1. Откройте https://neuroaudio777.ddns.net
2. Убедитесь, что сайт загружается по HTTPS
3. Проверьте, что приложение работает корректно
4. Загрузите тестовый аудиофайл
