from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_ats_score(job_description, resume_text):
    """Compute similarity between job description and resume text."""
    vect = TfidfVectorizer(stop_words="english")
    tfidf = vect.fit_transform([job_description, resume_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100, 2)
