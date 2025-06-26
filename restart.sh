#!/bin/bash
cd /opt/neuroaudio
docker-compose down
docker-compose up -d --build
echo "Neuroaudio перезапущен!"