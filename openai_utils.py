# openai_utils.py
import openai
import streamlit as st
from config import get_config

cfg = get_config()
openai.api_key = cfg.OPENAI_API_KEY

def transcribe_audio(wav_path: str) -> str:
    st.info("🔍 Транскрибируем аудио через Whisper API…")
    with open(wav_path, "rb") as f:
        resp = openai.Audio.transcribe(
            model=cfg.TRANSCRIBE_MODEL, file=f, temperature=cfg.TEMP_TRANSCRIBE
        )
    text = resp.get("text", "")
    st.success("✅ Транскрипция готова.")
    return text

def generate_document(transcript: str) -> str:
    st.info("📝 Генерируем документ категорий брака…")
    prompt = (
        "На основе следующей транскрипции встречи сотрудников сформируй документ в формате:\n"
        "1) Новые категории брака, НЕ подлежащие передаче с КЦ с 12.06:\n<список>\n\n"
        "2) Категории брака, НЕ подлежащие передаче с КЦ с 09.06:\n<список>\n\n"
        "3) Оставляем:\n<список>\n\n"
        f"Транскрипция:\n{transcript}\n"
        "Ответь только документом без лишних пояснений."
    )
    resp = openai.ChatCompletion.create(
        model=cfg.GPT_MODEL,
        messages=[
            {"role": "system", "content": "Ты ассистент для формирования служебного документа."},
            {"role": "user", "content": prompt}
        ],
        temperature=cfg.TEMP_SUMMARY
    )
    doc = resp.choices[0].message.content.strip()
    st.success("✅ Документ сформирован.")
    return doc
