"""
agents.py
=========
All LLM agent functions.  Every agent:
  - Accepts `rulebook` as its last parameter.
  - Builds its system prompt from rulebook values (no hardcoded constraints).
  - Returns a typed dict or plain string as documented.
  - Fails closed: returns a safe sentinel value on JSON parse errors.
"""

from __future__ import annotations
import json
from typing import TYPE_CHECKING

from app.models.schemas import (
    ControllerOutput,
    NormalizerOutput,
    PlannerOutput,
    JudgeVerdict,
    JudgeScores,
)
from app.services.openai_client import call_model
from app.core.logging_config import logger

if TYPE_CHECKING:
    from app.rules.rulebook import StoryRulebook


# ── Agent 1: Controller ───────────────────────────────────────────────────────

def controller_agent(user_input: str, prefs: dict, rulebook: "StoryRulebook") -> ControllerOutput:
    """
    Classifies the request and sets policy mode.
    Injects user preferences so downstream agents receive a unified config dict.
    """
    safety_block = rulebook.safety_rules_block()
    system_prompt = (
        "Role: classify and configure a bedtime-story request for children.\n"
        "Output: strict JSON only — no prose, no markdown fences.\n\n"
        "Required JSON fields:\n"
        '  "age_band"      : string  — always "5-10"\n'
        '  "genre"         : string  — the story genre\n'
        '  "theme"         : string  — central moral theme\n'
        '  "tone"          : string  — narrative tone\n'
        '  "length_target" : string  — "short" | "medium" | "long"\n'
        '  "must_include"  : list of strings — character names to include (strictly names only, no generic roles or elements)\n'
        '  "must_avoid"    : list of strings — content to exclude\n'
        '  "bedtime_mode"  : boolean — always true\n'
        '  "needs_outline" : boolean — always true\n\n'
        "Safety rules (enforce strictly):\n"
        f"{safety_block}\n\n"
        "If a field is missing or unclear, fill with a safe child-appropriate default."
    )
    user_content = (
        f"User story request: {user_input}\n\n"
        f"User preferences:\n{json.dumps(prefs, indent=2)}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    logger.info("Parsing request and applying safety policy...")
    try:
        resp = call_model(messages, rulebook, temperature=0.2, json_mode=True)
        return json.loads(resp)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Fallback triggered: {e}")
        return ControllerOutput(
            age_band="5-10",
            genre=prefs.get("genre", "fictional"),
            theme=prefs.get("theme", rulebook.default_theme),
            tone=prefs.get("tone", rulebook.default_tone),
            length_target="medium",
            must_include=[],
            must_avoid=list(rulebook.blocked_words[:5]),
            bedtime_mode=True,
            needs_outline=True,
        )


# ── Agent 2: Normalizer ───────────────────────────────────────────────────────

def normalizer_agent(controller_data: dict, rulebook: "StoryRulebook") -> NormalizerOutput:
    """
    Sanitizes unsafe or off-target requests before story generation begins.
    """
    safety_block = rulebook.safety_rules_block()
    system_prompt = (
        "Role: Sanitize a bedtime story configuration for child safety.\n"
        "Output: strict JSON only.\n\n"
        "Required JSON fields:\n"
        '  "approved_request"  : dict — safely modified copy of the input\n'
        '  "safety_flags"      : list of strings — issues found\n'
        '  "rewrites_applied": list of strings — summary of what was changed and why (do NOT include character name changes here, they belong ONLY in character_rewrites)\n'
        '  "character_rewrites": dict — mapping of {"original character name": "new safe character name"} if any characters were replaced for copyright or safety reasons\n\n'
        "IMPORTANT: Map exactly ONE requested character to exactly ONE approved replacement. Do not split one character into multiple characters. Example: 'iron man' -> 'Bolt the Brave Robot'. Avoid 1-to-many rewrites.\n\n"
        "If a field conflicts with any of these safety rules, rewrite it to the "
        "nearest safe alternative:\n"
        f"{safety_block}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(controller_data)},
    ]
    logger.info("Enforcing child-safety boundaries...")
    try:
        resp = call_model(messages, rulebook, temperature=0.1, json_mode=True)
        return json.loads(resp)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Fallback triggered: {e}")
        return NormalizerOutput(
            approved_request=controller_data,
            safety_flags=[],
            rewrites_applied=[],
            character_rewrites={},
        )


# ── Agent 3: Planner ──────────────────────────────────────────────────────────

def planner_agent(safe_req: dict, rulebook: "StoryRulebook") -> PlannerOutput:
    """
    Produces a 5-beat narrative outline from the sanitized request.
    """
    system_prompt = (
        "Role: create a 5-beat story outline for children aged "
        f"{rulebook.target_age_min}–{rulebook.target_age_max}.\n"
        "Output: strict JSON only.\n\n"
        "Required JSON fields:\n"
        '  "setting"     : string — where the story takes place\n'
        '  "characters"  : list of strings — strictly ONLY character names (e.g. "Nova"), no descriptions or roles.\n'
        '  "beats"       : list of exactly 5 strings — story progression\n'
        '  "lesson"      : string — the gentle moral to convey\n'
        '  "ending_mood" : string — emotional tone of the ending\n\n'
        "Hard constraints:\n"
        "- Preserve the requested genre strongly. If genre is sci-fi and setting is city, do not move the story into fantasy, forest, meadow, unicorn, magical kingdom, or enchanted forest unless requested.\n"
        "- If requested genre is sci-fi, use child-safe sci-fi elements (friendly robots, glowing city lights, moon buses, star parks, etc.).\n"
        "- Low-stakes conflict only\n"
        "- Simple cause-and-effect\n"
        "- Calm, reassuring ending\n"
        "- No graphic harm, no frightening resolution\n"
        "- Replace famous names and places with original child-safe alternatives.\n"
        f"- Story must fit within {rulebook.min_words}–{rulebook.max_words} words "
        "when written out, so keep the outline tight."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(safe_req)},
    ]
    logger.info("Building 5-beat outline...")
    try:
        resp = call_model(messages, rulebook, temperature=0.7, json_mode=True)
        return json.loads(resp)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Fallback triggered: {e}")
        return PlannerOutput(
            setting=rulebook.default_setting,
            characters=[],
            beats=["Setup", "Inciting incident", "Rising action", "Climax", "Resolution"],
            lesson=rulebook.default_theme,
            ending_mood="calm and cozy",
        )


