from __future__ import annotations

from pathlib import Path

def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def infer_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback
