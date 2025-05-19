"""Main entry point for the unify CLI."""
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

# Aggiungi la directory cli al path per permettere gli import
sys.path.append(str(Path(__file__).parent.parent))

from unify_cli import __app_name__, __version__
from unify_cli.commands import backend, frontend

app = typer.Typer(
    name=__app_name__,
    help="CLI tool for managing the Shoe Production Manager application.",
    add_completion=False,
)
app.add_typer(backend.app, name="backend", help="Manage the backend service.")
app.add_typer(frontend.app, name="frontend", help="Manage the frontend service.")

console = Console()


def version_callback(value: bool):
    """Display version and exit."""
    if value:
        console.print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    )
) -> None:
    """Shoe Production Manager CLI."""
    pass


if __name__ == "__main__":
    app()
