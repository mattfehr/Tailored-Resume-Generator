from fastapi import APIRouter, UploadFile, Form

router = APIRouter()

@router.post("/rewrite", tags=["Resume"])
async def rewrite_resume(
    resume: UploadFile,
    job_description: str = Form(...)
):
    """
    Stub endpoint for resume rewriting.
    Later this will:
      1. Extract text from the uploaded resume.
      2. Extract keywords from job description.
      3. Rewrite via Gemini API.
      4. Compute ATS score.
    """
    # Mock response
    return {
        "tailored_resume": "This is a sample rewritten resume text for the MVP.",
        "ats_score": 84.6,
        "keywords": ["Python", "APIs", "Machine Learning"]
    }
