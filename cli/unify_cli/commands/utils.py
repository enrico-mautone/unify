"""Utility functions for the unify CLI commands."""
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

def run_command(
    cmd: list,
    cwd: str,
    env: Optional[Dict[str, str]] = None,
    capture_output: bool = False,
) -> Tuple[int, str, str]:
    """Run a shell command and return the result.
    
    Args:
        cmd: List of command and arguments
        cwd: Working directory
        env: Environment variables
        capture_output: Whether to capture stdout/stderr
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env or os.environ,
            capture_output=capture_output,
            text=True,
        )
        return (
            result.returncode,
            result.stdout if capture_output else "",
            result.stderr if capture_output else "",
        )
    except subprocess.CalledProcessError as e:
        return (e.returncode, "", str(e))
    except Exception as e:
        return (-1, "", str(e))


def check_node_installed() -> bool:
    """Check if Node.js is installed and available in PATH."""
    try:
        subprocess.run(
            ["node", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def check_python_installed() -> bool:
    """Check if Python is installed and available in PATH."""
    try:
        subprocess.run(
            ["python", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
