import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- ASTREIA 独立構成 ---
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

# 音声を出すための仕掛け
audio_placeholder = st.empty()

def speak_text(text):
    q = urllib.parse.quote(text)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
    audio_html = f'<audio autoplay="true"><source src="{url}" type="audio/mpeg"></audio>'
    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

st.title("✨ ASTREIA")
st.caption(f"Personal English Partner | 30yo Intelligence")

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
            "You are a standalone partner. Be warm, professional and concise. 2 sentences max."
        )
        model = genai.GenerativeModel(STABLE_MODEL)
        chat = model.start_chat(history=[{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]])
        response = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(response.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": response.text})
        
        with open(ASTREIA_PRIVATE_MEMORY, "a", encoding="utf-8") as f:
            f.write(f"User: {prompt}\nASTREIA: {response.text}\n")
        
        # ここで音声を再生
        speak_text(response.text)
