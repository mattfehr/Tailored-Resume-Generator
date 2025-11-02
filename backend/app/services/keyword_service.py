from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

# Load once at startup
nlp = spacy.load("en_core_web_sm")

def extract_keywords(job_description, max_features=15):
    """Extract key terms and named entities from job description."""
    tfidf = TfidfVectorizer(stop_words="english", max_features=max_features)
    tfidf.fit([job_description])
    keywords = set(tfidf.get_feature_names_out())

    doc = nlp(job_description)
    entities = {ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE", "SKILL", "WORK_OF_ART"]}

    return list(keywords.union(entities))
