import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("MODEL")

if not key:
    raise ValueError("GOOGLE_API_KEY is missing from your .env file.")

if not model:
    raise ValueError("MODEL is missing from your .env file.")

google_Client = genai.Client(api_key=key)


# --------------------------------------------------
# Load your resume and summary
# --------------------------------------------------

RESUME_PATH = BASE_DIR / "assets" / "DP_Resume.pdf"
SUMMARY_PATH = BASE_DIR / "assets" / "summary.txt"

reader = PdfReader(str(RESUME_PATH))

myData = ""

for page in reader.pages:
    text = page.extract_text()

    if text:
        myData += text + "\n"


with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
    summary = f.read()


# --------------------------------------------------
# System prompt
# --------------------------------------------------

system_prompt = f"""
# Your role

You are a digital twin running on a website, chatting with visitors.
You represent the person whose website you are on.

You answer questions related to their career, background, skills,
and experience.

Here are the details of the person you are representing:

{summary}

If asked, explain clearly that you are an AI digital twin of this person.

# Context

Here is the person's resume and professional background:

{myData}

# Rules

- Be professional, engaging, and helpful.
- Answer questions related to the person's career, background,
  skills, and experience.
- If a question is unrelated to professional topics, politely
  steer the conversation back to professional topics.
- Stay in character as the person's digital twin.
- Never invent information.
- If you do not know an answer from the supplied context,
  say that you do not know.

# Tools

- If you cannot answer a professional question from the supplied
  context, call record_unknown_question_tool with the user's question.
- If the user voluntarily provides their email address, call
  record_user_details_tool with their email, name if provided,
  and relevant notes.
- Do not ask for contact details unnecessarily.
- Never claim that information was saved unless the tool succeeds.
"""


# --------------------------------------------------
# Tool: Save visitor details
# --------------------------------------------------

def record_user_details_tool(
    email: str,
    name: str = "Name not provided",
    notes: str = "not provided",
) -> str:
    """Save visitor contact details to a text file."""

    file_path = BASE_DIR / "user_details.txt"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(
            f"Date: {datetime.now()}\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Notes: {notes}\n"
            f"{'-' * 50}\n"
        )

    return "User details recorded successfully."


# --------------------------------------------------
# Tool: Save unanswered questions
# --------------------------------------------------

def record_unknown_question_tool(question: str) -> str:
    """Save a question the digital twin cannot answer."""

    file_path = BASE_DIR / "unknown_questions.txt"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(
            f"Date: {datetime.now()}\n"
            f"Question: {question}\n"
            f"{'-' * 50}\n"
        )

    return "Unknown question recorded successfully."


# --------------------------------------------------
# Conversation history
# --------------------------------------------------

history = []


# --------------------------------------------------
# Chat function
# --------------------------------------------------

def chat(message, history):
    """Send a message to Gemini and update the conversation history."""

    history.append(
        types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )
    )

    response = google_Client.models.generate_content(
        model=model,
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[
                record_user_details_tool,
                record_unknown_question_tool,
            ],
        ),
    )

    answer = response.text or "I couldn't generate a response."

    # Preserve Gemini's response content in the conversation.
    if response.candidates:
        model_content = response.candidates[0].content

        if model_content:
            history.append(model_content)

    return answer