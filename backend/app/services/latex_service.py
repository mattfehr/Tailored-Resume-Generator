import re
from textwrap import dedent

SECTION_HEADERS = [
    "Education", "Experience", "Projects",
    "Technical Skills", "Skills", "Awards",
    "Certifications", "Research", "Leadership"
]

# ---------- helpers

def latex_escape(s: str) -> str:
    if not s:
        return ""
    # Minimal escaping (enough for emails/links/parentheses)
    s = s.replace("\\", r"\\").replace("&", r"\&").replace("%", r"\%")
    s = s.replace("$", r"\$").replace("#", r"\#").replace("_", r"\_")
    s = s.replace("{", r"\{").replace("}", r"\}").replace("~", r"\textasciitilde{}")
    s = s.replace("^", r"\textasciicircum{}")
    return s

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d \-\(\)]{7,}\d)")
URL_RE   = re.compile(r"(https?://[^\s]+)")
LINKEDIN_RE = re.compile(r"(https?://(www\.)?linkedin\.com/in/[^\s]+)", re.I)
GITHUB_RE   = re.compile(r"(https?://(www\.)?github\.com/[^\s]+)", re.I)

def extract_contact_info(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Heuristic: first non-empty line with letters as the name
    name = next((l for l in lines[:5] if re.search(r"[A-Za-z]{2,}", l)), "Candidate Name")

    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)

    return {
        "name": latex_escape(name),
        "email": latex_escape(email.group(0)) if email else "",
        "phone": latex_escape(phone.group(0)) if phone else "",
        "linkedin": latex_escape(linkedin.group(0)) if linkedin else "",
        "github": latex_escape(github.group(0)) if github else ""
    }

def to_resume_items(block: str) -> str:
    """
    Turn lines that look like bullets into Jake-styled bullet list.
    Recognizes lines starting with -, •, or *.
    Non-bullet paragraphs pass through unchanged.
    """
    lines = [l.strip() for l in block.splitlines()]
    bullet_lines, out, open_list = [], [], False

    def flush_list():
        nonlocal bullet_lines, out, open_list
        if bullet_lines:
            out.append(r"\resumeItemListStart")
            for b in bullet_lines:
                out.append(rf"\resumeItem{{{latex_escape(b)}}}")
            out.append(r"\resumeItemListEnd")
            bullet_lines = []
        open_list = False

    for l in lines:
        if re.match(r"^(\-|\*|•)\s+", l):
            bullet_lines.append(re.sub(r"^(\-|\*|•)\s+", "", l))
            open_list = True
        elif l:
            if open_list:
                flush_list()
            out.append(latex_escape(l))
    if open_list:
        flush_list()

    return "\n".join(out) if out else latex_escape(block.strip())

def extract_sections(text: str) -> dict:
    """
    Detect common resume sections, return {Section: content}.
    """
    sections = {}
    pattern = rf"({'|'.join(SECTION_HEADERS)})(.*?)(?=(?:{'|'.join(SECTION_HEADERS)}|$))"
    for m in re.finditer(pattern, text, re.I | re.S):
        header = m.group(1).strip().title()
        content = re.sub(r"\n{2,}", "\n", m.group(2)).strip()
        sections[header] = content
    return sections

# ---------- template

JAKE_BASE = dedent(r"""
% Jake-styled resume (header slimmed; body intact)
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

\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}
\addtolength{\oddsidemargin}{-0.5in}\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}\addtolength{\topmargin}{-.5in}\addtolength{\textheight}{1.0in}

\urlstyle{same}\raggedbottom\raggedright\setlength{\tabcolsep}{0in}
\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]
\pdfgentounicode=1

\newcommand{\resumeItem}[1]{\item\small{{#1 \vspace{-2pt}}}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

\begin{center}
    \textbf{\Huge \scshape {NAME}} \\ \vspace{1pt}
    \small {CONTACT_LINE}
\end{center}

\section{Education}
{EDU}

\section{Experience}
{EXP}

\section{Projects}
{PROJ}

\section{Technical Skills}
{SKILLS}

\end{document}
""")

def fill_jake_template_from_text(text: str) -> str:
    meta = extract_contact_info(text)
    sections = extract_sections(text)

    edu = to_resume_items(sections.get("Education", ""))
    exp = to_resume_items(sections.get("Experience", ""))
    proj = to_resume_items(sections.get("Projects", ""))
    skills = to_resume_items(sections.get("Technical Skills", sections.get("Skills", "")))

    contact_bits = [meta["phone"], meta["email"]]
    if meta["linkedin"]: contact_bits.append(meta["linkedin"])
    if meta["github"]:   contact_bits.append(meta["github"])
    contact_line = " | ".join(filter(None, contact_bits)) or "Contact Info Here"

    return (JAKE_BASE
            .replace("{NAME}", meta["name"] or "Candidate Name")
            .replace("{CONTACT_LINE}", latex_escape(contact_line))
            .replace("{EDU}", edu or "")
            .replace("{EXP}", exp or "")
            .replace("{PROJ}", proj or "")
            .replace("{SKILLS}", skills or "")
            ).strip()

# ---------- public API

def wrap_in_jake_template(text: str) -> str:
    """Build a Jake-style LaTeX resume from plain text (PDF/DOCX extraction)."""
    return fill_jake_template_from_text(text)

def clean_and_validate_latex(latex_code: str) -> str:
    """If the input isn’t LaTeX, wrap it; otherwise sanitize."""
    latex_code = (latex_code or "").strip()
    if "\\begin{document}" not in latex_code or "\\end{document}" not in latex_code:
        latex_code = wrap_in_jake_template(latex_code)
    latex_code = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", latex_code)
    return latex_code.strip()
