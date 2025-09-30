"""Configuration for the minimal chat API."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def _load_list(value: str | None) -> List[str]:
    if not value:
        return ["*"]
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in value.split(",") if item.strip()]


API_PREFIX = os.environ.get("API_PREFIX", "/api")
CHAT_STORAGE_PATH = Path(
    os.environ.get("CHAT_STORAGE_PATH", DATA_DIR / "chats.json")
)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
ALLOWED_ORIGINS = _load_list(os.environ.get("ALLOWED_ORIGINS"))
