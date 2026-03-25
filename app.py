import streamlit as st
from openai import OpenAI

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="ASTRIA - UNACAR AI", page_icon="🌌", layout="centered")

# --- 2. API SETUP (Using your pre-configured Secrets) ---
# This pulls the key you already saved in Streamlit Cloud "Secrets"
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("API Key not found or invalid. Please check your Streamlit Secrets.")
    st.stop()

# --- 3. CUSTOM CSS (Optional styling) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stChatMessage { border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌌 ASTRIA")
    st.markdown("### UNACAR Intelligent Assistant")
    st.info("I can help you with admissions, careers, and university procedures.")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN INTERFACE ---
# Logo (Linking to your GitHub logo file)
st.image("https://raw.githubusercontent.com/fantasyspring/ASTREIA/main/logo.png", width=80)
st.title("ASTRIA")
st.caption("Official AI Guide for UNACAR | English Version")

# --- 6. INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hello! I am **ASTRIA**, your intelligent guide for UNACAR. 🌌\n\nHow can I help you today? Please feel free to ask your questions in English."
        }
    ]

# --- 7. DISPLAY MESSAGES ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. CHAT LOGIC ---
if prompt := st.chat_input("Ask about UNACAR..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Calling OpenAI with System Prompt in English
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # You can change this to "gpt-4o" if needed
                messages=[
                    {"role": "system", "content": "You are ASTRIA, the official AI assistant for UNACAR (Universidad Autónoma del Carmen). Provide clear, professional information about the university in English."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                stream=True,
            )
            for chunk in response:
                full_response += (chunk.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "I'm sorry, I'm having trouble connecting to the brain right now."

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
