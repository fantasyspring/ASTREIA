import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 設定 ---
STABLE_MODEL = "gemini-2.5-flash"
ASTREIA_PRIVATE_MEMORY = "astreia_memory.txt"

st.set_page_config(page_title="ASTREIA", page_icon="✨")

# APIキー設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーを設定してください。")

# 記憶と「直前の声」の保持
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
if "last_voice_text" not in st.session_state:
    st.session_state.last_voice_text = ""

# 音声再生用コンテナ
audio_box = st.container()

def play_voice(text):
    if text:
        q = urllib.parse.quote(text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
        audio_box.audio(url, format="audio/mpeg", autoplay=True)

st.title("✨ ASTREIA")

# --- リプレイ機能 ---
if st.session_state.last_voice_text:
    if st.button("🔄 Replay Last Voice"):
        play_voice(st.session_state.last_voice_text)

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
        # 30歳・知的・独立人格
        instruction = "You are ASTREIA, a 30yo brilliant woman. Standalone partner. Professional and warm English. Max 2 sentences."
        model = genai.GenerativeModel(STABLE_MODEL)
        
        # 履歴を考慮した生成
        history = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]]
        chat = model.start_chat(history=history)
        res = chat.send_message(f"System: {instruction}\nUser: {prompt}")
        
        st.markdown(res.text)
        
        # 状態の更新
        st.session_state.last_voice_text = res.text
        st.session_state.chat_memory.append({"role": "assistant", "content": res.text})
        
        # 記憶ファイルに保存
        with open(ASTREIA_PRIVATE_MEMORY, "a", encoding="utf-8") as f:
            f.write(f"User: {prompt}\nASTREIA: {res.text}\n")
        
        # 即座に再生
        play_voice(res.text)
