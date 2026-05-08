import uuid
from datetime import datetime, timezone
from typing import Optional

from app.rules.rulebook import RULEBOOK
from app.models.schemas import (
    AuditEvent,
    ChangeSummary,
    StorySession,
    StoryPreferences,
)
from app.utils.text_utils import (
    count_words,
    classify_word_count,
    trim_story_to_max_words,
)
from app.validators.validators import run_validators
from app.services.agents import (
    controller_agent,
    normalizer_agent,
    planner_agent,
    storyteller_agent,
    judge_agent,
    reviser_agent,
    compressor_agent,
    expander_agent,
)
from app.core.logging_config import logger

def _make_audit_event(
    step: str,
    input_summary: str,
    output_summary: str,
    word_count: Optional[int],
    status: str,
    issues: list,
    action: str,
    route_selected: Optional[str] = None,
    reason_for_route: Optional[str] = None,
) -> AuditEvent:
    return AuditEvent(
        step=step,
        input_summary=input_summary,
        output_summary=output_summary,
        word_count=word_count,
        status=status,
        issues=issues,
        action=action,
        route_selected=route_selected,
        reason_for_route=reason_for_route,
    )

def _build_change_summary(
    route_selected: str,
    reason_for_route: str,
    old_wc: int,
    new_wc: int,
    val_fails_before: list,
    val_fails_after: list,
    judge_before: str,
    judge_after: str,
    all_issues_before: list,
    all_issues_after: list,
) -> ChangeSummary:
    issues_fixed = [i for i in all_issues_before if i not in all_issues_after]
    remaining = [i for i in all_issues_after]
    
    return ChangeSummary(
        route_selected=route_selected,
        reason_for_route=reason_for_route,
        old_word_count=old_wc,
        new_word_count=new_wc,
        validator_failures_before=val_fails_before,
        validator_failures_after=val_fails_after,
        judge_verdict_before=judge_before,
        judge_verdict_after=judge_after,
        issues_fixed=issues_fixed,
        issues_remaining=remaining,
    )

