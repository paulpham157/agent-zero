from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from helpers import files
from helpers.security import safe_filename


MAX_INLINE_RESOURCE_BYTES = 512 * 1024
MAX_ATTACHMENT_BYTES = 16 * 1024 * 1024

_TEXT_MIME_PREFIXES = ("text/",)
_TEXT_MIME_TYPES = {
    "application/json",
    "application/javascript",
    "application/typescript",
    "application/xml",
    "application/x-yaml",
    "application/yaml",
    "application/toml",
    "application/sql",
}


@dataclass
class PromptParts:
    text: str = ""
    attachments: list[str] = field(default_factory=list)


def normalize_cwd(cwd: str | None) -> str:
    raw = str(cwd or "").strip() or os.getcwd()
    raw = os.path.expanduser(raw)
    translated = translate_windows_drive_path(raw)
    if translated:
        raw = translated
    return os.path.abspath(raw)


def normalize_path_for_compare(path: str | None) -> str:
    return os.path.normcase(os.path.normpath(normalize_cwd(path)))


def translate_windows_drive_path(path: str) -> str | None:
    match = re.match(r"^/?([A-Za-z]):[\\/](.*)$", str(path or ""))
    if not match:
        return None
    drive = match.group(1).lower()
    tail = match.group(2).replace("\\", "/").lstrip("/")
    return f"/mnt/{drive}/{tail}"


def path_from_file_uri(uri: str) -> Path | None:
    raw = str(uri or "").strip()
    if not raw:
        return None

    parsed = urlparse(raw)
    if parsed.scheme and parsed.scheme != "file":
        return None

    if parsed.scheme == "file":
        if parsed.netloc and parsed.netloc not in {"", "localhost"}:
            return None
        path_text = unquote(parsed.path or "")
    else:
        path_text = unquote(raw)

    translated = translate_windows_drive_path(path_text)
    if translated:
        return Path(translated)
    return Path(path_text)


def stringify_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        preview = content.get("preview")
        if isinstance(preview, str) and preview.strip():
            return preview
        raw = content.get("raw_content")
        if raw is not None:
            return stringify_message_content(raw)
    if isinstance(content, list):
        parts = [stringify_message_content(item) for item in content]
        return "\n".join(part for part in parts if part)
    try:
        return json.dumps(content, ensure_ascii=False)
    except Exception:
        return str(content)


def prompt_blocks_to_user_message(
    prompt: list[Any],
    *,
    context_id: str,
    message_id: str,
) -> PromptParts:
    text_parts: list[str] = []
    attachments: list[str] = []

    for index, block in enumerate(prompt or []):
        block_type = str(getattr(block, "type", "") or "").strip()
        if block_type == "text" or hasattr(block, "text"):
            text = str(getattr(block, "text", "") or "")
            if text:
                text_parts.append(text)
            continue

        if block_type == "image":
            _append_media_block(
                block,
                context_id=context_id,
                message_id=message_id,
                index=index,
                kind="image",
                text_parts=text_parts,
                attachments=attachments,
            )
            continue

        if block_type == "audio":
            _append_media_block(
                block,
                context_id=context_id,
                message_id=message_id,
                index=index,
                kind="audio",
                text_parts=text_parts,
                attachments=attachments,
            )
            continue

        if block_type == "resource_link":
            _append_resource_link(block, text_parts=text_parts, attachments=attachments)
            continue

        if block_type == "resource":
            _append_embedded_resource(
                block,
                context_id=context_id,
                message_id=message_id,
                index=index,
                text_parts=text_parts,
                attachments=attachments,
            )

    text = "\n\n".join(part for part in text_parts if part).strip()
    if not text and attachments:
        text = "Please inspect the attached file(s)."
    return PromptParts(text=text, attachments=attachments)


def _append_media_block(
    block: Any,
    *,
    context_id: str,
    message_id: str,
    index: int,
    kind: str,
    text_parts: list[str],
    attachments: list[str],
) -> None:
    uri = str(getattr(block, "uri", "") or "").strip()
    mime_type = str(getattr(block, "mime_type", "") or "").strip() or None
    data = str(getattr(block, "data", "") or "").strip()

    if uri:
        path = path_from_file_uri(uri)
        if path and path.exists():
            attachments.append(str(path))
            text_parts.append(f"[Attached {kind}: {path}]")
            return
        text_parts.append(f"[Attached {kind} reference: {uri}]")
        return

    if not data:
        return

    try:
        raw = base64.b64decode(data.split(",", 1)[-1], validate=False)
    except Exception:
        raw = data.encode("utf-8", errors="replace")

    saved = _save_attachment_bytes(
        context_id=context_id,
        message_id=message_id,
        index=index,
        label=kind,
        data=raw,
        mime_type=mime_type,
    )
    attachments.append(saved)
    text_parts.append(f"[Attached {kind}: {saved}]")


