from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from app.services import parsing_service, latex_service, keyword_service, rewrite_service, score_service
from io import BytesIO
import requests
import re

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
        tailored_resume = rewrite_service.rewrite_resume_with_gemini(
            latex_resume, job_description, keywords
        )

        # Compute ATS score
        ats_score = score_service.compute_ats_score(job_description, tailored_resume)

        return {
            "tailored_resume": tailored_resume,
            "ats_score": ats_score,
            "keywords": keywords,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.post("/compile", tags=["Resume"])
async def compile_latex(latex_content: str = Form(...)):
    """
    Compiles LaTeX into a PDF using latexonline.cc (no local TeX installation required).
    Automatically cleans Markdown fences and unsupported includes.
    """
    try:
        # Sanitize LaTeX content
        latex_content = latex_content.strip()
        latex_content = re.sub(r"^```[a-zA-Z]*|```$", "", latex_content, flags=re.MULTILINE).strip()
        latex_content = latex_content.replace(
            "\\input{glyphtounicode}",
            "% Removed glyphtounicode for remote compilation"
        )

        # Send to latexonline.cc for PDF compilation
        print("Sending to latexonline.cc for compilation...")
        response = requests.get(
            "https://latexonline.cc/compile",
            params={"text": latex_content},
            timeout=90
        )
        print("LATEXONLINE STATUS:", response.status_code)
        print("LATEXONLINE HEADERS:", response.headers)
        print("LATEXONLINE BODY (first 300):", response.text[:300])

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"LaTeX API returned {response.status_code}: {response.text[:500]}"
            )

        # Return PDF stream to frontend
        pdf_stream = BytesIO(response.content)
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=tailored_resume.pdf"}
        )

    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Remote LaTeX API timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error using LaTeX API: {str(e)}")
