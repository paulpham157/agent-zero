from __future__ import annotations

import asyncio
import json
import logging
import threading
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Deque


logger = logging.getLogger(__name__)

CTX_IS_ACP = "acp_session"
CTX_CWD = "acp_cwd"
CTX_ADDITIONAL_DIRECTORIES = "acp_additional_directories"
CTX_MODE = "acp_mode"
CTX_CONFIG_OPTIONS = "acp_config_options"
CTX_MODEL_ID = "acp_model_id"
CTX_WORKDIR = "workdir_path"

DEFAULT_MODE = "default"

_MAX_RAW_OUTPUT = 12000


@dataclass
class SessionBridge:
    context_id: str
    session_id: str
    conn: Any
    loop: asyncio.AbstractEventLoop
    response_text_sent: str = ""
    thought_text_sent: str = ""
    message_id: str = ""
    tool_queues: dict[str, Deque[str]] = field(default_factory=lambda: defaultdict(deque))
    lock: threading.RLock = field(default_factory=threading.RLock)


_bridges_by_context: dict[str, SessionBridge] = {}
_bridges_by_session: dict[str, SessionBridge] = {}
_registry_lock = threading.RLock()


def register_bridge(
    *,
    context_id: str,
    session_id: str,
    conn: Any,
    loop: asyncio.AbstractEventLoop,
) -> SessionBridge:
    bridge = SessionBridge(
        context_id=context_id,
        session_id=session_id,
        conn=conn,
        loop=loop,
    )
    with _registry_lock:
        _bridges_by_context[context_id] = bridge
        _bridges_by_session[session_id] = bridge
    return bridge


def unregister_bridge(context_id: str | None = None, session_id: str | None = None) -> None:
    with _registry_lock:
        bridge = None
        if context_id:
            bridge = _bridges_by_context.pop(context_id, None)
        if session_id:
            bridge = _bridges_by_session.pop(session_id, None) or bridge
        if bridge:
            _bridges_by_context.pop(bridge.context_id, None)
            _bridges_by_session.pop(bridge.session_id, None)


def get_bridge_for_context(context_id: str) -> SessionBridge | None:
    with _registry_lock:
        return _bridges_by_context.get(context_id)


def get_bridge_for_session(session_id: str) -> SessionBridge | None:
    with _registry_lock:
        return _bridges_by_session.get(session_id)


def reset_turn(context_id: str, message_id: str = "") -> None:
    bridge = get_bridge_for_context(context_id)
    if not bridge:
        return
    with bridge.lock:
        bridge.response_text_sent = ""
        bridge.thought_text_sent = ""
        bridge.message_id = message_id
        bridge.tool_queues.clear()


def send_agent_delta(context_id: str, full_text: str) -> bool:
    bridge = get_bridge_for_context(context_id)
    if not bridge:
        return False
    full_text = str(full_text or "")
    with bridge.lock:
        previous = bridge.response_text_sent
        if full_text == previous:
            return False
        if full_text.startswith(previous):
            delta = full_text[len(previous) :]
        else:
            delta = full_text
        bridge.response_text_sent = full_text
    if not delta:
        return False
    return _send_acp_helper_update(bridge, "update_agent_message_text", delta)


def send_agent_text(context_id: str, text: str) -> bool:
    bridge = get_bridge_for_context(context_id)
    if not bridge:
        return False
    text = str(text or "")
    if not text:
        return False
    with bridge.lock:
        bridge.response_text_sent += text
    return _send_acp_helper_update(bridge, "update_agent_message_text", text)


def send_agent_thought_delta(context_id: str, full_text: str) -> bool:
    bridge = get_bridge_for_context(context_id)
    if not bridge:
        return False
    full_text = str(full_text or "")
    with bridge.lock:
        previous = bridge.thought_text_sent
        if full_text == previous:
            return False
        if full_text.startswith(previous):
            delta = full_text[len(previous) :]
        else:
            delta = full_text
        bridge.thought_text_sent = full_text
    if not delta:
        return False
    return _send_acp_helper_update(bridge, "update_agent_thought_text", delta)


