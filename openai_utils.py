import streamlit as st
from openai import OpenAI
from config import get_config

cfg = get_config()
client = OpenAI(api_key=cfg.OPENAI_API_KEY)

def transcribe_audio(wav_path: str) -> str:
    st.info("🔍 Транскрибируем аудио через Whisper API…")
    try:
        with open(wav_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=cfg.TRANSCRIBE_MODEL, 
                file=audio_file,
                temperature=cfg.TEMP_TRANSCRIBE,
                response_format="text"
            )
        st.success("✅ Транскрипция готова.")
        return transcript
    except Exception as e:
        st.error(f"🚨 Ошибка транскрибации: {str(e)}")
        st.stop()

def generate_document(transcript: str) -> str:
    st.info("📝 Генерируем документ категорий брака…")
    prompt = (
        "Сформируй структурированный документ на основе транскрипции встречи. "
        "Используй только следующий формат:\n\n"
        
        "### Новые категории брака, НЕ подлежащие передаче с КЦ с 12.06:\n"
        "<список с нумерацией>\n\n"
        
        "### Категории брака, НЕ подлежащие передаче с КЦ с 09.06:\n"
        "<список с нумерацией>\n\n"
        
        "### Оставляем:\n"
        "<список с нумерацией>\n\n"
        
        "Примеры категорий:\n"
        "- 'Нет времени' → ставим напоминание перезвонить\n"
        "- 'Неуверенность в сумме долга' → уточняем сумму\n"
        "- Ипотека/автокредит → не передаем\n"
        "- Высокий доход → считаем формулу\n"
        "- 'Не в городе' → ставим задачу на перезвон\n"
        "- 'Просто интересно' → не лид\n\n"
        
        f"Транскрипция:\n{transcript}\n\n"
        "Ответь ТОЛЬКО документом в указанном формате без пояснений!"
    )
    
    try:
        response = client.chat.completions.create(
            model=cfg.GPT_MODEL,
            messages=[
                {"role": "system", "content": "Ты эксперт по категоризации брака в кредитном центре"},
                {"role": "user", "content": prompt}
            ],
            temperature=cfg.TEMP_SUMMARY,
            max_tokens=1000
        )
        doc = response.choices[0].message.content
        st.success("✅ Документ сформирован.")
        return doc.strip()
    except Exception as e:
        st.error(f"🚨 Ошибка генерации документа: {str(e)}")
        st.stop()
        