from __future__ import annotations

from dataclasses import dataclass
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

console = Console()


@dataclass(frozen=True)
class MenuViewModel:
    title: str
    breadcrumb: str
    items: List[str]
    footer_keys: str
    status: str


def render_menu(vm: MenuViewModel) -> None:
    console.clear()
    console.print(Text(vm.breadcrumb, style="bold"))

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column(justify="right", width=4)
    table.add_column(justify="left")
    for i, label in enumerate(vm.items, start=1):
        table.add_row(f"({i})", label)

    panel = Panel.fit(
        table,
        title=vm.title,
        subtitle=Text(vm.status, style="dim"),
        border_style="cyan",
    )
    console.print(panel)
    console.print(Text(vm.footer_keys, style="dim"))


def render_markdown_screen(title: str, breadcrumb: str, md_text: str, status: str, footer_keys: str) -> None:
    console.clear()
    console.print(Text(breadcrumb, style="bold"))
    console.print(
        Panel(
            Markdown(md_text),
            title=title,
            subtitle=Text(status, style="dim"),
            border_style="green",
        )
    )
    console.print(Text(footer_keys, style="dim"))


def render_message(title: str, message: str) -> None:
    console.print(Panel(message, title=title, border_style="magenta"))
