from __future__ import annotations

from typing import Any


def regulatory_scan_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = prior, context
    g = goal.lower()
    jurisdictions: list[str] = []
    if any(x in g for x in ("eu", "europe", "gdpr")):
        jurisdictions.append("EU-GDPR-relevant (verify entity nexus)")
    if any(x in g for x in ("us", "usa", "hipaa", "fcc")):
        jurisdictions.append("US-sector-rules (verify)")
    if not jurisdictions:
        jurisdictions.append("Undetermined — map data flows and entity locations")
    return {
        "scan_id": "stub-compliance-scan",
        "jurisdictions_flagged": jurisdictions,
        "themes": ["privacy", "consumer disclosures", "sector licensing (if regulated)"],
        "note": "Replace with counsel-reviewed sources and jurisdiction-specific research.",
    }


def obligation_matrix_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = goal, prior, context
    return {
        "matrix_id": "stub-obligation-matrix",
        "rows": [
            {"obligation": "Privacy notice + lawful basis", "evidence": "product collects personal data"},
            {"obligation": "Data processing agreements", "evidence": "subprocessors / cloud"},
            {"obligation": "Security measures documentation", "evidence": "B2B buyers will ask"},
        ],
        "note": "Not legal advice — template for diligence questions only.",
    }
