import os
import warnings
import logging
import asyncio
from dataclasses import dataclass
from getpass import getpass
import time

import openai
import whisper
from pydub import AudioSegment
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# сразу после импорта logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


# Подавляем специфические предупреждения
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# ----------------- Configuration ----------------- #
@dataclass
class Config:
    TELEGRAM_TOKEN: str
    OPENAI_API_KEY: str
    WHISPER_MODEL: str = "base"
    GPT_MODEL: str = "gpt-4-turbo"
    AUDIO_CACHE: str = "audio_cache"
    TEMP_TRANSCRIBE: float = 0.2
    TEMP_SUMMARY: float = 0.5

    def __post_init__(self):
        os.makedirs(self.AUDIO_CACHE, exist_ok=True)


# ----------------- Audio Processor ----------------- #
class AudioProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    async def prepare(self, update: Update, status_msg) -> str:
        if not update.message.audio:
            raise ValueError("Пожалуйста, отправьте аудиофайл в формате MP3 или WAV.")

        file_name = update.message.audio.file_name
        tg_file = await update.message.audio.get_file()
        file_size = tg_file.file_size / 1024  # in KB
        await status_msg.edit_text(f"🔄 Загружаем аудиофайл '{file_name}' ({file_size:.2f} KB)...")

        ext = os.path.splitext(file_name)[1].lower()
        if ext not in ['.mp3', '.wav']:
            raise ValueError("Неподдерживаемый формат файла. Пожалуйста, отправьте аудиофайл в формате MP3 или WAV.")

        raw_path = os.path.join(self.config.AUDIO_CACHE, f"{tg_file.file_id}{ext}")
        await tg_file.download_to_drive(custom_path=raw_path)
        self.logger.info(f"Downloaded audio to {raw_path}")
        await status_msg.edit_text(f"✅ Файл '{file_name}' загружен.")

        if ext == '.mp3':
            await status_msg.edit_text(f"🔄 Конвертация '{file_name}' из MP3 в WAV...")
            wav_path = os.path.splitext(raw_path)[0] + '.wav'
            audio = AudioSegment.from_mp3(raw_path)
            audio.export(wav_path, format="wav")
            self.logger.info(f"Converted MP3 to WAV: {wav_path}")
            os.remove(raw_path)
            await status_msg.edit_text(f"✅ Конвертация завершена: '{os.path.basename(wav_path)}'")
            return wav_path

        return raw_path


# ----------------- Meeting Processor ----------------- #
class MeetingProcessor:
    def __init__(self, config: Config):
        openai.api_key = config.OPENAI_API_KEY
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Загружаем модель Whisper...")
        self.whisper_model = whisper.load_model(config.WHISPER_MODEL)
        self.logger.info("Модель Whisper загружена.")

    async def transcribe(self, audio_path: str, status_msg) -> str:
        self.logger.info("Начало транскрипции")
        await status_msg.edit_text("🔍 Транскрипция аудио... Это может занять несколько минут.")
        result = await asyncio.to_thread(self.whisper_model.transcribe, audio_path)
        text = result.get('text', '')
        self.logger.info("Транскрипция завершена")
        await status_msg.edit_text("✅ Транскрипция готова.")
        return text

    async def extract_rejects(self, transcript: str, status_msg) -> str:
        self.logger.info("Генерация документа по транскрипции")
        await status_msg.edit_text("📝 Генерация документа... Пожалуйста, подождите.")
        prompt = (
            "На основе следующей транскрипции встречи сотрудников сформируй документ в формате:\n"
            "1) Новые категории брака, НЕ подлежащие передаче с КЦ с 12.06:\n"
            "<пронумерованный список>\n\n"
            "2) Категории брака, НЕ подлежащие передаче с КЦ с 09.06:\n"
            "<пронумерованный список>\n\n"
            "3) Оставляем:\n"
            "<список через дефис>\n"
            f"Транскрипция:\n{transcript}\n"
            "Ответь только документом, без пояснений."
        )
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=self.config.GPT_MODEL,
            messages=[
                {"role": "system", "content": "Ты помощник для формирования документа из протокола собрания."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.TEMP_SUMMARY
        )
        doc = response.choices[0].message.content.strip()
        self.logger.info("Документ с категориями брака сформирован")
        await status_msg.edit_text("✅ Документ сформирован.")
        return doc


# ----------------- Telegram Bot ----------------- #
class RejectsBot:
    def __init__(self, config: Config):
        self.config = config
        self.audio_proc = AudioProcessor(config)
        self.meeting_proc = MeetingProcessor(config)

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        self.app = Application.builder().token(config.TELEGRAM_TOKEN).build()
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(MessageHandler(filters.AUDIO, self.handle))

    async def start(self, update: Update, context):
        await update.message.reply_text(
            "🤖 Добро пожаловать! Я бот для обработки аудиозаписей встреч.\n"
            "Отправьте мне аудиофайл в формате MP3 или WAV, и я сформирую документ с категориями брака."
        )

    async def handle(self, update: Update, context):
        status = await update.message.reply_text("🔄 Запуск обработки...")
        audio_path = None
        start_time = time.time()
        try:
            # Подготовка аудио
            audio_path = await self.audio_proc.prepare(update, status)

            # Транскрипция
            transcript = await self.meeting_proc.transcribe(audio_path, status)

            # Извлечение категорій брака
            document = await self.meeting_proc.extract_rejects(transcript, status)

            # Отправка результата
            duration = time.time() - start_time
            await status.edit_text(f"📄 Готовый документ:\n{document}\n\nВремя обработки: {duration:.2f} секунд.")
        except ValueError as e:
            await status.edit_text(f"❌ Ошибка: {e}")
        except openai.error.OpenAIError as e:
            await status.edit_text("❌ Ошибка при обращении к OpenAI API. Пожалуйста, попробуйте позже.")
        except Exception as e:
            self.logger.error(f"Неизвестная ошибка: {e}")
            await status.edit_text("❌ Произошла неизвестная ошибка. Пожалуйста, попробуйте позже.")
        finally:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    self.logger.info(f"Удален файл {audio_path}")
                except Exception as e:
                    self.logger.warning(f"Не удалось удалить файл {audio_path}: {e}")

    def run(self):
        self.logger.info("RejectsBot запущен")
        self.app.run_polling()


# ----------------- Entry Point ----------------- #
if __name__ == '__main__':
    config = Config(
        TELEGRAM_TOKEN=getpass('Telegram Token: '),
        OPENAI_API_KEY=getpass('OpenAI API Key: ')
    )
    bot = RejectsBot(config)
    bot.run()
    