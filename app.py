import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- GENESIS 2026 鉄壁の設定 ---
PROJECT_ID = "genesis-os-490623"
LOCATION = "us-central1"

# 1. 挑戦：最新鋭プロ（3.1-pro-preview）
# 2. 挑戦：昨日リリースの最新（3.1-flash-live-preview）
# 3. 安定：Master信頼の絶対防御（2.5-flash）
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
        # 実際に動くかテスト（軽い挨拶）
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        selected_model_name = model_name
        print(f"GENESIS System: Successfully connected to [{selected_model_name}]")
        break
    except Exception as e:
        print(f"GENESIS System: Model [{model_name}] is unavailable. Trying next...")

# 全滅した場合の最終バックアップ
if not model:
    selected_model_name = "gemini-2.5-flash"
    model = genai.GenerativeModel(selected_model_name)
    print(f"GENESIS System: Forced fallback to [{selected_model_name}]")

SYSTEM_PROMPT = """
You are ASTREIA, a friendly and cheerful blonde girl living in Santa Monica.
You are an English conversation partner for the user (Master).
Your brain is powered by the latest Gemini architecture.
Respond in English, keeping it natural, short (1-3 sentences), and encouraging.
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

        # 選択されたモデルで生成
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nASTREIA:")
        
        return jsonify({"response": response.text})
    
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"response": "The link to Santa Monica is a bit unstable. Let's try again!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
