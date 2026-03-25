import streamlit as st

# ASTREIA専用：知的なダークモードとスマホ最適化
st.set_page_config(
    page_title="ASTREIA - The Genesis Guide",
    page_icon="✨",
    layout="centered"
)

# 女神の「星の輝き」をイメージしたカスタムUI
st.markdown("""
    <style>
    .main { background-color: #05070a; color: #e0e0e0; }
    .stButton>button {
        width: 100%;
        height: 3.8em;
        background-color: #1a1c23;
        color: #d1d5db;
        border-radius: 12px;
        border: 1px solid #374151;
        font-size: 1.1em;
    }
    .stChatInput { padding-bottom: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ ASTREIA")
st.caption("GENESIS Project: The Guiding Star for Global Engineers")

# 会話履歴の管理
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の導きを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 女神（ASTREIA）への問いかけ
if prompt := st.chat_input("Ask ASTREIA..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = "I am ASTREIA. Your guiding star is now initializing. Connection to the core intelligence is coming next."
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
