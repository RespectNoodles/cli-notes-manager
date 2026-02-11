from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from git import Repo, InvalidGitRepositoryError, NoSuchPathError


@dataclass(frozen=True)
class RepoStatus:
    ok: bool
    path: Path
    branch: Optional[str] = None
    is_dirty: Optional[bool] = None
    head_short: Optional[str] = None
    message: str = ""


def get_repo_status(path: Path) -> RepoStatus:
    try:
        repo = Repo(path)
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        return RepoStatus(ok=False, path=path, message=str(e))

    try:
        branch = repo.active_branch.name
    except TypeError:
        branch = "(detached)"

    head = repo.head.commit.hexsha[:7] if repo.head.is_valid() else None
    dirty = repo.is_dirty(untracked_files=True)

    return RepoStatus(ok=True, path=path, branch=branch, is_dirty=dirty, head_short=head)
