# mcp_handler.py DOX

## Purpose

- Own the `mcp_handler.py` helper module.
- This module loads MCP server configuration and exposes MCP tools to agents.
- Keep this file-level DOX profile synchronized with `mcp_handler.py` because this directory is intentionally flat.

## Ownership

- `mcp_handler.py` owns the runtime implementation.
- `mcp_handler.py.dox.md` owns durable notes about responsibilities, contracts, side effects, and verification for that implementation.
- Classes:
- `MCPTool` (`Tool`)
  - `get_log_object(self) -> LogItem`
  - `async execute(self, **kwargs)`
  - `async before_execution(self, **kwargs)`
  - `async after_execution(self, response: Response, **kwargs)`
- `MCPServerRemote` (`BaseModel`)
  - `get_error(self) -> str`
  - `get_log(self) -> str`
  - `get_tools(self) -> List[dict[str, Any]]`
  - `has_tool(self, tool_name: str) -> bool`
  - `async call_tool(self, tool_name: str, input_data: Dict[str, Any]) -> CallToolResult`
  - `update(self, config: dict[str, Any]) -> 'MCPServerRemote'`
  - `async initialize(self) -> 'MCPServerRemote'`
- `MCPServerLocal` (`BaseModel`)
  - `get_error(self) -> str`
  - `get_log(self) -> str`
  - `get_tools(self) -> List[dict[str, Any]]`
  - `has_tool(self, tool_name: str) -> bool`
  - `async call_tool(self, tool_name: str, input_data: Dict[str, Any]) -> CallToolResult`
  - `update(self, config: dict[str, Any]) -> 'MCPServerLocal'`
  - `async initialize(self) -> 'MCPServerLocal'`
- `MCPConfig` (`BaseModel`)
  - `get_instance(cls) -> 'MCPConfig'`
  - `wait_for_lock(cls)`
  - `update(cls, config_str: str) -> Any`
  - `normalize_config(cls, servers: Any)`
  - `get_server_log(self, server_name: str) -> str`
  - `get_servers_status(self) -> list[dict[str, Any]]`
  - `get_server_detail(self, server_name: str) -> dict[str, Any]`
  - `is_initialized(self) -> bool`
- `MCPClientBase` (`ABC`)
  - `async update_tools(self) -> 'MCPClientBase'`
  - `has_tool(self, tool_name: str) -> bool`
  - `get_tools(self) -> List[dict[str, Any]]`
  - `async call_tool(self, tool_name: str, input_data: Dict[str, Any]) -> CallToolResult`
  - `get_log(self)`
- `MCPClientLocal` (`MCPClientBase`)
- `CustomHTTPClientFactory` (`ABC`)
- `MCPClientRemote` (`MCPClientBase`)
  - `get_session_id(self) -> Optional[str]`
- Top-level functions:
- `_mcp_get(item: Any, key: str, default: Any=...) -> Any`
- `normalize_name(name: str) -> str`
- `_determine_server_type(config_dict: dict) -> str`: Determine the server type based on configuration, with backward compatibility.
- `_is_streaming_http_type(server_type: str) -> bool`: Check if the server type is a streaming HTTP variant.
- `initialize_mcp(mcp_servers_config: str)`
- Notable constants/configuration names: `MCP_MEDIA_TOKENS_ESTIMATE`, `MAX_MCP_RESOURCE_TEXT_CHARS`, `T`.

## Runtime Contracts

- Helper modules own reusable framework APIs and must preserve public callers unless all callers, tests, and docs are updated together.
- Update this file whenever public functions, classes, persistence behavior, path/security assumptions, side effects, or cross-module contracts change.
- `MCPTool` is a `Tool`.
- `MCPTool` defines `execute(...)`.
- Observed side-effect areas: filesystem writes, network calls, WebSocket state, settings/state persistence, secret handling.
- Imported dependency areas include: `abc`, `anyio.streams.memory`, `asyncio`, `contextlib`, `datetime`, `helpers`, `helpers.log`, `helpers.print_style`, `helpers.tool`, `httpx`, `json`, `mcp`, `mcp.client.sse`, `mcp.client.stdio`, `mcp.client.streamable_http`, `mcp.shared.message`.

## Key Concepts

- Important called helpers/classes observed in the source: `TypeVar`, `name.strip.lower`, `re.sub`, `Field`, `PrivateAttr`, `threading.Lock`, `config_dict.lower`, `server_type.lower`, `MCPConfig.get_instance.is_initialized`, `self.agent.context.log.log`, `str.strip`, `media_artifacts.guess_extension`, `callable`, `self._content_item_dump`, `join`, `Response`, `self.get_log_object`, `self._raw_tool_response`, `additional.pop`, `self._coerce_media_token_estimate`.
- Keep request/response, tool, or helper semantics documented here at the same time as source changes.

## Work Guidance

- Preserve public helper APIs used by core code and plugins unless every caller is updated.
- Keep path, auth, secret, persistence, network, and subprocess behavior explicit and bounded.
- Prefer adding cohesive helper functions here only when behavior is reused across modules.

## Verification

- Run targeted tests for changed helper behavior; run security regressions for auth, filesystem, WebSocket, tunnel, upload, or secret-handling helpers.
- Related tests observed by source search:
  - `tests/test_mcp_handler_multimodal.py`

## Child DOX Index

No child DOX files.
