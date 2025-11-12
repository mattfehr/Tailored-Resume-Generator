from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import re
import google.generativeai as genai
from app.config import Config

nlp = spacy.load("en_core_web_sm")

# Common technical terms and patterns to prioritize
TECH_TERMS = {
    "python", "java", "javascript", "typescript", "react", "node", "express",
    "fastapi", "flask", "django", "sql", "postgresql", "mysql", "mongodb", "nosql",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git", "api", "rest",
    "graphql", "linux", "tensorflow", "pytorch", "machine learning", "deep learning",
    "nlp", "data analysis", "computer vision", "backend", "frontend", "devops",
    "cloud", "bash", "shell", "pipelines", "spark", "hadoop", "kafka", "airflow"
}

# Common irrelevant words and HR/soft-skill terms
BLACKLIST = {
    "team", "company", "role", "culture", "impact", "candidate", "environment",
    "driven", "motivated", "communication", "fast", "excited", "humble",
    "growing", "good", "great", "ability", "smart", "challenge", "job",
    "apply", "internship", "position", "collaboration", "learning", "people"
}


def extract_relevant_sections(job_text: str) -> str:
    """Extract only likely relevant sections (skills/responsibilities)."""
    text = job_text.replace("\n", " ").strip()
    pattern = r"(responsibilit(?:y|ies)|requirement(?:s)?|qualification(?:s)?|skills?|what you['’]ll do|looking for)"
    matches = list(re.finditer(pattern, text, re.IGNORECASE))
    return text[matches[0].start():] if matches else text


def extract_keywords(job_description: str, max_features: int = 25):
    """Extract meaningful, technical keywords from job description."""
    focused_text = extract_relevant_sections(job_description)

    # Step 1: TF-IDF extraction
    tfidf = TfidfVectorizer(stop_words="english", max_features=max_features)
    tfidf.fit([focused_text])
    tfidf_keywords = set(tfidf.get_feature_names_out())

    # Step 2: spaCy NER & noun filtering
    doc = nlp(focused_text)
    spacy_keywords = {
        token.text.lower()
        for token in doc
        if token.pos_ in {"NOUN", "PROPN"} and len(token.text) > 2
    }

    # Step 3: Combine + filter
    combined = tfidf_keywords.union(spacy_keywords)
    filtered = {
        kw for kw in combined
        if kw.lower() not in BLACKLIST
        and not kw.isdigit()
        and len(kw) > 2
    }

    # Step 4: Prioritize tech terms if present
    tech_related = [kw for kw in filtered if kw.lower() in TECH_TERMS]
    general_terms = [kw for kw in filtered if kw.lower() not in TECH_TERMS]

    # Merge, keeping tech ones first
    final_keywords = tech_related + general_terms
    return sorted(set(final_keywords))[:max_features]


def extract_skills_with_gemini(job_description: str):
    """Use Gemini for refined skill extraction."""
    prompt = f"""
    From the job description below, extract **only the technical hard skills, tools,
    frameworks, and technologies** (e.g., Python, SQL, React, AWS, CI/CD).
    Exclude personality traits, adjectives, and soft skills like communication or teamwork.
    Return a comma-separated list of up to 15 skills.

    Job Description:
    {job_description}
    """
    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return [skill.strip() for skill in response.text.split(",") if len(skill.strip()) > 1]