def start_tool(context_id: str, tool_name: str, tool_args: dict[str, Any] | None = None) -> str:
    bridge = get_bridge_for_context(context_id)
    if not bridge:
        return ""

    normalized_name = str(tool_name or "tool")
    if normalized_name == "response":
        return ""

    tool_call_id = f"a0-{uuid.uuid4().hex}"
    title = _tool_title(normalized_name, tool_args or {})
    kind = _tool_kind(normalized_name, tool_args or {})
    raw_input = _json_safe(tool_args or {})

    try:
        import acp

        update = acp.start_tool_call(
            tool_call_id,
            title,
            kind=kind,
            status="in_progress",
            raw_input=raw_input,
        )
    except Exception:
        logger.debug("Could not build ACP tool start", exc_info=True)
        return ""

    with bridge.lock:
        bridge.tool_queues[normalized_name].append(tool_call_id)
    _send_update(bridge, update)
    return tool_call_id


def finish_tool(context_id: str, tool_name: str, response: Any) -> bool:
    bridge = get_bridge_for_context(context_id)
    if not bridge:
        return False
    normalized_name = str(tool_name or "tool")
    if normalized_name == "response":
        return False

    with bridge.lock:
        queue = bridge.tool_queues.get(normalized_name)
        if not queue:
            return False
        tool_call_id = queue.popleft()
        if not queue:
            bridge.tool_queues.pop(normalized_name, None)

    message = getattr(response, "message", response)
    raw_output = _truncate_raw_output(message)
    try:
        import acp

        update = acp.update_tool_call(
            tool_call_id,
            status="completed",
            raw_output=raw_output,
        )
    except Exception:
        logger.debug("Could not build ACP tool completion", exc_info=True)
        return False
    _send_update(bridge, update)
    return True


async def send_update_async(session_id: str, update: Any) -> bool:
    bridge = get_bridge_for_session(session_id)
    if not bridge:
        return False
    try:
        await bridge.conn.session_update(session_id, update)
        return True
    except Exception:
        logger.debug("Could not send ACP update", exc_info=True)
        return False


def _send_acp_helper_update(bridge: SessionBridge, helper_name: str, text: str) -> bool:
    try:
        import acp

        helper = getattr(acp, helper_name)
        update = helper(text)
    except Exception:
        logger.debug("Could not build ACP text update", exc_info=True)
        return False
    _send_update(bridge, update)
    return True


def _send_update(bridge: SessionBridge, update: Any) -> None:
    if bridge.loop.is_closed():
        return

    async def _deliver() -> None:
        await bridge.conn.session_update(bridge.session_id, update)

    future = asyncio.run_coroutine_threadsafe(_deliver(), bridge.loop)

    def _log_failure(done_future: Any) -> None:
        try:
            done_future.result()
        except Exception:
            logger.debug("Failed to send ACP session update", exc_info=True)

    future.add_done_callback(_log_failure)


def _tool_title(tool_name: str, tool_args: dict[str, Any]) -> str:
    action = tool_args.get("action") or tool_args.get("method") or ""
    if action:
        return f"{tool_name}: {action}"
    return tool_name.replace("_", " ").strip().title() or "Tool"


def _tool_kind(tool_name: str, tool_args: dict[str, Any]) -> str:
    probe = " ".join(
        str(value).lower()
        for value in (tool_name, tool_args.get("action", ""), tool_args.get("method", ""))
    )
    if any(token in probe for token in ("read", "list", "show", "inspect")):
        return "read"
    if any(token in probe for token in ("write", "edit", "patch", "replace", "create")):
        return "edit"
    if any(token in probe for token in ("delete", "remove")):
        return "delete"
    if any(token in probe for token in ("move", "rename")):
        return "move"
    if any(token in probe for token in ("search", "find", "grep")):
        return "search"
    if any(token in probe for token in ("terminal", "shell", "python", "node", "code_execution")):
        return "execute"
    if any(token in probe for token in ("browser", "fetch", "http")):
        return "fetch"
    return "other"


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _truncate_raw_output(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        if len(value) <= _MAX_RAW_OUTPUT:
            return value
        hidden = len(value) - _MAX_RAW_OUTPUT
        return value[:_MAX_RAW_OUTPUT] + f"\n\n[ACP output truncated: {hidden} characters hidden]"
    return _json_safe(value)
