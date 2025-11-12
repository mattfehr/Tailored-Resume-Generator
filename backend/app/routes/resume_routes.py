from fastapi import APIRouter, UploadFile, Form, HTTPException
from app.services import parsing_service, latex_service, keyword_service, rewrite_service, score_service

router = APIRouter()

@router.post("/rewrite", tags=["Resume"])
async def rewrite_resume(
    resume: UploadFile | None = None,
    latex_content: str | None = Form(None),
    job_description: str = Form(...)
):
    """
    Handles two input cases:
    1. File upload (PDF/DOCX)
    2. Raw LaTeX upload (string)
    """
    try:
        # Determine input type
        if resume:
            resume_text = parsing_service.extract_text_from_resume(resume)
            latex_resume = latex_service.wrap_in_jake_template(resume_text)
        elif latex_content:
            latex_resume = latex_service.clean_and_validate_latex(latex_content)
        else:
            raise HTTPException(status_code=400, detail="Please upload a file or provide LaTeX content.")

        # Extract keywords from job description
        keywords = keyword_service.extract_keywords(job_description)

        # Rewrite using Gemini
        tailored_resume = rewrite_service.rewrite_resume_with_gemini(latex_resume, job_description, keywords)

        # Compute ATS score
        ats_score = score_service.compute_ats_score(job_description, tailored_resume)

        return {
            "tailored_resume": tailored_resume,
            "ats_score": ats_score,
            "keywords": keywords
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
