from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import re
import google.generativeai as genai
from app.config import Config

nlp = spacy.load("en_core_web_sm")

# Priority technical terms (hard skills)
TECH_TERMS = {
    "python", "java", "javascript", "typescript", "react", "node", "express",
    "fastapi", "flask", "django", "sql", "postgresql", "mysql", "mongodb",
    "nosql", "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git",
    "api", "rest", "graphql", "linux", "tensorflow", "pytorch",
    "machine learning", "deep learning", "nlp", "data analysis",
    "computer vision", "backend", "frontend", "devops", "cloud",
    "bash", "shell", "pipelines", "spark", "hadoop", "kafka", "airflow"
}

# Words to exclude (generic nouns, soft skills, HR fluff)
BLACKLIST = {
    "team", "company", "role", "culture", "impact", "candidate", "environment",
    "driven", "motivated", "communication", "fast", "excited", "humble",
    "growing", "good", "great", "ability", "smart", "challenge", "job",
    "apply", "internship", "position", "collaboration", "learning", "people",
    "experience", "background", "responsibilities", "requirements"
}

def extract_relevant_sections(job_text: str) -> str:
    """Focus keyword extraction on relevant JD sections."""
    text = job_text.replace("\n", " ").strip()
    pattern = r"(responsibilit(?:y|ies)|requirement(?:s)?|qualification(?:s)?|skills?|what you['’]ll do|looking for)"
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    return text[matches[0].start():] if matches else text


def extract_skills_with_gemini(job_description: str):
    """Use Gemini to extract only hard skills/tools."""
    prompt = f"""
    Extract ONLY technical hard skills, tools, frameworks, and technologies 
    from the following job description.

    Do NOT include:
    - Soft skills (communication, teamwork, problem-solving)
    - Generic verbs (develop, build, create)
    - HR terms (role, responsibility, candidate, culture)
    - Adjectives (passionate, motivated, fast-paced)
    - Generic nouns (experience, environment)

    Return a comma-separated list of up to 15 skills.

    Job Description:
    {job_description}
    """

    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Convert Gemini output to Python list
    return [skill.strip() for skill in text.split(",") if len(skill.strip()) > 1]


def extract_keywords(job_description: str, max_features: int = 25):
    """
    Hybrid keyword extraction:
      1. Try Gemini (best results)
      2. Fall back to TF-IDF + spaCy if Gemini fails
    """

    # -------------------- GEMINI EXTRACTION --------------------
    try:
        skills = extract_skills_with_gemini(job_description)
        # basic sanity filter
        clean_skills = [
            kw for kw in skills
            if kw.lower() not in BLACKLIST and len(kw) > 1
        ]
        if len(clean_skills) >= 3:
            return clean_skills[:max_features]
    except Exception as e:
        print("Gemini skill extraction failed:", e)

    # -------------------- FALLBACK: TF-IDF + spaCy --------------------
    print("Using fallback TF-IDF extraction...")

    focused = extract_relevant_sections(job_description)

    tfidf = TfidfVectorizer(stop_words="english", max_features=max_features)
    tfidf.fit([focused])
    tfidf_keywords = set(tfidf.get_feature_names_out())

    doc = nlp(focused)
    spacy_keywords = {
        token.text.lower()
        for token in doc
        if token.pos_ in {"NOUN", "PROPN"} and len(token.text) > 2
    }

    combined = tfidf_keywords.union(spacy_keywords)

    # Remove junk and blacklist
    filtered = {
        kw for kw in combined
        if kw.lower() not in BLACKLIST
        and not kw.isdigit()
        and len(kw) > 2
    }

    # Prioritize tech terms
    tech_related = [kw for kw in filtered if kw.lower() in TECH_TERMS]
    general_terms = [kw for kw in filtered if kw.lower() not in TECH_TERMS]

    final_keywords = tech_related + general_terms

    return sorted(set(final_keywords))[:max_features]
