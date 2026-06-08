# Chat Components DOX

## Purpose

- Own chat composer, attachments, message queue, navigation, and top-section component groups.

## Ownership

- `input/` owns composer input, progress, banners, and bottom action bars.
- `attachments/` owns drag/drop and attachment preview UI.
- `message-queue/` owns queued message display and store state.
- `navigation/` owns chat navigation state.
- `top-section/` owns chat header/top area.

## Local Contracts

- Preserve Store Gating for all store-backed chat components.
- Use shared API, WebSocket, notification, and attachment helpers where available.
- Do not bypass CSRF or WebSocket state-sync expectations.

## Work Guidance

- Keep composer and attachment changes responsive across desktop and mobile.
- Coordinate payload changes with backend chat, upload, and WebSocket handlers.

## Verification

- Smoke-test sending, queued messages, attachments, drag/drop, and navigation after visible changes.

## Child DOX Index

No child DOX files.
