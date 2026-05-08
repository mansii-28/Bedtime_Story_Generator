"""
main.py
=======
CLI entrypoint and display orchestration for the Bedtime Story Generator.

Pipeline execution has been abstracted out to `story_pipeline.py`.
This module only handles user input and progressive-style CLI output
of the returned structured `StorySession`.

Run:
    python3 main.py
"""

from app.rules.rulebook import RULEBOOK
from app.models.schemas import (
    ChangeSummary,
    StorySession,
    StoryPreferences,
)
from app.utils.text_utils import count_words
from app.services.story_pipeline import generate_story_session


# ─────────────────────────────────────────────────────────────────────────────
# Display constants
# ─────────────────────────────────────────────────────────────────────────────

W  = 62                      # line width
DIV  = "─" * W
BDIV = "═" * W


def _header(text: str) -> None:
    """Thin divider with a label."""
    pad = max(0, W - len(text) - 4)
    print(f"\n{DIV}")
    print(f"  {text}")
    print(DIV)


def _banner(text: str) -> None:
    """Bold divider with a label — used for major milestones."""
    print(f"\n{BDIV}")
    print(f"  {text}")
    print(BDIV)


def _label(key: str, value: str) -> None:
    print(f"  {key:<18} {value}")


def _bullet(text: str, icon: str = "•") -> None:
    print(f"    {icon} {text}")


# ─────────────────────────────────────────────────────────────────────────────
# Structured display helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_story_block(story: str, label: str, word_count: int) -> None:
    _header(f"{label}  ({word_count} words)")
    print()
    print(story)
    print()


def _print_validation_result(val: dict) -> None:
    _header("Validation Result")
    wc     = val["metrics"]["word_count"]
    status = "✅  PASS" if val["passed"] else "❌  FAIL"
    _label("Status:", status)
    _label("Word count:", f"{wc}  (limit: {RULEBOOK.min_words}–{RULEBOOK.max_words})")

    if val["failures"]:
        print("  Hard failures:")
        for f in val["failures"]:
            _bullet(f, "✗")
    else:
        print("  No hard failures.")

    if val["warnings"]:
        print("  Warnings:")
        for w in val["warnings"]:
            _bullet(w, "⚠")


def _print_judge_verdict(verdict: dict, attempt_label: str = "") -> None:
    _header(f"Judge Verdict{' — ' + attempt_label if attempt_label else ''}")
    overall = "✅  APPROVED" if verdict.get("overall_pass") else "❌  NOT APPROVED"
    _label("Overall:", overall)
    _label("Verdict:", verdict.get("verdict", "unknown"))
    _label("Reasoning:", verdict.get("reasoning_summary", "—"))

    scores = verdict.get("scores", {})
    if scores:
        print("  Dimension scores (1–5):")
        # Print in two columns for readability
        items = list(scores.items())
        for i in range(0, len(items), 2):
            left  = f"{items[i][0][:22]:<22} {items[i][1]}"
            right = f"{items[i+1][0][:22]:<22} {items[i+1][1]}" if i+1 < len(items) else ""
            print(f"    {left}    {right}")

    must_fix = verdict.get("must_fix", [])
    if must_fix:
        print("  Must fix:")
        for issue in must_fix:
            _bullet(issue, "✗")

    should_fix = verdict.get("should_fix", [])
    if should_fix:
        print("  Should fix (optional):")
        for s in should_fix:
            _bullet(s, "·")


def _print_what_changed(cs: ChangeSummary) -> None:
    _header("What Changed")
    _label("Route selected:", cs["route_selected"])
    _label("Reason:", cs["reason_for_route"])
    _label("Word count:", f"{cs['old_word_count']} → {cs['new_word_count']} words")

    if cs["issues_fixed"]:
        print("  Issues resolved:")
        for f in cs["issues_fixed"]:
            _bullet(f, "✓")
    else:
        print("  Issues resolved:  none")

    if cs["issues_remaining"]:
        print("  Still remaining:")
        for r in cs["issues_remaining"]:
            _bullet(r, "⚠")
    else:
        print("  Still remaining:  none")


def _print_audit_trail(audit_trail: list) -> None:
    _banner("Audit Trail")
    for i, event in enumerate(audit_trail, 1):
        wc_str = f"  |  words: {event['word_count']}" if event.get("word_count") else ""
        print(f"\n  [{i}] {event['step']}")
        print(f"       status : {event['status']}{wc_str}")
        print(f"       input  : {event['input_summary']}")
        print(f"       output : {event['output_summary']}")
        if event["issues"]:
            for iss in event["issues"]:
                print(f"       issue  : {iss}")
        if event.get("route_selected"):
            print(f"       route  : {event['route_selected']}")
        if event.get("reason_for_route"):
            print(f"       reason : {event['reason_for_route']}")
        print(f"       action : {event['action']}")


# ─────────────────────────────────────────────────────────────────────────────
# Session object printer
# ─────────────────────────────────────────────────────────────────────────────

