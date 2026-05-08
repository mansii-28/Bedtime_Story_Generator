def count_words(text: str) -> int:
    """Returns the number of whitespace-separated tokens in *text*."""
    return len(text.split())


def classify_word_count(word_count: int, min_words: int, max_words: int) -> str:
    """Classifies the word count relative to limits."""
    if word_count < min_words:
        return "too_short"
    if word_count > max_words:
        return "too_long"
    return "within_range"


def trim_story_to_max_words(story: str, max_words: int) -> str:
    """
    Deterministic last-resort trim: truncates at the last sentence boundary
    that keeps the text within *max_words*.  If no sentence boundary is found,
    hard-truncates at *max_words* tokens.
    """
    words = story.split()
    if len(words) <= max_words:
        return story

    # Try to truncate at the last sentence end (. ! ?) within the budget
    truncated = " ".join(words[:max_words])
    for punct in (".", "!", "?"):
        idx = truncated.rfind(punct)
        if idx != -1:
            return truncated[: idx + 1].strip()

    # Fallback: hard word cut
    return truncated.strip()
