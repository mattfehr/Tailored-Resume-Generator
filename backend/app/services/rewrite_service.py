import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def rewrite_resume_with_gemini(latex_resume, job_description, keywords):
    """Rewrite the LaTeX resume using Gemini, keeping structure intact."""
    prompt = f"""
You are a LaTeX-aware resume rewriting assistant.
Rewrite the LaTeX resume below to better align with the job description.
Only modify text content between \\begin{{document}} and \\end{{document}}.
Preserve formatting and do not fabricate new information.

Job Description:
{job_description}

Important Keywords: {', '.join(keywords)}

LaTeX Resume:
{latex_resume}
"""

    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()
