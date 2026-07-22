"""
Central app settings. Groq key is read from the environment only —
never hardcode it here. Copy .env.example to .env and fill it in.
"""
import os
from dotenv import load_dotenv

load_dotenv()         


class Settings:
    GROQ_API_KEY: str | None = os.environ.get("GROQ_API_KEY")

    # Fastest Groq-hosted model — needed to hit the <5s response target.
    GROQ_MODEL: str = "whisper-large-v3"

    # USD per 1M tokens. Verified against Groq's pricing page as of July 2026 —
    # check https://groq.com/pricing before relying on this for real billing.
    PRICING: dict = {
        "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
        "whisper-large-v3": {"hourly": 0.03},
    }

    # Preferred caption languages, in priority order.
    PREFERRED_LANGUAGES: list = ["en", "en-US", "en-GB"]

    # Max chars of raw transcript sent to the LLM in one shot (keeps very
    # long videos fast and within the model's practical output budget).
    MAX_INPUT_CHARS: int = 15_000

    # CORS — tighten this to your real frontend origin in production.
    CORS_ORIGINS: list = ["*"]


settings = Settings()
                                               