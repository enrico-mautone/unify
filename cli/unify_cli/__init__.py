"""Unify CLI package for managing the Shoe Production Manager application."""

__app_name__ = "unify"
__version__ = "0.1.0"

from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# Environment files
ENV_FILES = {
    "dev": {
        "backend": BACKEND_DIR / ".env.development",
        "frontend": FRONTEND_DIR / ".env.development",
    },
    "test": {
        "backend": BACKEND_DIR / ".env.test",
        "frontend": FRONTEND_DIR / ".env.test",
    },
    "prod": {
        "backend": BACKEND_DIR / ".env.production",
        "frontend": FRONTEND_DIR / ".env.production",
    },
}
