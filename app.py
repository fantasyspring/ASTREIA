import streamlit as st
import random

# --- ASTREIAの基本設定 ---
st.set_page_config(page_title="ASTREIA Buddy", page_icon="🎙️")

def main():
    st.title("🎙️ ASTREIA - Your English Buddy")
    
    # サイドバー：Mousegirl専用の「バディ・メモリー」
    with st.sidebar:
        st.header("👤 Buddy Memory")
        st.info("User: Mousegirl\nStatus: Learning English\nGoal: Global Friendship")
        # 将来的にSQLiteから読み込むデータをここに表示
        st.write("---")
        st.image("https://via.placeholder.com/150", caption="ASTREIA (Placeholder)")

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello Mousegirl! I'm ASTREIA. Ready to practice? What are you wearing today?"}
        ]

    # 履歴の表示
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 入力フォーム
    if prompt := st.chat_input("Say something to ASTREIA..."):
        # ユーザーの入力を表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- ここが将来のAI（Gemini）接続ポイント ---
        # 現時点では簡易レスポンス
        response = f"I hear you! You said: '{prompt}'. (Connecting Gemini API in Phase 2...)"
        
        # ASTREIAの返答を表示
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
