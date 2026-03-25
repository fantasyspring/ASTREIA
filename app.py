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

# --- ユーザー設定 ---
USER_PROFILE = {
    "name": "David",
    "style": "Professional, logical, conclusion-first",
    "interests": "Semiconductor technology, Science, Education",
}

st.set_page_config(page_title="ASTREIA GENESIS-V1", page_icon="✨")

# API設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("ERROR: GEMINI_API_KEY is missing in Secrets.")

if "messages" not in st.session_state:
    st.session_state.messages = []

def play_audio(text):
    tts = gTTS(text=text, lang='en', tld='com')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# --- UI構築 ---
st.title("✨ ASTREIA (GENESIS OS Inside)")
st.caption(f"Project: {PROJECT_ID} | Active Models: {STABLE_MODEL} & {HIGH_SPEC_MODEL}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()
input_col, mic_col = st.columns([0.85, 0.15])

with input_col:
    text_input = st.chat_input("Type or Speak...")

with mic_col:
    audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key='recorder')

user_content = None

# 1. 音声認識（STT） - STABLE_MODEL(gemini-2.5-flash) を使用
if text_input:
    user_content = text_input
elif audio_data:
    with st.spinner("Processing Voice..."):
        model_stt = genai.GenerativeModel(STABLE_MODEL)
        audio_blob = {'mime_type': 'audio/wav', 'data': audio_data['bytes']}
        stt_res = model_stt.generate_content(["Transcribe accurately.", audio_blob])
        user_content = stt_res.text

# 2. メイン思考（LLM） - HIGH_SPEC_MODEL(gemini-3.1-pro-preview) を使用
if user_content:
    st.session_state.messages.append({"role": "user", "content": user_content})
    with st.chat_message("user"):
        st.markdown(user_content)

    with st.chat_message("assistant"):
        system_instruction = (
            f"You are ASTREIA. Partner: {USER_PROFILE['name']}. Style: {USER_PROFILE['style']}. "
            f"Interests: {USER_PROFILE['interests']}. Mode: {THINKING_MODE}. "
            "Reply in 2 natural sentences. Direct professional correction in () if required."
        )
        
        model = genai.GenerativeModel(HIGH_SPEC_MODEL)
        history = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
        chat = model.start_chat(history=history)
        
        response = chat.send_message(f"System: {system_instruction}\nUser: {user_content}")
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        play_audio(response.text)
