import re
from typing import Dict

class PaymentModule:

    KNOWN_NGO_UPIS = {
        "pmcares@sbi", "redcross@sbi", "cmikirelief@sbi", "goonj@icici",
        "akshayapatra@hdfcbank", "cryindia@kotak", "giveindia@yesbank",
        "helpageindia@axis", "oxfamindia@icici", "savechildren@sbi",
        "pratham@hdfc", "careindia@axis", "smilefoundation@sbi",
        "sewa@sbi", "khalsa@sbi", "worldvision@hdfcbank", "planind@sbi",
        "actionaid@icici", "wateraid@axis", "unicef@sbi", "ndrf@sbi",
        "tatrust@sbi", "infosysfoundation@hdfcbank", "reliancefoundation@sbi",
    }

    PERSONAL_UPI_SUFFIXES = [
        "@ybl", "@okicici", "@oksbi", "@okhdfcbank", "@paytm",
        "@apl", "@ibl", "@axl", "@freecharge", "@upi",
        "@gpay", "@phonepe", "@postbank", "@slice",
    ]

    ORG_UPI_SUFFIXES = [
        "@sbi", "@hdfcbank", "@icici", "@axis", "@kotak",
        "@yesbank", "@pnb", "@boi", "@cbi", "@idfcfirst",
    ]

    @staticmethod
    def extract_upi(text: str) -> list[str]:
        pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
        return re.findall(pattern, text)

    @staticmethod
    def verify_payment_consistency(org_name: str, payment_id: str) -> Dict:
        if not payment_id:
            return {"status": "Unverifiable", "confidence": 0.0, "details": "No payment ID found in the appeal"}

        pid_lower = payment_id.lower()

        if pid_lower in PaymentModule.KNOWN_NGO_UPIS:
            return {
                "status": "Verified",
                "confidence": 0.95,
                "details": f"Payment ID '{payment_id}' is a registered NGO payment endpoint"
            }

        crypto_patterns = [
            (r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", "Bitcoin"),
            (r"^0x[a-fA-F0-9]{40}$", "Ethereum"),
        ]
        for pattern, crypto_name in crypto_patterns:
            if re.match(pattern, payment_id):
                return {
                    "status": "Flagged",
                    "confidence": 0.95,
                    "details": f"Payment destination is a {crypto_name} wallet address, highly unusual for legitimate relief"
                }

        is_personal = any(pid_lower.endswith(suffix) for suffix in PaymentModule.PERSONAL_UPI_SUFFIXES)

        if is_personal and org_name:
            org_tokens = set(org_name.lower().replace("-", " ").split())
            upi_prefix = pid_lower.split("@")[0]
            has_overlap = any(len(token) > 2 and token in upi_prefix for token in org_tokens)
            if not has_overlap:
                return {
                    "status": "Flagged",
                    "confidence": 0.85,
                    "details": f"Payment ID '{payment_id}' appears to be a personal account not matching NGO name '{org_name}'"
                }

        if is_personal and not org_name:
            return {
                "status": "Flagged",
                "confidence": 0.7,
                "details": f"Payment ID '{payment_id}' uses a personal UPI handle with no identifiable organisation"
            }

        is_org_upi = any(pid_lower.endswith(suffix) for suffix in PaymentModule.ORG_UPI_SUFFIXES)
        if is_org_upi and org_name:
            org_tokens = set(org_name.lower().replace("-", " ").split())
            upi_prefix = pid_lower.split("@")[0]
            has_overlap = any(len(token) > 2 and token in upi_prefix for token in org_tokens)
            if has_overlap:
                return {
                    "status": "Verified",
                    "confidence": 0.7,
                    "details": f"Payment ID format is institutional and name matches the claimed organisation"
                }

        return {
            "status": "Verified",
            "confidence": 0.5,
            "details": "Payment ID format is acceptable and does not strongly contradict organisation name"
        }
