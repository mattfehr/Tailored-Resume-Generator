from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from app.services import parsing_service, latex_service, keyword_service, rewrite_service, score_service
import subprocess
import tempfile
import shutil
from pathlib import Path

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

@router.post("/compile", tags=["Resume"])
async def compile_latex(latex_content: str = Form(...)):
    """
    Compiles LaTeX into a PDF and returns it as a downloadable file.
    Accepts raw LaTeX via form field 'latex_content'.
    Automatically cleans Markdown fences and unsupported includes.
    """
    try:
        import re
        # 🧹 Sanitize LaTeX content
        latex_content = latex_content.strip()

        # Remove Markdown-style code fences like ```latex ... ```
        latex_content = re.sub(r"^```[a-zA-Z]*|```$", "", latex_content, flags=re.MULTILINE).strip()

        # Remove Overleaf-only includes that break local compilation
        latex_content = latex_content.replace("\\input{glyphtounicode}", "% Removed glyphtounicode for local compilation")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_path = tmpdir_path / "resume.tex"
            pdf_path = tmpdir_path / "resume.pdf"
            log_path = tmpdir_path / "compile.log"

            tex_path.write_text(latex_content, encoding="utf-8")

            # Prefer latexmk (more robust), else fallback to pdflatex
            if shutil.which("latexmk"):
                cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", tex_path.name]
            else:
                cmd = ["pdflatex", "-interaction=nonstopmode", tex_path.name]

            # Increase timeout slightly to handle first-time MiKTeX installs
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=120
            )

            log_output = proc.stdout.decode("utf-8", errors="ignore")
            log_path.write_text(log_output)

            if not pdf_path.exists():
                # Print last few lines of log for debugging
                tail = "\n".join(log_output.splitlines()[-40:])
                print("===== LATEX ERROR LOG =====")
                print(tail)
                print("===========================")
                raise HTTPException(status_code=422, detail=f"PDF compilation failed.\n{tail}")

            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename="tailored_resume.pdf"
            )

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="LaTeX compilation timed out (possibly installing packages).")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compiling LaTeX: {e}")
