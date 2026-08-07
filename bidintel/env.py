"""Load environment variables from .env if present."""

from __future__ import annotations

from pathlib import Path


def load_dotenv() -> None:
    try:
        from dotenv import load_dotenv as _load
    except ImportError:
        return
    root = Path(__file__).resolve().parent.parent
    for name in (".env", ".env.local"):
        path = root / name
        if path.is_file():
            _load(path, override=False)
