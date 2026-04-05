from orchestrator.router import route_user_goal


def test_route_defaults_to_idea_to_strategy() -> None:
    r = route_user_goal("anything")
    assert r.pipeline_id == "idea-to-strategy"
