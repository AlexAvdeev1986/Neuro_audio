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