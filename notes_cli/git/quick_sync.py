from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass(frozen=True)
class QuickSyncPlan:
    commands: List[List[str]]  # argv lists
    human: List[str]           # printable lines


def plan_quick_sync(repo_path: Path, commit_message: str) -> QuickSyncPlan:
    cmds = [
        ["git", "-C", str(repo_path), "status"],
        ["git", "-C", str(repo_path), "add", "-A"],
        ["git", "-C", str(repo_path), "commit", "-m", commit_message],
        ["git", "-C", str(repo_path), "push"],
    ]
    human = [
        f"git -C {repo_path} status",
        f"git -C {repo_path} add -A",
        f'git -C {repo_path} commit -m "{commit_message}"',
        f"git -C {repo_path} push",
    ]
    return QuickSyncPlan(commands=cmds, human=human)


def run_plan(plan: QuickSyncPlan) -> List[Tuple[str, int, str, str]]:
    results = []
    for argv in plan.commands:
        p = subprocess.run(argv, capture_output=True, text=True)
        results.append((" ".join(argv), p.returncode, p.stdout, p.stderr))
        if p.returncode != 0:
            break
    return results
