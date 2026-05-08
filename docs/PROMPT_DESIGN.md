# Prompt Design

## Strategies for Reliability

### 1. Rulebook-Driven Prompts
Instead of hardcoding constraints into system prompts, all agents derive their behavior from the centralized `RULEBOOK` (see `app/rules/rulebook.py`). This allows us to update the entire system's behavior (e.g., changing word limits or safety rules) by editing a single file.

### 2. Strict JSON Mode
Agents use OpenAI's JSON mode where possible. We enforce a "Strict JSON" rule in the system prompts to ensure that agents do not return markdown fences or conversational filler, which could break the parser.

### 3. Temperature Tuning
We use variable temperature settings based on the agent's goal:
- **Creative Agents** (Planner, Storyteller): `temp=0.7 to 0.8` to allow for narrative variety and "spark."
- **Audit/Safety Agents** (Normalizer, Controller, Judge): `temp=0.1 to 0.2` for deterministic, repeatable decision-making.
- **Revision Agents** (Compressor, Reviser): `temp=0.3 to 0.5` to balance surgical fixes with creative flow.

### 4. Zero-Shot with Strong Personas
Each agent is given a specific persona:
- **Normalizer**: "Professional child-safety auditor."
- **Storyteller**: "Calm, gentle bedtime storyteller."
- **Judge**: "Strict take-home evaluator using a multi-dimension rubric."

## Stagnation Recovery
The pipeline monitors if a revision attempt failed to make meaningful progress. If stagnation is detected:
1.  The word-count difference between drafts is checked.
2.  If issues persist, the next agent receives a **"STAGNATION DETECTED"** header.
3.  This header overrides standard instructions, commanding "aggressive, drastic changes" to break the deadlock.
