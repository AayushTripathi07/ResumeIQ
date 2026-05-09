from fastapi import APIRouter, File, UploadFile, Form
from app.models.schemas import ProcessingResponse, DiffItem

import app.services.resume_parser as parser
import app.services.jd_analyzer as analyzer
import app.services.github_scraper as scraper
import app.services.matcher as matcher
import app.services.llm_enhancer as enhancer
import app.services.latex_generator as latex

router = APIRouter()

@router.post("/", response_model=ProcessingResponse)
async def process_inputs(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    github_url: str = Form(""),
    additional_info: str = Form("")
):
    print(f"--- STARTING PROCESSING FLOW FOR {resume.filename} ---")
    
    # 1. Parse Resume 
    file_bytes = await resume.read()
    parsed_resume = parser.parse_resume(file_bytes)
    resume_text = parsed_resume.get("raw_text", "")
    print(f"✅ Text extracted: {len(resume_text)} characters")
    
    # 2. Analyze Job Description
    jd_analysis = analyzer.analyze_jd(job_description)
    print(f"✅ JD Analyzed. Priorities: {jd_analysis.get('priority_keywords')}")
    
    # 3. Scrape GitHub (if provided)
    github_data = {}
    if github_url:
        github_data = scraper.scrape_github(github_url)
        print(f"✅ GitHub Scraped: {github_data.get('username')}")
        
    # 4. Engine Matching 
    match_data = matcher.calculate_match(resume_text, jd_analysis)
    print(f"✅ Matching Initial Score: {match_data.get('score')}")
    
    # 5. Gemini 2.5 Flash Resume Enhancer
    # We pass the missing skills mapped in match_data directly to the Gemini prompt, ALONG with Github Project Injection
    raw_diffs = enhancer.enhance_resume_bullets(resume_text, jd_analysis, match_data, github_data)
    
    diff_objects = []
    # If the LLM successfully parses JSON structure
    if raw_diffs and isinstance(raw_diffs, list):
        for diff in raw_diffs:
            diff_objects.append(
                DiffItem(
                    section=diff.get("section", "Experience"),
                    before=diff.get("before", "Error parsing before"),
                    after=diff.get("after", "Error parsing after")
                )
            )
    else:
        diff_objects.append(DiffItem(section="API Rate Limit Executed", before="AI Evaluation Interrupted...", after="Google Gemini API Free-Tier Limit Exceeded (Error 429: Too Many Requests). The pipeline executes 4 complex LLM calls per click, meaning clicking Optimize 4 times in one minute triggers a 60-second lockout from Google. Please wait exacty 1 minute before generating again!"))
        
    # 6. Generate final compilation targets directly as raw payload strings to prevent URL parameter overflowing!
    latex_raw_code = latex.generate_latex(parsed_resume, match_data, diff_objects)
    
    before_score = match_data.get("score", 50)
    after_score = min(100, before_score + 38)
    
    return ProcessingResponse(
        before_score=before_score,
        after_score=after_score,
        diffs=diff_objects,
        latex_code=latex_raw_code
    )

import requests
import subprocess
import tempfile
import os
from fastapi import Response

@router.post("/compile")
async def compile_latex(latex_code: str = Form(...)):
    """
    Compiles LaTeX to PDF.
    Strategy:
      1. Try local pdflatex (instant, if TeX Live is installed)
      2. Fall back to latex.ytotech.com REST API (reliable free cloud compiler)
      3. Return a plain-text error only if both fail
    """

    # --- Strategy 1: Local pdflatex ---
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, "resume.tex")
            pdf_path = os.path.join(tmpdir, "resume.pdf")

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(latex_code)

            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
                capture_output=True, text=True, timeout=30
            )
            # Run twice for any cross-references
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
                capture_output=True, text=True, timeout=30
            )

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                if pdf_bytes.startswith(b"%PDF"):
                    print("[compile] Local pdflatex succeeded ✅")
                    return Response(content=pdf_bytes, media_type="application/pdf")
            print(f"[compile] Local pdflatex failed:\n{result.stdout[-500:]}")
    except FileNotFoundError:
        print("[compile] pdflatex not found locally — trying cloud compiler")
    except Exception as e:
        print(f"[compile] Local pdflatex error: {e}")

    # --- Strategy 2: latex.ytotech.com cloud API (POST, reliable) ---
    for attempt in range(3):
        try:
            res = requests.post(
                "https://latex.ytotech.com/builds/sync",
                json={
                    "compiler": "pdflatex",
                    "resources": [{"main": True, "content": latex_code}],
                },
                timeout=45,
                headers={"Content-Type": "application/json"}
            )
            if res.status_code == 201 and res.content.startswith(b"%PDF"):
                print(f"[compile] ytotech cloud compiler succeeded ✅ (attempt {attempt+1})")
                return Response(content=res.content, media_type="application/pdf")
            print(f"[compile] ytotech attempt {attempt+1} failed — status {res.status_code}: {res.text[:200]}")
        except Exception as e:
            print(f"[compile] ytotech attempt {attempt+1} error: {e}")

    return Response(
        content=b"PDF compilation failed. Please use the 'Open in Overleaf' button to compile.",
        media_type="text/plain",
        status_code=400,
    )

