import re

def wrap_in_latex_structure(text: str) -> str:
    """Wrap extracted text in a minimal LaTeX structure."""
    return f"""
\\documentclass[11pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{enumitem}}
\\begin{{document}}
{text}
\\end{{document}}
"""

def clean_and_validate_latex(latex_code: str) -> str:
    """Clean uploaded LaTeX and ensure it's compilable."""
    latex_code = latex_code.strip()
    if not ("\\begin{document}" in latex_code and "\\end{document}" in latex_code):
        latex_code = wrap_in_latex_structure(latex_code)
    # Remove non-printable chars
    latex_code = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", latex_code)
    return latex_code
