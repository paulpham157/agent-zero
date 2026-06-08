# Welcome Components DOX

## Purpose

- Own the WebUI welcome screen, discovery cards, banners, and related state.

## Ownership

- `welcome-screen.html` owns welcome screen markup and layout.
- `welcome-store.js` owns welcome state, banners, cards, and actions.

## Local Contracts

- Keep banner and discovery card behavior compatible with Python `banners` extensions.
- Supported banner/card CTA actions must stay synchronized with plugin discovery contracts.
- Do not show setup prompts for already configured plugins when backend status can prevent it.

## Work Guidance

- Coordinate visual card or CTA changes with plugin discovery and onboarding surfaces.

## Verification

- Smoke-test alert banners, feature cards, dismissal, priority ordering, and CTA actions after changes.

## Child DOX Index

No child DOX files.
