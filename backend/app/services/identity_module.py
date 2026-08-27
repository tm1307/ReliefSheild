import re
from typing import Dict, Optional

class IdentityModule:
    """
    Simulates checking an NGO against a public registry and checking domain whois data.
    """
    
    MOCK_REGISTRY = {
        "red cross society": {"status": "registered", "id": "NGO12345"},
        "save the children": {"status": "registered", "id": "NGO98765"},
        "local flood relief": {"status": "registered", "id": "NGO45678"}
    }
    
    @staticmethod
    def verify_organisation(org_name: str) -> Dict:
        """
        Check if the organisation name exists in our (mocked) registry.
        """
        if not org_name:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "No organisation name provided"}
            
        org_name_lower = org_name.lower().strip()
        
        for registered_name, data in IdentityModule.MOCK_REGISTRY.items():
            if registered_name in org_name_lower or org_name_lower in registered_name:
                return {
                    "status": "Verified",
                    "confidence": 0.9,
                    "details": f"Found in NGO Darpan mock registry: {data['id']}"
                }
                
        return {
            "status": "Flagged",
            "confidence": 0.6,
            "details": "Organisation not found in official registries"
        }
        
    @staticmethod
    def verify_domain(domain_url: str) -> Dict:
        """
        Check domain registration age and details (Mocked)
        """
        if "scam-relief-2023.com" in domain_url:
            return {"status": "Flagged", "confidence": 0.95, "details": "Domain registered < 48 hours ago"}
            
        return {"status": "Verified", "confidence": 0.7, "details": "Domain age > 1 year"}
