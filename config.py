import os
from dataclasses import dataclass
import streamlit as st
from dotenv import load_dotenv

# Загружаем .env (должен лежать рядом с кодом)
load_dotenv()

@dataclass
class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = "gpt-4-turbo"
    TRANSCRIBE_MODEL: str = "whisper-1"
    TEMP_TRANSCRIBE: float = 0.2
    TEMP_SUMMARY: float = 0.5

@st.cache_resource
def get_config() -> Config:
    # Если ключ не задан в .env, запрашиваем вручную
    if not os.getenv("OPENAI_API_KEY"):
        key = st.text_input("Введите OpenAI API Key", type="password")
        os.environ["OPENAI_API_KEY"] = key
    return Config()
