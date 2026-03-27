import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# --- 初期設定 ---
load_dotenv()
app = Flask(__name__)

# --- GENESIS 2026 鉄壁の設定 ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Render等の環境では書き込み可能な /tmp を使うか、エラーを無視する設計にする
USER_DATA_FILE = 'user_data.json'

# モデル選択の砦
MODELS_TO_TRY = ["gemini-3.1-pro-preview", "gemini-3.1-flash-live-preview", "gemini-2.5-flash"]
model = None

for m_name in MODELS_TO_TRY:
    try:
        test_model = genai.GenerativeModel(m_name)
        # 起動テスト
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        print(f"GENESIS: Connected to [{m_name}]")
        break
    except:
        continue

if not model:
    model = genai.GenerativeModel("gemini-2.5-flash")
    print("GENESIS: Forced fallback to [gemini-2.5-flash]")

# --- ユーザーデータ管理（堅牢版） ---
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Read Error: {e}")
    return None

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Write Error: {e}")

# --- ペルソナ設定 ---
PERSONA_CATALOG = {
    "17": {"image": "avatar.png", "desc": "a 17-year-old high school student. Energetic Gen-Z friend."},
    "30": {"image": "avatar_30.png", "desc": "a 30-year-old professional. Sophisticated peer."},
    "50": {"image": "avatar_50.png", "desc": "a 50-year-old wise mentor. Warm and experienced friend."}
}

@app.route('/')
def index():
    user_data = load_user_data()
    first_launch = user_data is None
    
    can_change = True
    avatar_img = "avatar.png"
    
    if user_data:
        # インストールから10日経過チェック
        try:
            install_date = datetime.datetime.fromisoformat(user_data.get('install_date'))
            days_passed = (datetime.datetime.now() - install_date).days
            if days_passed > 10:
                can_change = False
        except:
            pass
            
        age = user_data.get('selected_age', '17')
        avatar_img = PERSONA_CATALOG.get(age, PERSONA_CATALOG["17"])["image"]
            
    return render_template('index.html', 
                           first_launch=first_launch, 
                           user_data=user_data,
                           can_change=can_change,
                           avatar_image=avatar_img)

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
    save_user_data(new_data)
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    user_data = load_user_data()
    if not user_data:
        return jsonify({"response": "Please complete the setup first!"})

    user_input = request.json.get('message', '')
    age = user_data.get('selected_age', '17')
    persona = PERSONA_CATALOG.get(age, PERSONA_CATALOG["17"])

    # システムプロンプトの構築
    system_prompt = f"""You are ASTREIA, {persona['desc']} in Santa Monica.
You are the best friend of {user_data['user_name']}.
Your memory of this friend: {user_data['memory']}

Rules:
- Respond briefly (under 20 words).
- If the user asks for natural English, say "Sure! You can say it like this:".
- If you learn something new about the user, start with [MEM]."""

    # 履歴をGeminiの形式に整形
    history = []
    for msg in user_data.get('chat_history', [])[-10:]:
        history.append({"role": msg["role"], "parts": [msg["parts"][0]]})

    try:
        # ChatSession を使用して文脈を維持
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(f"{system_prompt}\n\nUser: {user_input}")
        ai_response = response.text

        # 記憶[MEM]の処理
        if "[MEM]" in ai_response:
            parts = ai_response.split("[MEM]")
            new_info = parts[1].split(".")[0].strip()
            if new_info and new_info not in user_data['memory']:
                user_data['memory'].append(new_info)
            ai_response = ai_response.replace(f"[MEM]{new_info}", "").strip()

        # 履歴更新
        user_data['chat_history'].append({"role": "user", "parts": [user_input]})
        user_data['chat_history'].append({"role": "model", "parts": [ai_response]})
        
        # 履歴制限 (20件)
        if len(user_data['chat_history']) > 20:
            user_data['chat_history'] = user_data['chat_history'][-20:]
            
        save_user_data(user_data)
        return jsonify({'response': ai_response})

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'response': "Sorry, my signal is weak! Let's try again!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
