# Развертывание проекта Neuro_audio на сервере Ubuntu

# Полная настройка Neuro\_audio с Docker, Nginx, SSL и Watchtower

## Что будет делаться:

1. Соберём Docker-образ для Streamlit-приложения.
2. Установим nginx-proxy + Let's Encrypt.
3. Настроим HTTPS с доменом neuroaudio777.ddns.net.
4. Добавим Watchtower для автообновления контейнеров.

---

## Подготовка сервера

```bash

# Установка виртуального окружения
sudo apt install python3.10-venv
apt install python3-pip
sudo apt install git
# Клонируем репозиторий
git clone https://github.com/AlexAvdeev1986/Neuro_audio.git

cd Neuro_audio
python3 -m venv venv
source venv/bin/activate


# Для обработки аудио

sudo apt install -y ffmpeg

# Если проблеммы то
sudo apt install -y ffmpeg > /dev/null  

# Для Транскрибации аудиофайлов

pip install git+https://github.com/openai/whisper.git 

# устанавливаем зависимости
pip install -r requirements.txt

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker и Docker Compose
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Nginx для реверс-прокси
sudo apt install nginx -y
sudo systemctl enable nginx

```

#

## 1. Установка Docker и Docker Compose

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

---

## 2. Структура проекта

```
~/neuro-audio/
├── app.py
├── audio_utils.py
├── config.py
├── openai_utils.py
├── requirements.txt
├── Dockerfile
├── .env
└── docker-compose.yml
```

---

## 3. Dockerfile

```Dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false
CMD ["streamlit", "run", "app.py"]
```

---

## 4. requirements.txt

```txt
streamlit
openai
python-dotenv
pydub
```

---

## 5. .env

```env
OPENAI_API_KEY=your_openai_key
```

---

## 6. docker-compose.yml

```yaml
version: '3.8'

services:
  nginx-proxy:
    image: jwilder/nginx-proxy:latest
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/nginx/certs
      - /etc/nginx/vhost.d
      - /usr/share/nginx/html
      - /var/run/docker.sock:/tmp/docker.sock:ro
    restart: unless-stopped

  letsencrypt:
    image: jrcs/letsencrypt-nginx-proxy-companion
    container_name: nginx-proxy-letsencrypt
    depends_on:
      - nginx-proxy
    volumes:
      - /etc/nginx/certs
      - /etc/nginx/vhost.d
      - /usr/share/nginx/html
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      NGINX_PROXY_CONTAINER: nginx-proxy
    restart: unless-stopped

  neuro-audio:
    build: .
    image: neuro-audio:latest
    container_name: neuro-audio
    expose:
      - "8501"
    environment:
      VIRTUAL_HOST: neuroaudio777.ddns.net
      LETSENCRYPT_HOST: neuroaudio777.ddns.net
      LETSENCRYPT_EMAIL: your@email.com
      STREAMLIT_SERVER_PORT: 8501
      STREAMLIT_SERVER_HEADLESS: "true"
    restart: unless-stopped

  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 300 --cleanup
    restart: unless-stopped
```

---

## 7. Старт

```bash
docker-compose build
docker-compose up -d
```

---

## 8. Проверка

После старта приложение будет доступно по:

```
https://neuroaudio777.ddns.net
```

---

## Альтернативы:

* Traefik (вместо nginx-proxy)
* GitHub Actions CI/CD + DockerHub
* VPS с auto-deploy через CapRover/Portainer

🔹 Все запущенные контейнеры:
bash
Copy
Edit
docker ps
🔹 Все контейнеры, включая остановленные:
bash
Copy
Edit
docker ps -a
❌ Удаление контейнеров
🔹 Удалить один контейнер:
bash
Copy
Edit
docker stop <container_id>
docker rm <container_id>
Например:

bash
docker rm d4f5b1c3f6ab
🔹 Удалить все остановленные контейнеры:
bash
Copy
Edit
docker container prune
Будет подтверждение y/n — нажми y.

