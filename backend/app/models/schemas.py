from pydantic import BaseModel
from typing import List, Optional

class JDAnalysis(BaseModel):
    required_skills: List[str]
    experience_level: str
    priority_keywords: List[str]

class DiffItem(BaseModel):
    section: str
    before: str
    after: str

class ProcessingResponse(BaseModel):
    before_score: int
    after_score: int
    diffs: List[DiffItem]
    latex_url: Optional[str] = None
    pdf_download_url: Optional[str] = None
    latex_code: str = ""
