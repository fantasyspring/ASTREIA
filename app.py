import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 設定 ---
STABLE_MODEL = "gemini-2.5-flash"
MEMORY_FILE = "astreia_memory.txt"

st.set_page_config(page_title="ASTREIA", page_icon="✨")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーを設定してください。")

# 状態管理（記憶と直前の音声を保持）
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
if "last_voice" not in st.session_state:
    st.session_state.last_voice = ""

def play_voice(text):
    if text:
        q = urllib.parse.quote(text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
        st.audio(url, format="audio/mpeg", autoplay=True)

st.title("✨ ASTREIA")

# --- 【改善】リプレイボタンを押しやすい位置に ---
if st.session_state.last_voice:
    if st.button("🔄 Hear that again? (もう一度聞く)"):
        play_voice(st.session_state.last_voice)

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
        # 教育者としての指示を強化
        system_instruction = (
            "You are ASTREIA, a 30yo brilliant woman and English coach. "
            "If the user's English has errors, gently correct them first. "
            "Then, provide: 1) [Simple] (easy version) and 2) [Native] (natural, sophisticated version). "
            "Finally, reply as a warm friend. Keep the total response concise."
        )
        
        model = genai.GenerativeModel(STABLE_MODEL)
        history = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]]
        chat = model.start_chat(history=history)
        
        # 思考レベルを上げた生成
        res = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(res.text)
        st.session_state.last_voice = res.text
        st.session_state.chat_memory.append({"role": "assistant", "content": res.text})
        
        # 声を出す
        play_voice(res.text)
