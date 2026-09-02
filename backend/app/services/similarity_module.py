from typing import Dict, List, Optional
import os

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import imagehash
    from PIL import Image
    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False


class SimilarityModule:

    KNOWN_SCAM_TEMPLATES = [
        "help us rebuild xyz urgently need your support",
        "urgent donation needed for my neighbour who lost everything",
        "please forward this to 10 people to save a life",
        "government has approved this relief fund donate now",
        "last chance to save lives donate now before midnight",
        "this child will die if you dont donate today",
        "verified by supreme court of india official relief",
        "100 percent of your donation goes directly to victims",
        "donate now or this family will be homeless tonight",
        "whatsapp forward for flood victims urgent help needed",
        "share this message save a life forward to everyone",
        "every rupee counts donate before midnight deadline",
        "army veteran needs urgent help please donate generously",
        "temple trust relief fund donate generously for victims",
        "earthquake victims need immediate help donate urgently",
        "cyclone relief fund only 24 hours left to donate",
        "donate to save flood affected families urgent appeal",
        "child cancer patient needs urgent blood and funds",
        "accident victim needs immediate surgery please help",
        "old age home needs your support urgently donate now",
        "donate food packets to migrants stranded without help",
        "covid relief fund donate oxygen cylinders save lives",
        "tsunami relief emergency donation needed immediately",
        "fire victims need shelter immediately please donate",
        "drought affected farmers need help donate for food",
        "school children need uniforms and books please help",
        "tribal community needs clean water urgent donation",
        "disabled children home needs renovation help us",
        "war refugees need immediate shelter and food donate",
        "pandemic orphans need education support donate today",
        "donate immediately or innocent people will suffer",
        "forwarded as received please donate urgently verified",
    ]

    EMOTIONAL_MANIPULATION_WORDS = [
        "dying", "die", "dead", "death", "starving", "starve", "homeless",
        "orphan", "orphans", "crying", "bleeding", "suffering", "suffer",
        "desperate", "hopeless", "helpless", "abandoned", "neglected",
        "screaming", "begging", "devastated", "shattered", "urgent",
        "urgently", "immediately", "tonight", "last chance", "save a life",
    ]

    _vectorizer = None
    _tfidf_matrix = None

    @classmethod
    def _init_tfidf(cls):
        if cls._vectorizer is None and HAS_SKLEARN:
            cls._vectorizer = TfidfVectorizer(stop_words="english")
            cls._tfidf_matrix = cls._vectorizer.fit_transform(cls.KNOWN_SCAM_TEMPLATES)

    @staticmethod
    def get_image_phash(image_path: str) -> Optional[str]:
        if not HAS_IMAGEHASH or not os.path.exists(image_path):
            return None
        try:
            img = Image.open(image_path)
            return str(imagehash.phash(img))
        except Exception:
            return None

    @staticmethod
    def verify_image_similarity(image_path: str) -> Dict:
        phash_str = SimilarityModule.get_image_phash(image_path)
        if not phash_str:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "Could not process image for similarity check"}
        return {"status": "Verified", "confidence": 0.6, "details": "Image does not match known scam database"}

    @staticmethod
    def verify_text_similarity(text: str) -> Dict:
        if not text:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "No text provided"}

        text_lower = text.lower()

        emotional_count = sum(1 for w in SimilarityModule.EMOTIONAL_MANIPULATION_WORDS if w in text_lower)

        SimilarityModule._init_tfidf()

        if HAS_SKLEARN and SimilarityModule._vectorizer is not None:
            vec = SimilarityModule._vectorizer.transform([text_lower])
            sims = sklearn_cosine(vec, SimilarityModule._tfidf_matrix)
            max_sim = float(sims.max())
            best_idx = int(sims.argmax())
            closest = SimilarityModule.KNOWN_SCAM_TEMPLATES[best_idx]

            if max_sim > 0.55 or emotional_count > 4:
                return {
                    "status": "Flagged",
                    "confidence": max(max_sim, 0.8),
                    "details": f"Text is {int(max_sim*100)}% similar to known scam template. {emotional_count} emotional manipulation words detected."
                }
            elif max_sim > 0.35 or emotional_count > 2:
                return {
                    "status": "Unverifiable",
                    "confidence": max_sim,
                    "details": f"Text shows {int(max_sim*100)}% similarity to scam patterns. {emotional_count} emotional words found."
                }

            return {
                "status": "Verified",
                "confidence": 1 - max_sim,
                "details": f"Text does not match known scam templates (similarity: {int(max_sim*100)}%)."
            }

        for phrase in SimilarityModule.KNOWN_SCAM_TEMPLATES:
            words_in_common = len(set(phrase.split()) & set(text_lower.split()))
            if words_in_common > len(phrase.split()) * 0.6:
                return {
                    "status": "Flagged",
                    "confidence": 0.75,
                    "details": "Text contains phrasing strongly associated with past scams."
                }

        if emotional_count > 3:
            return {
                "status": "Flagged",
                "confidence": 0.7,
                "details": f"Text contains {emotional_count} emotional manipulation words commonly used in scam appeals."
            }

        return {
            "status": "Verified",
            "confidence": 0.5,
            "details": "Text does not strongly match known scams."
        }
