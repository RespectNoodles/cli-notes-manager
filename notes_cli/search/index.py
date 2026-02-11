from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Doc:
    rel_path: str
    title: str
    body: str


Index = List[Doc]


def build_index(notes_root: Path) -> Index:
    docs: List[Doc] = []
    for p in notes_root.rglob("*.md"):
        if p.name.startswith(".") or "/." in p.as_posix():
            continue
        rel = p.relative_to(notes_root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        title = _infer_title(text, p.stem)
        docs.append(Doc(rel_path=rel, title=title, body=text))
    return docs


def query_index(index: Index, query: str, limit: int = 20) -> List[Doc]:
    q = query.lower().strip()
    scored: List[tuple[int, Doc]] = []
    for d in index:
        hay = (d.title + "\n" + d.body).lower()
        if q in hay:
            score = 0
            if q in d.title.lower():
                score += 10
            score += max(0, 5 - hay.find(q) // 500)
            scored.append((score, d))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [d for _s, d in scored[:limit]]


def _infer_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback
