"""
schemas.py
==========
TypedDict definitions for every structured payload that flows between agents.
Importing these gives editors type-checking and makes the pipeline contract explicit without requiring Pydantic.
"""

from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Controller ────────────────────────────────────────────────────────────────

class ControllerOutput(TypedDict):
    age_band: str
    genre: str
    theme: str
    tone: str
    length_target: str
    must_include: List[str]
    must_avoid: List[str]
    bedtime_mode: bool
    needs_outline: bool


# ── Normalizer ────────────────────────────────────────────────────────────────

class NormalizerOutput(TypedDict):
    approved_request: Dict[str, Any]
    safety_flags: List[str]
    rewrites_applied: List[str]
    character_rewrites: Dict[str, str]


# ── Planner ───────────────────────────────────────────────────────────────────

class PlannerOutput(TypedDict):
    setting: str
    characters: List[str]
    beats: List[str]       # exactly 5 beats
    lesson: str
    ending_mood: str


# ── Judge ─────────────────────────────────────────────────────────────────────

class JudgeScores(TypedDict):
    user_alignment: int
    age_appropriateness: int
    emotional_safety: int
    coherence_continuity: int
    bedtime_suitability: int
    vocabulary_readability: int
    engagement: int
    moral_subtlety: int


class JudgeVerdict(TypedDict):
    overall_pass: bool
    scores: JudgeScores
    must_fix: List[str]
    should_fix: List[str]
    reasoning_summary: str
    verdict: str            # "approved" | "needs_revision" | "failed"
    invalid_schema: bool    # True if the LLM returned malformed JSON


# ── Validators ────────────────────────────────────────────────────────────────

class ValidatorMetrics(TypedDict):
    word_count: int


class ValidatorResult(TypedDict):
    passed: bool
    hard_fail: bool         # True = must not ship without fixing
    failures: List[str]     # hard failures
    warnings: List[Dict[str, str]]     # structured warnings: type, severity, message
    metrics: ValidatorMetrics


# ── Audit trail ───────────────────────────────────────────────────────────────

class AuditEvent(TypedDict):
    step: str
    input_summary: str
    output_summary: str
    word_count: Optional[int]
    status: str             # "pass" | "fail" | "info"
    issues: List[str]
    action: str             # what was done next
    route_selected: Optional[str]
    reason_for_route: Optional[str]


# ── User preferences ───────────────────────────────────────

class StoryPreferences(TypedDict):
    genre: str              # required
    characters: str         # optional
    setting: str            # optional
    theme: str              # optional
    tone: str               # optional


class StoryRequest(BaseModel):
    """Pydantic model used by FastAPI to validate incoming JSON requests."""
    genre: str = Field(..., min_length=2, max_length=40)
    characters: Optional[str] = Field(None, max_length=100)
    setting: Optional[str] = Field(None, max_length=100)
    theme: Optional[str] = Field(None, max_length=100)
    tone: Optional[str] = Field(None, max_length=100)


# ── What-changed summary (between two drafts) ────────────────────────────────

class ChangeSummary(TypedDict):
    route_selected: str
    reason_for_route: str
    old_word_count: int
    new_word_count: int
    validator_failures_before: List[str]
    validator_failures_after: List[str]
    judge_verdict_before: str
    judge_verdict_after: str
    issues_fixed: List[str]
    issues_remaining: List[str]


# ── Session object ────────────────────────────────────────────────────────────

class StorySession(TypedDict):
    session_id: str
    created_at: str                 # ISO-8601 timestamp
    status: str                           # "approved" | "failed_validation" | "needs_user_retry"
    user_preferences: Dict[str, Any]
    rulebook_snapshot: Dict[str, Any]
    character_rewrites: Dict[str, str]    # For frontend display
    original_story: str
    final_story: str
    revision_history: List[str]          # one entry per draft (including original)
    change_summaries: List[ChangeSummary] # one entry per revision (len = revision_history - 1)
    judge_verdicts: List[JudgeVerdict]
    validator_results: List[ValidatorResult]
    audit_trail: List[AuditEvent]
    failure_reason: Optional[str]         # populated when status != "approved"
