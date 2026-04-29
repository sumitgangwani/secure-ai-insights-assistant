import os
from google import genai

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

client = genai.Client()


def generate_answer(question: str, tool_results: dict) -> str:
    if not os.getenv("GEMINI_API_KEY"):
        return "Gemini API key is missing. Please set GEMINI_API_KEY in backend/.env."

    prompt = f"""
You are a secure internal analytics assistant.

Rules:
- Use only the provided tool results.
- Do not invent numbers.
- Mention which sources were used.
- Keep the answer concise and business-focused.

Question:
{question}

Tool results:
{tool_results}

Answer:
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or "No response generated."