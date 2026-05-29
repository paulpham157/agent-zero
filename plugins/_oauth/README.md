# OAuth Connections

Generic local OAuth bridge for Agent Zero.

The first provider is `Codex/ChatGPT Account`:

- signs in with OpenAI's Codex device-code flow
- writes credentials to an Agent Zero-owned `auth.json` file
- refreshes local tokens when needed
- exposes a loopback OpenAI-compatible wrapper at `/oauth/codex/v1`

Tokens in `auth.json` are password-equivalent credentials. Keep this plugin on trusted local machines only. Do not configure `auth_file_path` to share a rotating refresh-token file with Codex CLI or another client.
