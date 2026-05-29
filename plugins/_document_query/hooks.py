from __future__ import annotations

import importlib
import importlib.util
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from helpers.errors import format_error
from helpers.print_style import PrintStyle


_LOCK = threading.Lock()
_CHECKED = False
_PLUGIN_DIR = Path(__file__).resolve().parent
_REQUIREMENTS_FILE = _PLUGIN_DIR / "requirements.txt"


def has_liteparse() -> bool:
    return importlib.util.find_spec("liteparse") is not None


def ensure_dependencies(raise_on_error: bool = True) -> bool:
    """Install framework-runtime dependencies needed by the plugin."""
    global _CHECKED

    if _CHECKED and has_liteparse():
        return True

    with _LOCK:
        if _CHECKED and has_liteparse():
            return True
        if has_liteparse():
            _CHECKED = True
            return True

        try:
            _install_requirements()
            importlib.invalidate_caches()
            if not has_liteparse():
                raise RuntimeError(
                    "Document Query dependency 'liteparse' is still unavailable after installation"
                )
            _CHECKED = True
            return True
        except Exception as e:
            message = (
                "Document Query: failed to install LiteParse dependency: "
                f"{format_error(e)}"
            )
            if raise_on_error:
                raise RuntimeError(message) from e
            PrintStyle.error(message)
            return False


def install() -> bool:
    return ensure_dependencies(raise_on_error=True)


def _install_requirements() -> None:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError(
            "Document Query plugin requires 'uv' to install liteparse automatically"
        )
    if not _REQUIREMENTS_FILE.is_file():
        raise RuntimeError(
            f"Document Query requirements file not found: {_REQUIREMENTS_FILE}"
        )

    cmd = [
        uv,
        "pip",
        "install",
        "--python",
        sys.executable,
        "-r",
        str(_REQUIREMENTS_FILE),
    ]

    PrintStyle.info("Document Query: liteparse not found, installing plugin dependency")
    subprocess.check_call(cmd, cwd=str(_PLUGIN_DIR))
