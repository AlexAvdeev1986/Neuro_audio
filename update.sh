#!/bin/bash
cd /opt/neuroaudio

# Остановка приложения
docker-compose down

# Обновление кода (если используется git)
# git pull origin main

# Пересборка и запуск
docker-compose up -d --build

echo "Neuroaudio обновлен и перезапущен!"