import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 構成設定 ---
STABLE_MODEL = "gemini-2.5-flash"
THINKING_MODE = "high"
ASTREIA_PRIVATE_MEMORY = "astreia_memory.txt"

st.set_page_config(page_title="ASTREIA", page_icon="✨")

# API設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーをSecretsに設定してください。")

# 記憶の復元
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
    if os.path.exists(ASTREIA_PRIVATE_MEMORY):
        with open(ASTREIA_PRIVATE_MEMORY, "r", encoding="utf-8") as f:
            for line in f:
                if "User: " in line:
                    st.session_state.chat_memory.append({"role": "user", "content": line.replace("User: ", "").strip()})
                elif "ASTREIA: " in line:
                    st.session_state.chat_memory.append({"role": "assistant", "content": line.replace("ASTREIA: ", "").strip()})

st.title("✨ ASTREIA")

# 過去の会話表示
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 入力
if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_instruction = (
            f"Level: {THINKING_MODE}. You are ASTREIA, a 30yo empathetic friend. "
            "Standalone mode. Warm, professional English. Max 2 sentences."
        )
        model = genai.GenerativeModel(STABLE_MODEL)
        history = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]]
        chat = model.start_chat(history=history)
        response = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        # 1. まずテキストを表示
        st.markdown(response.text)
        
        # 2. 次に「音声プレイヤー」を確実に表示
        q = urllib.parse.quote(response.text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
        st.audio(url, format="audio/mpeg", autoplay=True)
        
        # 3. 記憶を更新
        st.session_state.chat_memory.append({"role": "assistant", "content": response.text})
        with open(ASTREIA_PRIVATE_MEMORY, "a", encoding="utf-8") as f:
            f.write(f"User: {prompt}\nASTREIA: {response.text}\n")
