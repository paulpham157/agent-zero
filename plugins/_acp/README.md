# Agent Client Protocol

This builtin plugin exposes Agent Zero through the Agent Client Protocol (ACP)
over stdio so ACP-capable editors can create, load, resume, and prompt Agent
Zero sessions directly from a workspace.

## Usage

From the Agent Zero repository or runtime container:

```bash
python -m plugins._acp
```

For the Dockerized Agent Zero runtime, point the editor command at the
framework interpreter inside the container, for example:

```bash
docker exec -i agent-zero /opt/venv-a0/bin/python -m plugins._acp
```

ACP reserves stdout for JSON-RPC, so the adapter writes diagnostics to stderr.

## Checks

```bash
python -m plugins._acp --check
python -m plugins._acp --registry
```

The ACP Python SDK is provided by `agent-client-protocol`.
Fresh Docker images install it through the root `requirements.txt`; self-updated
instances lazy-install the same root pin through `plugins/_acp/hooks.py` the
first time the ACP stdio entrypoint starts.
