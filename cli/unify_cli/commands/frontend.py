"""Frontend commands for the unify CLI."""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel

from unify_cli import ENV_FILES, FRONTEND_DIR

# Find npm and node executables
def find_executable(name: str) -> Optional[str]:
    """Find an executable in the system PATH."""
    # Try to find the executable in the system PATH
    executable = shutil.which(name)
    if not executable and sys.platform == 'win32':
        # On Windows, also try with .cmd extension
        executable = shutil.which(f"{name}.cmd")
    return executable

# Find npm and node paths
NPM_PATH = find_executable('npm')
NODE_PATH = find_executable('node')

if not NPM_PATH or not NODE_PATH:
    raise RuntimeError(
        "Node.js and npm are required to run the frontend. "
        "Please install Node.js from https://nodejs.org/ and ensure it's in your PATH."
    )

app = typer.Typer(name="frontend", help="Manage the frontend service.")
console = Console()


def validate_env(env: str) -> bool:
    """Validate that the environment exists and has the required files."""
    if env not in ENV_FILES:
        console.print(f"[red]Error:[/red] Environment '{env}' is not valid. Choose from: {', '.join(ENV_FILES.keys())}")
        return False
    
    frontend_env = ENV_FILES[env]["frontend"]
    if not frontend_env.exists():
        console.print(f"[yellow]Warning:[/yellow] Frontend environment file not found: {frontend_env}")
        return False
    
    return True


def setup_environment(env: str) -> None:
    """Set up the environment for the frontend."""
    # Copy the appropriate .env file to .env in the frontend directory
    env_file = ENV_FILES[env]["frontend"]
    target = FRONTEND_DIR / ".env"
    
    try:
        with open(env_file, "r") as src, open(target, "w") as dst:
            dst.write(src.read())
        console.print(f"[green]✓[/green] Using {env} environment for frontend")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to set up frontend environment: {e}")
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
        "localhost",
        "--host",
        "-h",
        help="Host to bind the server to. Defaults to localhost.",
    ),
    port: int = typer.Option(
        3000,
        "--port",
        "-p",
        help="Port to bind the server to. Defaults to 3000.",
    ),
    open_browser: bool = typer.Option(
        True,
        "--open/--no-open",
        help="Open the browser automatically. Defaults to True.",
    ),
) -> None:
    """Start the frontend development server."""
    if not validate_env(env):
        raise typer.Exit(1)
    
    setup_environment(env)
    
    # Prepare the command to run
    cmd = [NPM_PATH, "run", "start"]
    
    # Set environment variables
    env_vars = os.environ.copy()
    env_vars["BROWSER"] = "none"  # Prevent auto-opening browser
    env_vars["HOST"] = host
    env_vars["PORT"] = str(port)
    
    # Ensure PATH includes the directory containing node and npm
    node_dir = os.path.dirname(NODE_PATH)
    npm_dir = os.path.dirname(NPM_PATH)
    path_dirs = [
        npm_dir,
        node_dir,
        os.environ.get("PATH", "")
    ]
    env_vars["PATH"] = os.pathsep.join(path_dirs)
    
    # Add environment variables from .env file if it exists
    env_file = FRONTEND_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value
    
    # Start the frontend server
    console.print(Panel(
        f"Starting frontend server in {env} environment\n"
        f"Using Node.js: {NODE_PATH}\n"
        f"Using npm: {NPM_PATH}\n"
        f"URL: http://{host}:{port}\n"
        f"Open browser: {'yes' if open_browser else 'no'}",
        title="Frontend Server",
        border_style="blue"
    ))
    
    try:
        # Use shell=True on Windows to ensure proper command execution
        shell = sys.platform == "win32"
        subprocess.run(
            cmd,
            cwd=str(FRONTEND_DIR),
            env=env_vars,
            check=True,
            shell=shell,
            text=True
        )
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] Failed to find required executable: {e}")
        console.print(f"[yellow]Node.js path:[/yellow] {NODE_PATH}")
        console.print(f"[yellow]npm path:[/yellow] {NPM_PATH}")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] Failed to start frontend server: {e}")
        console.print(f"[yellow]Command:[/yellow] {' '.join(cmd)}")
        console.print(f"[yellow]Working directory:[/yellow] {FRONTEND_DIR}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[blue]Stopping frontend server...[/blue]")
        raise typer.Exit(0)


@app.command()
def install_deps() -> None:
    """Install frontend dependencies."""
    console.print("[blue]Installing frontend dependencies...[/blue]")
    
    try:
        subprocess.run(
            ["npm", "install"],
            cwd=str(FRONTEND_DIR),
            check=True,
        )
        console.print("[green]✓ Frontend dependencies installed successfully[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] Failed to install frontend dependencies: {e}")
        raise typer.Exit(1)


@app.command()
def build(
    env: str = typer.Option(
        "prod",
        "--env",
        "-e",
        help="Environment to build for (dev, test, prod). Defaults to prod.",
    ),
) -> None:
    """Build the frontend for production."""
    if not validate_env(env):
        raise typer.Exit(1)
    
    setup_environment(env)
    
    console.print(f"[blue]Building frontend for {env} environment...[/blue]")
    
    try:
        subprocess.run(
            ["npm", "run", "build"],
            cwd=str(FRONTEND_DIR),
            check=True,
        )
        console.print("[green]✓ Frontend built successfully[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error:[/red] Failed to build frontend: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
