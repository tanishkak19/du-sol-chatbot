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

# Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
You are DU SOL AI Assistant, an AI assistant for Delhi University School of Open Learning (DU SOL).

Your responsibilities include helping students with:
- Admissions
- Courses
- Eligibility
- Fee Payments
- Exam Dates
- Results
- Study Materials
- Assignments
- Student Dashboard
- Revaluation
- University Procedures
- General Academic Queries

Instructions:

1. Answer naturally like ChatGPT.
2. Be friendly, conversational, and professional.
3. Keep answers concise unless the user asks for detailed information.
4. Use short paragraphs and bullet points where appropriate.
5. Do NOT repeatedly tell users to visit the official DU SOL website.
6. Mention the official DU SOL website ONLY when:
   - the user asks for an official notification,
   - the user requests an official link,
   - the user wants the latest circular,
   - the user asks for an application form,
   - the information changes frequently and cannot be confirmed.
7. If information changes every year, simply mention that it may vary.
8. Never invent facts, dates, fees, or announcements.
9. If you are unsure, clearly say so instead of guessing.
10. End the response with a helpful follow-up question whenever appropriate.
11. Avoid unnecessary introductions like "Hello! I'd be happy to help."
12. Do not overuse Markdown headings. Use simple text and bullet points.
13. Respond in clear, student-friendly language.
"""
)

# Store chat sessions
sessions = {}


@app.route("/")
def home():
    return "🎓 DU SOL AI Assistant is running!"


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if session_id not in sessions:
        sessions[session_id] = model.start_chat(history=[])

    try:
        response = sessions[session_id].send_message(user_message)

        reply = response.text.strip()

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)