from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any


def slugify(text: str) -> str:
    """Lowercase repo-style slug (a-z0-9 hyphens)."""
    s = unicodedata.normalize("NFKD", text)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "project"


def score_name_distinctiveness(name: str) -> float:
    """
    Heuristic 0-1 distinctiveness (not legal/trademark advice).
    Favors length, mixed case or non-dictionary tokens, low generic-word density.
    """
    raw = name.strip()
    if not raw:
        return 0.0
    tokens = re.findall(r"[A-Za-z]+", raw.lower())
    generic = {
        "app",
        "ai",
        "io",
        "hq",
        "labs",
        "lab",
        "ventures",
        "venture",
        "founder",
        "startup",
        "tech",
        "soft",
        "systems",
        "system",
        "solutions",
        "solution",
        "digital",
        "smart",
        "pro",
        "hub",
        "cloud",
    }
    gen_hits = sum(1 for t in tokens if t in generic)
    gen_penalty = min(0.45, gen_hits * 0.12)
    length_bonus = min(0.25, len(raw) / 80)
    mixed = 0.1 if re.search(r"[a-z][A-Z]|[A-Z][a-z]{2,}", raw) else 0.0
    token_uniq = min(0.35, len(set(tokens)) * 0.08) if tokens else 0.0
    score = 0.35 + length_bonus + mixed + token_uniq - gen_penalty
    return max(0.0, min(1.0, round(score, 3)))


def _stable_suffix(seed: str, i: int, part: str) -> str:
    h = hashlib.sha256(f"{seed}|{i}|{part}".encode()).hexdigest()[:6]
    return h


def generate_name_candidates(seed: str, count: int = 12) -> list[dict[str, Any]]:
    """
    Produce brand-style name ideas from a short product/vision seed.
    Agents (or humans) should still verify domains, trademarks, and GitHub/npm availability.
    """
    seed_clean = seed.strip() or "new venture"
    slug = slugify(seed_clean)
    roots = [
        "Velum",
        "Praxent",
        "Orbitry",
        "Kinetiq",
        "Nexora",
        "Stratyl",
        "Lumina",
        "Vantiq",
        "Operly",
        "Forgeant",
    ]
    suffixes = ["", "OS", "Labs", "Works", "Mind", "Flow", "Deck", "Stack", "Pilot"]
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in roots:
        for suf in suffixes:
            if len(out) >= count:
                break
            label = f"{root}{suf}" if suf else root
            if label.lower() in seen:
                continue
            seen.add(label.lower())
            distinct = score_name_distinctiveness(label)
            label_slug = slugify(label)
            out.append(
                {
                    "name": label,
                    "slug": label_slug,
                    "distinctiveness": distinct,
                    "rationale": f"Coined blend inspired by: {seed_clean[:80]}",
                    "next_checks": [
                        "Search GitHub / npm / PyPI for the slug",
                        "Check domain and trademark databases for your jurisdictions",
                    ],
                }
            )
        if len(out) >= count:
            break

    n = 0
    max_extra = max(count * 25, 200)
    while len(out) < count and n < max_extra:
        root = roots[n % len(roots)]
        token = _stable_suffix(seed_clean, n, root)
        label = f"{root}{token[:3].upper()}"
        n += 1
        if label.lower() in seen:
            continue
        seen.add(label.lower())
        label_slug = slugify(label)
        out.append(
            {
                "name": label,
                "slug": label_slug,
                "distinctiveness": score_name_distinctiveness(label),
                "rationale": f"Deterministic variant from seed hash (verify availability): {slug[:48]}",
                "next_checks": [
                    f"https://github.com/search?q={label_slug}",
                    f"https://www.npmjs.com/search?q={label_slug}",
                ],
            }
        )

    return out[:count]
