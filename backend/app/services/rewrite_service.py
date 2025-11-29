import google.generativeai as genai
from app.config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def rewrite_resume_with_gemini(
    latex_resume,
    job_description,
    keywords,
    experiences=None,
    projects=None
):
    """
    Rewrite a LaTeX resume to align with a job description.
    Uses saved experiences and projects for personalization when provided.
    """
    
    # Ensure lists are never None
    experiences = experiences or []
    projects = projects or []

    # Format experiences for prompt
    formatted_experiences = "\n".join(
        f"- {exp.get('role', '')} at {exp.get('company', '')} "
        f"({exp.get('start_date', '')} → {exp.get('end_date', 'Present')}): "
        + "; ".join(exp.get('bullets', []))
        for exp in experiences
    ) or "None provided"

    # Format projects for prompt
    formatted_projects = "\n".join(
        f"- {proj.get('name', '')} "
        f"({proj.get('start_date', '')} → {proj.get('end_date', 'Present')}), "
        f"Tech: {', '.join(proj.get('tech_stack', []))}. "
        f"Bullets: {'; '.join(proj.get('bullets', []))}"
        for proj in projects
    ) or "None provided"

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
- Preserve one-page length.
- Naturally integrate these keywords only when relevant:
  {", ".join(keywords)}
- DO NOT invent new experiences or projects.
- If helpful and relevant, integrate or reference details from the user's saved experiences and projects to better match the job description.
- ONLY use saved experiences/projects when they authentically match the job duties or keywords.

USER'S SAVED EXPERIENCES:
{formatted_experiences}

USER'S SAVED PROJECTS:
{formatted_projects}

BEGIN NOW.

Job Description:
\"\"\"{job_description}\"\"\"

Original LaTeX Resume:
\"\"\"{latex_resume}\"\"\"
"""

    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()
