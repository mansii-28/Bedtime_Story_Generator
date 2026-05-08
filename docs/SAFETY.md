# Safety & Guardrails

## Multilayered Defense

### Layer 1: The "Fail-Closed" Philosophy
Our system operates on a **fail-closed** principle. If the Judge cannot provide a valid JSON evaluation, or if the Deterministic Validators detect a "hard failure" (e.g., prohibited keywords), the story is automatically blocked from being displayed as "Approved."

### Layer 2: Normalization & Character Rewriting
The `Normalizer Agent` is the first line of defense. It identifies copyrighted or potentially problematic character names and maps them to original, child-safe alternatives.
- **Example**: "Iron Man" → "Brave Metal Hero."
- **Benefit**: This prevents the LLM from pulling in external, potentially mature context associated with the original character.

### Layer 3: Deterministic Validators (`ground_truth`)
We do not rely solely on LLMs for safety. `app/validators/validators.py` performs strict keyword and metric checks:
- **Prohibited Words**: A list including "death," "blood," "kill," "scary," etc.
- **Word Count**: Ensures stories remain between 80 and 300 words.
- **Genre Drift**: Specifically prevents "sci-fi" stories from drifting into "fantasy" (e.g., catching terms like "magic," "wizard," "enchanted").

### Layer 4: Semantic Judging
The `Judge Agent` evaluates the story's "Emotional Safety" and "Bedtime Suitability" on a 1-5 scale. Any score below 3 for these dimensions triggers an automatic revision.

### Layer 5: Bounded Revision Loop
By capping the revision process at **2 attempts**, we ensure that if a request is fundamentally flawed or unsafe, the system will eventually stop and report a failure rather than endlessly iterating.

## Character Rewrite Mapping
The system preserves the original user request and the final approved character names. This allows the UI to show a clean "Safety Adjustment" card (e.g., **"Iron Man was replaced with Brave Robot to keep the story original and safe."**) ensuring transparency for parents.
