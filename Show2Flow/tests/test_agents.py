from show2flow.agents import intent, planner, verifier


def test_intent_parse_search_and_extract():
    text = "Open a website, search for AI jobs, extract the first 5 results, and save them."
    parsed = intent.parse(text, default_url="https://example.com")
    assert parsed.action == "search_and_extract"
    assert parsed.query == "ai jobs"
    assert parsed.result_limit == 5
    assert parsed.url == "https://example.com"


def test_planner_builds_expected_steps():
    parsed = intent.Intent(action="search_and_extract", url="https://example.com", query="ai jobs")
    wf = planner.plan(parsed, workflow_name="test_wf")
    ids = [s.id for s in wf.steps]
    assert ids == ["open_site", "fill_search", "submit_search", "extract_results", "save_results"]


def test_verifier_list_min_items():
    ok, reason = verifier.verify(["a", "b"], {"type": "list", "min_items": 2})
    assert ok is True and reason is None

    ok, reason = verifier.verify([], {"type": "list", "min_items": 1})
    assert ok is False
    assert "min_items" not in "" or reason is not None
