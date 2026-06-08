# Sidebar Components DOX

## Purpose

- Own left sidebar layout, chat/task lists, top actions, and bottom preferences components.

## Ownership

- `left-sidebar.html` and `sidebar-store.js` own sidebar shell and shared state.
- `top-section/` owns header and quick actions.
- `chats/` owns chat list UI and state.
- `tasks/` owns task list UI and state.
- `bottom/` owns lower sidebar controls and preferences panel.

## Local Contracts

- Preserve responsive sidebar behavior and collapsed/expanded state.
- Keep chat and task list updates compatible with WebSocket state sync.
- Avoid text or controls overflowing fixed sidebar widths.

## Work Guidance

- Coordinate navigation and state changes with WebSocket sync and chat/project stores.

## Verification

- Smoke-test sidebar collapse, chat list, task list, quick actions, and preferences after changes.

## Child DOX Index

No child DOX files.
