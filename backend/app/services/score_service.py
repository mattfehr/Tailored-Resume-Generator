from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def keyword_match_score(keywords, resume_text):
    resume_lower = resume_text.lower()
    hits = 0
    
    for kw in keywords:
        if kw.lower() in resume_lower:
            hits += 1

    if len(keywords) == 0:
        return 0.0

    return hits / len(keywords)

def semantic_similarity(job_description, resume_text):
    vect = TfidfVectorizer(stop_words="english")
    tfidf = vect.fit_transform([job_description, resume_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return score

def compute_ats_score(job_description, resume_text, keywords):
    kw_score = keyword_match_score(keywords, resume_text)
    semantic = semantic_similarity(job_description, resume_text)

    final = (0.6 * kw_score) + (0.4 * semantic)
    return round(final * 100, 2)
