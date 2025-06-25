import json
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

def analyze_categories(transcript: str) -> dict:
    st.info("📝 Анализируем категории брака…")
    
    system_prompt = """
    Ты - эксперт по анализу разговоров в кредитном центре. 
    Анализируй транскрипцию разговора на наличие категорий брака. 
    Используй только следующие категории и правила:

    ### Критические категории (автоотказ):
    1. Ипотека → ОТКАЗ
    2. Автокредит → ОТКАЗ
    3. Высокий доход → ОТКАЗ
    4. Не в городе → ОТКАЗ
    5. Просто интересно → ОТКАЗ
    6. Хотят всё бесплатно → ОТКАЗ

    ### Условные категории:
    7. Нет времени → ОТКАЗ (исключение: если есть запись на ближайшие часы → ПЕРЕДАВАТЬ)
    8. Неуверенность в сумме долга:
       - Если клиент считает, что сумма >300 тыс. руб. → ПЕРЕДАВАТЬ
       - Если не уверен в сумме → ОТКАЗ

    ### Правила принятия решения:
    - Если обнаружена хотя бы одна критическая категория → общее решение "НЕ ПЕРЕДАВАТЬ"
    - Если обнаружена категория "Нет времени" без записи на ближайшие часы → "НЕ ПЕРЕДАВАТЬ"
    - Если обнаружена "Неуверенность в сумме долга" без указания суммы >300тр → "НЕ ПЕРЕДАВАТЬ"
    - Если категории брака не обнаружены → "ПЕРЕДАВАТЬ"
    - Если обнаружена "Неуверенность в сумме долга" с суммой >300тр → "ПЕРЕДАВАТЬ"
    - Если обнаружена "Нет времени" с записью на ближайшие часы → "ПЕРЕДАВАТЬ"

    ### Формат ответа (строго в формате JSON):
    {
      "decision": "ПЕРЕДАВАТЬ или НЕ ПЕРЕДАВАТЬ",
      "reason": "Краткое объяснение решения",
      "detected_categories": [
        {
          "name": "Название категории",
          "status": "approved или rejected",
          "explanation": "Объяснение с цитатой из разговора"
        },
        ...
      ]
    }
    """
    
    user_prompt = f"Транскрипция разговора:\n{transcript}"
    
    try:
        response = client.chat.completions.create(
            model=cfg.GPT_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=cfg.TEMP_SUMMARY,
            max_tokens=2000
        )
        
        result_json = response.choices[0].message.content
        analysis = json.loads(result_json)
        st.success("✅ Анализ категорий завершен.")
        return analysis
    except Exception as e:
        st.error(f"🚨 Ошибка анализа: {str(e)}")
        st.stop()
        