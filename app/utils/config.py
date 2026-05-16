from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()  # load from .env if present

class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://user:password@localhost:5432/route_agent",
    )

settings = Settings()