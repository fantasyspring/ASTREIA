import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 設定 ---
STABLE_MODEL = "gemini-2.5-flash"
st.set_page_config(page_title="ASTREIA", page_icon="✨")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
if "last_voice_url" not in st.session_state:
    st.session_state.last_voice_url = ""

st.title("✨ ASTREIA")

# --- 【最優先】画面最上部に再生バーを固定 ---
if st.session_state.last_voice_url:
    st.info("🔄 Last Voice / 聞き直しはこちら")
    st.audio(st.session_state.last_voice_url, format="audio/mpeg")

# チャット履歴
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 入力欄
if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 添削と会話を同時に行う指示
        system_instruction = (
            "You are ASTREIA, a 30yo brilliant English coach. "
            "Step 1: Correct the user's English if it's unnatural. "
            "Step 2: Show [Simple] and [Native] versions of 'what the user wanted to say'. "
            "Step 3: Reply to the conversation naturally. "
            "Keep it concise."
        )
        
        model = genai.GenerativeModel(STABLE_MODEL)
        chat = model.start_chat(history=[{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_memory[:-1]])
        res = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(res.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": res.text})
        
        # 音声URLを作成して保存
        q = urllib.parse.quote(res.text)
        new_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=en&client=tw-ob"
        st.session_state.last_voice_url = new_url
        
        # 実行時にも鳴らす
        st.audio(new_url, format="audio/mpeg", autoplay=True)
        st.rerun() # 画面を更新してトップのプレイヤーに反映させる
