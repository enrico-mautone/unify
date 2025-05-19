"""Backend commands for the unify CLI."""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from unify_cli import ENV_FILES, BACKEND_DIR

app = typer.Typer(name="backend", help="Manage the backend service.")
console = Console()


def validate_env(env: str) -> bool:
    """Validate that the environment exists and has the required files."""
    if env not in ENV_FILES:
        console.print(f"[red]Error:[/red] Environment '{env}' is not valid. Choose from: {', '.join(ENV_FILES.keys())}")
        return False
    
    backend_env = ENV_FILES[env]["backend"]
    if not backend_env.exists():
        console.print(f"[yellow]Warning:[/yellow] Backend environment file not found: {backend_env}")
        return False
    
    return True


def setup_environment(env: str) -> None:
    """Set up the environment for the backend."""
    # Copy the appropriate .env file to .env in the backend directory
    env_file = ENV_FILES[env]["backend"]
    target = BACKEND_DIR / ".env"
    
    try:
        with open(env_file, "r") as src, open(target, "w") as dst:
            dst.write(src.read())
        console.print(f"[green]✓[/green] Using {env} environment for backend")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to set up backend environment: {e}")
        raise typer.Exit(1)


@app.command()
def start(
    env: str = typer.Option(
        "dev",
        "--env",
        "-e",
        help="Environment to run (dev, test, prod). Defaults to dev.",
    ),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind the server to. Defaults to 0.0.0.0.",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to bind the server to. Defaults to 8000.",
    ),
    reload: bool = typer.Option(
        True,
        "--reload/--no-reload",
        help="Enable/disable auto-reload. Defaults to True in dev, False otherwise.",
    ),
) -> None:
    """Start the backend server."""
    # Set reload based on environment if not explicitly set
    if reload is None:
        reload = env == "dev"
    
    if not validate_env(env):
        raise typer.Exit(1)
    
    setup_environment(env)
    
    # Build the uvicorn command
    cmd = [
        "uvicorn",
        "main:app",
        f"--host={host}",
        f"--port={port}",
    ]
    
    if reload:
        cmd.append("--reload")
    
    # Add environment variables
    env_vars = os.environ.copy()
    env_vars["PYTHONPATH"] = str(BACKEND_DIR.absolute())
    
    console.print(Panel.fit(
        f"Starting backend server in [bold]{env}[/bold] environment\n"
        f"Host: [cyan]{host}[/cyan]\n"
        f"Port: [cyan]{port}[/cyan]\n"
        f"Reload: {'[green]enabled[/green]' if reload else '[yellow]disabled[/yellow]'}",
        title="Backend Server"
    ))
    
    try:
        subprocess.run(cmd, cwd=str(BACKEND_DIR), env=env_vars, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] Failed to start backend server: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[blue]Stopping backend server...[/blue]")
        raise typer.Exit(0)


@app.command()
def install_deps() -> None:
    """Install backend dependencies."""
    console.print("[blue]Installing backend dependencies...[/blue]")
    
    try:
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            cwd=str(BACKEND_DIR),
            check=True,
        )
        console.print("[green]✓ Backend dependencies installed successfully[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] Failed to install backend dependencies: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
