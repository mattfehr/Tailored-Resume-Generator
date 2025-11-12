import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def rewrite_resume_with_gemini(latex_resume, job_description, keywords):
    """
    Rewrite a LaTeX resume to align with a job description.
    Keeps it one page, same format, and integrates provided keywords naturally.
    """
    prompt = f"""
You are an expert technical resume editor who edits LaTeX resumes for software and AI roles.

Your task:
- Rewrite the LaTeX resume content to align closely with the provided job description.
- Maintain the original LaTeX structure, formatting, and layout.
- Keep the resume one page long.
- Modify **only** the text content between \\begin{{document}} and \\end{{document}}.
- Naturally integrate the following keywords **only when contextually relevant**:
  {', '.join(keywords)}
- Emphasize technical skills, tools, and measurable achievements most relevant to the job.
- Strengthen phrasing using concise, action-driven, and professional language.
- Where possible, quantify impact or results (e.g., “reduced load time by 30%” instead of “improved performance”).
- Do NOT invent new experiences, companies, or technologies — only reword and emphasize existing content.
- Do NOT add extra sections, metadata, or comments.
- IMPORTANT: Return **only the raw LaTeX source code**.
- Do NOT wrap it in markdown formatting.
- Do NOT include triple backticks, language tags (like ```latex), or any other fencing.
- Your entire response must begin with a LaTeX comment or \\documentclass and end with \\end{{document}}.

Job Description:
\"\"\"{job_description}\"\"\"

Original LaTeX Resume:
\"\"\"{latex_resume}\"\"\"
"""

    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()
