import os
import time
import streamlit as st
from audio_utils import prepare_audio
from openai_utils import transcribe_audio, generate_document
from config import get_config

# Инициализация конфига
cfg = get_config()

# Настройка страницы
st.set_page_config(
    page_title="Анализ разговоров → Категории брака", 
    page_icon="📋",
    layout="wide"
)

# Стили
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1E90FF;
    }
    .category-box {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .new-category { border-left: 5px solid #FF4B4B; background-color: #fff0f0; }
    .existing-category { border-left: 5px solid #0F9D58; background-color: #f0fff0; }
    .keep-category { border-left: 5px solid #4285F4; background-color: #f0f8ff; }
    .download-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .result-card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .section-title {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .rule-item {
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #3498db;
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("🎙️ Анализ разговоров → 📋 Категории брака")
st.caption("Загрузите запись разговора → Получите транскрипцию и структурированный документ с категориями")

# Правила категорий
with st.expander("📋 Правила категоризации брака", expanded=True):
    st.subheader("Новые категории (с 12.06)")
    st.markdown("""
    <div class="rule-item">1. <span class="highlight">Нет времени</span> → Ставим напоминание перезвонить</div>
    <div class="rule-item">2. <span class="highlight">Неуверенность в сумме долга</span> → 
        <ul>
            <li>Если >300 тыс. руб. → передаем</li>
            <li>Если неуверен → уточняем и перезваниваем</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Категории брака (с 09.06)")
    st.markdown("""
    <div class="rule-item">1. <span class="highlight">Ипотека</span> → не передаем (нет заказчика)</div>
    <div class="rule-item">2. <span class="highlight">Автокредит</span> → не передаем (нет заказчика)</div>
    <div class="rule-item">3. <span class="highlight">Высокий доход</span> → считаем формулу</div>
    <div class="rule-item">4. <span class="highlight">Не в городе</span> → ставим задачу на перезвон</div>
    <div class="rule-item">5. <span class="highlight">Просто интересно</span> → не лид</div>
    <div class="rule-item">6. <span class="highlight">Хотят всё бесплатно</span> → не лид</div>
    """, unsafe_allow_html=True)

# Главный контейнер
with st.container():
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("1. Загрузка аудио")
        uploaded = st.file_uploader(
            "Выберите аудиофайл разговора", 
            type=["mp3", "wav"],
            accept_multiple_files=False,
            help="Поддерживаются MP3 и WAV файлы записей разговоров"
        )
        
        if uploaded:
            st.success(f"✅ Файл загружен: {uploaded.name}")
            if st.button("🚀 Начать анализ", type="primary", use_container_width=True):
                st.session_state.process = True
        else:
            st.info("ℹ️ Загрузите mp3 или wav файл разговора")
            st.session_state.clear()
    
    if uploaded and st.session_state.get("process"):
        progress_bar = st.progress(0, text="Подготовка аудио...")
        
        try:
            # Шаг 1: Подготовка аудио
            time.sleep(0.5)
            progress_bar.progress(15, text="Конвертация аудио...")
            wav_file = prepare_audio(uploaded)
            
            # Шаг 2: Транскрибация
            time.sleep(0.5)
            progress_bar.progress(35, text="Транскрибация (это займет 1-5 минут)...")
            transcript = transcribe_audio(wav_file)
            st.session_state.transcript = transcript
            
            # Шаг 3: Генерация документа
            time.sleep(0.5)
            progress_bar.progress(65, text="Анализ категорий брака...")
            document = generate_document(transcript)
            st.session_state.document = document
            
            # Завершение
            time.sleep(0.5)
            progress_bar.progress(100, text="Готово!")
            time.sleep(0.5)
            progress_bar.empty()
            
            # Очистка временных файлов
            try:
                os.remove(wav_file)
            except:
                pass
                
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")
            st.stop()
    
    # Отображение результатов
    if st.session_state.get("document"):
        with col2:
            st.subheader("2. Результаты анализа")
            
            # Транскрипт
            with st.expander("📝 Полная транскрипция разговора", expanded=True):
                st.text_area("Транскрипция", 
                            st.session_state.transcript, 
                            height=300,
                            label_visibility="collapsed")
            
            # Документ с категориями
            st.subheader("📋 Категории брака", divider="blue")
            document = st.session_state.document
            
            # Автоматическое форматирование документа
            sections = {
                "Новые категории": "new-category",
                "Категории брака": "existing-category",
                "Оставляем": "keep-category"
            }
            
            for section, css_class in sections.items():
                start_idx = document.find(f"### {section}")
                if start_idx >= 0:
                    end_idx = document.find("###", start_idx + 1)
                    content = document[start_idx:end_idx].strip() if end_idx != -1 else document[start_idx:]
                    
                    # Извлекаем только список
                    if ":" in content:
                        content = content.split(":", 1)[1].strip()
                    
                    with st.container():
                        st.markdown(f'<div class="category-box {css_class}">'
                                   f'<h3>{section}</h3>'
                                   f'<div style="margin-top:0.5rem">{content}</div>'
                                   f'</div>', 
                                   unsafe_allow_html=True)
            
            # Секция скачивания
            st.subheader("💾 Сохранить результаты", divider="gray")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Скачать транскрипцию",
                    data=st.session_state.transcript,
                    file_name="транскрипция_разговора.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="Скачать документ с категориями",
                    data=st.session_state.document,
                    file_name="категории_брака.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                