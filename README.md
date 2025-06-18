# Neuro_audio

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


