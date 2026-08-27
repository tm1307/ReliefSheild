import re
from typing import Dict

class PaymentModule:
    """
    Cross-checks payment identifiers with the claimed organisation.
    """
    
    PERSONAL_UPI_SUFFIXES = ['@ybl', '@okicici', '@oksbi', '@okhdfcbank', '@paytm', '@apl']
    
    @staticmethod
    def extract_upi(text: str) -> list[str]:
        pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
        return re.findall(pattern, text)
        
    @staticmethod
    def verify_payment_consistency(org_name: str, payment_id: str) -> Dict:
        """
        Check if the payment destination makes sense for the organisation.
        """
        if not payment_id:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "No payment ID found"}
            
        payment_id_lower = payment_id.lower()
        
        if any(payment_id_lower.endswith(suffix) for suffix in PaymentModule.PERSONAL_UPI_SUFFIXES):
            if org_name and org_name.lower().split()[0] not in payment_id_lower:
                return {
                    "status": "Flagged",
                    "confidence": 0.85,
                    "details": f"Payment ID '{payment_id}' appears to be a personal account not matching NGO name '{org_name}'"
                }
                
        return {
            "status": "Verified",
            "confidence": 0.5,
            "details": "Payment ID format is acceptable and does not strongly contradict organisation name"
        }