def print_story_session(session: StorySession) -> None:
    """Takes the structured object and prints it progressively, exactly like before."""
    res = session
    audit = res["audit_trail"]
    
    # ── Phase 1
    _header("Phase 1 — Request Analysis")
    
    norm_event = next((e for e in audit if e["step"] == "normalization"), None)
    if norm_event and norm_event["issues"]:
        print("  ⚠  Safety rewrites applied:")
        for r in norm_event["issues"]:
            _bullet(r)

    setup_event = next((e for e in audit if e["step"] == "setup"), None)
    if setup_event:
        parts = setup_event["output_summary"].split(" | ")
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                _label(k.capitalize() + ":", v)
    
    # ── Phase 2
    _header("Phase 2 — Generating First Draft")
    _print_story_block(res["revision_history"][0], "First Draft", count_words(res["revision_history"][0]))
    _print_validation_result(res["validator_results"][0])
    _print_judge_verdict(res["judge_verdicts"][0], "Initial")
    
    # ── Phase 3
    if len(res["revision_history"]) > 1:
        _header("Phase 3 — Validation & Revision Loop")
        print(f"  Max revisions allowed: {session['rulebook_snapshot']['max_revision_attempts']}")
        
        for i, cs in enumerate(res["change_summaries"]):
            _header(f"Revision {i + 1} — Applying Fixes")
            
            stag_event = next((e for e in audit if e["step"] == f"stagnation_detected_{i + 1}"), None)
            if stag_event:
                print("  ⚠  Stagnation detected! Applying stronger instructions.")
                
            route = cs["route_selected"]
            reason = cs["reason_for_route"]
            print(f"  {reason} Routing to {route.capitalize()} Agent.")
            print(f"  {route.capitalize()} output: {cs['new_word_count']} words")
            
            trim_event = next((e for e in audit if e["step"] == f"deterministic_trim_{i + 1}"), None)
            if trim_event:
                print(f"  Compressor still over limit. Applying deterministic trim...")

            _print_what_changed(cs)
            _print_story_block(res["revision_history"][i+1], f"Revision {i + 1}", cs["new_word_count"])
            _print_validation_result(res["validator_results"][i+1])
            _print_judge_verdict(res["judge_verdicts"][i+1], f"Revision {i + 1}")
            
    # ── Final Output
    if res["status"] == "approved":
        _banner("🌟  FINAL APPROVED STORY  🌟")
        print()
        print(res["final_story"])
        print()
    else:
        _banner("⛔  STORY COULD NOT BE APPROVED")
        print()
        _label("Status:", res["status"])
        _label("Reason:", res["failure_reason"] or "unknown")
        print()
        print("  Best available draft (NOT approved — do not present as final):\n")
        print(res["final_story"])
        print()

    _print_audit_trail(audit)
    
    _banner("Session Summary")
    _label("Session ID:", session["session_id"])
    _label("Created at:", session["created_at"])
    _label("Status:", res["status"])
    _label("Drafts produced:", str(len(res["revision_history"])))
    _label("Final word count:", str(count_words(res["final_story"])))
    if res.get("failure_reason"):
        print()
        print("  Failure reason:")
        _bullet(res["failure_reason"])


# ─────────────────────────────────────────────────────────────────────────────
# User preference intake
# ─────────────────────────────────────────────────────────────────────────────

def collect_user_preferences() -> StoryPreferences:
    """
    Interactive CLI intake.  Genre is mandatory; all others are optional.
    """
    print()
    print(BDIV)
    print("  🌙  Bedtime Story Generator")
    print(f"  Stories for children aged {RULEBOOK.target_age_min}–{RULEBOOK.target_age_max}")
    print(f"  Word limit: {RULEBOOK.min_words}–{RULEBOOK.max_words} words")
    print(f"  Max revisions: {RULEBOOK.max_revision_attempts}")
    print(BDIV)
    print()
    print("  Answer the questions below to customise your story.")
    print("  Fields marked [required] must be filled in.")
    print("  Fields marked [optional] can be left blank for safe defaults.")
    print()

    # ── Genre — required ──────────────────────────────────────────────────────
    genre = ""
    while not genre.strip():
        genre = input("  What genre would you like?\n"
                      "  (e.g. fantasy, adventure, animal tale, sci-fi)  [required]: ").strip()
        if not genre:
            print("  ⚠  Genre is required. Please enter a genre.\n")

    # ── Optional fields ───────────────────────────────────────────────────────
    print()
    characters = input(
        "  Any characters you'd like in the story?\n"
        "  (e.g. a brave rabbit, Superman, a tiny wizard)  [optional]: "
    ).strip()

    print()
    setting = input(
        "  Any setting or location?\n"
        "  (e.g. moon village, enchanted forest, underwater city)  [optional]: "
    ).strip()

    print()
    theme = input(
        "  Any theme or moral you'd like to convey?\n"
        "  (e.g. kindness, sharing, courage, never give up)  [optional]: "
    ).strip()

    print()
    tone = input(
        "  Any tone preference?\n"
        "  (e.g. calm and magical, whimsical, cozy, adventurous)  [optional]: "
    ).strip()

    prefs = StoryPreferences(
        genre=genre,
        characters=characters or "",
        setting=setting   or RULEBOOK.default_setting,
        theme=theme       or RULEBOOK.default_theme,
        tone=tone         or RULEBOOK.default_tone,
    )

    print()
    print(f"  Got it!  Generating your story... This may take a moment.")
    print()

    return prefs


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    while True:
        prefs = collect_user_preferences()
        session = generate_story_session(prefs)
        print_story_session(session)

        # ── Continue or exit ──────────────────────────────────────────────────
        print()
        answer = input(
            "  Would you like to generate another story? [yes / no]: "
        ).strip().lower()

        if answer in ("no", "n", "done", "exit", "quit"):
            print()
            print("  🌙  Good night. I hope your dreams are gentle, bright,")
            print("      and full of little adventures.  🌙")
            print()
            break

        print()
        print("  ✨  Great! Let's create another story.")


if __name__ == "__main__":
    main()