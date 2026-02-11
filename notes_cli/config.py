from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


@dataclass(frozen=True)
class AppConfig:
    repo_path: Path
    notes_root: str = "notes"
    default_branch: str = "main"
    allow_git_exec: bool = False
    editor: str = ""


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        raise FileNotFoundError(
            f"Missing config file: {config_path}\n"
            "Copy config.example.toml to config.toml and edit repo_path."
        )
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return _parse_config(data, config_path)


def _parse_config(data: dict[str, Any], config_path: Path) -> AppConfig:
    repo_path_raw = data.get("repo_path")
    if not repo_path_raw:
        raise ValueError(f"repo_path is required in {config_path}")
    repo_path = Path(repo_path_raw).expanduser()

    return AppConfig(
        repo_path=repo_path,
        notes_root=str(data.get("notes_root", "notes")),
        default_branch=str(data.get("default_branch", "main")),
        allow_git_exec=bool(data.get("allow_git_exec", False)),
        editor=str(data.get("editor", "")),
    )
