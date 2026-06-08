# call_subordinate.py DOX

## Purpose

- Own the `call_subordinate.py` agent tool.
- This module delegates work to a subordinate Agent Zero profile and returns its result.
- Keep this file-level DOX profile synchronized with `call_subordinate.py` because this directory is intentionally flat.

## Ownership

- `call_subordinate.py` owns the runtime implementation.
- `call_subordinate.py.dox.md` owns durable notes about responsibilities, contracts, side effects, and verification for that implementation.
- Classes:
- `Delegation` (`Tool`)
  - `async execute(self, message=..., reset=..., **kwargs)`
  - `get_log_object(self)`

## Runtime Contracts

- Tool modules must define `helpers.tool.Tool` subclasses and return `helpers.tool.Response` from `execute(...)`.
- Update this file whenever tool arguments, output shape, `break_loop` behavior, intervention handling, prompt instructions, or side effects change.
- `Delegation` is a `Tool`.
- `Delegation` defines `execute(...)`.
- Observed side-effect areas: filesystem writes, settings/state persistence.
- Imported dependency areas include: `agent`, `extensions.python.hist_add_tool_result`, `helpers.tool`, `initialize`.

## Key Concepts

- Important called helpers/classes observed in the source: `self.agent.get_data`, `subordinate.hist_add_user_message`, `subordinate.history.new_topic`, `Response`, `self.agent.context.log.log`, `initialize_agent`, `Agent`, `sub.set_data`, `self.agent.set_data`, `UserMessage`, `subordinate.monologue`, `self.agent.read_prompt`, `str.lower.strip`, `str.lower`.
- Keep request/response, tool, or helper semantics documented here at the same time as source changes.

## Work Guidance

- Keep tool output concise, model-readable, and safe for history persistence.
- Coordinate argument or behavior changes with prompt tool instructions and skill guidance.
- Respect intervention flow for long-running, external, or user-visible operations.

## Verification

- Run targeted tool and prompt-contract tests for changed behavior; smoke-test agent execution when no focused test exists.
- Related tests observed by source search:
  - `tests/test_default_prompt_budget.py`

## Child DOX Index

No child DOX files.
