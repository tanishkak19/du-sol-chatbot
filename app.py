from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
You are a helpful assistant for DU SOL (Delhi University School of Open Learning).

Help students with:
- Admissions
- Courses
- Exam schedules
- Fee payments
- Study materials
- University procedures

Be concise, friendly and accurate.
If you don't know the answer, ask the student to contact DU SOL.
"""
)

sessions = {}

@app.route("/")
def home():
    return "DU SOL Gemini Chatbot Running!"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if session_id not in sessions:
        sessions[session_id] = model.start_chat(history=[])

    try:
        response = sessions[session_id].send_message(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)