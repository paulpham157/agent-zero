# Canvas Components DOX

## Purpose

- Own the right-canvas component surface and its state.

## Ownership

- `right-canvas.html` owns canvas markup.
- `right-canvas-store.js` owns canvas state, surface registration, and actions.
- `right-canvas.css` owns canvas-specific styling.

## Local Contracts

- Keep registered surfaces compatible with WebUI extension hooks.
- Preserve responsive layout and avoid overlapping the chat/sidebar shells.
- Right-canvas rail and tab buttons are explicit canvas entry points; they must open surfaces in the canvas even when the same surface was last used as a floating modal.

## Work Guidance

- Use existing surface and extension helpers before adding new canvas infrastructure.

## Verification

- Smoke-test right-canvas open, close, resize, and registered surfaces after changes.

## Child DOX Index

No child DOX files.
