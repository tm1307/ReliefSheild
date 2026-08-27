from typing import Dict, List, Optional


class EvidenceGraphBuilder:
    """
    Builds a lightweight evidence graph linking:
    Appeal -> Organisation -> Domain -> Payment ID -> Sources
    
    Each node has a type and status. Each edge records the relationship
    and any contradiction detected. The graph is JSON-serializable for
    frontend visualization.
    """

    @staticmethod
    def build(
        appeal_text: str,
        org_name: str,
        payment_id: str,
        domains: List[str],
        verifications: List[Dict],
    ) -> Dict:
        """
        Build the evidence graph from extracted entities and verification results.
        Returns a JSON-serializable dict with 'nodes' and 'edges'.
        """
        nodes = []
        edges = []
        node_id = 0

        appeal_node_id = node_id
        nodes.append({
            "id": node_id,
            "type": "appeal",
            "label": "Submitted Appeal",
            "status": "neutral",
            "detail": appeal_text[:120] + ("..." if len(appeal_text) > 120 else ""),
        })
        node_id += 1

        id_verification = next((v for v in verifications if v.get("module_name") == "Identity"), None)
        if org_name:
            org_node_id = node_id
            org_status = id_verification["status"].lower() if id_verification else "unknown"
            nodes.append({
                "id": node_id,
                "type": "organisation",
                "label": org_name,
                "status": org_status,
                "detail": id_verification.get("details", "") if id_verification else "No identity check performed.",
            })
            edges.append({
                "source": appeal_node_id,
                "target": org_node_id,
                "relationship": "claims_to_be",
                "label": "Claims to represent",
                "status": org_status,
            })
            node_id += 1
        else:
            org_node_id = None
            gap_node_id = node_id
            nodes.append({
                "id": node_id,
                "type": "gap",
                "label": "No Organisation Found",
                "status": "flagged",
                "detail": "No organisation name could be extracted from the appeal.",
            })
            edges.append({
                "source": appeal_node_id,
                "target": gap_node_id,
                "relationship": "missing",
                "label": "No org identified",
                "status": "flagged",
            })
            node_id += 1

        for domain in domains:
            domain_node_id = node_id
            nodes.append({
                "id": node_id,
                "type": "domain",
                "label": domain[:50],
                "status": "neutral",
                "detail": f"Domain found in appeal: {domain}",
            })
            edges.append({
                "source": appeal_node_id,
                "target": domain_node_id,
                "relationship": "links_to",
                "label": "Links to",
                "status": "neutral",
            })
            if org_node_id is not None:
                edges.append({
                    "source": org_node_id,
                    "target": domain_node_id,
                    "relationship": "associated_domain",
                    "label": "Associated domain",
                    "status": "neutral",
                })
            node_id += 1

        pay_verification = next((v for v in verifications if v.get("module_name") == "Payment"), None)
        if payment_id:
            pay_node_id = node_id
            pay_status = pay_verification["status"].lower() if pay_verification else "unknown"
            nodes.append({
                "id": node_id,
                "type": "payment",
                "label": payment_id,
                "status": pay_status,
                "detail": pay_verification.get("details", "") if pay_verification else "",
            })
            edges.append({
                "source": appeal_node_id,
                "target": pay_node_id,
                "relationship": "collects_via",
                "label": "Collects donations via",
                "status": pay_status,
            })
            if org_node_id is not None:
                consistency_status = pay_status
                edges.append({
                    "source": org_node_id,
                    "target": pay_node_id,
                    "relationship": "payment_consistency",
                    "label": "Org ↔ Payment match" if pay_status == "verified" else "Org ↔ Payment MISMATCH",
                    "status": consistency_status,
                })
            node_id += 1

        sim_verification = next((v for v in verifications if v.get("module_name") == "Similarity"), None)
        if sim_verification and sim_verification.get("status") == "Flagged":
            sim_node_id = node_id
            nodes.append({
                "id": node_id,
                "type": "source",
                "label": "Past Campaign Match",
                "status": "flagged",
                "detail": sim_verification.get("details", "Similar to a previously seen appeal."),
            })
            edges.append({
                "source": appeal_node_id,
                "target": sim_node_id,
                "relationship": "similar_to",
                "label": "Matches previous appeal",
                "status": "flagged",
            })
            node_id += 1

        claim_verification = next((v for v in verifications if v.get("module_name") == "Claim"), None)
        if claim_verification and claim_verification.get("claims"):
            for claim in claim_verification["claims"]:
                claim_node_id = node_id
                nodes.append({
                    "id": node_id,
                    "type": "source",
                    "label": claim["claim"],
                    "status": claim["status"].lower(),
                    "detail": claim["detail"],
                })
                edges.append({
                    "source": appeal_node_id,
                    "target": claim_node_id,
                    "relationship": "makes_claim",
                    "label": "Claims",
                    "status": claim["status"].lower(),
                })
                node_id += 1

        return {
            "nodes": nodes,
            "edges": edges,
        }
