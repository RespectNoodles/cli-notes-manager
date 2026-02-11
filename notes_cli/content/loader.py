from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml


@dataclass(frozen=True)
class Item:
    label: str
    kind: str  # 'dir' | 'md'
    path: Path


@dataclass(frozen=True)
class IndexMeta:
    title: str
    order: List[str]
    hidden: List[str]
    aliases: dict[str, List[str]]


def load_index_meta(folder: Path) -> Optional[IndexMeta]:
    idx = folder / "_index.yml"
    if not idx.exists():
        return None
    data = yaml.safe_load(idx.read_text(encoding="utf-8")) or {}
    return IndexMeta(
        title=str(data.get("title", folder.name)),
        order=list(data.get("order", [])),
        hidden=list(data.get("hidden", [])),
        aliases={k: list(v) for k, v in (data.get("aliases", {}) or {}).items()},
    )


def list_folder(folder: Path) -> Tuple[str, List[Item], Optional[IndexMeta]]:
    meta = load_index_meta(folder)
    title = meta.title if meta else folder.name

    dirs = [p for p in folder.iterdir() if p.is_dir() and not p.name.startswith(".")]
    mds = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".md"]

    hidden = set(meta.hidden) if meta else set()
    dirs = [p for p in dirs if p.name not in hidden]
    mds = [p for p in mds if p.name not in hidden]

    items: List[Item] = []
    for d in sorted(dirs, key=lambda p: p.name.lower()):
        items.append(Item(label=pretty_name(d.name), kind="dir", path=d))
    for f in sorted(mds, key=lambda p: p.name.lower()):
        items.append(Item(label=pretty_name(f.stem), kind="md", path=f))

    if meta and meta.order:
        order_map = {name: i for i, name in enumerate(meta.order)}

        def key(it: Item):
            fname = it.path.name
            return (order_map.get(fname, 10_000), it.label.lower())

        items = sorted(items, key=key)

    return title, items, meta


def pretty_name(s: str) -> str:
    return s.replace("-", " ").replace("_", " ").strip().title()
