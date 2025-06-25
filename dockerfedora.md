# Установка Moby Engine (открытый аналог Docker)
sudo dnf install -y moby-engine

# Установка Docker CLI
sudo dnf install -y docker-cli

# Установка Docker Compose
sudo dnf install -y docker-compose

# Запуск и настройка
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

## Проверка установки
# Проверка версий
docker --version
docker-compose --version

# Запуск тестового контейнера
docker run --rm hello-world

# Проверка работы Docker Compose
mkdir test-docker && cd test-docker
cat > docker-compose.yml << EOF
version: '3'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
EOF

docker-compose up -d
curl localhost:8080
docker-compose down
cd ..
rm -rf test-docker

## Если ничего не помогает: Установка через Flatpak

# 1. Установка Flatpak
sudo dnf install -y flatpak

# 2. Добавление репозитория Flathub
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# 3. Установка Docker Desktop через Flatpak
flatpak install flathub com.docker.desktop

# 4. Запуск Docker Desktop
flatpak run com.docker.desktop

# 5. Настройка командной строки
echo "alias docker='flatpak run com.docker.desktop docker'" >> ~/.bashrc
source ~/.bashrc