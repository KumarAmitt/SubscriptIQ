import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Load .env file from root or backend
load_dotenv(ROOT_DIR / ".env")
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "SubscriptIQ Text-to-SQL Engine"
    API_V1_PREFIX: str = "/api"
    
    # PostgreSQL Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5433"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "subscriptiq")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5433')}/{os.getenv('DB_NAME', 'subscriptiq')}"
    )

    # Qdrant Vector Store
    QDRANT_PATH: str = str(BASE_DIR / "database" / "qdrant_storage")
    QDRANT_COLLECTION: str = "sql_few_shot_examples"

    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Configurable Model IDs from Environment
    GROQ_MODEL_PRIMARY: str = os.getenv("GROQ_MODEL_PRIMARY", "openai/gpt-oss-120b")
    GROQ_MODEL_SECONDARY: str = os.getenv("GROQ_MODEL_SECONDARY", "openai/gpt-oss-20b")
    GOOGLE_MODEL_PRIMARY: str = os.getenv("GOOGLE_MODEL_PRIMARY", "gemini-3.1-flash-lite")
    GOOGLE_MODEL_SECONDARY: str = os.getenv("GOOGLE_MODEL_SECONDARY", "gemma-4-26b-a4b-it")

    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-120b")

    # Currency Localization (Default: INR for Indian users)
    CURRENCY_CODE: str = os.getenv("APP_CURRENCY", "INR")
    CURRENCY_SYMBOL: str = os.getenv("APP_CURRENCY_SYMBOL", "₹")

    # Security & Tokens
    JWT_SECRET: str = os.getenv("JWT_SECRET", "subscriptiq_super_secret_jwt_key_2026_enterprise_secure")

    # Guardrails Defaults
    DEFAULT_ROW_LIMIT: int = int(os.getenv("DEFAULT_ROW_LIMIT", "1000"))
    MAX_ROW_LIMIT: int = int(os.getenv("MAX_ROW_LIMIT", "2000"))
    BLOCKED_OPERATIONS: list[str] = [
        "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "GRANT", "REVOKE", "CREATE"
    ]
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))

    @property
    def SUPPORTED_MODELS(self) -> list[dict]:
        return [
            {
                "id": self.GROQ_MODEL_PRIMARY,
                "name": f"Groq · {self.GROQ_MODEL_PRIMARY.split('/')[-1].upper()}",
                "provider": "groq",
                "provider_name": "Groq Cloud",
                "context_window": 131072,
                "badge": "Power Model",
                "speed": "Ultra-Fast",
                "is_default": (self.DEFAULT_MODEL == self.GROQ_MODEL_PRIMARY),
            },
            {
                "id": self.GROQ_MODEL_SECONDARY,
                "name": f"Groq · {self.GROQ_MODEL_SECONDARY.split('/')[-1].upper()}",
                "provider": "groq",
                "provider_name": "Groq Cloud",
                "context_window": 65536,
                "badge": "Balanced",
                "speed": "Hyper-Fast",
                "is_default": (self.DEFAULT_MODEL == self.GROQ_MODEL_SECONDARY),
            },
            {
                "id": self.GOOGLE_MODEL_PRIMARY,
                "name": f"Google · {self.GOOGLE_MODEL_PRIMARY.replace('-', ' ').title()}",
                "provider": "google",
                "provider_name": "Google DeepMind",
                "context_window": 1048576,
                "badge": "Recommended",
                "speed": "Sub-Second",
                "is_default": (self.DEFAULT_MODEL == self.GOOGLE_MODEL_PRIMARY),
            },
            {
                "id": self.GOOGLE_MODEL_SECONDARY,
                "name": f"Google · {self.GOOGLE_MODEL_SECONDARY.replace('-', ' ').title()}",
                "provider": "google",
                "provider_name": "Google DeepMind",
                "context_window": 131072,
                "badge": "Open Weights",
                "speed": "Fast",
                "is_default": (self.DEFAULT_MODEL == self.GOOGLE_MODEL_SECONDARY),
            },
        ]

    @property
    def ALLOWED_FOR_USERS(self) -> list[str]:
        raw = os.getenv("ALLOWED_MODELS", "")
        if raw:
            return [m.strip() for m in raw.split(",") if m.strip()]
        return [
            self.GROQ_MODEL_PRIMARY,
            self.GROQ_MODEL_SECONDARY,
            self.GOOGLE_MODEL_PRIMARY,
            self.GOOGLE_MODEL_SECONDARY,
        ]

settings = Settings()