def generate_story_session(preferences: StoryPreferences) -> StorySession:
    """
    Runs the full multi-agent pipeline and returns a StorySession.
    API-ready: performs no CLI printing directly.
    """
    session_id      = str(uuid.uuid4())[:8]
    created_at      = datetime.now(timezone.utc).isoformat()
    audit_trail     : list[AuditEvent]    = []
    revision_history: list[str]           = []
    change_summaries: list[ChangeSummary] = []
    judge_verdicts  : list                = []
    validator_results: list               = []

    parts = [f"A {preferences['genre']} bedtime story"]
    if preferences.get('characters'): parts.append(f"featuring {preferences['characters']}")
    if preferences.get('setting'): parts.append(f"set in {preferences['setting']}")
    if preferences.get('theme'): parts.append(f"about {preferences['theme']}")
    if preferences.get('tone'): parts.append(f"with a {preferences['tone']} tone")
    raw_input = " ".join(parts) + "."

    ctrl = controller_agent(raw_input, preferences, RULEBOOK)
    safe_out = normalizer_agent(ctrl, RULEBOOK)
    safe = safe_out.get("approved_request", ctrl)

    rewrites = safe_out.get("rewrites_applied", [])
    
    # Filter out redundant normalizer messages about characters
    setup_issues = [r for r in rewrites if "character" not in r.lower()]
    
    plan = planner_agent(safe, RULEBOOK)
    
    # Compute user-facing character rewrites
    user_chars_str = preferences.get("characters", "").strip()
    norm_char_rewrites = safe_out.get("character_rewrites", {})
    
    user_facing_rewrites = {}
    if user_chars_str and norm_char_rewrites:
        user_list = [c.strip() for c in user_chars_str.split(",") if c.strip()]
        norm_values = list(norm_char_rewrites.values())
        
        if len(user_list) == 1 and len(norm_values) > 0:
            safe_c_title = norm_values[0].title() if norm_values[0] else norm_values[0]
            user_facing_rewrites[user_list[0]] = safe_c_title
            setup_issues.append(f"Character rewrite: '{user_list[0]}' was replaced with '{safe_c_title}' to keep the story original and safe.")
        elif len(user_list) == len(norm_values):
            for orig, safe_c in zip(user_list, norm_values):
                safe_c_title = safe_c.title() if safe_c else safe_c
                user_facing_rewrites[orig] = safe_c_title
                setup_issues.append(f"Character rewrite: '{orig}' was replaced with '{safe_c_title}' to keep the story original and safe.")
        else:
            for orig, safe_c in norm_char_rewrites.items():
                safe_c_title = safe_c.title() if safe_c else safe_c
                user_facing_rewrites[orig] = safe_c_title
                setup_issues.append(f"Character rewrite: '{orig}' was replaced with '{safe_c_title}' to keep the story original and safe.")
    else:
        for orig, safe_c in norm_char_rewrites.items():
            safe_c_title = safe_c.title() if safe_c else safe_c
            user_facing_rewrites[orig] = safe_c_title
            setup_issues.append(f"Character rewrite: '{orig}' was replaced with '{safe_c_title}' to keep the story original and safe.")

    audit_trail.append(_make_audit_event(
        step="setup",
        input_summary=f"genre={preferences['genre']} | tone={preferences.get('tone', '')}",
        output_summary=(
            f"setting={plan.get('setting')} | "
            f"characters={plan.get('characters')} | "
            f"lesson={plan.get('lesson')}"
        ),
        word_count=None,
        status="info",
        issues=setup_issues,
        action="proceed_to_draft",
    ))

    # Initial draft
    story = storyteller_agent(safe, plan, RULEBOOK)
    original_story = story
    revision_history.append(story)
    
    audit_trail.append(_make_audit_event(
        step="draft_created",
        input_summary="plan",
        output_summary="first draft written",
        word_count=count_words(story),
        status="info",
        issues=[],
        action="evaluate",
    ))
    
    val = run_validators(story, plan, safe, RULEBOOK)
    verdict = judge_agent(story, safe, plan, RULEBOOK)
    validator_results.append(val)
    judge_verdicts.append(verdict)
    
    wc = val["metrics"]["word_count"]
    needs_revision_warnings = [w["message"] for w in val["warnings"] if w.get("severity") == "needs_revision"]
    all_issues = val["failures"] + verdict.get("must_fix", []) + needs_revision_warnings
    
    final_status = "failed_validation"
    failure_reason: Optional[str] = None
    
    stagnation_count = 0
    prev_story = ""
    prev_wc = 0
    prev_issues = []

    for attempt in range(RULEBOOK.max_revision_attempts):
        both_pass = val["passed"] and verdict.get("overall_pass", False)
        
        eval_step = "evaluate_initial" if attempt == 0 else f"evaluate_revision_{attempt}"
        
        if both_pass:
            audit_trail.append(_make_audit_event(
                step=eval_step,
                input_summary=f"draft_{attempt + 1} | {wc} words",
                output_summary="validators=PASS | judge=APPROVED",
                word_count=wc,
                status="pass",
                issues=[],
                action="finalize",
                route_selected="finalize",
                reason_for_route="All validators and judge criteria passed."
            ))
            break

        stagnation_mode = False
        if attempt > 0:
            same_failures_persist = any(i in all_issues for i in prev_issues)
            if story == prev_story or (abs(wc - prev_wc) < 5 and same_failures_persist):
                stagnation_count += 1
                stagnation_mode = True
                
                audit_trail.append(_make_audit_event(
                    step=f"stagnation_detected_{attempt}",
                    input_summary=f"draft_{attempt+1}",
                    output_summary="stagnation detected",
                    word_count=wc,
                    status="warning",
                    issues=[],
                    action="apply_stronger_instructions"
                ))
                
                if stagnation_count >= 2:
                    failure_reason = "System stagnated. Two consecutive revisions failed to make meaningful progress."
                    final_status = "failed_validation"
                    
                    audit_trail.append(_make_audit_event(
                        step=eval_step,
                        input_summary=f"draft_{attempt + 1} | {wc} words",
                        output_summary="validators=FAIL | judge=REJECTED | STAGNATED",
                        word_count=wc,
                        status="fail",
                        issues=all_issues,
                        action="failed_validation",
                        route_selected="failed_validation",
                        reason_for_route=failure_reason
                    ))
                    break
            else:
                stagnation_count = 0

        prev_story = story
        prev_wc = wc
        prev_issues = all_issues
        
        length_class = classify_word_count(wc, RULEBOOK.min_words, RULEBOOK.max_words)
        old_val = val
        old_verdict = verdict
        
        if length_class == "too_short":
            route = "expander"
            reason = f"Story is too short: {wc} words < {RULEBOOK.min_words} minimum."
            
            audit_trail.append(_make_audit_event(
                step=eval_step,
                input_summary=f"draft_{attempt + 1} | {wc} words",
                output_summary="validators=FAIL | judge=REJECTED",
                word_count=wc,
                status="fail",
                issues=all_issues,
                action="revise",
                route_selected=route,
                reason_for_route=reason
            ))
            
            story = expander_agent(story, wc, RULEBOOK, stagnation_mode)
            
        elif length_class == "too_long":
            route = "compressor"
            reason = f"Story is too long: {wc} words > {RULEBOOK.max_words} maximum."
            
            audit_trail.append(_make_audit_event(
                step=eval_step,
                input_summary=f"draft_{attempt + 1} | {wc} words",
                output_summary="validators=FAIL | judge=REJECTED",
                word_count=wc,
                status="fail",
                issues=all_issues,
                action="revise",
                route_selected=route,
                reason_for_route=reason
            ))
            
            story = compressor_agent(story, wc, RULEBOOK, stagnation_mode)
            new_wc = count_words(story)
            if new_wc > RULEBOOK.max_words:
                story = trim_story_to_max_words(story, RULEBOOK.max_words)
                audit_trail.append(_make_audit_event(
                    step=f"deterministic_trim_{attempt + 1}",
                    input_summary=f"post-compressor | {new_wc} words",
                    output_summary=f"trimmed to {count_words(story)} words",
                    word_count=count_words(story),
                    status="info",
                    issues=["Compressor exceeded word limit; deterministic trim applied."],
                    action="continue_to_validation",
                ))
        else:
            route = "reviser"
            reason = f"Word count is within range ({wc} words). Routing to Reviser Agent for quality/content issues."
            
            audit_trail.append(_make_audit_event(
                step=eval_step,
                input_summary=f"draft_{attempt + 1} | {wc} words",
                output_summary="validators=FAIL | judge=REJECTED",
                word_count=wc,
                status="fail",
                issues=all_issues,
                action="revise",
                route_selected=route,
                reason_for_route=reason
            ))
            
            story = reviser_agent(story, all_issues, wc, safe, plan, RULEBOOK, stagnation_mode)

        new_wc = count_words(story)
        
        audit_trail.append(_make_audit_event(
            step=f"revision_{attempt + 1}",
            input_summary=f"draft_{attempt + 1} | {prev_wc} words",
            output_summary=f"draft_{attempt + 2} | {new_wc} words",
            word_count=new_wc,
            status="info",
            issues=prev_issues,
            action="evaluate",
        ))

        val = run_validators(story, plan, safe, RULEBOOK)
        verdict = judge_agent(story, safe, plan, RULEBOOK)
        validator_results.append(val)
        judge_verdicts.append(verdict)
        wc = val["metrics"]["word_count"]
        needs_revision_warnings = [w["message"] for w in val["warnings"] if w.get("severity") == "needs_revision"]
        all_issues = val["failures"] + verdict.get("must_fix", []) + needs_revision_warnings

        cs = _build_change_summary(
            route_selected=route,
            reason_for_route=reason,
            old_wc=prev_wc,
            new_wc=wc,
            val_fails_before=old_val["failures"],
            val_fails_after=val["failures"],
            judge_before=old_verdict.get("verdict", "unknown"),
            judge_after=verdict.get("verdict", "unknown"),
            all_issues_before=prev_issues,
            all_issues_after=all_issues
        )
        change_summaries.append(cs)
        revision_history.append(story)

    both_pass = val["passed"] and verdict.get("overall_pass", False)
    if both_pass:
        final_status = "approved"
        # If it passes on the very last attempt, we need to log evaluate_revision_X
        # because the loop will break before logging it
        if len(revision_history) > 1:
            audit_trail.append(_make_audit_event(
                step=f"evaluate_revision_{len(revision_history) - 1}",
                input_summary=f"draft_{len(revision_history)} | {wc} words",
                output_summary="validators=PASS | judge=APPROVED",
                word_count=wc,
                status="pass",
                issues=[],
                action="finalize",
                route_selected="finalize",
                reason_for_route="All validators and judge criteria passed."
            ))
    elif final_status != "failed_validation":
        failure_reason = f"Story did not pass after {RULEBOOK.max_revision_attempts} revision(s). Remaining issues: {all_issues}"
        final_status = "failed_validation"
        
        audit_trail.append(_make_audit_event(
            step=f"evaluate_revision_{len(revision_history) - 1}",
            input_summary=f"draft_{len(revision_history)} | {wc} words",
            output_summary="validators=FAIL | judge=REJECTED",
            word_count=wc,
            status="fail",
            issues=all_issues,
            action="failed_validation",
            route_selected="failed_validation",
            reason_for_route=failure_reason
        ))

    rulebook_snapshot = {
        "min_words":            RULEBOOK.min_words,
        "max_words":            RULEBOOK.max_words,
        "max_revision_attempts":RULEBOOK.max_revision_attempts,
        "model":                RULEBOOK.model_name,
        "target_age":           f"{RULEBOOK.target_age_min}–{RULEBOOK.target_age_max}",
    }

    return StorySession(
        session_id=session_id,
        created_at=created_at,
        status=final_status,
        user_preferences=dict(preferences),
        rulebook_snapshot=rulebook_snapshot,
        character_rewrites=user_facing_rewrites,
        original_story=original_story,
        final_story=story,
        revision_history=revision_history,
        change_summaries=change_summaries,
        judge_verdicts=judge_verdicts,
        validator_results=validator_results,
        audit_trail=audit_trail,
        failure_reason=failure_reason,
    )
