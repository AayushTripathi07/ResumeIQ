import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

JD_PROMPT = """
You are an ATS parser logic layer.
Extract the absolutely critical hard skills, toolchains, and methodologies from this Job Description.
Limit tightly to the top 15 words.

Return ONLY a valid JSON list of strings representing the skills.

Job Description:
{jd_text}
"""

def _parse_skills(text: str) -> dict:
    cleaned = text.replace("```json", "").replace("```", "").strip()
    keywords = json.loads(cleaned)
    return {
        "required_skills": keywords,
        "experience_level": "Standard",
        "priority_keywords": keywords,
    }


def analyze_jd(jd_text: str) -> dict:
    """
    Uses Gemini to strictly isolate the technical capabilities missing in standard regex extraction.
    Falls back to Groq (llama-3.3-70b) if Gemini fails.
    """
    prompt = JD_PROMPT.format(jd_text=jd_text)

    # --- Primary: Gemini ---
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return _parse_skills(response.text)
    except Exception as e:
        print(f"[jd_analyzer] Gemini failed: {e} — switching to Groq fallback")

    # --- Fallback: Groq ---
    try:
        chat = _groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return _parse_skills(chat.choices[0].message.content)
    except Exception as e:
        print(f"[jd_analyzer] Groq fallback also failed: {e}")
        # Last-resort regex extraction
        words = jd_text.lower().replace(",", " ").split()
        return {"required_skills": words[:10], "priority_keywords": words[:10]}
