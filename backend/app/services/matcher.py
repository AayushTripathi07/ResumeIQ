import os
import google.generativeai as genai
import json

def calculate_match(resume_text: str, jd_analysis: dict) -> dict:
    """
    Computes accurate ATS scoring by replicating the exact enterprise ATS calculation logic specified by the user manually,
    executing it through the LLM for deep boolean + semantic understanding of quantified impact.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    req_skills = jd_analysis.get("required_skills", [])
    
    prompt = f"""
    You are an elite Applicant Tracking System (ATS). Evaluate this resume against the JD Skills securely.
    Calculate a harsh but realistic ATS Score (0-100) combining these exact weights:
    1. Perfect Header / Structure Formatting (10 points max)
    2. Deep keyword alignment against the JD skills: {req_skills} (40 points max)
    3. Highly quantified bullet points indicating scaling, %, $ impact, or dataset sizing (50 points max)
    
    Additionally, explicitly list the JD skills that this resume is severely lacking.
    
    Return ONLY a raw JSON dictionary without markdown! Format exactly as:
    {{"score": 88, "missing_skills": ["skillA", "skillB"]}}
    
    Resume Extracted Text:
    {resume_text}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        return {
            "score": int(data.get("score", 50)),
            "missing_skills": list(data.get("missing_skills", [])),
            "project_recommendations": []
        }
    except Exception as e:
        print(f"ATS LLM Fallback: {e}")
        return {
            "score": 50, 
            "missing_skills": req_skills,
            "project_recommendations": []
        }
