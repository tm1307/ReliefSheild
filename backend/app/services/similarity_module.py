import imagehash
from PIL import Image
import os
from typing import Dict, List, Optional

class SimilarityModule:
    """
    Checks for recycled appeals (text and images) against a database of known scams.
    """
    
    KNOWN_SCAM_HASHES = [
        "d879f879f879f879", # example hash
        "a1b2c3d4e5f60718"
    ]
    
    @staticmethod
    def get_image_phash(image_path: str) -> Optional[str]:
        """
        Calculate perceptual hash of an image for similarity comparison.
        """
        if not os.path.exists(image_path):
            return None
            
        try:
            img = Image.open(image_path)
            hash_val = imagehash.phash(img)
            return str(hash_val)
        except Exception as e:
            print(f"Error hashing image: {e}")
            return None
            
    @staticmethod
    def verify_image_similarity(image_path: str) -> Dict:
        """
        Check if the image closely matches a known scam.
        """
        phash_str = SimilarityModule.get_image_phash(image_path)
        if not phash_str:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "Could not hash image"}
            
        current_hash = imagehash.hex_to_hash(phash_str)
        
        for known_hash_str in SimilarityModule.KNOWN_SCAM_HASHES:
            known_hash = imagehash.hex_to_hash(known_hash_str)
            
            if current_hash - known_hash <= 5:
                return {
                    "status": "Flagged",
                    "confidence": 0.95,
                    "details": f"Image is highly similar to a known scam (Distance: {current_hash - known_hash})"
                }
                
        return {
            "status": "Verified",
            "confidence": 0.6,
            "details": "Image does not match known scam database"
        }
        
    @staticmethod
    def verify_text_similarity(text: str) -> Dict:
        """
        Check if text closely matches a known scam.
        In a full implementation, this uses pgvector to find cosine similarity of embeddings.
        """
        if not text:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "No text provided"}
            
        known_scam_phrases = ["help us rebuild xyz", "urgent donation needed for my neighbour"]
        
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in known_scam_phrases):
            return {
                "status": "Flagged",
                "confidence": 0.8,
                "details": "Text contains phrasing strongly associated with past scams."
            }
            
        return {
            "status": "Verified",
            "confidence": 0.5,
            "details": "Text does not strongly match known scams."
        }
