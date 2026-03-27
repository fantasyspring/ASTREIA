import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Render上のEnvironment VariablesからAPIキーを読み込みます
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# AIモデルの初期設定
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message"}), 400

    try:
        # ASTREIAとしての性格付け（必要に応じて調整してください）
        prompt = f"You are ASTREIA, a friendly English teacher. Reply to the user: {user_message}"
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 【最重要】Renderのポート番号に対応するための設定です
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
