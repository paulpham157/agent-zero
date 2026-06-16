# Chat Compaction Plugin DOX

## Purpose

- Own compacting an entire chat history into a single optimized summary message.
- Keep compaction prompt, helper, API, and modal behavior aligned.

## Ownership

- `plugin.yaml` and `default_config.yaml` own metadata and compaction defaults.
- `api/compact_chat.py` owns the compaction endpoint.
- `helpers/compactor.py` owns summary generation and history rewrite logic.
- `prompts/` owns compaction system and message prompts.
- `webui/` owns the compaction modal and store.

## Local Contracts

- Preserve chat history integrity and persistence after compaction.
- Keep generated summaries bounded by configured model and token limits.
- Do not discard original context data unless the compaction flow explicitly owns that behavior.
- Preserve loaded skill name/revision metadata in summaries without copying full skill bodies.

## Work Guidance

- Coordinate prompt changes with helper behavior and UI confirmation text.

## Verification

- Smoke-test compacting a chat and reloading it after persistence.

## Child DOX Index

No child DOX files.
