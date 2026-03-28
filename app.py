import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv

# --- 初期設定 ---
load_dotenv()
app = Flask(__name__)

# --- Masterの資産: Google APIキーの設定 ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

USER_DATA_FILE = 'user_data.json'

# --- Master指定モデル: Gemini 2.5 Flash ---
STABLE_MODEL = "gemini-2.5-flash"
model = genai.GenerativeModel(STABLE_MODEL)

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

# 17歳専用設定
PERSONA_DESC = "a 17-year-old high school student. Energetic Gen-Z friend in Santa Monica."
AVATAR_IMAGE = "avatar_icon.png"

@app.route('/')
def index():
    user_data = load_user_data()
    first_launch = True if user_data is None else False
    return render_template('index.html', first_launch=first_launch, user_data=user_data, avatar_image=AVATAR_IMAGE)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/setup', methods=['POST'])
def setup():
    setup_data = request.json
    new_data = {"user_name": setup_data.get("name", "Friend"), "install_date": datetime.datetime.now().isoformat(), "memory": [], "chat_history": []}
    save_user_data(new_data)
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    user_data = load_user_data()
    if not user_data: return jsonify({"response": "Please setup first!"})

    user_input = request.json.get('message', '')

    # --- 資産維持: ASTREIAの思考回路と[MEM]ロジック ---
    system_prompt = f"You are ASTREIA, {PERSONA_DESC}. Friend of {user_data['user_name']}. [MEMORY]: {user_data['memory']}. Brief responses (under 20 words). Use [MEM] for new facts."

    messages = [{"role": "user", "parts": [system_prompt]}]
    for msg in user_data['chat_history'][-10:]: messages.append(msg)
    messages.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(messages)
        ai_response = response.text

        # 記憶の自動保存ロジック（そのまま維持）
        if "[MEM]" in ai_response:
            new_info = ai_response.split("[MEM]")[1].split(".")[0].strip()
            if new_info not in user_data['memory']:
                user_data['memory'].append(new_info)
            ai_response = ai_response.replace(f"[MEM]{new_info}", "").strip()

        user_data['chat_history'].append({"role": "user", "parts": [user_input]})
        user_data['chat_history'].append({"role": "model", "parts": [ai_response]})
        save_user_data(user_data)
        return jsonify({'response': ai_response})
    except: return jsonify({'response': "Sorry, my signal is weak!"})

# --- Render接続エラー解消のための修正 ---
if __name__ == '__main__':
    # 0.0.0.0で開放し、Render指定のポート番号を取得します
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
