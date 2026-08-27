import re
from typing import Dict, List


class ClaimModule:
    """
    Verifies specific factual claims found in an appeal.
    Claims that cannot be corroborated are marked 'Unverifiable', NOT false.
    This follows the proposal principle: explicit about limits rather than presenting false certainty.
    """

    KNOWN_FACTS = {
        "govt_approval_claim": {
            "known_approved_orgs": ["red cross society", "save the children", "care india", "oxfam india"],
        },
        "tax_exemption_claim": {
            "known_exempt_orgs": ["red cross society", "save the children", "helpage india"],
        },
        "partnership_claim": {
            "known_partners": {
                "red cross society": ["government of india", "who", "unicef"],
                "save the children": ["unicef", "world bank"],
            },
        },
    }

    SUSPICIOUS_PATTERNS = [
        r"(?i)urgent(?:ly)?\s+(?:need|send|transfer|donate)",
        r"(?i)(?:last\s+chance|only\s+\d+\s+hours?\s+left|deadline\s+today)",
        r"(?i)(?:don'?t\s+verify|no\s+need\s+to\s+check|trust\s+(?:me|us))",
        r"(?i)(?:forward\s+(?:this|to)\s+(?:everyone|all|\d+\s+people))",
    ]

    @staticmethod
    def verify_claims(text: str) -> Dict:
        """
        Analyse the text for factual claims and check each against the knowledge base.
        Returns aggregate result for the Claim module.
        """
        if not text:
            return {
                "status": "Unverifiable",
                "confidence": 0.0,
                "details": "No text provided for claim analysis.",
                "claims": [],
            }

        claim_results = []
        text_lower = text.lower()

        if re.search(r"(?i)(?:government[\s-]?approved|govt[\s.-]?approved)", text):
            matched = False
            for org in ClaimModule.KNOWN_FACTS["govt_approval_claim"]["known_approved_orgs"]:
                if org in text_lower:
                    claim_results.append({
                        "claim": "Government approved",
                        "status": "Verified",
                        "detail": f"Organisation '{org}' is in the known government-approved list.",
                    })
                    matched = True
                    break
            if not matched:
                claim_results.append({
                    "claim": "Government approved",
                    "status": "Unverifiable",
                    "detail": "Claims government approval but the organisation could not be matched to known approved entities.",
                })

        if re.search(r"(?i)(?:FCRA|12A|80G)", text):
            matched = False
            for org in ClaimModule.KNOWN_FACTS["tax_exemption_claim"]["known_exempt_orgs"]:
                if org in text_lower:
                    claim_results.append({
                        "claim": "Tax exemption registration",
                        "status": "Verified",
                        "detail": f"Organisation '{org}' has known FCRA/12A/80G registration.",
                    })
                    matched = True
                    break
            if not matched:
                claim_results.append({
                    "claim": "Tax exemption registration",
                    "status": "Unverifiable",
                    "detail": "Claims tax-exempt status but could not be verified against known records.",
                })

        partnership_match = re.search(r"(?i)(?:partnered|partnership|affiliated)\s+(?:with|by)\s+([\w\s]+)", text)
        if partnership_match:
            claimed_partner = partnership_match.group(1).strip().lower()
            verified = False
            for org, partners in ClaimModule.KNOWN_FACTS["partnership_claim"]["known_partners"].items():
                if org in text_lower and any(p in claimed_partner for p in partners):
                    claim_results.append({
                        "claim": f"Partnership with {claimed_partner}",
                        "status": "Verified",
                        "detail": f"Partnership between '{org}' and '{claimed_partner}' is known.",
                    })
                    verified = True
                    break
            if not verified:
                claim_results.append({
                    "claim": f"Partnership with {claimed_partner}",
                    "status": "Unverifiable",
                    "detail": f"Claimed partnership with '{claimed_partner}' could not be corroborated.",
                })

        suspicious_found = []
        for pattern in ClaimModule.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text):
                suspicious_found.append(pattern)

        if suspicious_found:
            claim_results.append({
                "claim": "Pressure tactics detected",
                "status": "Flagged",
                "detail": f"Text contains {len(suspicious_found)} pressure/urgency pattern(s) commonly associated with fraudulent appeals.",
            })

        if re.search(r"(?i)(?:100%|all)\s+(?:funds?|donations?|money)\s+(?:go(?:es)?|sent|transferred)", text):
            claim_results.append({
                "claim": "100% funds utilisation",
                "status": "Unverifiable",
                "detail": "Claims all funds go directly to relief. This cannot be independently verified.",
            })

        if not claim_results:
            return {
                "status": "Unverifiable",
                "confidence": 0.5,
                "details": "No specific verifiable claims extracted from the appeal text.",
                "claims": [],
            }

        flagged = [c for c in claim_results if c["status"] == "Flagged"]
        unverifiable = [c for c in claim_results if c["status"] == "Unverifiable"]
        verified = [c for c in claim_results if c["status"] == "Verified"]

        if flagged:
            status = "Flagged"
            confidence = 0.8
            details = f"{len(flagged)} claim(s) flagged as suspicious. {len(unverifiable)} claim(s) could not be verified."
        elif unverifiable and not verified:
            status = "Unverifiable"
            confidence = 0.5
            details = f"{len(unverifiable)} claim(s) made but none could be independently verified."
        elif verified:
            status = "Verified"
            confidence = 0.7
            details = f"{len(verified)} claim(s) verified. {len(unverifiable)} claim(s) remain unverifiable."
        else:
            status = "Unverifiable"
            confidence = 0.5
            details = "Claims analysis inconclusive."

        return {
            "status": status,
            "confidence": confidence,
            "details": details,
            "claims": claim_results,
        }
