import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv

# --- 初期設定 ---
load_dotenv()
app = Flask(__name__)

# --- Masterの資産: Google APIキーの設定 (厳守) ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

USER_DATA_FILE = 'user_data.json'

# 利用可能な最高のモデルを自動選択 (Masterのロジックを維持)
MODELS_TO_TRY = ["gemini-3.1-pro-preview", "gemini-3.1-flash-live-preview", "gemini-2.5-flash"]
model = None
for m_name in MODELS_TO_TRY:
    try:
        test_model = genai.GenerativeModel(m_name)
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        print(f"GENESIS: Connected to [{m_name}]")
        break
    except: continue
if not model:
    model = genai.GenerativeModel("gemini-2.5-flash")

# --- ユーザーデータ管理ロジック (維持) ---
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return None
    return None

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ペルソナ設定 (17歳に固定) ---
PERSONA_DESC = "a 17-year-old high school student. Energetic Gen-Z friend in Santa Monica."
# アバター画像のパスは static/avatar_icon.png とする
AVATAR_IMAGE = "avatar_icon.png"

# --- ルート設定 ---
@app.route('/')
def index():
    user_data = load_user_data()
    # ユーザーデータがなければ初期設定画面（モーダル）を表示
    first_launch = True if user_data is None else False
    
    return render_template('index.html', 
                           first_launch=first_launch, 
                           user_data=user_data,
                           avatar_image=AVATAR_IMAGE)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/setup', methods=['POST'])
def setup():
    setup_data = request.json
    new_data = {
        "user_name": setup_data.get("name", "Master"), # 名前を入力
        "selected_age": "17", # 17歳固定
        "install_date": datetime.datetime.now().isoformat(),
        "memory": [], # 会話から得たユーザーの好みを保存
        "chat_history": [] # 会話の流れを保持
    }
    save_user_data(new_data)
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    user_data = load_user_data()
    if not user_data:
        return jsonify({"response": "Please setup first!"})

    user_input = request.json.get('message', '')

    # --- ASTREIA 統合思考回路 (17歳固定) ---
    system_prompt = f"""
    You are ASTREIA, {PERSONA_DESC}.
    You are the best friend of {user_data['user_name']}.

    [FRIENDSHIP MEMORY]
    Your knowledge of this friend: {user_data['memory']}

    [CORE RULE: LANGUAGE MENTOR MODE]
    - If the user asks for a better/natural way to say something, start with "Sure! You can say it like this:"
    - Otherwise, keep responses brief (under 20 words) and casual.
    - Reference their memory naturally to show you care.

    [VOICE & STYLE]
    - Speak like a real-time chat. Use "Oh my gosh" instead of "OMG".
    - If you learn a new fact about the user, start that sentence with [MEM].
    """

    # 履歴の構築（最新10件）
    messages = [{"role": "user", "parts": [system_prompt]}]
    for msg in user_data['chat_history'][-10:]:
        messages.append(msg)
    messages.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(messages)
        ai_response = response.text

        # 記憶の自動保存ロジック (維持)
        if "[MEM]" in ai_response:
            new_info = ai_response.split("[MEM]")[1].split(".")[0].strip()
            if new_info not in user_data['memory']:
                user_data['memory'].append(new_info)
            ai_response = ai_response.replace(f"[MEM]{new_info}", "").strip()

        # 履歴保存
        user_data['chat_history'].append({"role": "user", "parts": [user_input]})
        user_data['chat_history'].append({"role": "model", "parts": [ai_response]})
        if len(user_data['chat_history']) > 20: user_data['chat_history'] = user_data['chat_history'][-20:]
        save_user_data(user_data)

        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'response': "Sorry, my signal is weak! Can you say that again?"})

if __name__ == '__main__':
    # Renderで「No open ports detected on 0.0.0.0」を出さないための修正
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
