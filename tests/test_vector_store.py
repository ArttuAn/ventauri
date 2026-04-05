from memory.vector_store import VectorStore


def test_vector_store_search_orders_by_similarity() -> None:
    vs = VectorStore(dim=32)
    vs.add("a", "saas billing for clinics", {})
    vs.add("b", "recipe blog wordpress theme", {})
    hits = vs.search("b2b healthcare subscription software", k=2)
    assert hits[0][1].id == "a"
