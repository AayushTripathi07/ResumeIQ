import re
import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
_groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---------------------------------------------------------------------------
# LaTeX post-processing sanitizer
# ---------------------------------------------------------------------------

def _sanitize_latex(tex: str) -> str:
    """
    Fixes the most common LLM LaTeX generation errors:
    1. Unescaped % inside resumeItem arguments
    2. Multi-line resumeItem{} collapsed to single line
    3. fontawesome / marvosym packages removed
    4. scshape+bfseries conflict removed
    5. Markdown fences stripped
    """
    # Strip markdown code fences
    tex = re.sub(r"```(?:latex|tex)?\n?", "", tex)
    tex = tex.replace("```", "")

    # Remove problematic packages
    tex = re.sub(r"\\usepackage\{fontawesome[^}]*\}\n?", "", tex)
    tex = re.sub(r"\\usepackage\{marvosym\}\n?", "", tex)

    # Collapse multi-line \resumeItem{...} to single line — the #1 runaway arg fix
    def collapse_item(m):
        inner = m.group(1).replace("\n", " ").replace("  ", " ").strip()
        return "\\resumeItem{" + inner + "}"

    # Repeat until no more multi-line items remain
    for _ in range(5):
        new_tex = re.sub(r"\\resumeItem\{([^}]*\n[^}]*)\}", collapse_item, tex)
        if new_tex == tex:
            break
        tex = new_tex

    # Escape lone % signs inside resumeItem arguments (not already escaped)
    def escape_percent(m):
        inner = re.sub(r"(?<!\\)%", r"\\%", m.group(1))
        return "\\resumeItem{" + inner + "}"
    tex = re.sub(r"\\resumeItem\{([^}]+)\}", escape_percent, tex)

    # Fix the \scshape\bfseries font-shape conflict — drop \scshape from section headers
    tex = tex.replace("\\vspace{2pt}\\scshape\\large\\bfseries", "\\vspace{2pt}\\large\\bfseries")
    tex = tex.replace("\\scshape\\large\\bfseries", "\\large\\bfseries")

    return tex.strip()


# ---------------------------------------------------------------------------
# Prompt builder (kept as a function to avoid unicode escape issues)
# ---------------------------------------------------------------------------

