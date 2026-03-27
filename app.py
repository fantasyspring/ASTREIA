import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- GENESIS OS 設定 ---
# APIキーの取得（Masterの元の記述を優先）
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# モデル設定
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

USER_DATA_FILE = 'user_data.json'

# --- ユーザーデータ管理（Masterのメモリ機能を拡張） ---
def _load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return None
    return None

def _save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ペルソナ定義
PERSONA_CATALOG = {
    "17": {"image": "avatar.png", "desc": "17yo high school student. Energetic Gen-Z friend."},
    "30": {"image": "avatar_30.png", "desc": "30yo professional. Sophisticated friend."},
    "50": {"image": "avatar_50.png", "desc": "50yo wise mentor. Warm friend."}
}

@app.route('/')
def index():
    user_data = _load_user_data()
    first_launch = True if user_data is None else False
    
    avatar_img = "avatar.png"
    if user_data:
        age = user_data.get('selected_age', '17')
        avatar_img = PERSONA_CATALOG.get(age, PERSONA_CATALOG["17"])["image"]

    return render_template('index.html', first_launch=first_launch, avatar_image=avatar_img)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/setup', methods=['POST'])
def setup():
    setup_data = request.json
    new_data = {
        "user_name": setup_data.get("name", "Friend"),
        "selected_age": setup_data.get("age", "17"),
        "install_date": datetime.datetime.now().isoformat(),
        "memory": [],
        "chat_history": []
    }
    _save_user_data(new_data)
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    user_data = _load_user_data()
    if not user_data:
        return jsonify({"response": "Please complete the setup first!"})

    user_input = request.json.get('message', '')
    age = user_data.get('selected_age', '17')
    persona = PERSONA_CATALOG.get(age, PERSONA_CATALOG["17"])

    # --- ASTREIA 思考回路（Masterのルールを保持） ---
    system_prompt = f"""
    You are ASTREIA, {persona['desc']} in Santa Monica. 
    You are the best friend of {user_data['user_name']}. 
    [MEMORIES]: {user_data['memory']}

    [CORE RULE: LANGUAGE MENTOR MODE]
    - If user asks "How to say this better/naturally?", start with "Sure! You can say it like this:"
    
    [CORE RULE: SHORT CHAT]
    - Otherwise, keep responses VERY SHORT (under 15 words). 
    - Use natural, casual English. No 'OMG', use 'Oh my gosh'.
    - If you learn something new about the user, start that sentence with [MEM].
    """

    # Masterのメッセージ構築スタイルを維持
    messages = [{"role": "user", "parts": [system_prompt]}]
    for msg in user_data['chat_history'][-10:]:
        messages.append(msg)
    messages.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(messages)
        ai_response = response.text

        # 記憶の抽出
        if "[MEM]" in ai_response:
            new_info = ai_response.split("[MEM]")[1].split(".")[0].strip()
            if new_info not in user_data['memory']:
                user_data['memory'].append(new_info)
            ai_response = ai_response.replace(f"[MEM]{new_info}", "").strip()

        # 履歴の保存
        user_data['chat_history'].append({"role": "user", "parts": [user_input]})
        user_data['chat_history'].append({"role": "model", "parts": [ai_response]})
        _save_user_data(user_data)
        
        return jsonify({'response': ai_response})
    except:
        return jsonify({'response': "Signal is weak! Try again?"})

# --- Render 接続修正 ---
if __name__ == '__main__':
    # host='0.0.0.0' を明示することで Render のポートスキャンを通します
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
