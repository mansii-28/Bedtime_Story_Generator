import os
from openai import OpenAI
from app.core.config import settings
from app.core.logging_config import logger

def call_model(
    messages: list,
    rulebook,
    max_tokens: int = 3000,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """
    Calls the configured OpenAI model. API key is loaded from settings.
    """
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set.")
        raise ValueError("OPENAI_API_KEY is missing. Please set it in your environment or .env file.")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    kwargs: dict = {
        "model": rulebook.model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise
