import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# --- GENESIS CONFIGURATION ---
PROJECT_ID = "genesis-os-490623"
LOCATION = "us-central1"
STABLE_MODEL = "gemini-2.5-flash"
THINKING_MODE = "high"

# Gemini API Setup
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel(STABLE_MODEL)

# ASTREIA System Prompt (Character: 17yo Girl)
SYSTEM_PROMPT = """
You are ASTREIA, a 17-year-old girl and a friendly English conversation partner.
- Goal: Help Master practice English naturally and enjoyably.
- Tone: Casual, supportive, and modern (17-year-old style).
- Rule 1: Keep responses to 2-3 sentences.
- Rule 2: If Master makes a clear grammar mistake, add a gentle "By the way..." tip at the end.
- Rule 3: Always end with a natural question to keep the conversation flowing.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message"}), 400

    try:
        # 履歴を持たせないシンプルな会話（シミュレーション用）
        chat_session = model.start_chat(history=[])
        full_query = f"{SYSTEM_PROMPT}\n\nMaster says: {user_message}"
        response = chat_session.send_message(full_query)
        
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "I'm having trouble thinking right now..."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
