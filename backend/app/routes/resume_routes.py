from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from app.services import parsing_service, latex_service, keyword_service, rewrite_service, score_service
from io import BytesIO
import requests
import re
import json

router = APIRouter()

@router.post("/rewrite", tags=["Resume"])
async def rewrite_resume(
    resume: UploadFile | None = None,
    latex_content: str | None = Form(None),
    latex_resume: str | None = Form(None),
    job_description: str = Form(...)
):
    try:
        print("Parsing input...")
        if resume:
            resume_text = parsing_service.extract_text_from_resume(resume)
            latex_resume_final = latex_service.wrap_in_jake_template(resume_text)

        elif latex_resume:
            latex_resume_final = latex_service.clean_and_validate_latex(latex_resume)

        elif latex_content:
            latex_resume_final = latex_service.clean_and_validate_latex(latex_content)

        else:
            raise HTTPException(status_code=400, detail="Please upload a resume (PDF) or a LaTeX (.tex) file.")

        print("Extracting keywords...")
        keywords = keyword_service.extract_keywords(job_description)

        print("Rewriting resume...")
        tailored_resume = rewrite_service.rewrite_resume_with_gemini(
            latex_resume_final, job_description, keywords
        )

        print("ATS Scoring...")
        ats_score = score_service.compute_ats_score(job_description, tailored_resume, keywords)

        print("Done")
        return {
            "tailored_resume": tailored_resume,
            "ats_score": ats_score,
            "keywords": keywords,
            "job_description": job_description
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.post("/compile", tags=["Resume"])
async def compile_latex(latex_content: str = Form(...)):
    try:
        latex_content = latex_content.strip()
        latex_content = re.sub(r"^```[a-zA-Z]*|```$", "", latex_content, flags=re.MULTILINE).strip()
        latex_content = latex_content.replace(
            "\\input{glyphtounicode}",
            "% Removed glyphtounicode for remote compilation"
        )

        response = requests.get(
            "https://latexonline.cc/compile",
            params={"text": latex_content},
            timeout=90
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"LaTeX API returned {response.status_code}: {response.text[:500]}"
            )

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


@router.post("/score", tags=["Resume"])
async def score_resume(
    latex_body: str = Form(...),
    job_description: str = Form(...),
    keywords_json: str = Form(...)
):
    try:
        print("---- SCORE ENDPOINT RECEIVED ----")
        print("latex_content", latex_body)
        print("job_description (first 200 chars):", job_description[:200])
        print("keywords_json:", keywords_json)
        print("----------------------------------")

        cleaned_latex = latex_body.strip()
        cleaned_latex = re.sub(r"^```[a-zA-Z]*|```$", "", cleaned_latex, flags=re.MULTILINE).strip()

        keywords = json.loads(keywords_json)

        ats_score = score_service.compute_ats_score(
            job_description,
            cleaned_latex,
            keywords
        )

        return {
            "ats_score": ats_score,
            "keywords": keywords
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating ATS score: {str(e)}"
        )
