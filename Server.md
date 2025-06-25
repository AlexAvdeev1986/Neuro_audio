# Развертывание проекта Neuro_audio на сервере Ubuntu

Полная инструкция по развертыванию проекта Neuro_audio на сервере Ubuntu с использованием Docker, HTTPS и кастомного домена.

## Подготовка сервера

```bash

# Установка виртуального окружения
sudo apt install python3.10-venv
apt install python3-pip
sudo apt install git

python3 -m venv venv
source venv/bin/activate
git clone https://github.com/AlexAvdeev1986/Neuro_audio.git

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker и Docker Compose
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# Установка Nginx для реверс-прокси
sudo apt install nginx -y
sudo systemctl enable nginx
```

## Структура проекта

Создайте следующую структуру файлов на сервере:

```
/opt/neuro_audio/
├── docker-compose.yml
├── Dockerfile
├── .env
├── nginx/
│   ├── nginx.conf
│   └── ssl-params.conf
└── app/
    ├── app.py
    ├── audio_utils.py
    ├── config.py
    ├── openai_utils.py
    └── requirements.txt
```

## Конфигурационные файлы

### 1. Dockerfile (`/opt/neuro_audio/Dockerfile`)
```dockerfile
FROM python:3.10-slim

# Установка зависимостей для аудио
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. docker-compose.yml (`/opt/neuro_audio/docker-compose.yml`)
```yaml
version: '3.8'

services:
  neuro_audio_app:
    build: .
    container_name: neuro_audio_app
    restart: always
    env_file:
      - .env
    ports:
      - "8501:8501"
    volumes:
      - ./app:/app

  neuro_audio_nginx:
    image: nginx:alpine
    container_name: neuro_audio_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl-params.conf:/etc/nginx/ssl-params.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - neuro_audio_app
```

### 3. Конфигурация Nginx

`/opt/neuro_audio/nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/ssl-params.conf;
    
    server {
        listen 80;
        server_name neuroaudio777.ddns.net;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name neuroaudio777.ddns.net;

        ssl_certificate /etc/letsencrypt/live/neuroaudio777.ddns.net/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/neuroaudio777.ddns.net/privkey.pem;

        location / {
            proxy_pass http://neuro_audio_app:8501;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

`/opt/neuro_audio/nginx/ssl-params.conf`:
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
ssl_ecdh_curve secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```

### 4. requirements.txt (`/opt/neuro_audio/app/requirements.txt`)
```
openai>=1.0.0
streamlit>=1.33.0
pydub>=0.25.1
python-dotenv>=1.0.0
```

## Развертывание проекта

### 1. Получение SSL-сертификата
```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получите сертификат
sudo certbot certonly --standalone -d neuroaudio777.ddns.net --email your@email.com --agree-tos --non-interactive --keep-until-expiring

# Обновите права доступа
sudo chmod -R 755 /etc/letsencrypt/live
```

### 2. Настройка проекта
```bash
# Перейдите в директорию проекта
cd /opt/neuro_audio

# Создайте .env файл с вашим API ключом
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Скопируйте файлы приложения в директорию app/
# (app.py, audio_utils.py, config.py, openai_utils.py)

# Соберите и запустите контейнеры
docker-compose up -d --build
```

### 3. Настройка фаервола
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 4. Настройка автоматического обновления сертификатов
```bash
sudo crontab -e
```

Добавьте строку:
```bash
0 3 * * * /usr/bin/certbot renew --quiet --post-hook "docker exec neuro_audio_nginx nginx -s reload"
```

## Управление приложением

### Команды для управления
```bash
# Запуск приложения
docker-compose up -d

# Остановка приложения
docker-compose down

# Просмотр логов
docker logs neuro_audio_app
docker logs neuro_audio_nginx

# Обновление приложения
git pull origin main  # если используете Git
docker-compose down
docker-compose up -d --build
```

### Проверка работы
Откройте в браузере: `https://neuroaudio777.ddns.net`

## Особенности конфигурации

1. **Безопасность**:
   - Все соединения автоматически перенаправляются на HTTPS
   - Используются современные протоколы шифрования (TLS 1.2/1.3)
   - Реализованы дополнительные заголовки безопасности

2. **Производительность**:
   - Контейнеры автоматически перезапускаются при сбоях
   - Оптимизированная конфигурация Nginx
   - Изолированная среда выполнения

3. **Автоматизация**:
   - Автоматическое обновление SSL-сертификатов
   - Автоматический перезапуск Nginx после обновления сертификатов
   - Простое обновление приложения

4. **Масштабируемость**:
   - Конфигурация готова к добавлению новых сервисов
   - Возможность легко добавить балансировку нагрузки
   - Поддержка горизонтального масштабирования

## Решение возможных проблем

### Если домен не разрешается
1. Проверьте, что домен `neuroaudio777.ddns.net` указывает на IP-адрес вашего сервера
2. Убедитесь, что в DNS-настройках нет ошибок
3. Проверьте работу динамического DNS, если IP не статический

### Если не работает HTTPS
1. Проверьте наличие сертификатов:
   ```bash
   sudo ls /etc/letsencrypt/live/neuroaudio777.ddns.net/
   ```
2. Убедитесь, что права доступа корректны:
   ```bash
   sudo chmod -R 755 /etc/letsencrypt/live
   ```
3. Проверьте логи Nginx:
   ```bash
   docker logs neuro_audio_nginx
   ```

### Если приложение не запускается
1. Проверьте логи приложения:
   ```bash
   docker logs neuro_audio_app
   ```
2. Убедитесь, что API ключ в .env файле корректен
3. Проверьте, что все файлы приложения скопированы в директорию `app/`

Эта конфигурация обеспечит надежную и безопасную работу вашего приложения Neuro_audio с поддержкой HTTPS и кастомного домена.