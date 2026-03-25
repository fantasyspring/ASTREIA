import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os

# --- 設定 ---
STABLE_MODEL = "gemini-2.5-flash"
THINKING_MODE = "high"
ASTREIA_PRIVATE_MEMORY = "astreia_memory.txt"

st.set_page_config(page_title="ASTREIA", page_icon="✨")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーをSecretsに設定してください。")

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
    if os.path.exists(ASTREIA_PRIVATE_MEMORY):
        with open(ASTREIA_PRIVATE_MEMORY, "r", encoding="utf-8") as f:
            for line in f:
                if "User: " in line:
                    st.session_state.chat_memory.append({"role": "user", "content": line.replace("User: ", "").strip()})
                elif "ASTREIA: " in line:
                    st.session_state.chat_memory.append({"role": "assistant", "content": line.replace("ASTREIA: ", "").strip()})

def get_audio_bytes(text):
    # Google Translate TTSのリクエスト制限を回避するためライブラリを使用
    tts = gTTS(text=text, lang='en', tld='com')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

st.title("✨ ASTREIA")
st.caption("30yo Professional Partner | Standalone")

# 過去の会話
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_instruction = (
            f"Think at a '{THINKING_MODE}' level. You are ASTREIA, a 30-year-old brilliant woman. "
            "Be warm, professional and concise. 2 sentences max in English."
        )
        model = genai.GenerativeModel(STABLE_MODEL)
        chat = model.start_chat(history=[{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]])
        response = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(response.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": response.text})
        
        # 記憶に保存
        with open(ASTREIA_PRIVATE_MEMORY, "a", encoding="utf-8") as f:
            f.write(f"User: {prompt}\nASTREIA: {response.text}\n")
        
        # 音声生成と表示
        audio_bytes = get_audio_bytes(response.text)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
