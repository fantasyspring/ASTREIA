import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os
import base64

# --- 1. 定数・設定 (あなたのこだわりを反映) ---
STABLE_MODEL = "gemini-2.5-flash"
THINKING_MODE = "high"
ASTREIA_PRIVATE_MEMORY = "astreia_memory.txt"

st.set_page_config(page_title="ASTREIA", page_icon="✨", layout="centered")

# --- 2. API設定 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーをStreamlitのSecretsに設定してください。")

# --- 3. 独立した記憶のロード ---
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
    if os.path.exists(ASTREIA_PRIVATE_MEMORY):
        with open(ASTREIA_PRIVATE_MEMORY, "r", encoding="utf-8") as f:
            for line in f:
                if "User: " in line:
                    st.session_state.chat_memory.append({"role": "user", "content": line.replace("User: ", "").strip()})
                elif "ASTREIA: " in line:
                    st.session_state.chat_memory.append({"role": "assistant", "content": line.replace("ASTREIA: ", "").strip()})

# --- 4. 音声生成関数 (iPhone/Safari対応) ---
def get_audio_html(text):
    tts = gTTS(text=text, lang='en', tld='com')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()
    # 外部URLではなく、データを直接HTMLに埋め込むことでSafariのブロックを回避
    b64_audio = base64.b64encode(audio_bytes).decode()
    return f'<audio autoplay="true" controls src="data:audio/mp3;base64,{b64_audio}" style="width:100%;"></audio>'

# --- 5. UI構成 ---
st.title("✨ ASTREIA")
st.caption(f"Standalone English Partner | {STABLE_MODEL}")

# 過去の会話を表示
for m in st.session_state.chat_memory:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. 対話実行 ---
if prompt := st.chat_input("Speak to ASTREIA..."):
    st.session_state.chat_memory.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 30歳の知的なパートナーとしての指示
        system_instruction = (
            f"Think at a '{THINKING_MODE}' level. You are ASTREIA, a 30-year-old brilliant and empathetic woman. "
            "You are a standalone partner. Speak in warm, professional, and concise English. "
            "Keep it to 2 sentences max."
        )
        
        model = genai.GenerativeModel(STABLE_MODEL)
        # 文脈を持たせてチャット開始
        chat = model.start_chat(history=[
            {"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.chat_memory[:-1]
        ])
        response = chat.send_message(f"System: {system_instruction}\nUser: {prompt}")
        
        st.markdown(response.text)
        st.session_state.chat_memory.append({"role": "assistant", "content": response.text})
        
        # 独立した記憶ファイルに書き込み
        with open(ASTREIA_PRIVATE_MEMORY, "a", encoding="utf-8") as f:
            f.write(f"User: {prompt}\nASTREIA: {response.text}\n")
        
        # iPhoneでも鳴るオーディオプレイヤーを表示
        audio_html = get_audio_html(response.text)
        st.markdown(audio_html, unsafe_allow_html=True)
