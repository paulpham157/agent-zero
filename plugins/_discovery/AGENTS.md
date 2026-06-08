# Plugin Discovery DOX

## Purpose

- Own contextual plugin discovery cards and welcome-screen promotions.

## Ownership

- `plugin.yaml` owns metadata and always-enabled status.
- `extensions/` owns backend or WebUI discovery contributions.
- `webui/discovery-store.js` owns discovery UI state and actions.

## Local Contracts

- Discovery cards must be accurate, dismissible where appropriate, and avoid advertising already-complete setup.
- CTA actions must match supported welcome-screen action contracts.
- Keep card IDs unique and plugin-prefixed.

## Work Guidance

- Prefer backend status checks before surfacing setup or integration prompts.

## Verification

- Smoke-test welcome-screen discovery cards, ordering, dismissal, and CTA behavior after changes.

## Child DOX Index

No child DOX files.
