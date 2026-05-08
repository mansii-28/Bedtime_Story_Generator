import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configures structured but simple logging for the application."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Optional: reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger("bedtime-story")
