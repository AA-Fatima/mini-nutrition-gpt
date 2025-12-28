import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    APP_NAME: str = "Mini Nutrition GPT"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
