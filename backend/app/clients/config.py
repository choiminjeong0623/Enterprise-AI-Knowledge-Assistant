from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///knowledge_assistant.db"
    )

    PROJECT_NAME = "Enterprise AI Knowledge Assistant"

    VERSION = "1.0.0"


settings = Settings()