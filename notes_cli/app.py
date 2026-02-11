from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from rich.prompt import Prompt

from notes_cli.config import load_config, AppConfig
from notes_cli.content.loader import list_folder, Item
from notes_cli.content.markdown import read_markdown, infer_title
from notes_cli.git.status import get_repo_status
from notes_cli.git.quick_sync import plan_quick_sync, run_plan
from notes_cli.search.index import build_index, query_index
from notes_cli.ui.render import render_menu, render_markdown_screen, render_message, MenuViewModel
from notes_cli.utils.calc import safe_eval, CalcError

FOOTER_KEYS = "Keys: [B] Back  [M] Main  [S] Search  [G] Git  [U] QuickSync  [C] Calc  [H] Help  [Q] Quit"


@dataclass
class Screen:
    kind: str  # 'menu' | 'note'
    title: str
    path: Path
    items: Optional[List[Item]] = None
    note_path: Optional[Path] = None


def main() -> None:
    cfg = load_config(Path("config.toml"))
    notes_root = (cfg.repo_path / cfg.notes_root).resolve()
    if not notes_root.exists():
        raise SystemExit(f"notes_root not found: {notes_root}\nCheck config.toml")

    stack: List[Screen] = []
    current = build_menu_screen(notes_root)

    while True:
        status_str = format_status(cfg)
        breadcrumb = breadcrumb_from_stack(stack, current)

        if current.kind == "menu":
            vm = MenuViewModel(
                title=current.title,
                breadcrumb=breadcrumb,
                items=[it.label for it in (current.items or [])],
                footer_keys=FOOTER_KEYS,
                status=status_str,
            )
            render_menu(vm)

            raw = Prompt.ask("Type your choice").strip()
            action = normalize(raw)

            handled, next_screen = handle_global(action, cfg, notes_root, stack, current)
            if handled:
                current = next_screen or current
                continue

            idx = parse_int(action)
            if idx is None:
                render_message("Input", "Invalid choice. Use a number or one of the keys in the legend.")
                Prompt.ask("Press Enter", default="")
                continue

            items = current.items or []
            if not (1 <= idx <= len(items)):
                render_message("Input", "Number out of range.")
                Prompt.ask("Press Enter", default="")
                continue

            selected = items[idx - 1]
            stack.append(current)
            if selected.kind == "dir":
                current = build_menu_screen(selected.path)
            else:
                md = read_markdown(selected.path)
                title = infer_title(md, selected.path.stem)
                current = Screen(kind="note", title=title, path=selected.path.parent, note_path=selected.path)

        else:
            assert current.note_path is not None
            md = read_markdown(current.note_path)
            render_markdown_screen(current.title, breadcrumb, md, status_str, FOOTER_KEYS)
            raw = Prompt.ask("Command").strip()
            action = normalize(raw)

            handled, next_screen = handle_global(action, cfg, notes_root, stack, current)
            if handled:
                current = next_screen or current
                continue

            render_message("Input", "Unknown command.")
            Prompt.ask("Press Enter", default="")


def handle_global(
    action: str,
    cfg: AppConfig,
    notes_root: Path,
    stack: List[Screen],
    current: Screen,
) -> tuple[bool, Optional[Screen]]:
    if action == "Q":
        raise SystemExit(0)
    if action == "H":
        show_help()
        return True, None
    if action == "G":
        show_git_status(cfg)
        return True, None
    if action == "U":
        quick_sync(cfg)
        return True, None
    if action == "C":
        calculator()
        return True, None
    if action == "M":
        stack.clear()
        return True, build_menu_screen(notes_root)
    if action == "B":
        if stack:
            return True, stack.pop()
        return True, None
    if action == "S":
        opened = search_flow(notes_root)
        if opened is None:
            return True, None
        stack.append(current)
        md = read_markdown(opened)
        title = infer_title(md, opened.stem)
        return True, Screen(kind="note", title=title, path=opened.parent, note_path=opened)
    return False, None


