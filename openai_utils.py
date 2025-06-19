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
    st.info("📝 Анализируем категории брака…")
    prompt = (
        "Ты - эксперт по анализу разговоров в кредитном центре. "
        "На основе транскрипции разговора определи категории брака по следующим правилам:\n\n"
        
        "### Новые категории (с 12.06):\n"
        "1. Если клиент говорит 'нет времени' или подобное → 'Нет времени': ставим напоминание перезвонить\n"
        "2. Если клиент неуверен в сумме долга → 'Неуверенность в сумме долга': "
        "если сумма >300 тыс. руб. - передаем, иначе уточняем\n\n"
        
        "### Категории брака (с 09.06):\n"
        "1. Если упоминается ипотека → 'Ипотека': не передаем\n"
        "2. Если упоминается автокредит → 'Автокредит': не передаем\n"
        "3. Если высокий доход → 'Высокий доход': считаем формулу\n"
        "4. Если клиент не в городе → 'Не в городе': ставим задачу на перезвон\n"
        "5. Если клиент просто интересуется → 'Просто интересно': не лид\n"
        "6. Если клиент хочет всё бесплатно → 'Хотят всё бесплатно': не лид\n\n"
        
        "### Оставляем (передаем):\n"
        "Все остальные случаи, которые не попадают в категории брака\n\n"
        
        "Формат ответа:\n"
        "### Новые категории, НЕ подлежащие передаче с КЦ с 12.06:\n"
        "<список с нумерацией>\n\n"
        "### Категории брака, НЕ подлежащие передаче с КЦ с 09.06:\n"
        "<список с нумерацией>\n\n"
        "### Оставляем (передаем):\n"
        "<список с нумерацией>\n\n"
        
        f"Транскрипция разговора:\n{transcript}\n\n"
        "Ответь ТОЛЬКО документом в указанном формате без пояснений!"
    )
    
    try:
        response = client.chat.completions.create(
            model=cfg.GPT_MODEL,
            messages=[
                {"role": "system", "content": "Ты ассистент для анализа разговоров в кредитном центре"},
                {"role": "user", "content": prompt}
            ],
            temperature=cfg.TEMP_SUMMARY,
            max_tokens=1000
        )
        doc = response.choices[0].message.content
        st.success("✅ Анализ категорий завершен.")
        return doc.strip()
    except Exception as e:
        st.error(f"🚨 Ошибка анализа: {str(e)}")
        st.stop()
        