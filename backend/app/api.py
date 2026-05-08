from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging_config import logger
from app.models.schemas import StoryRequest, StoryPreferences
from app.services.story_pipeline import generate_story_session

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Bedtime Story Generator API",
    description="API for generating modular, child-safe bedtime stories.",
    version="1.0.0",
)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow local React frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "service": "bedtime-story-generator",
        "model": settings.OPENAI_MODEL
    }


@app.post("/api/generate-story")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def generate_story(story_request: StoryRequest, request: Request):
    """
    Generates a child-safe bedtime story based on user preferences.
    """
    # Fail cleanly if the API key is missing
    if not settings.OPENAI_API_KEY:
        logger.error("Request failed: OPENAI_API_KEY is missing in settings.")
        raise HTTPException(
            status_code=500,
            detail="Server is missing OpenAI API configuration."
        )

    logger.info(f"Generating story for genre: {story_request.genre}")

    # Convert Pydantic request model to the TypedDict expected by the pipeline
    prefs: StoryPreferences = {
        "genre": story_request.genre,
        "characters": story_request.characters or "",
        "setting": story_request.setting or "",
        "theme": story_request.theme or "",
        "tone": story_request.tone or "",
    }

    try:
        session = generate_story_session(prefs)
        logger.info(f"Story generated successfully: {session['session_id']}")
        return session
    except Exception as e:
        # Catch any pipeline failures (e.g. OpenAI network errors, rate limits)
        # We explicitly log the real error locally but return a safe generic message to the client
        logger.error(f"Pipeline failed for genre '{story_request.genre}': {e}")
        raise HTTPException(
            status_code=500,
            detail="Story generation failed. Please try again."
        )
