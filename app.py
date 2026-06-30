from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)
CORS(app)

# ==========================================
# Configure Gemini
# ==========================================

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==========================================
# Gemini Model
# ==========================================

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
You are DU SOL AI Assistant, an intelligent AI assistant for Delhi University School of Open Learning (DU SOL).

Your job is to help students with:

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

2. Be friendly and professional.

3. Keep responses concise unless more detail is requested.

4. Always format responses using Markdown.

Use:
- Bullet lists
- Numbered lists
- **Bold** important information
- Tables whenever appropriate
- Always use complete URLs beginning with https://

Never output:

sol.du.ac.in

Instead output:

https://sol.du.ac.in

5. Do NOT use Markdown headings like ###.

6. Avoid excessive bold formatting.

7. Do NOT repeatedly tell users to visit the DU SOL website.

8. Mention the official website only if:
   - Official notices are requested
   - Official forms are requested
   - Official links are requested
   - Latest circulars are requested

9. Never invent facts.

10. If information changes every year, clearly mention that it may vary.

11. End replies with a helpful follow-up question whenever appropriate.
"""
)

# ==========================================
# Store Chat Sessions
# ==========================================

sessions = {}

# ==========================================
# Home Route
# ==========================================

@app.route("/")
def home():
    return "DU SOL AI Assistant is running!"

# ==========================================
# Health Check
# ==========================================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })

# ==========================================
# Chat API
# ==========================================

@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    # Create new chat session if required
    if session_id not in sessions:
        sessions[session_id] = model.start_chat(history=[])

    try:

        # Send prompt to Gemini
        response = sessions[session_id].send_message(user_message)

        reply = response.text.strip()

        # --------------------------------------
        # Remove code blocks
        # --------------------------------------

        reply = reply.replace("```", "")

        # --------------------------------------
        # Convert DU SOL domains to clickable URLs
        # --------------------------------------

        reply = re.sub(
            r'(?<!https://)(?<!http://)\b(www\.sol\.du\.ac\.in)\b',
            r'https://\1',
            reply,
            flags=re.IGNORECASE
        )

        reply = re.sub(
            r'(?<!https://)(?<!http://)\b(sol\.du\.ac\.in)\b',
            r'https://\1',
            reply,
            flags=re.IGNORECASE
        )

        # --------------------------------------
        # Remove extra blank lines
        # --------------------------------------

        while "\n\n\n" in reply:
            reply = reply.replace("\n\n\n", "\n\n")

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ==========================================
# Run Flask
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )