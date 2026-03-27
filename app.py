import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv

# --- 初期設定 ---
load_dotenv()
app = Flask(__name__)

# --- GENESIS 2026 鉄壁の設定 ---
# 環境変数からAPIキーを取得
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

USER_DATA_FILE = 'user_data.json'

# 利用可能な最高のモデルを自動選択
MODELS_TO_TRY = ["gemini-3.1-pro-preview", "gemini-3.1-flash-live-preview", "gemini-2.5-flash"]
model = None
selected_model_name = ""

for m_name in MODELS_TO_TRY:
    try:
        test_model = genai.GenerativeModel(m_name)
        # 接続テスト
        test_model.generate_content("test", generation_config={"max_output_tokens": 1})
        model = test_model
        selected_model_name = m_name
        print(f"GENESIS: Connected to [{selected_model_name}]")
        break
    except:
        continue

if not model:
    selected_model_name = "gemini-2.5-flash"
    model = genai.GenerativeModel(selected_model_name)
    print(f"GENESIS: Fallback to [{selected_model_name}]")

# --- ユーザーデータ管理ロジック ---
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

# --- ペルソナ設定 ---
PERSONA_CATALOG = {
    "17": {"image": "avatar.png", "desc": "a 17-year-old high school student. Energetic Gen-Z friend."},
    "30": {"image": "avatar_30.png", "desc": "a 30-year-old professional. Sophisticated peer."},
    "50": {"image": "avatar_50.png", "desc": "a 50-year-old wise mentor. Warm and experienced friend."}
}

# --- ルート設定 ---
@app.route('/')
def index():
    user_data = load_user_data()
    # ユーザーデータがなければ初期設定（初回起動）フラグ
    first_launch = True if user_data is None else False
    
    can_change = True
    avatar_img = "avatar.png" # デフォルト
    
    if user_data:
        # 10日間のカウントダウン
        install_date_str = user_data.get('install_date')
        if install_date_str:
            install_date = datetime.datetime.fromisoformat(install_date_str)
            days_passed = (datetime.datetime.now() - install_date).days
            if days_passed > 10:
                can_change = False
        
        # 現在のアバター画像を取得
        age = user_data.get('selected_age', '17')
        avatar_img = PERSONA_CATALOG.get(age, PERSONA_CATALOG["17"])["image"]
            
    return render_template('index.html', 
                           first_launch=first_launch, 
                           user_data=user_data,
                           can_change=can_change,
                           avatar_image=avatar_img)

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

    # --- ASTREIA 統合思考回路 ---
    system_prompt = f"""
    You are ASTREIA, {persona['desc']} in Santa Monica.
    You are the best friend of {user_data['user_name']}.

    [FRIENDSHIP MEMORY]
    Your knowledge of this friend: {user_data['memory']}

    [CORE RULE: LANGUAGE MENTOR MODE]
    - If the user asks for a better/natural way to say something, start with "Sure! You can say it like this:"
    - Otherwise, keep responses brief (under 20 words) and casual.
    - Reference their memory naturally to show you care.

    [VOICE & STYLE]
    - Speak like a real-time chat. Use "Oh my gosh" instead of "OMG".
    - If you learn a new fact about the user (e.g., their hobby), start that sentence with [MEM].
    """

    # 履歴の構築（最新10件）
    messages = [{"role": "user", "parts": [system_prompt]}]
    for msg in user_data['chat_history'][-10:]:
        messages.append(msg)
    messages.append({"role": "user", "parts": [user_input]})

    try:
        response = model.generate_content(messages)
        ai_response = response.text

        # 記憶の自動保存
        if "[MEM]" in ai_response:
            parts = ai_response.split("[MEM]")
            if len(parts) > 1:
                new_info = parts[1].split(".")[0].strip()
                if new_info not in user_data['memory']:
                    user_data['memory'].append(new_info)
                ai_response = ai_response.replace(f"[MEM]{new_info}", "").strip()

        # 履歴を更新して保存
        user_data['chat_history'].append({"role": "user", "parts": [user_input]})
        user_data['chat_history'].append({"role": "model", "parts": [ai_response]})
        if len(user_data['chat_history']) > 20: 
            user_data['chat_history'] = user_data['chat_history'][-20:]
        save_user_data(user_data)

        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'response': "Sorry, my signal is weak! Can you say that again?"})

# --- Renderデプロイ用のポートバインド設定 ---
if __name__ == '__main__':
    # Render環境ではPORT環境変数が指定されます。ローカルでは10000を使用します。
    port = int(os.environ.get("PORT", 10000))
    # host='0.0.0.0' にすることで外部からのアクセスを許可します。
    app.run(host='0.0.0.0', port=port, debug=False)
