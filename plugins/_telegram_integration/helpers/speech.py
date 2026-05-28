from __future__ import annotations

import re
import uuid

from agent import AgentContext
from helpers import files
from plugins._telegram_integration.helpers.constants import (
    CTX_TG_SPEECH_ENABLED,
    CTX_TG_SPEECH_WARNING_SENT,
    DOWNLOAD_FOLDER,
)


MAX_SPEECH_CHARS = 1800


def is_enabled(context: AgentContext) -> bool:
    return bool(context.get_data(CTX_TG_SPEECH_ENABLED))


async def synthesize_attachment(context: AgentContext, text: str) -> tuple[str | None, str | None]:
    if not is_enabled(context):
        return None, None

    speech_text = _speech_text(text)
    if not speech_text:
        return None, "Speech mode is enabled, but there was no readable text to speak."

    try:
        from plugins._kokoro_tts.helpers import runtime
    except Exception:
        return None, _setup_message()

    if not runtime.is_globally_enabled():
        return None, _setup_message()

    try:
        audio = await runtime.synthesize_sentences([speech_text])
    except Exception as exc:
        return None, f"Speech mode is enabled, but text-to-speech failed: {exc}"

    if not audio:
        return None, "Speech mode is enabled, but text-to-speech returned no audio."

    name = f"telegram_speech_{context.id}_{uuid.uuid4().hex[:10]}.wav"
    relative_path = f"{DOWNLOAD_FOLDER}/{name}"
    files.write_file_base64(relative_path, audio)
    return files.get_abs_path_dockerized(relative_path), None


def consume_warning(context: AgentContext, warning: str | None) -> str | None:
    if not warning:
        context.data.pop(CTX_TG_SPEECH_WARNING_SENT, None)
        return None
    if context.data.get(CTX_TG_SPEECH_WARNING_SENT):
        return None
    context.data[CTX_TG_SPEECH_WARNING_SENT] = True
    return warning


def _setup_message() -> str:
    return (
        "Speech mode is enabled, but Kokoro TTS is not available. "
        "Enable the Kokoro TTS plugin from Agent Zero settings, then try again."
    )


def _speech_text(text: str) -> str:
    value = str(text or "")
    value = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[*_#>\-]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > MAX_SPEECH_CHARS:
        value = value[:MAX_SPEECH_CHARS].rstrip()
    return value
