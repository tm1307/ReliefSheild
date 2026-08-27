import pytesseract
from PIL import Image
import re
from typing import Dict, List, Optional
import io

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (OSError, ImportError):
    nlp = None

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    httpx = None
    BeautifulSoup = None


class ExtractionLayer:
    """
    Normalises text, links, and screenshots into a structured record.
    Extracts entities using NLP, OCR, and regex.
    """

    CLAIM_PATTERNS = [
        (r"(?i)(?:registered|approved|certified)\s+(?:under|by|with)\s+([\w\s]+)", "registration_claim"),
        (r"(?i)(?:partnered|partnership|affiliated)\s+(?:with|by)\s+([\w\s]+)", "partnership_claim"),
        (r"(?i)(?:government[\s-]?approved|govt[\s.-]?approved)", "govt_approval_claim"),
        (r"(?i)(?:FCRA|12A|80G)\s*(?:registration|certified|approved|number)", "tax_exemption_claim"),
        (r"(?i)(?:100%|all)\s+(?:funds?|donations?|money)\s+(?:go(?:es)?|sent|transferred)\s+(?:to|directly)", "funds_claim"),
    ]

    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        """Runs OCR on an uploaded screenshot."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    @staticmethod
    def fetch_url_content(url: str) -> str:
        """Fetches and extracts readable text from a URL."""
        if not httpx or not BeautifulSoup:
            return url  # Fallback: treat URL as text
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return text[:5000]  # Cap to avoid huge pages
        except Exception as e:
            print(f"URL fetch error: {e}")
            return url

    @staticmethod
    def extract_claims(text: str) -> List[str]:
        """Extracts verifiable factual claims from text."""
        claims = []
        if not text:
            return claims
        for pattern, claim_type in ExtractionLayer.CLAIM_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                claim_str = match.strip() if isinstance(match, str) else claim_type
                claims.append(f"{claim_type}: {claim_str}")
        return claims

    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """
        Extracts Named Entities (NGOs, Locations) and Regex-based entities (UPI, Bank, Domains).
        Also extracts verifiable claims.
        """
        entities = {
            "ORG": [],
            "LOC": [],
            "PAYMENT_ID": [],
            "DOMAIN": [],
            "CLAIM": [],
        }

        if not text:
            return entities

        upi_pattern = r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}"
        entities["PAYMENT_ID"].extend(re.findall(upi_pattern, text))

        domain_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        entities["DOMAIN"].extend(re.findall(domain_pattern, text))

        entities["CLAIM"] = ExtractionLayer.extract_claims(text)

        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "ORG" and ent.text not in entities["ORG"]:
                    entities["ORG"].append(ent.text)
                elif ent.label_ in ("GPE", "LOC"):
                    if ent.text not in entities["LOC"]:
                        entities["LOC"].append(ent.text)

        return entities

    @staticmethod
    def process_input(
        input_type: str,
        text_content: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> Dict:
        """
        Takes raw input, normalises to text, and extracts entities.
        """
        full_text = ""

        if input_type == "image" and image_bytes:
            full_text = ExtractionLayer.extract_text_from_image(image_bytes)
        elif input_type == "link" and text_content:
            full_text = ExtractionLayer.fetch_url_content(text_content)
        elif input_type == "text" and text_content:
            full_text = text_content

        extracted_data = ExtractionLayer.extract_entities(full_text)

        return {"raw_text": full_text, "entities": extracted_data}
