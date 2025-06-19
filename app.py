import os
import time
import streamlit as st
from audio_utils import prepare_audio
from openai_utils import transcribe_audio, analyze_categories
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
    .decision-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
    }
    .approved { background-color: #d4edda; color: #155724; border: 2px solid #c3e6cb; }
    .rejected { background-color: #f8d7da; color: #721c24; border: 2px solid #f5c6cb; }
    .rule-item {
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #3498db;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .detected-item {
        background: #fff3cd;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ffc107;
    }
    .reason-box {
        background: #e2e3e5;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .category-header {
        background: #6c757d;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin-top: 1.5rem;
    }
    .highlight {
        background-color: #fffacd;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("🎙️ Анализ разговоров → 📋 Категории брака")
st.caption("Загрузите запись разговора → Получите анализ категорий брака и решение по передаче лида")

# Правила категорий
with st.expander("📋 Правила категоризации брака", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Критические категории (автоотказ)")
        st.markdown("""
        <div class="rule-item">
            <b>1. Ипотека</b> → нет заказчика на залоги → <span class="highlight">ОТКАЗ</span>
        </div>
        <div class="rule-item">
            <b>2. Автокредит</b> → нет заказчика на залоги → <span class="highlight">ОТКАЗ</span>
        </div>
        <div class="rule-item">
            <b>3. Высокий доход</b> → считаем формулу → <span class="highlight">ОТКАЗ</span>
        </div>
        <div class="rule-item">
            <b>4. Не в городе</b> → ставим задачу на перезвон → <span class="highlight">ОТКАЗ</span>
        </div>
        <div class="rule-item">
            <b>5. Просто интересно</b> → не лид → <span class="highlight">ОТКАЗ</span>
        </div>
        <div class="rule-item">
            <b>6. Хотят всё бесплатно</b> → не лид → <span class="highlight">ОТКАЗ</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Условные категории")
        st.markdown("""
        <div class="rule-item">
            <b>1. Нет времени</b> → 
            <ul>
                <li>Нельзя фиксировать как лид → <span class="highlight">ОТКАЗ</span></li>
                <li>Ставим напоминание перезвонить</li>
                <li>Исключение: запись на ближайшие часы → <span class="highlight">ПЕРЕДАВАТЬ</span></li>
            </ul>
        </div>
        <div class="rule-item">
            <b>2. Неуверенность в сумме долга</b> → 
            <ul>
                <li>Считает, что >300 тыс. руб. → <span class="highlight">ПЕРЕДАВАТЬ</span></li>
                <li>Не уверен → уточнить и перезвонить → <span class="highlight">ОТКАЗ</span></li>
                <li>Проверить вместе на сайте ФССП</li>
            </ul>
        </div>
        <div class="rule-item">
            <b>Остальные случаи</b> → <span class="highlight">ПЕРЕДАВАТЬ</span>
        </div>
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
            
            # Шаг 3: Анализ категорий
            time.sleep(0.5)
            progress_bar.progress(65, text="Анализ категорий брака...")
            analysis_result = analyze_categories(transcript)
            st.session_state.analysis = analysis_result
            
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
    if st.session_state.get("analysis"):
        with col2:
            st.subheader("2. Результаты анализа")
            analysis = st.session_state.analysis
            
            # Транскрипт
            with st.expander("📝 Полная транскрипция разговора", expanded=False):
                st.text_area("Транскрипция", 
                            st.session_state.transcript, 
                            height=200,
                            label_visibility="collapsed")
            
            # Решение по записи
            st.subheader("📋 Решение по записи", divider="blue")
            
            if analysis["decision"] == "ПЕРЕДАВАТЬ":
                decision_class = "approved"
                decision_icon = "✅"
            else:
                decision_class = "rejected"
                decision_icon = "❌"
                
            st.markdown(
                f'<div class="decision-box {decision_class}">'
                f'{decision_icon} {analysis["decision"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Причина решения
            st.markdown(
                f'<div class="reason-box">'
                f'<b>Причина:</b> {analysis["reason"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Обнаруженные категории
            if analysis["detected_categories"]:
                st.subheader("🔍 Обнаруженные категории брака", divider="blue")
                
                for category in analysis["detected_categories"]:
                    status = "🟢 ПЕРЕДАВАТЬ" if category["status"] == "approved" else "🔴 ОТКАЗ"
                    st.markdown(
                        f'<div class="detected-item">'
                        f'<b>{category["name"]}</b> → {status}<br>'
                        f'<i>Обоснование:</i> {category["explanation"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.success("✅ Категории брака не обнаружены - запись передается")
            
            # Секция скачивания
            st.subheader("💾 Сохранить результаты", divider="gray")
            
            # Формируем текстовый отчёт для скачивания
            report = f"Анализ разговора: {uploaded.name}\n\n"
            report += f"Решение: {analysis['decision']}\n"
            report += f"Причина: {analysis['reason']}\n\n"
            
            if analysis["detected_categories"]:
                report += "Обнаруженные категории брака:\n"
                for cat in analysis["detected_categories"]:
                    status = "ПЕРЕДАВАТЬ" if cat["status"] == "approved" else "ОТКАЗ"
                    report += f"- {cat['name']} → {status}\n"
                    report += f"  Обоснование: {cat['explanation']}\n\n"
            
            report += "\n\nТранскрипция разговора:\n"
            report += st.session_state.transcript
            
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
                    label="Скачать полный отчёт",
                    data=report,
                    file_name="анализ_категорий_брака.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                