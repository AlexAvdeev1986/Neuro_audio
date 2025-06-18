import os
import streamlit as st
from config import get_config
from audio_utils import prepare_audio
from openai_utils import transcribe_audio, generate_document

# загружаем конфиг (теперь с поддержкой .env)
cfg = get_config()
st.set_page_config(page_title="Audio→Document", layout="wide")

st.title("🤖 Audio → Транскрипт → Документ категорий брака")
st.markdown("Файл mp3/wav → транскрипция → готовый документ")

uploaded = st.file_uploader("Выберите аудио файл", type=["mp3", "wav"])
if not uploaded:
    st.info("Загрузите mp3 или wav, чтобы начать.")
    st.stop()

# Подготовка
st.info("🔄 Подготовка аудио…")
wav_file = prepare_audio(uploaded)

# Транскрипция
transcript = transcribe_audio(wav_file)
st.text_area("📜 Транскрипт", transcript, height=200)

# Генерация документа
document = generate_document(transcript)
st.text_area("📄 Итоговый документ", document, height=200)

# Очистка
try:
    os.remove(wav_file)
except OSError:
    pass
