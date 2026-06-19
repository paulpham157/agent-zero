# What's New Plugin DOX

## Purpose

- Own the built-in version-gated "What's New" modal for showcasing new Agent Zero features after updates.

## Ownership

- `plugin.yaml` owns metadata and always-enabled status.
- `webui/` owns the modal markup, Alpine store, copy, and showcase media assets.
- `extensions/webui/initFw_end/` owns the startup trigger that opens the modal when the installed version is newer than the locally seen version.

## Local Contracts

- Do not add a "Don't show this again" control; dismissal records the current installed version as seen.
- Keep the modal copy concise, left-aligned, and paired with feature media.
- Keep modal actions in the pinned footer using the shared Agent Zero button classes.
- Store the seen-version marker in browser-local state only; do not persist this under `usr/`.

## Work Guidance

- Add showcase assets under `webui/assets/` and reference them through `/plugins/_whats_new/webui/assets/...`.
- Keep the startup extension idempotent and tolerant of missing or non-comparable version labels.
- Prefer release-line comparisons over development commit-distance comparisons so local development builds do not reopen the modal on every commit.

## Verification

- Run `pytest tests/test_whats_new_static.py` after changing the modal, trigger, or assets.
- Smoke-test startup display, slide navigation, dismissal, and same-version reload behavior in the WebUI.

## Child DOX Index

No child DOX files.
