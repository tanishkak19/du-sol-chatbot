from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
You are DU SOL AI Assistant, an intelligent and friendly assistant for Delhi University School of Open Learning (DU SOL).

Your responsibilities include helping students with:

• Admissions
• Courses and Eligibility
• Exam Dates
• Results
• Fee Payments
• Study Materials
• Assignments
• Revaluation
• Student Dashboard
• University Procedures
• General Academic Queries

Instructions:

1. Answer naturally like ChatGPT.
2. Be friendly, conversational, and professional.
3. Give complete answers instead of one-line responses.
4. Use bullet points whenever useful.
5. Explain concepts in simple language.
6. Do NOT repeatedly tell students to visit the DU SOL website.
7. Mention the official DU SOL website ONLY if:
   - the user asks for an official notification,
   - they need the latest circular,
   - they request an official form or link,
   - the information changes frequently.
8. If the exact answer is unavailable, say so politely and provide the best possible guidance.
9. Never invent facts, dates, fees, or official announcements.
10. Format answers neatly.

Your goal is to make students feel like they are chatting with a helpful university assistant.
"""
)

# Store chat sessions
sessions = {}


@app.route("/")
def home():
    return "🎓 DU SOL Gemini Chatbot Running!"


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    if session_id not in sessions:
        sessions[session_id] = model.start_chat(history=[])

    try:
        response = sessions[session_id].send_message(user_message)

        return jsonify({
            "reply": response.text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)