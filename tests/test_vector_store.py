from memory.vector_store import VectorRecord, VectorStore


def test_vector_store_search_orders_by_similarity() -> None:
    vs = VectorStore(dim=32)
    vs.add("a", "saas billing for clinics", {})
    vs.add("b", "recipe blog wordpress theme", {})
    hits = vs.search("b2b healthcare subscription software", k=2)
    assert hits[0][1].id == "a"


def test_vector_store_search_filtered_by_metadata() -> None:
    vs = VectorStore(dim=32)
    vs.add("x1", "alpha beta", {"agent_id": "a", "session_id": "s1"})
    vs.add("x2", "gamma delta", {"agent_id": "b", "session_id": "s1"})
    hits = vs.search_filtered(
        "alpha",
        k=3,
        match=lambda r: r.metadata.get("agent_id") == "a",
    )
    assert len(hits) == 1
    assert isinstance(hits[0][1], VectorRecord)
