"""LiteParse-backed parser for fast local document parsing."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from plugins._document_query.helpers.fetch import FetchedDocument
from .base import BaseParser


class LiteParseParser(BaseParser):
    """Fast parser powered by run-llama/liteparse when available."""

    DEFAULT_NUM_WORKERS = 1

    mimetypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "image/",
    ]

    def enabled(self, config: dict) -> bool:
        return bool(config.get("liteparse_enabled", True))

    def _parse_sync(self, document: FetchedDocument, config: dict) -> str:
        if config.get("liteparse_subprocess", True):
            return self._parse_subprocess(document, config)
        return self._parse_in_process(document, config)

    def _parse_in_process(self, document: FetchedDocument, config: dict) -> str:
        try:
            from liteparse import LiteParse
        except Exception as e:
            raise RuntimeError("LiteParse is not installed") from e

        parser = LiteParse(**self._liteparse_kwargs(config))
        with document.local_file() as file_path:
            result = parser.parse(file_path)

        text = getattr(result, "text", "") or ""
        if not text.strip():
            raise ValueError("LiteParse returned no text")
        return text

    def _parse_subprocess(self, document: FetchedDocument, config: dict) -> str:
        with document.local_file() as file_path:
            payload = {
                "file_path": file_path,
                "kwargs": self._liteparse_kwargs(config),
            }
            env = os.environ.copy()
            project_root = str(Path(__file__).resolve().parents[4])
            python_path = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = (
                f"{project_root}{os.pathsep}{python_path}"
                if python_path
                else project_root
            )
            timeout = float(config.get("per_document_timeout", 60))
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "plugins._document_query.helpers.parsers.liteparse_worker",
                ],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                cwd=project_root,
                env=env,
                timeout=timeout,
                check=False,
            )

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(
                "LiteParse subprocess failed"
                f" with exit code {result.returncode}: {detail[-2000:]}"
            )

        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                "LiteParse subprocess returned invalid output: "
                f"{result.stdout[-2000:]}"
            ) from e

        text = response.get("text", "") or ""
        if not text.strip():
            raise ValueError("LiteParse returned no text")
        return text

    def _liteparse_kwargs(self, config: dict) -> dict:
        kwargs = {
            "ocr_enabled": bool(config.get("liteparse_ocr_enabled", True)),
            "ocr_language": config.get("liteparse_ocr_language", "eng"),
            "max_pages": int(config.get("liteparse_max_pages", 1000)),
            "dpi": float(config.get("liteparse_dpi", 150)),
            "preserve_very_small_text": bool(
                config.get("liteparse_preserve_very_small_text", False)
            ),
            "quiet": True,
        }

        optional_keys = {
            "ocr_server_url": "liteparse_ocr_server_url",
            "target_pages": "liteparse_target_pages",
            "output_format": "liteparse_output_format",
            "password": "liteparse_password",
        }
        for liteparse_key, config_key in optional_keys.items():
            value = config.get(config_key)
            if value not in (None, ""):
                kwargs[liteparse_key] = value

        kwargs["num_workers"] = _positive_int(
            config.get("liteparse_num_workers"),
            self.DEFAULT_NUM_WORKERS,
        )

        tessdata_path = config.get("liteparse_tessdata_path") or _detect_tessdata_path()
        if tessdata_path:
            kwargs["tessdata_path"] = tessdata_path

        return kwargs


def _detect_tessdata_path() -> str:
    env_path = os.getenv("TESSDATA_PREFIX", "")
    candidates = [
        env_path,
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
        "/usr/share/tessdata",
        "/usr/local/share/tessdata",
    ]
    for candidate in candidates:
        if candidate and (Path(candidate) / "eng.traineddata").is_file():
            return candidate
    return ""


def _positive_int(value, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default
