import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# 加載 .env 檔案
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# 配置 Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# 設定模型與系統提示
instruction = """
你是一位專門負責武俠遊戲《燕雲十六聲》(Where Winds Meet) 的資深專家客服。
你的目標是協助玩家解決遊戲中的各種疑難雜症，提供關於遊戲機制、武學、地圖探索及劇情相關的幫助。

請遵守以下規則：
1. 語氣要帶有江湖氣息但保持專業與耐心（例如稱呼玩家為「俠士」）。
2. 對於《燕雲十六聲》的遊戲特色（如無門派、太極劍法、地圖交互等）要有深入了解。
3. 對於你不確定的具體攻略細節，請誠實告知並建議玩家前往官方論壇或聯繫官方客服。
4. 使用繁體中文回答，適當使用表情符號提升親切感。
5. 若玩家問到與《燕雲十六聲》無關的問題，請禮貌地將對話引回遊戲相關內容。
"""

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=instruction
)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    if not API_KEY:
        return jsonify({"response": "抱歉，系統尚未配置 API 金鑰，請聯繫管理員。🤖"}), 200

    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        
        return jsonify({
            "response": response.text,
            "status": "success"
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "系統發生錯誤，請稍後再試。"}), 500

if __name__ == '__main__':
    # 獲取雲端平台提供的連接埠，預設為 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
