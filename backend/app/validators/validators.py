"""
validators.py
=============
Deterministic, zero-LLM checks.  These are the ground-truth gate: a story
cannot be marked "approved" unless all hard validators pass.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from app.models.schemas import ValidatorResult, ValidatorMetrics
from app.utils.text_utils import count_words, classify_word_count

if TYPE_CHECKING:
    from app.rules.rulebook import StoryRulebook


# ── Main validator ────────────────────────────────────────────────────────────

def normalize_required_characters(plan: dict, approved_preferences: dict) -> list[str]:
    """
    Filters out generic phrases and roles from the planner's characters list.
    Prefer approved_characters from the normalizer/planner over raw user input.
    """
    approved_chars = approved_preferences.get("must_include", [])

    valid_chars = set()
    
    # Only Add explicitly approved characters (must_include)
    # These are the only characters we strictly require.
    for c in approved_chars:
        c_clean = c.strip()
        if c_clean:
            valid_chars.add(c_clean)

    return list(valid_chars)


def run_validators(
    story: str,
    plan: dict,
    safe_req: dict,
    rulebook: "StoryRulebook",
) -> ValidatorResult:
    """
    Run all deterministic checks.

    Hard failures (hard_fail=True) block approval:
      1. Story is empty
      2. Word count outside [min_words, max_words]
      3. No title detected
      4. No moral/lesson detected

    Soft warnings (do not block but are reported):
      5. Required characters from user prefs missing
      6. Blocked content words found
    """
    failures: list[str] = []
    warnings: list[dict[str, str]] = []
    word_count = count_words(story)

    # ── 1. Empty story ────────────────────────────────────────────────────────
    if not story or not story.strip():
        failures.append("Story is empty.")

    # ── 2. Word count ─────────────────────────────────────────────────────────
    if word_count < rulebook.min_words:
        failures.append(
            f"Story is too short: {word_count} words "
            f"(minimum is {rulebook.min_words})."
        )
    elif word_count > rulebook.max_words:
        failures.append(
            f"Story is too long: {word_count} words "
            f"(maximum is {rulebook.max_words})."
        )

    # ── 3. Title present ─────────────────────────────────────────────────────
    # Accept "Title: ..." or a short first line (≤10 words) as the title.
    story_stripped = story.strip()
    first_line = story_stripped.split("\n")[0].strip()
    has_title = (
        first_line.lower().startswith("title:")
        or (0 < len(first_line.split()) <= 10 and len(first_line) > 0)
    )
    if not has_title:
        failures.append("No title detected. The story should start with a title.")

    # ── 4. Moral / lesson present ────────────────────────────────────────────
    moral_keywords = ("moral:", "lesson:", "remember:", "the end.", "and so", "learned")
    story_lower = story.lower()
    has_moral = any(kw in story_lower for kw in moral_keywords)
    # Also check if planner lesson appears in story
    planner_lesson = plan.get("lesson", "")
    if planner_lesson:
        first_word_of_lesson = planner_lesson.split()[0].lower() if planner_lesson.split() else ""
        if first_word_of_lesson and first_word_of_lesson in story_lower:
            has_moral = True
    if not has_moral:
        failures.append(
            "No moral or lesson detected. The story should convey a gentle lesson."
        )

    # ── 5. Required characters ────────────────────────────────────────
    characters = normalize_required_characters(plan, safe_req)
    # Update the planner data to only contain actual character names as requested
    plan["characters"] = characters

    for char in characters:
        char_name = char.strip()
        if char_name and char_name.lower() not in story_lower:
            warnings.append({
                "type": "missing_character",
                "severity": "warning",
                "message": f"Character '{char_name}' from the plan was not found in the story."
            })

    # ── 6. Blocked content ────────────────────────────────────────────
    found_blocked = [
        w for w in rulebook.blocked_words if w.lower() in story_lower
    ]
    if found_blocked:
        warnings.append({
            "type": "blocked_content",
            "severity": "warning",
            "message": f"Potentially unsafe words found: {', '.join(found_blocked)}. Review for child-safety."
        })

    # ── 7. Semantic drift check ───────────────────────────────────────
    req_genre = safe_req.get("genre", "").lower()
    if req_genre == "sci-fi":
        fantasy_words = ['unicorn', 'enchanted forest', 'magic kingdom', 'fairy', 'wizard', 'spell', 'dragon', 'magic wand']
        found_drift = [w for w in fantasy_words if w.lower() in story_lower]
        if found_drift:
            # Check if user explicitly requested these words
            explicit_chars = safe_req.get("characters", "").lower()
            explicit_setting = safe_req.get("setting", "").lower()
            if not any(w in explicit_chars or w in explicit_setting for w in found_drift):
                warnings.append({
                    "type": "genre_drift",
                    "severity": "needs_revision",
                    "message": f"Potential genre drift: requested sci-fi but found fantasy words: {', '.join(found_drift)}."
                })

    passed = len(failures) == 0 and not any(w.get("severity") == "needs_revision" for w in warnings)
    hard_fail = not passed

    return ValidatorResult(
        passed=passed,
        hard_fail=hard_fail,
        failures=failures,
        warnings=warnings,
        metrics=ValidatorMetrics(word_count=word_count),
    )


def is_length_only_failure(val_result: ValidatorResult) -> bool:
    """
    Returns True if the *only* hard failure is a word-count violation.
    Used by main.py to route to compressor_agent instead of full reviser.
    """
    length_keywords = ("too short", "too long", "words")
    return (
        val_result["hard_fail"]
        and all(
            any(kw in f.lower() for kw in length_keywords)
            for f in val_result["failures"]
        )
    )