def build_menu_screen(folder: Path) -> Screen:
    title, items, _meta = list_folder(folder)
    return Screen(kind="menu", title=title, path=folder, items=items)


def breadcrumb_from_stack(stack: List[Screen], current: Screen) -> str:
    parts = ["Main"] + [s.title for s in stack] + [current.title]
    out: List[str] = []
    for p in parts:
        if not out or out[-1] != p:
            out.append(p)
    return " > ".join(out)


def normalize(s: str) -> str:
    return s.strip().upper()


def parse_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except ValueError:
        return None


def format_status(cfg: AppConfig) -> str:
    st = get_repo_status(cfg.repo_path)
    if not st.ok:
        return f"Repo: NOT OK ({cfg.repo_path})"
    dirty = "dirty" if st.is_dirty else "clean"
    head = st.head_short or ""
    return f"Repo: {st.branch} • {dirty} • {head}".strip(" •")


def show_help() -> None:
    msg = (
        "Help\n\n"
        "- Type a number to open a folder/note.\n"
        "- B = back, M = main menu, Q = quit\n"
        "- S = search notes\n"
        "- G = git status (detect-only)\n"
        "- U = quick sync (prints commands; optional exec via config)\n"
        "- C = calculator (safe)\n"
    )
    render_message("Help", msg)
    Prompt.ask("Press Enter", default="")


def show_git_status(cfg: AppConfig) -> None:
    st = get_repo_status(cfg.repo_path)
    if not st.ok:
        render_message("Git Status", f"Could not open repo at {cfg.repo_path}\n{st.message}")
    else:
        render_message(
            "Git Status",
            f"Path: {st.path}\nBranch: {st.branch}\nDirty: {st.is_dirty}\nHEAD: {st.head_short}",
        )
    Prompt.ask("Press Enter", default="")


def quick_sync(cfg: AppConfig) -> None:
    msg = Prompt.ask("Commit message", default="Update notes").strip()
    plan = plan_quick_sync(cfg.repo_path, msg)

    render_message("Quick Sync", "\n".join(["Commands that would run:"] + plan.human))
    if not cfg.allow_git_exec:
        render_message("Quick Sync", "Execution is disabled (allow_git_exec=false). Copy/paste the commands above.")
        Prompt.ask("Press Enter", default="")
        return

    confirm1 = Prompt.ask("Execute these commands? (yes/no)", default="no").strip().lower()
    if confirm1 != "yes":
        return
    confirm2 = Prompt.ask("Really run git add/commit/push? Type YES to confirm", default="no").strip()
    if confirm2 != "YES":
        return

    results = run_plan(plan)
    out_lines = []
    for cmd, rc, stdout, stderr in results:
        out_lines.append(f"$ {cmd}\nrc={rc}\n{stdout}\n{stderr}".strip())
    render_message("Quick Sync Results", "\n\n".join(out_lines) or "No output")
    Prompt.ask("Press Enter", default="")


def calculator() -> None:
    expr = Prompt.ask("Expression (e.g., (2+3)*4)", default="").strip()
    try:
        val = safe_eval(expr)
        render_message("Calculator", f"{expr} = {val}")
    except CalcError as e:
        render_message("Calculator", f"Error: {e}")
    Prompt.ask("Press Enter", default="")


def search_flow(notes_root: Path) -> Optional[Path]:
    q = Prompt.ask("Search", default="").strip()
    if not q:
        return None
    idx = build_index(notes_root)
    results = query_index(idx, q, limit=20)
    if not results:
        render_message("Search", "No matches.")
        Prompt.ask("Press Enter", default="")
        return None

    lines = [f"({i}) {r.title}  ({r.rel_path})" for i, r in enumerate(results, start=1)]
    render_message("Search Results", "\n".join(lines))
    raw = Prompt.ask("Open number (or Enter to cancel)", default="").strip()
    if not raw:
        return None
    n = parse_int(raw)
    if n is None or not (1 <= n <= len(results)):
        return None
    return notes_root / results[n - 1].rel_path
