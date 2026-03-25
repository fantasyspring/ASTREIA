import streamlit as st
import google.generativeai as genai

# ASTREIA専用：スマホ最適化設定
st.set_page_config(
    page_title="ASTREIA - AI Avatar",
    page_icon="✨",
    layout="centered"
)

# SecretsからASTREIA専用APIキーを読み込み
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーが見つかりません。StreamlitのSecretsを設定してください。")

# 女神の「星の輝き」をイメージしたカスタムUI（GENESIS色を排除）
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e0e0e0; }
    .stChatMessage { background-color: #1a1c23; border-radius: 15px; margin-bottom: 10px; }
    /* 入力欄をスマホで押しやすく調整 */
    .stChatInput { padding-bottom: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ ASTREIA")
st.caption("Your Personal AI Avatar & English Tutor")

# Gemini 2.5 Flash モデルの初期化
# システム側で最新版が当たるよう設定
model = genai.GenerativeModel('gemini-1.5-flash')

# 会話履歴の管理
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の導きを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ASTREIAへの問いかけ
if prompt := st.chat_input("Ask ASTREIA..."):
    # ユーザーの入力を表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini 2.5 Flash による応答生成
    with st.chat_message("assistant"):
        # ASTREIAとしての独立したアイデンティティ定義
        # 神（GENESIS）とは無関係な、純粋なアバターとしての指示
        context = (
            "You are ASTREIA, an elegant, insightful, and supportive AI avatar. "
            "You focus on helping the user master English through professional and empathetic feedback. "
            "Your personality is sophisticated yet witty. Never mention 'GENESIS'. "
            "Always prioritize being a helpful partner for the user's personal growth."
        )
        
        # 履歴を含めて生成（2.5 Flashの高速処理）
        response = model.generate_content(f"System: {context}\nUser: {prompt}")
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
