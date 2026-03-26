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

# --- アプリ本体に蓄積する「学習済みデータ」 ---
# ここに必要なことを書き込んでおけば、ASTREIAは履歴がなくても「わかっている」状態になります
USER_LEARNING_DATA = """
- David is a senior engineer (25+ years) in lithography.
- Prefers logic-first, high-spec discussion.
- Focus: Building GENESIS OS.
"""

st.set_page_config(page_title="ASTREIA GENESIS-V1", page_icon="✨")

# API設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # ローカル実行時は環境変数や直接入力でも対応可能に
    api_key = st.sidebar.text_input("API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)

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
st.title("✨ ASTREIA (GENESIS OS Prototype)")
st.caption(f"Project: {PROJECT_ID} | Running on: {HIGH_SPEC_MODEL}")

# 表示用の履歴（APIには投げない）
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

# STT（gemini-2.5-flash）
if text_input:
    user_content = text_input
elif audio_data:
    model_stt = genai.GenerativeModel(STABLE_MODEL)
    audio_blob = {'mime_type': 'audio/wav', 'data': audio_data['bytes']}
    stt_res = model_stt.generate_content(["Transcribe accurately.", audio_blob])
    user_content = stt_res.text

# 応答処理（gemini-3.1-pro-preview）
if user_content:
    st.session_state.messages.append({"role": "user", "content": user_content})
    with st.chat_message("user"):
        st.markdown(user_content)

    with st.chat_message("assistant"):
        # 履歴を送る代わりに、学習済みデータ(USER_LEARNING_DATA)をシステム指示に含める
        system_instruction = (
            f"You are ASTREIA. User Profile: {USER_LEARNING_DATA}. "
            f"Mode: {THINKING_MODE}. Reply in 2 sentences. Focus on high-level English. "
            "No full history provided, so focus ONLY on the current input."
        )
        
        model = genai.GenerativeModel(HIGH_SPEC_MODEL)
        # 履歴を送らず、単発のリクエストとして送信（クォータ節約）
        response = model.generate_content(f"System: {system_instruction}\nUser: {user_content}")
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        play_audio(response.text)
