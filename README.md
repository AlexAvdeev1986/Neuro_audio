# Neuro_audio


## 🎯 Анализатор Лидов по Аудио
## Автоматическая транскрипция аудиозаписей встреч и категоризация лидов на основе заданных правил.

## 🚀 Функции
## Транскрипция аудио через OpenAI Whisper API
## Автоматическая категоризация лидов по правилам брака
## Визуализация процесса с прогресс-барами и анимациями
## Интерактивный интерфейс с вкладками и результатами
## Экспорт результатов в текстовый файл
## 📋 Категории брака
## 🚫 Новые категории брака (НЕ передавать с 12.06):
## Нет времени - клиент говорит что нет времени, нужно поставить напомин


# Чтобы использовать Python 3.9 в проектах, создавайте виртуальные окружения:
```bash
python3.9 -m venv venv
source venv/bin/activate

python3.9 --version


# ## Установка зависимостей
# Выполните эту ячейку для установки необходимых библиотек

pip install -q python-telegram-bot openai yt-dlp whisper noisereduce soundfile numpy tqdm pydub nest_asyncio

# Зта установка помогает избежать несовместимостей и неожиданных изменений в API, которые могут возникнуть при обновлении до более новой версии.

pip install openai==0.28

# Для обработки аудио

sudo dnf install -y ffmpeg

# Если проблеммы то
sudo dnf install -y ffmpeg > /dev/null  

# Для Транскрибации аудиофайлов

pip install git+https://github.com/openai/whisper.git 

Как запускать

# bash
pip install python-dotenv


# Проще
pip install -r requirements.txt


pip install streamlit openai pydub
streamlit run app.py