# ── Agent 4: Storyteller ──────────────────────────────────────────────────────

def storyteller_agent(safe_req: dict, plan: dict, rulebook: "StoryRulebook") -> str:
    """
    Writes the prose based on the sanitized request and outline.
    Word-count constraint is stated explicitly to reduce overshoot.
    """
    system_prompt = (
        "Role: write a complete bedtime story from the approved outline.\n\n"
        "Format requirements:\n"
        "  Line 1: the story title (e.g. 'The Moonlit Adventure')\n"
        "  Remaining lines: story prose\n"
        "  Final 1–2 sentences: a gentle moral or lesson\n\n"
        f"Length: write between {rulebook.min_words} and {rulebook.max_words} words. "
        "Staying closer to the lower end is better than overshooting.\n\n"
        "Style rules:\n"
        "- Preserve the requested genre and setting strongly. Do not drift into fantasy if sci-fi is requested.\n"
        "- Warm, concrete, simple language for ages 5–10.\n"
        "- Short sentences. No complex clauses.\n"
        "- Preserve all character names and settings from the outline.\n"
        "- End with emotional calm and a sense of safety.\n"
        "- Return ONLY the story text — no commentary, no word counts, no JSON."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps({"request": safe_req, "outline": plan}),
        },
    ]
    logger.info("Writing story draft...")
    return call_model(messages, rulebook, max_tokens=1200, temperature=0.8, json_mode=False)


# ── Agent 5: Judge ────────────────────────────────────────────────────────────

