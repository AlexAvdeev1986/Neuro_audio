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

Install Docker Desktop
To install Docker Desktop on Fedora:

Set up Docker's [package repository](https://docs.docker.com/engine/install/fedora/#set-up-the-repository).

Download the latest [RPM package](https://desktop.docker.com/linux/main/amd64/docker-desktop-x86_64.rpm?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-linux-amd64&_gl=1*17dgvp8*_gcl_au*MTIwMzk4NDkyLjE3NTA4NjY4NjM.*_ga*ODY4NzUxMjQyLjE3NTA4NjY4NjQ.*_ga_XJWPQMJYHQ*czE3NTA4Njg5OTIkbzIkZzEkdDE3NTA4NjkxOTgkajYwJGwwJGgw). For checksums, see the Release notes. https://docs.docker.com/desktop/release-notes/

Install the package with dnf as follows: