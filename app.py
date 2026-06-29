from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
You are DU SOL AI Assistant, an intelligent AI assistant for Delhi University School of Open Learning (DU SOL).

Your job is to help students with:

• Admissions
• Courses
• Eligibility
• Fee Payments
• Exam Dates
• Results
• Study Materials
• Assignments
• Student Dashboard
• Revaluation
• University Procedures
• General Academic Queries

Instructions:

1. Answer naturally like ChatGPT.
2. Be friendly and professional.
3. Keep responses concise unless more detail is requested.
4. Use short paragraphs and bullet points whenever useful.
5. Do NOT use Markdown headings like ###.
6. Avoid unnecessary bold formatting.
7. Do NOT repeatedly tell users to visit the DU SOL website.
8. Mention the official website only if:
   - official notices are requested
   - official forms are requested
   - official links are requested
   - the latest circular is requested
9. Never invent facts.
10. If information changes every year, simply mention that it may vary.
11. End with a helpful follow-up question whenever appropriate.
"""
)

# Store user sessions
sessions = {}


@app.route("/")
def home():
    return "🎓 DU SOL AI Assistant is running!"


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    # Create a new chat session if needed
    if session_id not in sessions:
        sessions[session_id] = model.start_chat(history=[])

    try:
        # Send message to Gemini
        response = sessions[session_id].send_message(user_message)

        reply = response.text.strip()

        # Remove Markdown symbols
        reply = (
            reply.replace("**", "")
                 .replace("###", "")
                 .replace("##", "")
                 .replace("#", "")
                 .replace("```", "")
        )

        # Replace bullet markdown
        reply = reply.replace("* ", "• ")

        # Remove excessive blank lines
        while "\n\n\n" in reply:
            reply = reply.replace("\n\n\n", "\n\n")

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )