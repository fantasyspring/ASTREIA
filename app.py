import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- CONFIG ---
STABLE_MODEL = "gemini-2.5-flash"
st.set_page_config(page_title="ASTREIA", page_icon="✨")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
if "last_voice_url" not in st.session_state:
    st.session_state.last_voice_url = ""

def play_voice(url):
    st.audio(url, format="audio/mpeg", autoplay=True)

st.title("✨ ASTREIA")

# --- REPLAY BUTTON (STRICTLY FUNCTIONAL) ---
if st.session_state.last_voice_url:
    # This is the button you can click
    if st.button("🔄 Replay Last Voice"):
        play_voice(st.session_state.last_voice_url)

# CHAT HISTORY
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# INPUT
if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # STRICTLY ENGLISH ONLY INSTRUCTION
        system_instruction = (
            "You are ASTREIA, a 30yo brilliant woman and English partner. "
            "No Japanese. Strictly English. "
            "1. Correct the user's sentence if unnatural. "
            "2. Provide: [Simple] (easy) and [Native] (sophisticated) versions. "
            "3. Reply as a friend to keep the conversation going."
        )
        
        model = genai.GenerativeModel(STABLE_MODEL)
        chat = model.start_chat(history=[{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]])
        res = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(res.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": res.text})
        
        # CREATE VOICE URL
        q = urllib.parse.quote(res.text)
        new_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
        st.session_state.last_voice_url = new_url
        
        # PLAY IMMEDIATELY
        play_voice(new_url)
        st.rerun()
