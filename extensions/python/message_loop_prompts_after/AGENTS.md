# Message Loop Prompts After Extensions DOX

## Purpose

- Own prompt extras appended after primary message-loop prompt construction.

## Ownership

- Ordered Python files own current datetime, skill recall/load context, agent info, and workdir extras injection.

## Local Contracts

- Keep injected content bounded and clearly attributed.
- Preserve ordering where later prompt extras depend on earlier recall or load results.
- Do not expose secrets or private files from workdir extras.

## Work Guidance

- Coordinate prompt-extra changes with skill, workdir, and profile contracts.

## Verification

- Inspect rendered prompt extras or run prompt-construction tests after changes.

## Child DOX Index

No child DOX files.
