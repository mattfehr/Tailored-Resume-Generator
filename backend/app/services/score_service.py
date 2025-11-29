from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
import re


# ---------------------------
# HELPERS
# ---------------------------

def normalize(text: str):
    """Lowercase + remove punctuation for safer matching."""
    return re.sub(r"[^a-z0-9+]+", " ", text.lower())


def fuzzy_match(a: str, b: str, threshold=0.75):
    """Return True if strings are similar enough."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def keyword_match_score(keywords, resume_text):
    resume_norm = normalize(resume_text)
    resume_tokens = set(resume_norm.split())

    hits = 0

    for kw in keywords:
        kw_norm = normalize(kw)

        # 1. Direct substring match
        if kw_norm in resume_norm:
            hits += 1
            continue

        # 2. Exact token match
        for token in resume_tokens:
            if kw_norm == token:
                hits += 1
                break

        # 3. Fuzzy match
        else:
            for token in resume_tokens:
                if fuzzy_match(kw_norm, token):
                    hits += 1
                    break

    if len(keywords) == 0:
        return 0.0

    return hits / len(keywords)


def semantic_similarity(job_description, resume_text):
    vect = TfidfVectorizer(stop_words="english")
    tfidf = vect.fit_transform([job_description, resume_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return score


# ---------------------------
# FINAL ATS COMPUTATION
# ---------------------------

def compute_ats_score(job_description, resume_text, keywords):
    # Keyword score (primary)
    kw_score = keyword_match_score(keywords, resume_text)

    # Semantic relevance (TF-IDF boosted to give more impact)
    semantic = semantic_similarity(job_description, resume_text)
    semantic_boosted = min(semantic * 1.8, 1.0)   # <-- UPDATE #1

    # Weighted final score (keywords more important)
    final = (0.75 * kw_score) + (0.25 * semantic_boosted)   # <-- UPDATE #2

    # Clamp to 0–100%
    final = max(0, min(final, 1.0))

    return round(final * 100, 2)
