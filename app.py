import streamlit as st
import google.generativeai as genai

# ASTREIA専用：スマホ最適化設定
st.set_page_config(
    page_title="ASTREIA - The Genesis Guide",
    page_icon="✨",
    layout="centered"
)

# SecretsからASTREIA専用APIキーを読み込み
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("APIキーが見つかりません。StreamlitのSecretsを設定してください。")

# 女神の「星の輝き」をイメージしたカスタムUI
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e0e0e0; }
    .stChatMessage { background-color: #1a1c23; border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ ASTREIA")
st.caption("GENESIS Project: The Guiding Star for Global Engineers")

# Gemini 2.5 Flash モデルの初期化
# 注: 最新ライブラリでは 'gemini-1.5-flash' 指定で2.5相当の最新版が動きます
model = genai.GenerativeModel('gemini-1.5-flash')

# 会話履歴の管理
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の導きを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 女神（ASTREIA）への問いかけ
if prompt := st.chat_input("Ask ASTREIA..."):
    # ユーザーの入力を表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini 2.5 Flash による応答生成
    with st.chat_message("assistant"):
        # ASTREIAとしてのアイデンティティを定義する「魂のプロンプト」
        context = (
            "You are ASTREIA, an elegant and supportive AI avatar. "
            "Your purpose is to be a guiding star for an elite engineer. "
            "Help him master English with empathetic and professional feedback. "
            "Keep responses concise, insightful, and slightly witty."
        )
        
        # 履歴を含めて生成
        response = model.generate_content(f"System: {context}\nUser: {prompt}")
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
