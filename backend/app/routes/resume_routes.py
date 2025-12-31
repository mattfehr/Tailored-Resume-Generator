from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.services import parsing_service, latex_service, keyword_service, rewrite_service, score_service
from app.utils.auth import verify_jwt
from app.config import Config
from io import BytesIO
import requests
import re
import json

router = APIRouter()

# Supabase config for personalization
SUPABASE_URL = Config.SUPABASE_URL
SUPABASE_KEY = Config.SUPABASE_SERVICE_ROLE_KEY

supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


@router.post("/rewrite", tags=["Resume"])
async def rewrite_resume(
    request: Request,
    resume: UploadFile | None = None,
    latex_content: str | None = Form(None),
    latex_resume: str | None = Form(None),
    job_description: str = Form(...),
    template_id: str | None = Form(None),
):
    try:
        print("Parsing input...")

        # -------------------------
        # Load original LaTeX resume
        # -------------------------
        if resume:
            resume_text = parsing_service.extract_text_from_resume(resume)

            # Default template (Jake)
            template_latex = None

            # If user provided template_id, require auth and fetch it
            if template_id:
                auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
                if not auth_header or not auth_header.lower().startswith("bearer "):
                    raise HTTPException(status_code=401, detail="Login required to use custom templates.")

                token = auth_header.split(" ", 1)[1].strip()
                payload = verify_jwt(token)
                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid auth token.")

                tpl_res = requests.get(
                    f"{SUPABASE_URL}/rest/v1/resume_templates?id=eq.{template_id}&user_id=eq.{user_id}&select=latex",
                    headers=supabase_headers
                )
                if tpl_res.status_code != 200 or not tpl_res.json():
                    raise HTTPException(status_code=404, detail="Template not found.")
                template_latex = tpl_res.json()[0]["latex"]

            if template_latex:
                latex_resume_final = latex_service.wrap_in_template(resume_text, template_latex)
            else:
                latex_resume_final = latex_service.wrap_in_jake_template(resume_text)

        elif latex_resume:
            latex_resume_final = latex_service.clean_and_validate_latex(latex_resume)

        elif latex_content:
            latex_resume_final = latex_service.clean_and_validate_latex(latex_content)

        else:
            raise HTTPException(
                status_code=400,
                detail="Please upload a resume (PDF) or a LaTeX (.tex) file."
            )

        print("Extracting keywords...")
        keywords = keyword_service.extract_keywords(job_description)

        # -------------------------
        # Optional auth: try to read JWT from Authorization header
        # -------------------------
        experiences: list = []
        projects: list = []
        user_id = None

        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = verify_jwt(token)
                user_id = payload.get("sub")
            except Exception as e:
                print("JWT invalid or failed to verify, treating as guest. Error:", e)

        if user_id:
            print("Fetching personalized experiences and projects...")

            # Fetch experiences
            exp_res = requests.get(
                f"{SUPABASE_URL}/rest/v1/experiences?user_id=eq.{user_id}",
                headers=supabase_headers
            )
            if exp_res.status_code == 200:
                experiences = exp_res.json()

            # Fetch projects
            proj_res = requests.get(
                f"{SUPABASE_URL}/rest/v1/projects?user_id=eq.{user_id}",
                headers=supabase_headers
            )
            if proj_res.status_code == 200:
                projects = proj_res.json()

            print(f"Loaded {len(experiences)} experiences, {len(projects)} projects.")
        else:
            print("Guest user — skipping saved experiences/projects.")

        # -------------------------
        # Rewrite using Gemini
        # -------------------------
        print("Rewriting resume...")
        tailored_resume = rewrite_service.rewrite_resume_with_gemini(
            latex_resume_final,
            job_description,
            keywords,
            experiences=experiences,
            projects=projects
        )

        # -------------------------
        # Score rewritten resume
        # -------------------------
        print("ATS Scoring...")
        ats_score = score_service.compute_ats_score(
            job_description,
            tailored_resume,
            keywords
        )

        print("Done")
        return {
            "tailored_resume": tailored_resume,
            "ats_score": ats_score,
            "keywords": keywords,
            "job_description": job_description
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


@router.post("/compile", tags=["Resume"])
async def compile_latex(latex_content: str = Form(...)):
    try:
        latex_content = latex_content.strip()
        latex_content = re.sub(
            r"^```[a-zA-Z]*|```$",
            "",
            latex_content,
            flags=re.MULTILINE
        ).strip()

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
        cleaned_latex = re.sub(
            r"^```[a-zA-Z]*|```$",
            "",
            cleaned_latex,
            flags=re.MULTILINE
        ).strip()

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
