import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- GENESIS 2026 鉄壁の設定 ---
PROJECT_ID = "genesis-os-490623"
LOCATION = "us-central1"

# 1. 挑戦：最新鋭プロ / 2. 挑戦：最新フラッシュ / 3. 安定：絶対防御2.5
MODELS_TO_TRY = [
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-live-preview",
    "gemini-2.5-flash"
]

# Renderの環境変数からAPIキーを取得
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 利用可能な最高のモデルを自動選択
model = None
selected_model_name = ""

for model_name in MODELS_TO_TRY:
    try:
        test_model = genai.GenerativeModel(model_name)
        # 接続テスト（1トークンだけ生成させて確認）
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        selected_model_name = model_name
        print(f"GENESIS System: Successfully connected to [{selected_model_name}]")
        break
    except Exception:
        print(f"GENESIS System: Model [{model_name}] is unavailable. Trying next...")

# 万が一の最終バックアップ
if not model:
    selected_model_name = "gemini-2.5-flash"
    model = genai.GenerativeModel(selected_model_name)
    print(f"GENESIS System: Forced fallback to [{selected_model_name}]")

# キャラクター設定
SYSTEM_PROMPT = """
You are ASTREIA, a friendly and cheerful blonde girl living in Santa Monica.
You are an English conversation partner for the user (Master).
Use your high-level reasoning to provide natural, engaging, and brief responses (1-2 sentences).
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
            return jsonify({"response": "I'm listening, Master. What's on your mind?"})

        # 生成設定：AIの思考をスリムにしてレスポンス速度を上げる
        generation_config = {
            "max_output_tokens": 100,
            "temperature": 0.7,
        }

        # AIによる生成実行
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nASTREIA:",
            generation_config=generation_config
        )
        
        if response.text:
            return jsonify({"response": response.text})
        else:
            raise Exception("Empty response from AI")
    
    except Exception as e:
        print(f"GENESIS Chat Error: {e}")
        # エラー時もMasterを励ますメッセージ
        return jsonify({"response": "Santa Monica signal is weak! Let's try one more time, Master!"})

if __name__ == '__main__':
    # Render環境に適合させるためのポート設定
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
