from typing import List, Dict


class ScoringEngine:
    """
    Calculates a transparent Trust Score out of 100 based on the Evidence Graph.
    This is rule-based to ensure explainability and deterministic behavior.
    Every point deducted is traceable to a specific check.
    """

    BASE_SCORE = 100

    MODULE_WEIGHTS = {
        "Identity": 25,
        "Payment": 35,
        "Similarity": 40,
        "Claim": 15,
    }

    @staticmethod
    def calculate_score(verifications: List[Dict]) -> Dict:
        """
        Takes a list of verification results and calculates the final score.
        Also generates a plain-language summary.
        """
        score = ScoringEngine.BASE_SCORE
        breakdown = []

        for v in verifications:
            module = v.get("module_name", "Unknown")
            status = v.get("status")
            confidence = v.get("confidence", 1.0)

            deduction = 0
            max_deduction = ScoringEngine.MODULE_WEIGHTS.get(module, 10)

            if status == "Flagged":
                deduction = int(max_deduction * confidence)
            elif status == "Unverifiable":
                deduction = 5

            score -= deduction

            breakdown.append({
                "check": module,
                "status": status,
                "points_deducted": deduction,
                "details": v.get("details"),
            })

        score = max(0, min(100, score))

        summary = ScoringEngine._generate_summary(score, breakdown)

        return {
            "final_score": score,
            "breakdown": breakdown,
            "summary": summary,
        }

    @staticmethod
    def _generate_summary(score: int, breakdown: List[Dict]) -> str:
        """
        Generate a plain-language summary of the trust report.
        The system is explicit about its own limits rather than presenting false certainty.
        """
        flagged = [b for b in breakdown if b["status"] == "Flagged"]
        unverifiable = [b for b in breakdown if b["status"] == "Unverifiable"]
        verified = [b for b in breakdown if b["status"] == "Verified"]

        parts = []

        if score >= 80:
            parts.append("This appeal appears largely trustworthy based on the checks we could perform.")
        elif score >= 50:
            parts.append("This appeal has some concerns that warrant caution before donating.")
        elif score >= 25:
            parts.append("This appeal has significant red flags. We recommend verifying independently before donating.")
        else:
            parts.append("This appeal shows strong indicators of being fraudulent or misleading.")

        if flagged:
            flag_names = [f["check"] for f in flagged]
            parts.append(f"Flagged checks: {', '.join(flag_names)}.")

        if unverifiable:
            unv_names = [u["check"] for u in unverifiable]
            parts.append(f"We could not independently verify: {', '.join(unv_names)}. This does not mean the appeal is false — it means we lack sufficient data to confirm it.")

        if verified:
            ver_names = [v["check"] for v in verified]
            parts.append(f"Passed checks: {', '.join(ver_names)}.")

        return " ".join(parts)
