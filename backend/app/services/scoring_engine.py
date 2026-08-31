from typing import List, Dict


class ScoringEngine:
    """
    Calculates a transparent Trust Score out of 100 based on the Evidence Graph.
    Every point deducted is traceable to a specific check.
    """

    BASE_SCORE = 100

    MODULE_WEIGHTS = {
        "Identity": 25,
        "Payment": 35,
        "Similarity": 30,
        "Claim": 10,
    }

    @staticmethod
    def calculate_score(verifications: List[Dict]) -> Dict:
        score = ScoringEngine.BASE_SCORE
        breakdown = []
        recommendations = []

        for v in verifications:
            module = v.get("module_name", "Unknown")
            status = v.get("status")
            confidence = v.get("confidence", 1.0)

            deduction = 0
            max_deduction = ScoringEngine.MODULE_WEIGHTS.get(module, 10)

            if status == "Flagged":
                deduction = int(max_deduction * confidence)
                
                # Assign recommendations based on flagged modules
                if module == "Identity":
                    recommendations.append("Verify this organisation at the official NGO Darpan portal (ngodarpan.gov.in).")
                elif module == "Payment":
                    recommendations.append("Double-check the payment handle; it does not appear to be an official institutional account.")
                elif module == "Similarity":
                    recommendations.append("Exercise extreme caution: this appeal heavily recycles images or text from known scams.")
                elif module == "Claim":
                    recommendations.append("Be wary of the artificial urgency or pressure tactics used in this appeal.")
                    
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

        # Risk Classification
        if score >= 80:
            risk_level = "Low Risk"
        elif score >= 60:
            risk_level = "Medium Risk"
            if not recommendations:
                recommendations.append("Cross-check with official sources to ensure funds reach the intended cause.")
        elif score >= 40:
            risk_level = "High Risk"
            if not recommendations:
                recommendations.append("We strongly recommend finding a verified alternative organisation for this cause.")
        else:
            risk_level = "Critical Risk"
            recommendations.append("Do not donate. This appeal exhibits multiple severe fraud indicators.")

        summary = ScoringEngine._generate_summary(score, breakdown)

        return {
            "final_score": score,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "breakdown": breakdown,
            "summary": summary,
        }

    @staticmethod
    def _generate_summary(score: int, breakdown: List[Dict]) -> str:
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
            parts.append(f"We could not independently verify: {', '.join(unv_names)}. This does not mean it is false — just unconfirmed.")

        if verified:
            ver_names = [v["check"] for v in verified]
            parts.append(f"Passed checks: {', '.join(ver_names)}.")

        return " ".join(parts)
