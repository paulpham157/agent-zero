# mcp_servers_apply.py DOX

## Purpose

- Own the `mcp_servers_apply.py` API endpoint.
- This module handles MCP server servers apply requests.
- Keep this file-level DOX profile synchronized with `mcp_servers_apply.py` because this directory is intentionally flat.

## Ownership

- `mcp_servers_apply.py` owns the runtime implementation.
- `mcp_servers_apply.py.dox.md` owns durable notes about responsibilities, contracts, side effects, and verification for that implementation.
- Classes:
- `McpServersApply` (`ApiHandler`)
  - `async process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response`

## Runtime Contracts

- HTTP handlers must derive from `helpers.api.ApiHandler`; WebSocket handlers must derive from `helpers.ws.WsHandler`.
- Update this file whenever request payloads, authentication or CSRF requirements, response shapes, route side effects, or WebSocket event contracts change.
- `McpServersApply` is an `ApiHandler`.
- `McpServersApply` defines `process(...)`.
- Observed side-effect areas: settings/state persistence.
- Imported dependency areas include: `helpers.api`, `helpers.mcp_handler`, `helpers.settings`, `time`, `typing`.

## Key Concepts

- Important called helpers/classes observed in the source: `set_settings_delta`, `time.sleep`, `MCPConfig.get_instance.get_servers_status`, `MCPConfig.get_instance`.
- Keep request/response, tool, or helper semantics documented here at the same time as source changes.

## Work Guidance

- Preserve authentication, CSRF, loopback, and API-key checks unless the endpoint contract explicitly changes.
- Update frontend callers, plugin callers, and tests together when payload shape changes.
- Use `helpers.api.Response` for non-JSON responses, files, redirects, or status-specific replies.

## Verification

- Run endpoint-specific or API/WebSocket tests for changed behavior; smoke-test browser callers when no focused test exists.
- No direct test reference was found by name search; choose the nearest behavioral test or perform a focused smoke check.

## Child DOX Index

No child DOX files.
