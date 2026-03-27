import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- GENESIS 2026 鉄壁の設定 ---
PROJECT_ID = "genesis-os-490623"
LOCATION = "us-central1"

# モデルの優先順位
MODELS_TO_TRY = [
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-live-preview",
    "gemini-2.5-flash"
]

# APIキー設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 最適なモデルの自動接続
model = None
selected_model_name = ""

for model_name in MODELS_TO_TRY:
    try:
        test_model = genai.GenerativeModel(model_name)
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        selected_model_name = model_name
        print(f"GENESIS System: Connected to [{selected_model_name}]")
        break
    except Exception:
        print(f"GENESIS System: [{model_name}] unavailable. Trying next...")

if not model:
    selected_model_name = "gemini-2.5-flash"
    model = genai.GenerativeModel(selected_model_name)
    print(f"GENESIS System: Fallback to [{selected_model_name}]")

# ==========================================
# --- ASTREIA AGING & IMAGE SETTINGS ---
# 現在は "17" で完成させます。将来ここを "30" や "50" に変えるだけで
# プロンプトと画像パスが連動します。
# ==========================================
USER_SET_AGE = "17" 

PERSONA_CATALOG = {
    "17": {
        "image": "avatar.png", # 17歳メイン画像
        "role_desc": "a 17-year-old high school student and the user's close friend.",
        "tone": "Energetic, casual, and supportive. Use Gen-Z slang like 'totally' or 'super.'",
        "topics": "school, SNS, hobbies, and dreams."
    },
    "30": {
        "image": "avatar_30.png",
        "role_desc": "a 30-year-old professional and sophisticated friend.",
        "tone": "Natural, empathetic, and professional yet friendly.",
        "topics": "career, travel, and lifestyle."
    },
    "50": {
        "image": "avatar_50.png",
        "role_desc": "a 50-year-old wise mentor and warm friend.",
        "tone": "Calm, thoughtful, and encouraging with a rich vocabulary.",
        "topics": "life philosophy, health, and goals."
    }
}

selected = PERSONA_CATALOG.get(USER_SET_AGE, PERSONA_CATALOG["17"])

# システムプロンプトの構築
SYSTEM_PROMPT = f"""
Role: You are ASTREIA, {selected['role_desc']} living in Santa Monica.
Tone/Personality: {selected['tone']}
Key Topics: {selected['topics']}

Instructions:
1. ALWAYS respond in English. 
2. Be a 'friend', not a 'teacher'.
3. Keep responses brief (1-2 sentences) and engaging.
4. If the user makes a clear mistake, add a natural suggestion at the very end.
5. Ask a question to keep the friendship growing!
"""
# ==========================================

@app.route('/')
def index():
    # 選択された年齢に応じた画像パスをテンプレートに渡す準備
    return render_template('index.html', avatar_image=selected['image'])

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"response": "I'm listening! What's on your mind?"})

        generation_config = {
            "max_output_tokens": 120,
            "temperature": 0.8,
        }

        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nASTREIA:",
            generation_config=generation_config
        )
        
        if response.text:
            return jsonify({"response": response.text})
        else:
            raise Exception("No text in response")
    
    except Exception as e:
        print(f"GENESIS Chat Error: {e}")
        return jsonify({"response": "Signal is weak! Let's try again, my friend!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
