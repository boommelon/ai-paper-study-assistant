from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    papers_dir: Path
    cache_path: Path
    ai_api_key: str
    ai_base_url: str
    ai_model: str
    max_input_chars: int = 28_000


def get_settings() -> Settings:
    root = Path(__file__).resolve().parent
    papers_dir = Path(os.getenv("PAPERS_DIR", ".")).expanduser()
    cache_path = Path(os.getenv("CACHE_PATH", "data/cache.json")).expanduser()

    if not papers_dir.is_absolute():
        papers_dir = root / papers_dir
    if not cache_path.is_absolute():
        cache_path = root / cache_path

    return Settings(
        papers_dir=papers_dir.resolve(),
        cache_path=cache_path.resolve(),
        ai_api_key=os.getenv("AI_API_KEY", "").strip(),
        ai_base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1").strip(),
        ai_model=os.getenv("AI_MODEL", "gpt-4o-mini").strip(),
    )
