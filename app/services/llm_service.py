from langchain_openai import ChatOpenAI

from app.utils.config import settings

def get_llm() -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI client.

    Uses settings from .env via app.utils.config.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.model_name,
        temperature=0.1,
    )