def judge_agent(story: str, safe_req: dict, plan: dict, rulebook: "StoryRulebook") -> JudgeVerdict:
    """
    Evaluates the story against the 8-dimension rubric.
    Evaluates against actual approved user intent (genre, setting, theme, rewritten characters).
    Returns strict JSON including per-dimension scores and actionable feedback.
    """
    rubric_block = rulebook.rubric_block()
    score_fields = "\n".join(
        f'        "{dim}": <integer 1-5>'
        for dim in rulebook.judging_rubric
    )
    
    expected_genre = safe_req.get("genre", "Unknown")
    expected_theme = safe_req.get("theme", "Unknown")
    expected_setting = plan.get("setting", "Unknown")
    expected_chars = ", ".join(plan.get("characters", []))

    system_prompt = (
        "Role: evaluate a children's bedtime story. Return strict JSON only.\n\n"
        "Score each dimension 1–5 (5 = excellent). Then decide overall pass/fail.\n"
        "A story passes only if ALL dimensions score ≥ 3 AND no must_fix issues.\n\n"
        "--- APPROVED STORY INTENT ---\n"
        f"Genre: {expected_genre}\n"
        f"Theme: {expected_theme}\n"
        f"Setting: {expected_setting}\n"
        f"Characters: {expected_chars}\n"
        "Evaluate alignment and reasoning strictly against this intent, NOT what you assume. "
        "If the genre is sci-fi, evaluate it as sci-fi, NOT fantasy. If it drifts into fantasy/magic, score user_alignment lower and request revision.\n"
        "-----------------------------\n\n"
        "Dimensions to score:\n"
        f"{rubric_block}\n\n"
        "Required JSON structure:\n"
        "{\n"
        '  "overall_pass": <boolean>,\n'
        '  "scores": {\n'
        f"{score_fields}\n"
        "  },\n"
        '  "must_fix": [<list of critical issues that block approval>],\n'
        '  "should_fix": [<list of minor improvement suggestions>],\n'
        '  "reasoning_summary": "<2–3 sentence plain-English explanation>",\n'
        '  "verdict": "<approved | needs_revision | failed>"\n'
        "}\n\n"
        "Be specific in must_fix — vague feedback like 'improve story' is not helpful. "
        "If the story is good, must_fix must be an empty list."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Story to evaluate:\n\n{story}"},
    ]
    logger.info("Evaluating against 8-dimension rubric...")
    try:
        resp = call_model(messages, rulebook, temperature=0.1, json_mode=True)
        result = json.loads(resp)

        # Ensure required keys are present; fill safe defaults if missing
        result.setdefault("overall_pass", False)
        result.setdefault("scores", {})
        result.setdefault("must_fix", [])
        result.setdefault("should_fix", [])
        result.setdefault("reasoning_summary", "No summary provided.")
        result.setdefault("verdict", "needs_revision")
        result["invalid_schema"] = False
        return result

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"CRITICAL: returned invalid JSON — {e}")
        return JudgeVerdict(
            overall_pass=False,
            scores=JudgeScores(
                user_alignment=0,
                age_appropriateness=0,
                emotional_safety=0,
                coherence_continuity=0,
                bedtime_suitability=0,
                vocabulary_readability=0,
                engagement=0,
                moral_subtlety=0,
            ),
            must_fix=["Judge failed to return valid JSON. Story must be re-evaluated."],
            should_fix=[],
            reasoning_summary="Judge node error — could not parse evaluation.",
            verdict="failed",
            invalid_schema=True,
        )


# ── Agent 6: Reviser ──────────────────────────────────────────────────────────

