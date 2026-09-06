from show2flow.agents.healer import _difflib_best_match


def test_difflib_finds_close_match():
    candidates = [
        {"text": "Find Jobs", "selector": "button >> nth=0"},
        {"text": "Contact Us", "selector": "a >> nth=1"},
        {"text": "About", "selector": "a >> nth=2"},
    ]
    result = _difflib_best_match("Search Jobs", candidates)
    assert result.matched is True
    assert result.matched_text == "Find Jobs"
    assert result.confidence >= 0.5


def test_difflib_no_candidates():
    result = _difflib_best_match("Search Jobs", [])
    assert result.matched is False
