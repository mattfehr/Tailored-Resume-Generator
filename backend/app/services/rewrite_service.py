import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def rewrite_resume_with_gemini(latex_resume, job_description, keywords):
    """
    Rewrite a LaTeX resume to align with a job description.
    Keeps it one page, same format, and integrates provided keywords naturally.
    """
    prompt = f"""
You are an expert LaTeX resume editor. You will rewrite the content of a LaTeX resume while ensuring that the final output compiles successfully on latexonline.cc.

IMPORTANT — STRICT LATEX RULES (follow EXACTLY):

1. You MUST NOT modify ANYTHING in the preamble (everything before \\begin{{document}}).
2. You MUST preserve ALL existing LaTeX commands and macros exactly as they are.
3. You MUST NOT introduce any new LaTeX commands, new macros, or new environments.
4. You MUST NOT use Markdown formatting (NO backticks, NO ```).
5. Only modify the text content BETWEEN \\begin{{document}} and \\end{{document}}.
6. Do NOT add icons, tables, custom environments, or unsupported packages.
7. Bullet points must use ONLY the existing commands provided in the original LaTeX (e.g., \\resumeItem, \\resumeItemListStart, etc.).
8. If the original resume uses custom commands, you must use them EXACTLY as written and NEVER invent new ones.
9. Do NOT add \\resume, \\resumeSection, \\resumeSubheading, or any unrecognized LaTeX commands.
10. Output MUST be fully compilable LaTeX compatible with latexonline.cc.

YOUR TASK:
- Rewrite only the *content* of the resume so it strongly aligns with the provided job description.
- Keep the structure, layout, macros, and sections exactly the same.
- Preserve the one-page length.
- Naturally integrate these keywords only when relevant:
  {", ".join(keywords)}
- Emphasize technical accomplishments, quantified impact, and role-relevant experience.
- Do NOT invent new jobs, responsibilities, or technologies.
- Return **only the raw LaTeX source code**, with:
    - the original preamble unchanged
    - revised content inside the document body
    - ending with \\end{{document}}

BEGIN NOW.

Job Description:
\"\"\"{job_description}\"\"\"\n
Original LaTeX Resume:
\"\"\"{latex_resume}\"\"\"\n
"""

    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()
