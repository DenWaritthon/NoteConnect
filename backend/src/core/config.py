"""Application configuration loaded from environment variables.

Production code should import configuration from this module instead of reading
environment variables directly. That keeps model names, thresholds, and database
settings centralized and easy to override per environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENV_PATH = BACKEND_DIR / ".env"


def load_env_file(path: Path = DEFAULT_ENV_PATH) -> None:
    """Load simple KEY=VALUE pairs into the process environment if unset."""
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


@dataclass(frozen=True)
class DatabaseConfig:
    """Connection settings for PostgreSQL."""

    host: str
    port: int
    name: str
    user: str
    password: str
    url: str | None = None

    @property
    def connect_kwargs(self) -> dict[str, object]:
        if self.url:
            return {"conninfo": self.url}

        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.name,
            "user": self.user,
            "password": self.password,
        }


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings used by the database and AI pipeline."""

    database: DatabaseConfig
    api_secret_key: str | None
    api_key_header_name: str
    embedding_model: str
    nli_model: str
    explanation_model: str
    explanation_max_new_tokens: int
    embedding_dimension: int
    similarity_threshold: float
    threshold_scale: float
    similarity_top_k: int
    similar_word_threshold: float


def get_config() -> AppConfig:
    """Build the application configuration from `.env` and process env."""
    load_env_file()

    return AppConfig(
        database=DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=_get_int("DB_PORT", 5432),
            name=os.getenv("DB_NAME", "noteconnect"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            url=os.getenv("DATABASE_URL"),
        ),
        api_secret_key=os.getenv("API_SECRET_KEY"),
        api_key_header_name=os.getenv("API_KEY_HEADER_NAME", "X-API-Key"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL",
            os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2"),
        ),
        nli_model=os.getenv(
            "NLI_MODEL",
            os.getenv("NLI_MODEL_NAME", "cross-encoder/nli-deberta-v3-base"),
        ),
        explanation_model=os.getenv("EXPLANATION_MODEL", "Qwen/Qwen3-0.6B"),
        explanation_max_new_tokens=_get_int("EXPLANATION_MAX_NEW_TOKENS", 128),
        embedding_dimension=_get_int("EMBEDDING_DIMENSION", 768),
        similarity_threshold=_get_float("SIMILARITY_THRESHOLD", 0.40),
        threshold_scale=_get_float("THRESHOLD_SCALE", 0.20),
        similarity_top_k=_get_int("SIMILARITY_TOP_K", 10),
        similar_word_threshold=_get_float("SIMILAR_WORD_THRESHOLD", 0.55),
    )
