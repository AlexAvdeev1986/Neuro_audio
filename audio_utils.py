import os
import tempfile
from pydub import AudioSegment
import streamlit as st

ALLOWED_EXT = [".mp3", ".wav"]

def prepare_audio(uploaded_file) -> str:
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("❌ Поддерживаются только mp3 и wav")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    if ext == ".mp3":
        wav_path = tmp_path.replace(".mp3", ".wav")
        AudioSegment.from_mp3(tmp_path).export(wav_path, format="wav")
        os.remove(tmp_path)
        return wav_path

    return tmp_path
