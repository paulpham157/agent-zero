from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plugins._acp.helpers.content import (
    normalize_cwd,
    path_from_file_uri,
    prompt_blocks_to_user_message,
)
from plugins._acp import hooks


def test_acp_manifest_declares_builtin_plugin() -> None:
    manifest = (ROOT / "plugins" / "_acp" / "plugin.yaml").read_text(encoding="utf-8")
    assert "name: _acp" in manifest
    assert "always_enabled: true" in manifest
    assert 'version: "1.19"' in manifest


def test_acp_registry_metadata_matches_release() -> None:
    registry = (ROOT / "plugins" / "_acp" / "acp_registry" / "agent.json").read_text(
        encoding="utf-8"
    )
    assert '"version": "1.19"' in registry
    assert '"license": "MIT"' in registry


def test_acp_dependency_is_pinned() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "agent-client-protocol==0.10.1" in requirements


def test_acp_hook_uses_root_requirement_pin() -> None:
    assert hooks.get_acp_requirement() == "agent-client-protocol==0.10.1"
    assert not (ROOT / "plugins" / "_acp" / "requirements.txt").exists()


def test_acp_entrypoint_attempts_lazy_dependency_install() -> None:
    entry = (ROOT / "plugins" / "_acp" / "entry.py").read_text(encoding="utf-8")
    assert "_import_acp_or_install()" in entry
    assert "hooks.ensure_dependencies(raise_on_error=False)" in entry


def test_acp_initialize_metadata_uses_release_version_constant() -> None:
    server = (ROOT / "plugins" / "_acp" / "helpers" / "server.py").read_text(
        encoding="utf-8"
    )
    assert "version=AGENT_ZERO_ACP_VERSION" in server


def test_context_workdir_override_is_wired() -> None:
    code_execution = (
        ROOT / "plugins" / "_code_execution" / "tools" / "code_execution_tool.py"
    ).read_text(encoding="utf-8")
    workdir_prompt = (
        ROOT / "extensions" / "python" / "message_loop_prompts_after" / "_75_include_workdir_extras.py"
    ).read_text(encoding="utf-8")
    assert 'get_data("workdir_path")' in code_execution
    assert 'get_data("workdir_path")' in workdir_prompt


def test_file_uri_path_translation() -> None:
    assert str(path_from_file_uri("file:///tmp/example.py")) == "/tmp/example.py"
    assert str(path_from_file_uri("file:///C:/Users/Ada/work/app.py")) == "/mnt/c/Users/Ada/work/app.py"
    assert path_from_file_uri("https://example.com/app.py") is None


def test_prompt_blocks_inline_text_resource(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("hello ACP", encoding="utf-8")
    block = SimpleNamespace(
        type="resource_link",
        uri=source.as_uri(),
        name="notes.md",
        mime_type="text/markdown",
    )

    parts = prompt_blocks_to_user_message(
        [SimpleNamespace(type="text", text="Read this"), block],
        context_id="static-test",
        message_id="msg",
    )

    assert "Read this" in parts.text
    assert "hello ACP" in parts.text
    assert parts.attachments == []


def test_normalize_cwd_returns_absolute_path() -> None:
    assert Path(normalize_cwd(".")).is_absolute()
