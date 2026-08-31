from typing import Dict, Any, Tuple
from app.services.similarity_module import SimilarityModule

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class TextSimilarityEngine:
    def __init__(self):
        self.templates = SimilarityModule.KNOWN_SCAM_TEMPLATES
        self.vectorizer = None
        self.tfidf_matrix = None
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(self.templates)

    def find_most_similar(self, text: str) -> Tuple[float, str]:
        if not SKLEARN_AVAILABLE:
            return 0.0, ""
            
        vec = self.vectorizer.transform([text.lower()])
        sims = cosine_similarity(vec, self.tfidf_matrix)[0]
        max_idx = sims.argmax()
        return float(sims[max_idx]), self.templates[max_idx]
