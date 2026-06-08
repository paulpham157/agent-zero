# agent_profile_set.py DOX

## Purpose

- Own the `agent_profile_set.py` API endpoint.
- This module sets the active agent profile for a chat context and returns profile label metadata.
- Keep this file-level DOX profile synchronized with `agent_profile_set.py` because this directory is intentionally flat.

## Ownership

- `agent_profile_set.py` owns the runtime implementation.
- `agent_profile_set.py.dox.md` owns durable notes about responsibilities, contracts, side effects, and verification for that implementation.
- Classes:
- `SetAgentProfile` (`ApiHandler`)
  - `async process(self, input: dict, request: Request) -> dict | Response`
- Top-level functions:
- `_agent_profile_labels() -> dict[str, str]`

## Runtime Contracts

- HTTP handlers must derive from `helpers.api.ApiHandler`; WebSocket handlers must derive from `helpers.ws.WsHandler`.
- Update this file whenever request payloads, authentication or CSRF requirements, response shapes, route side effects, or WebSocket event contracts change.
- `SetAgentProfile` is an `ApiHandler`.
- `SetAgentProfile` defines `process(...)`.
- Observed side-effect areas: filesystem writes, settings/state persistence.
- Imported dependency areas include: `agent`, `helpers`, `helpers.api`, `helpers.persist_chat`, `helpers.state_monitor_integration`, `initialize`.

## Key Concepts

- Important called helpers/classes observed in the source: `str.strip`, `context.is_running`, `_agent_profile_labels`, `initialize_agent`, `save_tmp_chat`, `mark_dirty_for_context`, `subagents.get_all_agents_list`, `Response`, `agent.get_data`.
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
