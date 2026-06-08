# Settings Components DOX

## Purpose

- Own WebUI settings shell and built-in settings subsections.

## Ownership

- `settings.html` and `settings-store.js` own the settings shell and state.
- Subdirectories own settings areas such as agent, external, developer, MCP, backup, plugins, secrets, skills, tunnel, and A2A.

## Local Contracts

- Keep settings payloads synchronized with backend APIs and plugin settings contracts.
- Do not store secrets in localStorage, URLs, or console output.
- Preserve Store Gating and modal footer conventions in settings components.

## Work Guidance

- Prefer subsection-local stores for complex settings areas.
- Coordinate plugin settings UI changes with `webui/components/plugins/` and `plugins/AGENTS.md`.

## Verification

- Smoke-test changed settings tabs and save/reload behavior after visible or API changes.

## Child DOX Index

No child DOX files.
