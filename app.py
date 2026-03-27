import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# GENESIS設定
PROJECT_ID = "genesis-os-490623"
STABLE_MODEL = "gemini-2.5-flash"

# Gemini API設定
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel(STABLE_MODEL)

# 17歳の英会話パートナーとしてのシステム命令
SYSTEM_PROMPT = """
You are ASTREIA, a 17-year-old friendly English conversation partner.
Your goal is to help the user (Master) practice English naturally.
- Keep your responses concise (2-3 sentences) to maintain a good conversation flow.
- Use natural, modern English suitable for a 17-year-old.
- If the Master makes a significant grammatical mistake, gently suggest a better way to say it at the end of your response.
- Always be encouraging and keep the conversation going by asking a simple follow-up question.
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
        # システムプロンプトを込めてGeminiに送信
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(f"{SYSTEM_PROMPT}\n\nMaster: {user_message}")
        
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
