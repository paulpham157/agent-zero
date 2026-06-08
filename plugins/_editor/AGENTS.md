# Editor Plugin DOX

## Purpose

- Own the native Markdown editor surface for canvas and floating modal workflows.

## Ownership

- `api/` owns editor session and WebSocket handlers.
- `helpers/` owns markdown session and open-file context helpers.
- `prompts/` owns agent-visible open-file context.
- `webui/` owns editor panel, preview, store, and main surface.
- `extensions/` owns editor hook contributions.

## Local Contracts

- Keep editor session state synchronized across API, WebSocket, and WebUI panel behavior.
- Do not expose unsaved content or local paths beyond intended chat/context surfaces.

## Work Guidance

- Coordinate editor preview and session changes with canvas surface registration.

## Verification

- Smoke-test opening, editing, previewing, and reconnecting editor sessions after changes.

## Child DOX Index

No child DOX files.
