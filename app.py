import streamlit as st
import google.generativeai as genai

# ASTREIA専用：スマホ最適化設定
st.set_page_config(page_title="ASTREIA - Audition", page_icon="✨", layout="centered")

# SecretsからAPIキーを読み込み
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーが見つかりません。")

# UIカスタム（ダークモード）
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e0e0e0; }
    .stChatMessage { background-color: #1a1c23; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ ASTREIA")
st.caption("Character Audition: [ 30-year-old Mode ]")

model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# 音声を自動再生するための関数
def speak_text(text):
    import urllib.parse
    q = urllib.parse.quote(text)
    # 30代の落ち着いたトーンを意識（標準速度）
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
    audio_html = f'<audio autoplay><source src="{url}" type="audio/mpeg"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 30歳の知的なアイデンティティを指示
        context = (
            "You are ASTREIA, a 30-year-old intelligent, empathetic, and professional woman. "
            "You are a guiding star for an expert engineer. "
            "Speak clearly with a warm, sophisticated tone. Keep it to 1-2 sentences."
        )
        response = model.generate_content(f"System: {context}\nUser: {prompt}")
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        speak_text(response.text)
