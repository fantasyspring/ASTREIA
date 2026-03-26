import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import base64
import os
import warnings

# ---【マスター指定の絶対基準】---
PROJECT_ID = "genesis-os-490623"
LOCATION = "us-central1"
STABLE_MODEL = "gemini-2.5-flash"
HIGH_SPEC_MODEL = "gemini-3.1-pro-preview"
THINKING_MODE = "high"
warnings.filterwarnings("ignore", category=UserWarning)

# --- 教育的コンテキスト（本体蓄積用） ---
CONTEXT = """
- User: David, Senior Engineer (25+ yrs).
- Field: Semiconductor/Liquid Crystal Lithography.
- Goal: Build GENESIS OS / Professional English Training.
"""

st.set_page_config(page_title="ASTREIA High-Speed", page_icon="⚡")

# API設定
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key not found.")

if "messages" not in st.session_state:
    st.session_state.messages = []

def play_audio(text):
    tts = gTTS(text=text, lang='en', tld='com')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# --- UI ---
st.title("⚡ ASTREIA (Flash Mode)")
st.caption(f"Using {STABLE_MODEL} for high stability and speed.")

# 表示用の履歴（メモリ節約のためAPIには直近のみ送信）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()
input_col, mic_col = st.columns([0.85, 0.15])

with input_col:
    text_input = st.chat_input("Input here...")
with mic_col:
    audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key='recorder')

user_content = None

# 1. 音声認識（STT）- 2.5-flash
if text_input:
    user_content = text_input
elif audio_data:
    with st.spinner("Listening..."):
        model_stt = genai.GenerativeModel(STABLE_MODEL)
        audio_blob = {'mime_type': 'audio/wav', 'data': audio_data['bytes']}
        stt_res = model_stt.generate_content(["Transcribe.", audio_blob])
        user_content = stt_res.text

# 2. 思考・回答生成（LLM）- 2.5-flash に一本化してエラー回避
if user_content:
    st.session_state.messages.append({"role": "user", "content": user_content})
    with st.chat_message("user"):
        st.markdown(user_content)

    with st.chat_message("assistant"):
        system_instruction = (
            f"You are ASTREIA. Context: {CONTEXT} Mode: {THINKING_MODE}. "
            "Reply in 2 natural sentences. Direct professional correction in () if required."
        )
        
        # クォータの緩い 2.5-flash をメイン思考に使用
        model = genai.GenerativeModel(STABLE_MODEL)
        
        # 履歴を送らず単発処理にすることでトークンとリソースを節約
        response = model.generate_content(f"System: {system_instruction}\nUser: {user_content}")
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        play_audio(response.text)
