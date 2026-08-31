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
        try:
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    @staticmethod
    def fetch_url_content(url: str) -> str:
        if not httpx or not BeautifulSoup:
            return url
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return text[:5000]
        except Exception as e:
            print(f"URL fetch error: {e}")
            return url

    @staticmethod
    def extract_claims(text: str) -> List[str]:
        claims = []
        if not text:
            return claims
        for pattern, claim_type in ExtractionLayer.CLAIM_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                claim_str = match.strip() if isinstance(match, str) else claim_type
                claims.append(f"{claim_type}: {claim_str}")
        return list(set(claims))

    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        entities = {
            "ORG": set(),
            "LOC": set(),
            "PAYMENT_ID": set(),
            "DOMAIN": set(),
            "CLAIM": set(),
            "PHONE": set(),
            "BANK_INFO": set(),
        }

        if not text:
            return {k: list(v) for k, v in entities.items()}

        # UPI IDs
        upi_pattern = r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}"
        entities["PAYMENT_ID"].update(re.findall(upi_pattern, text))

        # Domains
        domain_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
        entities["DOMAIN"].update(re.findall(domain_pattern, text))

        # Indian Phone Numbers (+91 or just 10 digits starting with 6-9)
        phone_pattern = r"(?:\+91[\s-]?)?[6789]\d{9}"
        entities["PHONE"].update(re.findall(phone_pattern, text))

        # Bank IFSC codes and account numbers
        ifsc_pattern = r"[A-Z]{4}0[A-Z0-9]{6}"
        entities["BANK_INFO"].update(re.findall(ifsc_pattern, text))
        
        acct_pattern = r"\b\d{9,18}\b"
        # Only add likely account numbers if they appear near banking keywords
        if re.search(r"(?i)(?:a/c|account|bank|ifsc)", text):
            entities["BANK_INFO"].update(re.findall(acct_pattern, text))

        # Claims
        for c in ExtractionLayer.extract_claims(text):
            entities["CLAIM"].add(c)

        # NLP Entities
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    entities["ORG"].add(ent.text)
                elif ent.label_ in ("GPE", "LOC"):
                    entities["LOC"].add(ent.text)

        return {k: list(v) for k, v in entities.items()}

    @staticmethod
    def process_input(
        input_type: str,
        text_content: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> Dict:
        full_text = ""

        if input_type == "image" and image_bytes:
            full_text = ExtractionLayer.extract_text_from_image(image_bytes)
        elif input_type == "link" and text_content:
            full_text = ExtractionLayer.fetch_url_content(text_content)
        elif input_type == "text" and text_content:
            full_text = text_content

        extracted_data = ExtractionLayer.extract_entities(full_text)

        return {"raw_text": full_text, "entities": extracted_data}
