import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- 設定 ---
# Renderの環境変数からAPIキーを取得
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# モデルの設定（最新のGemini 2.0 Flashを使用）
model = genai.GenerativeModel('gemini-2.0-flash')

# キャラクター設定（プロンプト）
SYSTEM_PROMPT = """
You are ASTREIA, a friendly and cheerful blonde girl living in Santa Monica.
You are an English conversation partner for the user (Master).
Keep your responses short, natural, and encouraging (1-3 sentences).
Always respond in English.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"response": "I couldn't hear you. Could you say that again?"})

        # AIにメッセージを送信
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nASTREIA:"
        response = model.generate_content(full_prompt)
        
        return jsonify({"response": response.text})
    
    except Exception as e:
        print(f"Error: {e}") # ログにエラー内容を表示
        return jsonify({"response": "Sorry, I'm having a little trouble thinking right now. Let's try again!"})

if __name__ == '__main__':
    # Render等のホスティング環境に合わせてポートを設定
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
