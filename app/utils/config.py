
from dataclasses import dataclass
import os

# Optional user-managed secrets override
try:
    from . import secrets as _secrets  # create app/utils/secrets.py locally (not committed)
except Exception:
    _secrets = None

@dataclass
class Settings:
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    INDEX_DIR: str = "indices/vector"
    DOCS_DIR: str = "data/docs"

    # OpenAI RAG (no secrets committed; set via env or secrets.py)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-3-small"

    # Replicate T2I (no secrets committed; set via env or secrets.py)
    USE_DIFFUSERS: bool = False
    T2I_PROVIDER: str = "replicate"
    T2I_API_KEY: str = ""
    T2I_MODEL: str = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

    # Weather Agent
    WEATHER_PROVIDER: str = "stub"
    WEATHER_API_KEY: str = "1d56903457d644918ac31651251110"

    # SQL Agent
    SQL_DB_PATH: str = "data/demo.db"
    LOG_LEVEL: str = "INFO"

    # Recommender
    RECOMMENDER_ONLINE_ENRICHMENT: bool = False  # set True to let LLM suggest brands/links


settings = Settings()

# Override from environment or local secrets module if available
def _override(name: str, default_val):
    env_val = os.getenv(name)
    if env_val is not None:
        return env_val if not isinstance(default_val, bool) else env_val.lower() in {"1","true","yes","on"}
    if _secrets is not None and hasattr(_secrets, name):
        return getattr(_secrets, name)
    return default_val

settings.OPENAI_API_KEY = _override("OPENAI_API_KEY", settings.OPENAI_API_KEY)
settings.OPENAI_MODEL = _override("OPENAI_MODEL", settings.OPENAI_MODEL)
settings.OPENAI_EMBEDDINGS_MODEL = _override("OPENAI_EMBEDDINGS_MODEL", settings.OPENAI_EMBEDDINGS_MODEL)

settings.T2I_API_KEY = _override("T2I_API_KEY", settings.T2I_API_KEY)
settings.T2I_MODEL = _override("T2I_MODEL", settings.T2I_MODEL)

settings.WEATHER_API_KEY = _override("WEATHER_API_KEY", settings.WEATHER_API_KEY)

settings.SQL_DB_PATH = _override("SQL_DB_PATH", settings.SQL_DB_PATH)
settings.LOG_LEVEL = _override("LOG_LEVEL", settings.LOG_LEVEL)

settings.RECOMMENDER_ONLINE_ENRICHMENT = _override("RECOMMENDER_ONLINE_ENRICHMENT", settings.RECOMMENDER_ONLINE_ENRICHMENT)


# Ensure LangChain/OpenAI SDK v1 picks up the key from env
if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
