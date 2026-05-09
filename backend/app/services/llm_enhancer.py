import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

PROMPT_TEMPLATE = """
You are an elite technical recruiter and resume optimizer.
You must output ONLY a valid JSON Array.

Context:
- Job Description Requirements: {jd_analysis}
- ATS Keyword Gaps: {missing_skills}
- User Github Repos to Inject/Sub in: {github_repos}

Goal:
1. Read the provided Resume Text.
2. Completely swap weak or irrelevant 'Projects' with the top Github Repos provided if they better match the JD.
3. Ensure the newly constructed resume fits on ONE PAGE. Be exceedingly concise. Follow the STAR methodology.

Return a raw JSON array of the most significant changes you made. Schema:
[
  {{
    "section": "Experience / Projects",
    "before": "old text you removed or upgraded",
    "after": "new text you generated focusing strictly on brevity and keywords"
  }}
]

Original Resume Text:
{resume_text}
"""

def _build_prompt(resume_text: str, jd_analysis: dict, match_data: dict, github_data: dict) -> str:
    return PROMPT_TEMPLATE.format(
        jd_analysis=jd_analysis,
        missing_skills=match_data.get("missing_skills", []),
        github_repos=github_data.get("recent_repos", []) if github_data else "None provided",
        resume_text=resume_text,
    )


def _parse_json(text: str) -> list:
    text = text.strip().replace("```json", "").replace("```", "").strip()
    return list(json.loads(text))


def enhance_resume_bullets(resume_text: str, jd_analysis: dict, match_data: dict, github_data: dict = None) -> list:
    """
    Passes GitHub repos directly mapping them over the original projects seamlessly!
    Falls back to Groq (llama-3.3-70b) if Gemini fails.
    """
    prompt = _build_prompt(resume_text, jd_analysis, match_data, github_data)

    # --- Primary: Gemini ---
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        return _parse_json(response.text)
    except Exception as e:
        print(f"[llm_enhancer] Gemini failed: {e} — switching to Groq fallback")

    # --- Fallback: Groq ---
    try:
        chat = _groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return _parse_json(chat.choices[0].message.content)
    except Exception as e:
        print(f"[llm_enhancer] Groq fallback also failed: {e}")
        return []
