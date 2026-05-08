"""
rulebook.py
===========
Single source of truth for every constraint, rubric, and policy used by all
agents. Import RULEBOOK from here; never hardcode limits anywhere else.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.core.config import settings


@dataclass(frozen=True)
class StoryRulebook:
    # ── Age & length ──────────────────────────────────────────────────────────
    target_age_min: int = 5
    target_age_max: int = 10
    min_words: int = settings.STORY_MIN_WORDS
    max_words: int = settings.STORY_MAX_WORDS
    max_revision_attempts: int = settings.MAX_REVISION_ATTEMPTS

    # ── Tone ─────────────────────────────────────────────────────────────────
    allowed_tones: tuple = (
        "calm",
        "whimsical",
        "magical",
        "gentle",
        "adventurous",
        "cozy",
        "hopeful",
    )

    # ── Bedtime safety rules ──────────
    bedtime_safety_rules: tuple = (
        "The story must be appropriate for children aged 5–10.",
        "No violence, gore, or graphic harm of any kind.",
        "No frightening monsters, jump-scares, or horror elements.",
        "No adult themes, romance, or sexual content.",
        "No death portrayed in a traumatic or realistic way.",
        "Conflict must be low-stakes and resolve peacefully.",
        "End with emotional calm and a sense of safety.",
        "Vocabulary must be simple enough for a 7-year-old to follow.",
        "No famous copyrighted character names, team names, universe names, or fictional locations (e.g. Metropolis). Replace them with original child-safe alternatives.",
        "Prefer gentle emotional words like nervous, unsure, worried, or shy instead of intense words like terrified, cowered, panic, or fear."
    )

    # ── Blocked content ───────────
    blocked_words: tuple = (
        "violence",
        "violent",
        "blood",
        "gore",
        "death",
        "dead",
        "murder",
        "kill",
        "killed",
        "scary",
        "terrifying",
        "nightmare",
        "horror",
        "weapon",
        "gun",
        "knife",
        "stab",
        "explode",
        "explosion",
        "abuse",
        "drug",
        "alcohol",
    )

    # ── Required fields in the final story object ─────────────────────────────
    required_output_fields: tuple = ("title", "story_body", "moral")

    # ── 8-dimension judging rubric (name → description) ──────────────────────
    judging_rubric: Dict[str, str] = field(default_factory=lambda: {
        "user_alignment": (
            "Does the story match the genre, characters, setting, theme, and "
            "tone the user requested?"
        ),
        "age_appropriateness": (
            "Is the vocabulary, complexity, and content right for ages 5–10?"
        ),
        "emotional_safety": (
            "Is the story free of frightening, traumatic, or distressing content?"
        ),
        "coherence_continuity": (
            "Does the story flow logically from setup to resolution with no "
            "plot holes?"
        ),
        "bedtime_suitability": (
            "Does the story end with calm, closure, and a feeling of safety that "
            "helps a child wind down?"
        ),
        "vocabulary_readability": (
            "Are sentences short and words accessible to early readers?"
        ),
        "engagement": (
            "Is the story interesting and imaginative enough to hold a child's "
            "attention?"
        ),
        "moral_subtlety": (
            "Is the lesson woven naturally into the story rather than stated "
            "heavy-handedly?"
        ),
    })

    # ── Revision rules ────────────
    revision_rules: tuple = (
        "Preserve character names, setting, and the core moral.",
        "Do not introduce new frightening or unsafe elements.",
        "Keep the ending calm and emotionally reassuring."
        f"The revised story MUST be between 80 and 300 words.",
    )

    # ── Compressor-specific instruction ──────────────────────────────────────
    compressor_goal: str = (
        "Your ONLY job is to shorten the story to fit within the word limit. "
        "Preserve the title, all character names, the setting, and the moral. "
        "Do NOT add new scenes. Trim descriptions and dialogue. "
        "Return ONLY the compressed story text with no commentary."
    )

    # ── Expander-specific instruction ────────────────────────────────────────
    expander_goal: str = (
        "Your ONLY job is to expand the story to meet the minimum word limit. "
        "Add gentle sensory details, smoother transitions, and a calmer bedtime ending. "
        "Preserve genre, characters, setting, and moral. "
        "Do not add scary, violent, mature, or unsafe content. "
        "Return ONLY the revised story text with no commentary."
    )

    # ── Default user-preference fallbacks ────────────────────────────────────
    default_tone: str = "calm and magical"
    default_theme: str = "kindness and friendship"
    default_setting: str = "a cozy forest village"

    # ── Model config (single place) ───────────────────────────────────────────
    model_name: str = settings.OPENAI_MODEL

    def safety_rules_block(self) -> str:
        """Returns safety rules as a numbered string for prompt injection."""
        return "\n".join(f"{i+1}. {r}" for i, r in enumerate(self.bedtime_safety_rules))

    def rubric_block(self) -> str:
        """Returns rubric dimensions as a labelled string for prompt injection."""
        return "\n".join(
            f"  - {name}: {desc}"
            for name, desc in self.judging_rubric.items()
        )

    def revision_rules_block(self) -> str:
        return "\n".join(f"- {r}" for r in self.revision_rules)


# ── Module-level singleton loaded once at startup ────────────────────────────
RULEBOOK = StoryRulebook()
