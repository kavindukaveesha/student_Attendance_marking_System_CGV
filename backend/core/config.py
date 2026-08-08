"""Application settings loaded from `.env` via pydantic-settings.

Exposes the `settings` singleton used everywhere else — no other module reads
environment variables directly.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite:///./output/attendance.db"

    MATCH_THRESHOLD: float = 0.25
    INK_THRESHOLD: float = 0.02

    PROCESSED_DIR: str = "output/processed"
    SHEETS_DIR: str = "data/signing_sheets"
    SIGNATURES_DIR: str = "data/signatures"

    @property
    def processed_path(self) -> Path:
        p = Path(self.PROCESSED_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def sheets_path(self) -> Path:
        p = Path(self.SHEETS_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def signatures_path(self) -> Path:
        p = Path(self.SIGNATURES_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
