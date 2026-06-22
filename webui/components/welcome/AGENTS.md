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
- The welcome screen mounts the shared chat composer to start a new chat; keep it mutually exclusive with the normal chat input DOM.
- Render `system-resources` as the dedicated System Resources panel, not as a generic alert banner.

## Work Guidance

- Coordinate visual card or CTA changes with plugin discovery and onboarding surfaces.
- Keep the lower welcome grid focused on Connect Channels, OAuth accounts, and System Resources unless the target design changes.

## Verification

- Smoke-test alert banners, feature cards, dismissal, priority ordering, and CTA actions after changes.

## Child DOX Index

No child DOX files.
