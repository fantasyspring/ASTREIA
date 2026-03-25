import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 設定 ---
STABLE_MODEL = "gemini-2.5-flash"
MEMORY_FILE = "astreia_memory.txt"

st.set_page_config(page_title="ASTREIA", page_icon="✨")

# APIキー設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーを設定してください。")

# 記憶の復元
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []

# --- 【重要】音声を画面の一番上に配置するコンテナ ---
audio_box = st.container()

# 音声生成関数
def play_voice(text):
    q = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
    # ここに音声バーを出現させる
    audio_box.audio(url, format="audio/mpeg", autoplay=True)

st.title("✨ ASTREIA")

# 会話履歴の表示
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 入力欄
if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 30歳・知的・独立人格の設定
        instruction = "You are ASTREIA, a 30yo brilliant woman. Speak in professional and warm English. Max 2 sentences."
        model = genai.GenerativeModel(STABLE_MODEL)
        
        # 簡易記憶
        res = model.generate_content(f"System: {instruction}\nContext: {st.session_state.chat_memory[-5:]}\nUser: {prompt}")
        
        st.markdown(res.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": res.text})
        
        # 声を「画面上部」に出す
        play_voice(res.text)
