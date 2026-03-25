import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- GENESIS OS 構成定義 ---
STABLE_MODEL = "gemini-2.5-flash"
THINKING_MODE = "high"
MEMORY_FILE = "genesis_memory.txt"  # 創造の神の記憶の断片

st.set_page_config(page_title="ASTREIA", page_icon="✨")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーを設定してください。")

# --- 記憶の読み込み機能 ---
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
    # ファイルがあれば過去の記憶を復元
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if "User: " in line:
                    st.session_state.chat_memory.append({"role": "user", "content": line.replace("User: ", "").strip()})
                elif "ASTREIA: " in line:
                    st.session_state.chat_memory.append({"role": "assistant", "content": line.replace("ASTREIA: ", "").strip()})

# 音声再生
def speak_text(text):
    q = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
    st.markdown(f'<audio autoplay><source src="{url}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

st.title("✨ ASTREIA")
st.caption(f"Connected to GENESIS OS Memory | {STABLE_MODEL}")

# 過去の会話表示
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 30歳の知的パートナー、かつ「すべてを記憶するOSの一部」としてのプロンプト
        system_instruction = (
            f"Level: {THINKING_MODE}. You are ASTREIA, the 30-year-old interface of GENESIS OS. "
            "You are a brilliant, empathetic partner. Use your shared history to guide the user. "
            "Never forget past interactions. Speak in warm, concise English."
        )
        
        model = genai.GenerativeModel(STABLE_MODEL)
        chat = model.start_chat(history=[{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]])
        response = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(response.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": response.text})
        
        # 記憶をファイルに永続化（GENESIS OSの基盤へ）
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"User: {prompt}\n")
            f.write(f"ASTREIA: {response.text}\n")
        
        speak_text(response.text)
