# ---【マスター指定の絶対基準】---
PROJECT_ID = "genesis-os-490623"
LOCATION = "us-central1"
STABLE_MODEL = "gemini-2.5-flash"
HIGH_SPEC_MODEL = "gemini-3.1-pro-preview"
THINKING_MODE = "high"
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import base64
import os

# --- 教育的コンテキスト（本体蓄積用） ---
# ASTREIAがあなたの背景を理解し、適切な距離感で話すための設定
CONTEXT = """
- User: David, Senior Engineer (25+ yrs).
- Field: Semiconductor/Liquid Crystal Lithography.
- Goal: Professional English Training & Intelligent Conversation.
"""

st.set_page_config(page_title="ASTREIA English", page_icon="✨")

# API設定
# Streamlit Cloudの場合はSecrets、ローカルの場合は環境変数から取得
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key not found. Please set GEMINI_API_KEY.")

if "messages" not in st.session_state:
    st.session_state.messages = []

def play_audio(text):
    """テキストを音声に変換して自動再生する"""
    try:
        tts = gTTS(text=text, lang='en', tld='com')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio Error: {e}")

# --- UI構築 ---
st.title("✨ ASTREIA")
st.caption(f"Connected via {STABLE_MODEL} | Location: {LOCATION}")

# 履歴表示（UI上のスクロール用）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()
# 入力インターフェース（テキストとマイクの共存）
input_col, mic_col = st.columns([0.85, 0.15])

with input_col:
    text_input = st.chat_input("Type your message here...")
with mic_col:
    # 音声入力ボタン
    audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key='recorder')

user_content = None

# 1. 入力の取得と音声認識（STT）
if text_input:
    user_content = text_input
elif audio_data:
    with st.spinner("Listening..."):
        # 2.5-flashを使用して高速に文字起こし
        model_stt = genai.GenerativeModel(STABLE_MODEL)
        audio_blob = {'mime_type': 'audio/wav', 'data': audio_data['bytes']}
        try:
            stt_res = model_stt.generate_content(["Transcribe the following English audio exactly.", audio_blob])
            user_content = stt_res.text
        except Exception as e:
            st.error(f"STT Error: {e}")

# 2. 回答の生成と音声出力
if user_content:
    # ユーザー発言を画面と履歴に追加
    st.session_state.messages.append({"role": "user
