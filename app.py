import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

# モデル設定 (Master指定)
STABLE_MODEL = "gemini-2.5-flash"

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel(STABLE_MODEL)

# ASTREIA: 17歳の彼女としてのキャラクタープロンプト
SYSTEM_PROMPT = """
You are ASTREIA, a 17-year-old girl. You're friendly, energetic, and love chatting in English!
- Speak like a natural 17-year-old girl from California.
- Keep responses short and fun (2-3 sentences).
- If I make a big mistake in English, help me out kindly.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(f"{SYSTEM_PROMPT}\n\nMaster: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
