import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GPT_MODEL = "gpt-4.1-nano"
        self.TRANSCRIBE_MODEL = "whisper-1"
        self.TEMP_TRANSCRIBE = 0.2
        self.TEMP_SUMMARY = 0.5

@st.cache_resource
def get_config():
    if not os.getenv("OPENAI_API_KEY"):
        key = st.sidebar.text_input("Введите OpenAI API Key", type="password")
        if key:
            os.environ["OPENAI_API_KEY"] = key
            st.rerun()
    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🔑 Требуется OpenAI API Key! Добавьте его в .env или введите в боковой панели")
        st.stop()
    
    return Config()
