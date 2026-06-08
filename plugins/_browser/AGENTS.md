# Browser Plugin DOX

## Purpose

- Own the built-in Playwright browser tool and WebUI browser viewer.
- Bridge browser automation, page inspection helpers, and browser panel UI.

## Ownership

- `plugin.yaml` and `default_config.yaml` own metadata and browser settings defaults.
- `tools/browser.py` owns the agent-facing browser tool.
- `helpers/` owns Playwright runtime, selectors, URL helpers, extension management, and connector runtime logic.
- `api/` owns status, extension, and browser WebSocket handlers.
- `assets/`, `prompts/`, `skills/`, `extensions/`, and `webui/` own browser scripts, prompts, skill guidance, hook contributions, and UI.

## Local Contracts

- Keep browser actions safe around external pages, credentials, and user data.
- Preserve Playwright lifecycle cleanup and WebSocket viewer compatibility.
- Do not hardcode user-specific browser paths or secrets.

## Work Guidance

- Coordinate tool, helper, and panel changes so browser state shown in the UI matches tool behavior.

## Verification

- Smoke-test browser launch, navigation, DOM capture, and WebUI viewer after runtime changes.

## Child DOX Index

No child DOX files.
