import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import base64
import os

# --- 1. ASTREIA の性格・スタイル設定 ---
STABLE_MODEL = "gemini-1.5-flash" # 2026年現在の安定版
USER_PROFILE = {
    "name": "David",
    "style": "Professional, logical, conclusion-first",
    "interests": "Science, Technology, Education",
}

st.set_page_config(page_title="ASTREIA Hybrid", page_icon="🎙️")

# API設定
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please set GEMINI_API_KEY in secrets.")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 音声再生用関数（自動再生タグ付き）
def play_audio(text):
    tts = gTTS(text=text, lang='en', tld='com')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# --- UI構築 ---
st.title("✨ ASTREIA: Hybrid English Partner")
st.write(f"Logged in as: **{USER_PROFILE['name']}** (Style: {USER_PROFILE['style']})")

# 会話履歴の表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 入力セクション（ここが重要） ---
st.divider()
cols = st.columns([0.8, 0.2])

with cols[0]:
    # テキスト入力（電車・バス用）
    text_input = st.chat_input("Type or Speak...")

with cols[1]:
    # 音声入力（歩行・自宅用）
    audio_input = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key='recorder')

# ロジック処理
user_content = None
if text_input:
    user_content = text_input
elif audio_input:
    # 音声データをテキストに変換（Geminiのマルチモーダル機能を利用）
    st.info("Analyzing your voice...")
    model = genai.GenerativeModel(STABLE_MODEL)
    audio_data = {'mime_type': 'audio/wav', 'data': audio_input['bytes']}
    response = model.generate_content([
        "Please transcribe this English audio into text accurately.",
        audio_data
    ])
    user_content = response.text

if user_content:
    # 1. ユーザー発言を表示
    st.session_state.messages.append({"role": "user", "content": user_content})
    with st.chat_message("user"):
        st.markdown(user_content)

    # 2. ASTREIA の回答生成
    with st.chat_message("assistant"):
        system_prompt = (
            f"You are ASTREIA, a 30yo brilliant woman and English partner. "
            f"Your partner is {USER_PROFILE['name']}. Always match his style: {USER_PROFILE['style']}. "
            "Reply in 2-3 natural sentences. Provide a brief correction in () if needed."
        )
        
        model = genai.GenerativeModel(STABLE_MODEL)
        # 履歴を反映させて会話
        history = [{"role": "user" if m["role"]=="user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
        chat = model.start_chat(history=history)
        ai_response = chat.send_message(f"{system_prompt}\n\nUser says: {user_content}")
        
        full_text = ai_response.text
        st.markdown(full_text)
        st.session_state.messages.append({"role": "assistant", "content": full_text})
        
        # 3. 音声で返答（イヤホン推奨）
        play_audio(full_text)
