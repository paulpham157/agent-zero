# Time Travel Plugin DOX

## Purpose

- Own Agent Zero workspace history, diff inspection, travel, snapshots, and revert for active `/a0/usr` workspaces.

## Ownership

- `helpers/time_travel.py` owns history storage, diff, travel, snapshot, preview, and revert mechanics.
- `api/` owns history list, diff, preview, revert, snapshot, and travel endpoints.
- `webui/` owns the time-travel panel, store, main surface, and thumbnail.
- `plugin.yaml` and `extensions/` own metadata and hook contributions.

## Local Contracts

- Keep history operations scoped to Agent Zero-owned workspaces.
- Revert and travel operations must avoid unintended writes outside managed workspace paths.
- Preserve enough metadata for clear preview and diff inspection before destructive actions.

## Work Guidance

- Coordinate API and UI changes so users can inspect effects before applying travel or revert operations.

## Verification

- Smoke-test snapshot, list, diff, preview, travel, and revert flows after changes.

## Child DOX Index

No child DOX files.
