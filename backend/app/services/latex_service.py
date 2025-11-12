import re
from textwrap import dedent

# Common resume sections to detect in plain text
SECTION_HEADERS = [
    "Education",
    "Experience",
    "Projects",
    "Skills",
    "Technical Skills",
    "Awards",
    "Certifications",
    "Research",
    "Leadership",
]


def extract_sections(text: str):
    """
    Extract sections from plain text by detecting known headers.
    Returns a dict like {"Education": "...", "Experience": "..."}.
    """
    sections = {}
    pattern = rf"({'|'.join(SECTION_HEADERS)})(.*?)(?=(?:{'|'.join(SECTION_HEADERS)}|$))"
    matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)

    for match in matches:
        header = match.group(1).strip().title()
        content = re.sub(r"\n{2,}", "\n", match.group(2)).strip()
        sections[header] = content

    return sections


def fill_jake_template(sections: dict) -> str:
    """
    Fills Jake's LaTeX template with extracted section content.
    Missing sections are skipped gracefully.
    """

    # Use safe fallbacks
    edu = sections.get("Education", "N/A")
    exp = sections.get("Experience", "")
    proj = sections.get("Projects", "")
    skills = sections.get("Skills", sections.get("Technical Skills", ""))

    # --- Jake's resume LaTeX template (trimmed to essential structure) ---
    template = dedent(r"""
    %-------------------------
    % Resume in LaTeX (based on Jake Gutierrez)
    %-------------------------

    \documentclass[letterpaper,11pt]{article}

    \usepackage{latexsym}
    \usepackage[empty]{fullpage}
    \usepackage{titlesec}
    \usepackage{marvosym}
    \usepackage[usenames,dvipsnames]{color}
    \usepackage{enumitem}
    \usepackage[hidelinks]{hyperref}
    \usepackage{fancyhdr}
    \usepackage[english]{babel}
    \usepackage{tabularx}
    \input{glyphtounicode}

    \pagestyle{fancy}
    \fancyhf{}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}

    \addtolength{\oddsidemargin}{-0.5in}
    \addtolength{\evensidemargin}{-0.5in}
    \addtolength{\textwidth}{1in}
    \addtolength{\topmargin}{-.5in}
    \addtolength{\textheight}{1.0in}

    \urlstyle{same}
    \raggedbottom
    \raggedright
    \setlength{\tabcolsep}{0in}

    \titleformat{\section}{
      \vspace{-4pt}\scshape\raggedright\large
    }{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

    \pdfgentounicode=1

    %-------------------------------------------
    \begin{document}

    %----------HEADING----------
    \begin{center}
        \textbf{\Huge \scshape Candidate Name} \\ \vspace{1pt}
        \small Contact Info Here \\
        \href{mailto:example@email.com}{example@email.com} $|$ 
        \href{https://linkedin.com/in/...}{linkedin.com/in/...} $|$
        \href{https://github.com/...}{github.com/...}
    \end{center}

    %-----------EDUCATION-----------
    \section{Education}
    {EDU_CONTENT}

    %-----------EXPERIENCE-----------
    \section{Experience}
    {EXP_CONTENT}

    %-----------PROJECTS-----------
    \section{Projects}
    {PROJ_CONTENT}

    %-----------TECHNICAL SKILLS-----------
    \section{Technical Skills}
    {SKILLS_CONTENT}

    \end{document}
    """)

    # Inject content
    filled = (
        template
        .replace("{EDU_CONTENT}", edu)
        .replace("{EXP_CONTENT}", exp)
        .replace("{PROJ_CONTENT}", proj)
        .replace("{SKILLS_CONTENT}", skills)
    )

    return filled.strip()


def wrap_in_jake_template(text: str) -> str:
    """
    Wrap plain extracted text into Jake's LaTeX resume structure.
    """
    sections = extract_sections(text)
    return fill_jake_template(sections)


def clean_and_validate_latex(latex_code: str) -> str:
    """
    Clean LaTeX or text input and ensure it's compilable.
    - If plain text, wrap it in Jake's LaTeX template.
    - If valid LaTeX, sanitize and return as-is.
    """
    latex_code = latex_code.strip()

    # Detect if it already looks like LaTeX
    if not ("\\begin{document}" in latex_code and "\\end{document}" in latex_code):
        latex_code = wrap_in_jake_template(latex_code)

    # Remove non-printable chars
    latex_code = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", latex_code)
    latex_code = re.sub(r"[^\S\r\n]+", " ", latex_code)

    return latex_code.strip()