def _append_resource_link(
    block: Any,
    *,
    text_parts: list[str],
    attachments: list[str],
) -> None:
    uri = str(getattr(block, "uri", "") or "").strip()
    if not uri:
        return
    name = _resource_display_name(block, uri)
    mime_type = str(getattr(block, "mime_type", "") or "").strip() or None
    path = path_from_file_uri(uri)

    if path is None:
        text_parts.append(f"[Attached resource: {name}]\nURI: {uri}")
        return

    if not path.exists():
        text_parts.append(f"[Attached resource unavailable: {name}]\nURI: {uri}\nPath: {path}")
        return

    if _is_probably_text(path, mime_type):
        try:
            size = path.stat().st_size
            data = path.read_bytes()[:MAX_INLINE_RESOURCE_BYTES]
            body = decode_text_bytes(data, mime_type) or ""
            if size > MAX_INLINE_RESOURCE_BYTES:
                body += f"\n\n[Truncated to {MAX_INLINE_RESOURCE_BYTES} of {size} bytes]"
            text_parts.append(f"[Attached file: {name}]\nURI: {uri}\n\n{body}")
            return
        except OSError as exc:
            text_parts.append(f"[Attached file unreadable: {name}]\nURI: {uri}\nError: {exc}")
            return

    attachments.append(str(path))
    text_parts.append(f"[Attached file: {path}]")


def _append_embedded_resource(
    block: Any,
    *,
    context_id: str,
    message_id: str,
    index: int,
    text_parts: list[str],
    attachments: list[str],
) -> None:
    resource = getattr(block, "resource", None)
    if resource is None:
        return

    uri = str(getattr(resource, "uri", "") or "").strip()
    mime_type = str(getattr(resource, "mime_type", "") or "").strip() or None
    if hasattr(resource, "text"):
        body = str(getattr(resource, "text", "") or "")
        text_parts.append(f"[Attached resource: {uri or 'embedded text'}]\n\n{body}")
        return

    blob = str(getattr(resource, "blob", "") or "")
    if not blob:
        return

    try:
        data = base64.b64decode(blob, validate=True)
    except Exception:
        data = blob.encode("utf-8", errors="replace")

    text = decode_text_bytes(data[:MAX_INLINE_RESOURCE_BYTES], mime_type)
    if text is not None and _is_text_mime(mime_type):
        if len(data) > MAX_INLINE_RESOURCE_BYTES:
            text += f"\n\n[Truncated to {MAX_INLINE_RESOURCE_BYTES} of {len(data)} bytes]"
        text_parts.append(f"[Attached resource: {uri or 'embedded text'}]\n\n{text}")
        return

    saved = _save_attachment_bytes(
        context_id=context_id,
        message_id=message_id,
        index=index,
        label="resource",
        data=data,
        mime_type=mime_type,
    )
    attachments.append(saved)
    text_parts.append(f"[Attached resource: {saved}]")


def _save_attachment_bytes(
    *,
    context_id: str,
    message_id: str,
    index: int,
    label: str,
    data: bytes,
    mime_type: str | None,
) -> str:
    if len(data) > MAX_ATTACHMENT_BYTES:
        data = data[:MAX_ATTACHMENT_BYTES]

    extension = mimetypes.guess_extension((mime_type or "").split(";", 1)[0]) or ".bin"
    base_name = safe_filename(f"{label}-{message_id}-{index}{extension}") or f"{label}-{index}{extension}"
    from helpers import persist_chat

    attach_dir = files.get_abs_path(persist_chat.get_chat_folder_path(context_id), "acp")
    os.makedirs(attach_dir, exist_ok=True)
    path = os.path.join(attach_dir, base_name)
    with open(path, "wb") as handle:
        handle.write(data)
    return files.normalize_a0_path(path)


def _resource_display_name(block: Any, uri: str) -> str:
    title = str(getattr(block, "title", "") or "").strip()
    name = str(getattr(block, "name", "") or "").strip()
    if title and name and title != name:
        return f"{title} ({name})"
    if title:
        return title
    if name:
        return name
    parsed = urlparse(uri)
    return Path(unquote(parsed.path or uri)).name or uri or "resource"


def _is_text_mime(mime_type: str | None) -> bool:
    mime = (mime_type or "").split(";", 1)[0].strip().lower()
    if not mime:
        return False
    return mime.startswith(_TEXT_MIME_PREFIXES) or mime in _TEXT_MIME_TYPES


def _is_probably_text(path: Path, mime_type: str | None) -> bool:
    if _is_text_mime(mime_type):
        return True
    guessed, _encoding = mimetypes.guess_type(str(path))
    if _is_text_mime(guessed):
        return True
    return path.suffix.lower() in {
        ".md",
        ".txt",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml",
        ".html",
        ".css",
        ".sql",
        ".sh",
    }


def decode_text_bytes(data: bytes, mime_type: str | None = None) -> str | None:
    if b"\x00" in data and not _is_text_mime(mime_type):
        return None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")