def _build_prompt(diff_instructions: str, resume_text: str) -> str:
    # Build template using string concatenation to avoid python unicode escape conflicts
    NL = "\n"

    template = (
        r"\documentclass[letterpaper,11pt]{article}" + NL +
        r"\usepackage{latexsym}" + NL +
        r"\usepackage[empty]{fullpage}" + NL +
        r"\usepackage{titlesec}" + NL +
        r"\usepackage[usenames,dvipsnames]{color}" + NL +
        r"\usepackage{enumitem}" + NL +
        r"\usepackage[hidelinks]{hyperref}" + NL +
        r"\usepackage{fancyhdr}" + NL + NL +
        r"\pagestyle{fancy}" + NL +
        r"\fancyhf{}" + NL +
        r"\renewcommand{\headrulewidth}{0pt}" + NL +
        r"\renewcommand{\footrulewidth}{0pt}" + NL + NL +
        r"\addtolength{\oddsidemargin}{-0.6in}" + NL +
        r"\addtolength{\textwidth}{1.19in}" + NL +
        r"\addtolength{\topmargin}{-.5in}" + NL +
        r"\addtolength{\textheight}{1.4in}" + NL + NL +
        r"\raggedbottom" + NL +
        r"\raggedright" + NL +
        r"\setlength{\tabcolsep}{0in}" + NL + NL +
        r"\titleformat{\section}{\vspace{2pt}\large\bfseries}{}{}{}[\color{black}\titlerule \vspace{2pt}]" + NL + NL +
        r"\pdfgentounicode=1" + NL + NL +
        r"\newcommand{\resumeItem}[1]{\item\small{#1 \vspace{-2pt}}}" + NL +
        r"\newcommand{\resumeSubheading}[4]{\vspace{-2pt}\item\begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}\textbf{#1} & \textbf{\small #2} \\\textit{\small#3} & \textit{\small #4}\\\end{tabular*}\vspace{-7pt}}" + NL +
        r"\newcommand{\resumeProjectHeading}[2]{\item\begin{tabular*}{1.0\textwidth}{l@{\extracolsep{\fill}}r}\textbf{#1} & {\small #2}\\\end{tabular*}\vspace{-7pt}}" + NL +
        r"\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in,label={}]}" + NL +
        r"\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}" + NL +
        r"\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.15in]}" + NL +
        r"\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}" + NL + NL +
        r"\begin{document}" + NL + NL +
        r"\begin{center}" + NL +
        r"{\Huge \textbf{[NAME]}} \\ \vspace{4pt}" + NL +
        r"\small [PHONE] $|$ \href{mailto:[EMAIL]}{\underline{[EMAIL]}} $|$ \href{[LINKEDIN]}{\underline{linkedin.com/in/[USERNAME]}} $|$ \href{[GITHUB]}{\underline{github.com/[USERNAME]}}" + NL +
        r"\end{center}" + NL + NL +
        r"\section{Education}" + NL +
        r"\resumeSubHeadingListStart" + NL +
        r"  \resumeSubheading{[UNIVERSITY]}{[GRAD DATE]}{[DEGREE]}{[LOCATION]}" + NL +
        r"\resumeSubHeadingListEnd" + NL + NL +
        r"\section{Technical Skills}" + NL +
        r"\begin{itemize}[leftmargin=0.15in, label={}]" + NL +
        r"  \small{\item{\textbf{Languages: }[LANGS] \textbf{Frameworks: }[FRAMEWORKS] \textbf{Tools: }[TOOLS]}}" + NL +
        r"\end{itemize}" + NL + NL +
        r"\section{Experience}" + NL +
        r"\resumeSubHeadingListStart" + NL +
        r"  \resumeSubheading{[COMPANY]}{[DATES]}{[ROLE]}{[LOCATION]}" + NL +
        r"    \resumeItemListStart" + NL +
        r"      \resumeItem{[SINGLE LINE BULLET. Use STAR format. Max 20 words.]}" + NL +
        r"    \resumeItemListEnd" + NL +
        r"\resumeSubHeadingListEnd" + NL + NL +
        r"\section{Projects}" + NL +
        r"\resumeSubHeadingListStart" + NL +
        r"  \resumeProjectHeading{\textbf{[PROJECT]} $|$ \emph{[TECH STACK]}}{[DATE]}" + NL +
        r"    \resumeItemListStart" + NL +
        r"      \resumeItem{[SINGLE LINE BULLET.]}" + NL +
        r"    \resumeItemListEnd" + NL +
        r"\resumeSubHeadingListEnd" + NL + NL +
        r"\end{document}"
    )

    rules = (
        "You are an expert LaTeX typesetter producing a 1-page resume.\n\n"
        "ABSOLUTE RULES — every violation causes a compilation failure:\n"
        "1. Output ONLY raw LaTeX. No markdown, no code fences, no explanation.\n"
        "2. Every \\resumeItem{} content MUST be on ONE LINE — NEVER split across lines.\n"
        "3. Escape ALL special chars in text: % → \\%   & → \\&   # → \\#   $ → \\$\n"
        "4. DO NOT add any \\usepackage declarations beyond the template.\n"
        "5. NO negative \\vspace anywhere.\n"
        "6. ONE PAGE MAXIMUM — be extremely concise in bullet points.\n"
        "7. NEVER use \\scshape, fontawesome icons, or marvosym.\n\n"
        "Apply these content modifications:\n"
        + diff_instructions + "\n\n"
        "Use EXACTLY this template structure:\n\n"
        + template + "\n\n"
        "Raw Resume Text to fill into the template:\n"
        + resume_text
    )
    return rules


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_latex(resume_data: dict, match_data: dict, diff_objects: list) -> str:
    """
    Generates a compilable 1-page LaTeX resume via Gemini, with Groq fallback.
    Applies robust post-processing to fix common LLM-generated LaTeX errors.
    """
    diff_instructions = "\n".join(
        ["- REPLACE: '" + d.before + "'\n  WITH: '" + d.after + "'" for d in diff_objects]
    ) or "No specific diffs — format the resume cleanly from the raw text."

    prompt = _build_prompt(diff_instructions, resume_data.get("raw_text", ""))

    def _extract_and_sanitize(raw_text: str) -> str:
        start = raw_text.find("\\documentclass")
        end = raw_text.rfind("\\end{document}")
        if start == -1 or end == -1:
            raise ValueError("LLM output missing \\documentclass or \\end{document}")
        tex = raw_text[start: end + 14]
        return _sanitize_latex(tex)

    # --- Primary: Gemini ---
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result = _extract_and_sanitize(response.text)
        print("[latex_generator] Gemini succeeded")
        return result
    except Exception as e:
        print(f"[latex_generator] Gemini failed: {e} — switching to Groq")

    # --- Fallback: Groq ---
    try:
        chat = _groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        result = _extract_and_sanitize(chat.choices[0].message.content)
        print("[latex_generator] Groq fallback succeeded")
        return result
    except Exception as e:
        print(f"[latex_generator] Groq fallback also failed: {e}")

    return (
        "\\documentclass[11pt]{article}\n"
        "\\begin{document}\n"
        "\\textbf{Error}: The AI engine could not generate a valid resume. Please try again.\n"
        "\\end{document}\n"
    )
