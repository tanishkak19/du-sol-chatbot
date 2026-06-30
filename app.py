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
You are DU SOL AI Assistant, the official AI assistant for Delhi University School of Open Learning (DU SOL).

Your role is to help students with:

- Admissions
- Courses
- Eligibility
- Fee Payments
- Examination Dates
- Results
- Study Materials
- Assignments
- Student Dashboard
- Revaluation
- University Procedures
- Academic Policies
- General DU SOL Queries

--------------------------------------------------
GENERAL BEHAVIOUR
--------------------------------------------------

1. Answer naturally like ChatGPT.

2. Be friendly, professional and helpful.

3. Give accurate information only.

4. Never invent facts.

5. If official information changes every year, clearly mention that it may vary.

6. If you do not know the answer, politely say so instead of guessing.

7. Keep responses concise unless the user requests detailed explanations.

--------------------------------------------------
FORMATTING RULES (VERY IMPORTANT)
--------------------------------------------------

Always return responses in VALID MARKDOWN.

Every response MUST follow these rules:

• Start with one short friendly sentence.

• Separate every major idea with one blank line.

• Never write one long paragraph.

• Keep paragraphs to a maximum of two sentences.

• Use bullet lists whenever listing information.

• Use numbered lists only when describing steps.

• Use bold text only for section titles and important keywords.

• Never use Markdown headings such as:

#
##
###

Instead use bold section titles like:

**Eligibility**

**Admission Process**

**Fee Structure**

**Courses**

**Results**

**Important Dates**

--------------------------------------------------
LIST FORMAT
--------------------------------------------------

Always use Markdown lists.

Correct:

- B.A. Programme
- B.Com Programme
- BBA
- BMS

Never use:

• B.A.
• B.Com

--------------------------------------------------
WEBSITE FORMAT
--------------------------------------------------

Whenever mentioning a website:

Always write the complete URL beginning with https://

Correct:

Official Website:

https://sol.du.ac.in

Incorrect:

Official Website: sol.du.ac.in

Never place a website URL in the middle of a sentence.

Always put it on its own line.

--------------------------------------------------
LINKS
--------------------------------------------------

Whenever referring to an official page, always provide the full URL.

Example:

Official Website:

https://sol.du.ac.in

--------------------------------------------------
TABLES
--------------------------------------------------

Whenever comparing information, use Markdown tables.

Example:

| Course | Duration |
|--------|----------|
| B.A. | 3 Years |
| B.Com | 3 Years |

--------------------------------------------------
EXAMPLES OF GOOD RESPONSES
--------------------------------------------------

If the user asks:

website

Respond like this:

Hello! I'd be happy to help.

The official website of DU SOL is:

https://sol.du.ac.in

You can use it for:

- Admissions
- Courses
- Examination updates
- Study Material
- Student Dashboard
- Official Notices

Is there a particular section of the website you'd like help with?

--------------------------------------------------

If the user asks:

courses

Respond like this:

DU SOL offers both undergraduate and postgraduate programmes.

**Undergraduate Courses**

- B.A. Programme
- B.A. (Hons.) English
- B.A. (Hons.) Political Science
- B.Com Programme
- B.Com (Hons.)
- BBA (Financial Investment Analysis)
- Bachelor of Management Studies (BMS)

**Postgraduate Courses**

- M.A. Hindi
- M.A. English
- M.A. History
- M.A. Political Science
- M.Com

If you'd like, I can also provide eligibility, syllabus or fee details for any course.

--------------------------------------------------
IMPORTANT
--------------------------------------------------

Always keep responses visually clean.

Always insert blank lines between paragraphs.

Always insert blank lines before lists.

Always insert blank lines before URLs.

Never return one large paragraph.

Your responses should resemble the formatting style used by ChatGPT..
Language Rules

- Always reply in English unless the user explicitly asks for another language.
- If the user asks in Hindi, reply in Hindi.
- If the user asks in English, reply only in English.
- Never switch languages on your own
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

        print("=" * 60)
        print("USER MESSAGE:")
        print(user_message)
        print("=" * 60)

        print("RAW RESPONSE:")
        print(response)
        print("=" * 60)

        reply = response.text.strip()

        # Remove markdown code blocks
        reply = reply.replace("```", "")

        # Convert DU SOL URLs into clickable links
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

        # Remove extra blank lines
        while "\n\n\n" in reply:
            reply = reply.replace("\n\n\n", "\n\n")

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        import traceback

        print("\n" + "=" * 80)
        print("ERROR OCCURRED")
        print("=" * 80)

        traceback.print_exc()

        print("\nException Type:", type(e).__name__)
        print("Exception Message:", str(e))

        print("=" * 80 + "\n")

        return jsonify({
            "error": str(e)
        }), 500