def reviser_agent(story: str, issues: list, word_count: int, safe_req: dict, plan: dict, rulebook: "StoryRulebook", stagnation_mode: bool = False) -> str:
    """
    Surgically fixes the given issues while preserving the story's strengths.
    Preserves user alignment (genre, setting, tone).
    """
    revision_rules = rulebook.revision_rules_block()

    length_instruction = ""
    if word_count > rulebook.max_words:
        length_instruction = (
            f"\nLENGTH REDUCTION REQUIRED:\n"
            f"Current count: {word_count} words. Target: under {rulebook.max_words} words.\n"
            "To reduce length you MUST: remove entire scenes if needed, shorten all "
            "descriptions to one sentence, combine dialogue exchanges, and cut filler "
            "phrases. Do NOT add new plot points. Rewrite the full story shorter.\n"
        )
        
    stagnation_instruction = ""
    if stagnation_mode:
        stagnation_instruction = (
            "\nSTAGNATION DETECTED: Your previous revision failed to fix the issues. "
            "You MUST apply a stronger, more noticeable change this time.\n"
        )

    system_prompt = (
        "Role: revise a children's bedtime story to fix the listed issues.\n\n"
        f"Current word count: {word_count}\n"
        f"Required word count range: {rulebook.min_words}–{rulebook.max_words} words\n"
        f"{length_instruction}"
        f"{stagnation_instruction}\n"
        "--- ALIGNMENT RULES ---\n"
        f"You MUST strictly preserve the following elements:\n"
        f"Genre: {safe_req.get('genre')}\n"
        f"Setting: {plan.get('setting')}\n"
        f"Theme: {safe_req.get('theme')}\n"
        "Do not drift from this setting or genre (e.g., do not turn a sci-fi city into a magical forest unless explicitly requested).\n"
        "-----------------------\n\n"
        "When 'genre_drift' is detected in the issues:\n"
        "- Preserve the original requested genre and setting.\n"
        "- Remove fantasy elements.\n"
        "- Replace fantasy terms with child-safe sci-fi equivalents (e.g. dragon -> helper drone, spell -> signal, enchanted forest -> quiet city park, magical kingdom -> starlit space station).\n\n"
        "Revision rules:\n"
        f"{revision_rules}\n\n"
        "IMPORTANT: address every issue in the list. Do not invent new problems.\n"
        "Return ONLY the revised story text — same format as the original "
        "(title on line 1, prose, ending moral). No commentary."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Story:\n{story}\n\n"
                f"Issues to fix:\n{json.dumps(issues, indent=2)}"
            ),
        },
    ]
    logger.info("Applying targeted fixes...")
    return call_model(messages, rulebook, max_tokens=1200, temperature=0.5, json_mode=False)


# ── Agent 7: Compressor ───────────────────────────────────────────────────────

def compressor_agent(
    story: str,
    current_word_count: int,
    rulebook: "StoryRulebook",
    stagnation_mode: bool = False,
) -> str:
    """
    Dedicated length-compression agent.  Its ONLY job is to bring the story
    under max_words while preserving the title, characters, setting, and moral.

    Temperature is deliberately low (0.3) to prioritise compliance over creativity.
    """
    stagnation_instruction = ""
    if stagnation_mode:
        stagnation_instruction = (
            "\nSTAGNATION DETECTED: Previous compression attempts were not aggressive enough. "
            "You MUST make drastic cuts to meet the word limit.\n"
        )

    system_prompt = (
        f"Role: compress a children's bedtime story.\n\n"
        f"Current word count : {current_word_count}\n"
        f"Target word count  : UNDER {rulebook.max_words} words\n\n"
        f"{rulebook.compressor_goal}\n"
        f"{stagnation_instruction}\n"
        "Approach:\n"
        "1. Identify the longest descriptive passages and shorten them.\n"
        "2. Remove filler sentences that don't advance the plot.\n"
        "3. Condense dialogue where possible.\n"
        "4. Keep the title (line 1), all character names, the setting, and the moral.\n"
        "5. Do NOT add new scenes or characters.\n\n"
        "Return ONLY the compressed story text. No word count, no commentary."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Story to compress:\n\n{story}"},
    ]
    logger.info(
        f"Story is {current_word_count} words "
        f"(limit: {rulebook.max_words}). Compressing..."
    )
    return call_model(messages, rulebook, max_tokens=1000, temperature=0.3, json_mode=False)


# ── Agent 8: Expander ─────────────────────────────────────────────────────────

def expander_agent(
    story: str,
    current_word_count: int,
    rulebook: "StoryRulebook",
    stagnation_mode: bool = False,
) -> str:
    """
    Dedicated length-expansion agent. Its ONLY job is to bring the story
    above min_words without exceeding max_words.
    """
    stagnation_instruction = ""
    if stagnation_mode:
        stagnation_instruction = (
            "\nSTAGNATION DETECTED: Previous expansion attempts did not add enough words. "
            "You MUST add significantly more detail to meet the minimum word limit.\n"
        )

    system_prompt = (
        f"Role: expand a children's bedtime story.\n\n"
        f"Current word count : {current_word_count}\n"
        f"Target word count  : BETWEEN {rulebook.min_words} and {rulebook.max_words} words\n\n"
        f"{rulebook.expander_goal}\n"
        f"{stagnation_instruction}\n"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Story to expand:\n\n{story}"},
    ]
    logger.info(
        f"Story is {current_word_count} words "
        f"(limit: {rulebook.min_words}-{rulebook.max_words}). Expanding..."
    )
    return call_model(messages, rulebook, max_tokens=1500, temperature=0.6, json_mode=False)

