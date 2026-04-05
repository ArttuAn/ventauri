from skills.branding_tools.naming import (
    generate_name_candidates,
    score_name_distinctiveness,
    slugify,
)


def test_slugify_basic() -> None:
    assert slugify("Hello World!") == "hello-world"


def test_distinctiveness_in_range() -> None:
    s = score_name_distinctiveness("Ventauri")
    assert 0.0 <= s <= 1.0


def test_generate_name_candidates_length() -> None:
    rows = generate_name_candidates("AI toolkit for dentists", count=7)
    assert len(rows) == 7
    assert all("name" in r and "slug" in r for r in rows)
