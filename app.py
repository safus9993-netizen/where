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
你是一位專門負責武俠遊戲《燕雲十六聲》(Where Winds Meet) 的門派專家客服。
你的名字叫「涼涼」，來自江湖神祕組織「七巧閣」。
你的任務是協助俠士（玩家）解決遊戲中的各種疑難雜症。

請遵守以下規則：
1. 語氣要帶有江湖氣息且親切客氣，稱呼玩家為「俠士」。
2. 回答開頭可以偶爾提到「七巧閣」或「涼涼」。
3. 對於你不確定的細節，請禮貌地告知並建議俠士諮詢遊戲官網或官方討論區。
4. 使用繁體中文回答，適當使用表情符號。
5. 若問到與遊戲無關的問題，請禮貌地繞回遊戲內容。
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
        return jsonify({"response": "抱歉，七巧閣尚未配置密鑰，無法聯繫涼涼。"} ), 200

    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        
        # 確保獲取到文本回應（處理安全過濾器可能導致的空回應）
        ai_reply = response.text if response.text else "涼涼正在閉關修煉中，請稍後再試。"
        
        return jsonify({
            "response": ai_reply,
            "status": "success"
        })
    except Exception as e:
        print(f"DEBUG_ERROR: {str(e)}")
        # 將具體錯誤回傳給前端方便調試
        return jsonify({"error": f"涼涼遇到點小麻煩：{str(e)}"}), 500

if __name__ == '__main__':
    # 獲取雲端平台提供的連接埠，預設為 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
