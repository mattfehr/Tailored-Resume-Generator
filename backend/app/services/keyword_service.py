from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import re
import google.generativeai as genai
from app.config import Config

nlp = spacy.load("en_core_web_sm")

def extract_relevant_sections(job_text: str) -> str:
    """Extracts only sections likely describing skills or requirements."""
    # Normalize spacing
    text = job_text.replace("\n", " ").strip()

    # Look for specific section keywords
    pattern = r"(responsibilit(?:y|ies)|requirement(?:s)?|qualification(?:s)?|skills?|what you['’]ll do|what we['’]re looking for)"
    matches = list(re.finditer(pattern, text, re.IGNORECASE))

    if not matches:
        return text  # fallback if no section headers found

    # Take from first relevant section onward
    start_idx = matches[0].start()
    return text[start_idx:]

def extract_keywords(job_description, max_features=20):
    """Extract meaningful keywords and entities from job description."""
    # Step 1: focus on relevant sections
    focused_text = extract_relevant_sections(job_description)

    # Step 2: TF-IDF keyword extraction
    tfidf = TfidfVectorizer(stop_words="english", max_features=max_features)
    tfidf.fit([focused_text])
    keywords = set(tfidf.get_feature_names_out())

    # Step 3: Entity recognition for technical terms and skills
    doc = nlp(focused_text)
    entities = {
        ent.text.strip()
        for ent in doc.ents
        if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE", "WORK_OF_ART"]
        and len(ent.text.split()) <= 3  # avoid long entity phrases
    }

    # Step 4: Filter out generic HR words
    blacklist = {
        "team", "company", "location", "role", "culture", "impact", "candidate",
        "responsibilities", "requirements", "internship", "job", "apply"
    }

    filtered = [kw for kw in keywords.union(entities) if kw.lower() not in blacklist]
    return sorted(filtered)

def extract_skills_with_gemini(job_description):
    prompt = f"""
    Extract a comma-separated list of the top 10 technical and soft skills 
    required in the following job description. Return only the skill names.

    {job_description}
    """
    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return [skill.strip() for skill in response.text.split(",")]
