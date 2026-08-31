import re
from typing import Dict, Any

class WhoisLookup:
    SUSPICIOUS_DOMAIN_WORDS = ['relief-now', 'donate-fast', 'urgent-help', 'donate-now', 'help-now', 'fund-relief', 'quick-donate', 'emergency-fund', 'save-now', 'crisis-help']
    TRUSTED_TLDS = ['.gov.in', '.org.in', '.ac.in', '.org', '.edu']
    UNTRUSTED_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.buzz', '.click', '.link']
    
    @staticmethod
    def analyze_domain(domain: str) -> Dict[str, Any]:
        domain_lower = domain.lower()
        domain_age_days = None
        status = 'Unverifiable'
        confidence = 0.5
        details = []

        try:
            import whois
            from datetime import datetime
            w = whois.whois(domain)
            if w.creation_date:
                creation_date = w.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                domain_age_days = (datetime.now() - creation_date).days
                if domain_age_days < 30:
                    details.append("Domain is very new (less than 30 days)")
                    status = 'Flagged'
                    confidence = 0.8
        except Exception:
            pass

        score = 50
        if any(word in domain_lower for word in WhoisLookup.SUSPICIOUS_DOMAIN_WORDS):
            score -= 30
            details.append("Contains suspicious keywords")
            
        if any(domain_lower.endswith(tld) for tld in WhoisLookup.TRUSTED_TLDS):
            score += 30
            details.append("Uses trusted TLD")
            
        if any(domain_lower.endswith(tld) for tld in WhoisLookup.UNTRUSTED_TLDS):
            score -= 40
            details.append("Uses untrusted TLD")
            
        if score >= 80:
            status = 'Verified'
            confidence = min(score/100, 1.0)
        elif score <= 40:
            status = 'Flagged'
            confidence = (100-score)/100
            
        return {
            'status': status,
            'confidence': confidence,
            'details': details,
            'domain_age_days': domain_age_days
        }
