# Message Loop Prompts After Extensions DOX

## Purpose

- Own prompt extras and history-output adjustments appended after primary message-loop prompt construction.

## Ownership

- Ordered Python files own current datetime, skill recall/load context, loaded-skill reattachment, agent info, parallel job status, and workdir extras injection.

## Local Contracts

- Keep injected content bounded and clearly attributed.
- Preserve ordering where later prompt extras depend on earlier recall or load results.
- Do not expose secrets or private files from workdir extras.
- Explicitly loaded skill instructions belong in normal tool-result history; this hook may recall candidate skills, but must not reinject loaded skill bodies through prompt extras every turn.
- If compression hides an explicitly loaded skill body, this hook may reattach the missing visible revision as a bounded normal tool-result history message.

## Work Guidance

- Coordinate prompt-extra changes with skill, workdir, and profile contracts.

## Verification

- Inspect rendered prompt extras or run prompt-construction tests after changes.

## Child DOX Index

No child DOX files.
