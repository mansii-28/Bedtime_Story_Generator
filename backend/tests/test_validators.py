import pytest
from app.validators.validators import run_validators
from app.rules.rulebook import RULEBOOK

def test_validator_word_count_boundaries():
    # Test short story
    story = "Too short."
    plan = {"lesson": "Be kind."}
    safe_req = {"genre": "fantasy"}
    res = run_validators(story, plan, safe_req, RULEBOOK)
    assert res["passed"] is False
    assert any("too short" in f.lower() for f in res["failures"])

    # Test long story (mocking)
    story = "word " * 301
    res = run_validators(story, plan, safe_req, RULEBOOK)
    assert res["passed"] is False
    assert any("too long" in f.lower() for f in res["failures"])

def test_genre_drift_detection():
    # Story requested as sci-fi but contains fantasy words
    story = "Title: Space Adventure\nIn a galaxy far away, a brave robot found a dragon and a magic wand. The end."
    plan = {"lesson": "Teamwork."}
    safe_req = {"genre": "sci-fi"}
    res = run_validators(story, plan, safe_req, RULEBOOK)
    
    # It should fail because genre_drift has severity 'needs_revision'
    assert res["passed"] is False
    assert any(w["type"] == "genre_drift" for w in res["warnings"])

def test_missing_character_warning():
    story = "Title: Small Story\nThis story is about a brave robot. The end."
    plan = {"lesson": "Courage.", "characters": ["Zara"]}
    safe_req = {"genre": "adventure", "must_include": ["Zara"]}
    res = run_validators(story, plan, safe_req, RULEBOOK)
    
    assert any("Zara" in w["message"] for w in res["warnings"])
