import re
from typing import Dict, List


class ClaimModule:
    """
    Verifies specific factual claims found in an appeal.
    Claims that cannot be corroborated are marked 'Unverifiable', NOT false.
    """

    KNOWN_FACTS = {
        "govt_approval_claim": {
            "known_approved_orgs": [
                "red cross society", "save the children", "care india", "oxfam india",
                "goonj", "cry", "akshaya patra", "helpage india", "world vision",
                "smile foundation", "pratham", "plan india", "unicef", "pm cares"
            ],
        },
        "tax_exemption_claim": {
            "known_exempt_orgs": [
                "red cross society", "save the children", "helpage india", "goonj",
                "akshaya patra foundation", "cry", "give india", "oxfam",
                "pm cares fund", "chief minister relief fund", "ndrf"
            ],
        },
        "partnership_claim": {
            "known_partners": {
                "red cross society": ["government of india", "who", "unicef", "indian army"],
                "save the children": ["unicef", "world bank", "who"],
                "goonj": ["various corporates", "tata trusts"],
                "akshaya patra": ["state governments", "central government"],
                "unicef": ["united nations", "who", "government of india"],
                "cry": ["tata trusts", "wipro foundation"],
            },
        },
    }

    SUSPICIOUS_PATTERNS = [
        r"(?i)urgent(?:ly)?\s+(?:need|send|transfer|donate)",
        r"(?i)(?:don'?t\s+verify|no\s+need\s+to\s+check|trust\s+(?:me|us))",
    ]

    @staticmethod
    def verify_claims(text: str) -> Dict:
        if not text:
            return {
                "status": "Unverifiable",
                "confidence": 0.0,
                "details": "No text provided for claim analysis.",
                "claims": [],
            }

        claim_results = []
        text_lower = text.lower()

        # 1. Celebrity / Endorsement Claims (Require external validation)
        celeb_match = re.search(r"(?i)(?:supported by|backed by|endorsed by|in association with) (pm|chief minister|modi|salman|shah rukh|tata|ambani)", text_lower)
        if celeb_match:
            claim_results.append({
                "claim": f"Endorsement by {celeb_match.group(1).title()}",
                "status": "Unverifiable",
                "detail": "High-profile endorsements are frequently faked in scams and require official source verification.",
            })

        # 2. Specific Monetary Claims
        if re.search(r"(?i)₹?\s*\d+\s+(?:feeds|saves|rescues|protects)\s+(?:a family|a life|\d+ lives)", text_lower):
            claim_results.append({
                "claim": "Specific monetary outcome guarantee",
                "status": "Unverifiable",
                "detail": "Highly specific monetary guarantees are common emotional triggers and cannot be independently audited here.",
            })

        # 3. Timeline Urgency (Flagged)
        if re.search(r"(?i)(?:only \d+ hours left|deadline today|last day to donate|act now or)", text_lower):
            claim_results.append({
                "claim": "Artificial timeline urgency",
                "status": "Flagged",
                "detail": "Arbitrary countdowns and extreme urgency are classic pressure tactics used by fraudsters.",
            })

        # 4. Forwarding Pressure (Flagged)
        if re.search(r"(?i)(?:share with \d+ people|forward to everyone|forward this to all)", text_lower):
            claim_results.append({
                "claim": "Viral forwarding pressure",
                "status": "Flagged",
                "detail": "Legitimate NGOs rarely demand users forward messages to specific numbers of people.",
            })

        # 5. Government Approval
        if re.search(r"(?i)(?:government[\s-]?approved|govt[\s.-]?approved|recognized by govt)", text):
            matched = False
            for org in ClaimModule.KNOWN_FACTS["govt_approval_claim"]["known_approved_orgs"]:
                if org in text_lower:
                    claim_results.append({
                        "claim": "Government approved",
                        "status": "Verified",
                        "detail": f"Organisation '{org.title()}' is in the known government-approved list.",
                    })
                    matched = True
                    break
            if not matched:
                claim_results.append({
                    "claim": "Government approved",
                    "status": "Unverifiable",
                    "detail": "Claims government approval but the organisation could not be matched to known approved entities.",
                })

        # 6. Tax Exemption (FCRA/12A/80G)
        if re.search(r"(?i)(?:FCRA|12A|80G)", text):
            matched = False
            for org in ClaimModule.KNOWN_FACTS["tax_exemption_claim"]["known_exempt_orgs"]:
                if org in text_lower:
                    claim_results.append({
                        "claim": "Tax exemption registration",
                        "status": "Verified",
                        "detail": f"Organisation '{org.title()}' has known FCRA/12A/80G registration.",
                    })
                    matched = True
                    break
            if not matched:
                claim_results.append({
                    "claim": "Tax exemption registration",
                    "status": "Unverifiable",
                    "detail": "Claims tax-exempt status but could not be verified against known records.",
                })

        # 7. Partnerships
        partnership_match = re.search(r"(?i)(?:partnered|partnership|affiliated)\s+(?:with|by)\s+([\w\s]+)", text)
        if partnership_match:
            claimed_partner = partnership_match.group(1).strip().lower()
            verified = False
            for org, partners in ClaimModule.KNOWN_FACTS["partnership_claim"]["known_partners"].items():
                if org in text_lower and any(p in claimed_partner for p in partners):
                    claim_results.append({
                        "claim": f"Partnership with {claimed_partner.title()}",
                        "status": "Verified",
                        "detail": f"Partnership between '{org.title()}' and '{claimed_partner.title()}' is known.",
                    })
                    verified = True
                    break
            if not verified:
                claim_results.append({
                    "claim": f"Partnership with {claimed_partner.title()}",
                    "status": "Unverifiable",
                    "detail": f"Claimed partnership with '{claimed_partner.title()}' could not be corroborated.",
                })

        # 8. Suspicious Words
        suspicious_found = []
        for pattern in ClaimModule.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text):
                suspicious_found.append(pattern)

        if suspicious_found:
            claim_results.append({
                "claim": "Pressure tactics detected",
                "status": "Flagged",
                "detail": f"Text contains {len(suspicious_found)} urgency/pressure pattern(s) commonly associated with fraudulent appeals.",
            })

        # Final Aggregation
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
            confidence = 0.85
            details = f"{len(flagged)} claim(s) flagged as highly suspicious. {len(unverifiable)} claim(s) unverifiable."
        elif unverifiable and not verified:
            status = "Unverifiable"
            confidence = 0.5
            details = f"{len(unverifiable)} claim(s) made but none could be independently verified."
        elif verified:
            status = "Verified"
            confidence = 0.75
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
