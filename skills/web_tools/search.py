from __future__ import annotations

from typing import Any


def web_search_stub(query: str) -> dict[str, Any]:
    """Replace with Firecrawl / SerpAPI / Bing — deterministic placeholder for MVP."""
    return {
        "query": query,
        "snippets": [
            "Buyers consolidating tools; willingness to pay rises with measurable ROI.",
            "Vertical SaaS outperforming horizontal in 12-18 month CAC payback.",
        ],
        "sources": ["stub://ventauri.demo/news", "stub://ventauri.demo/report"],
    }
