from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_whats_new_modal_uses_showcase_assets_and_branded_footer():
    html = (PROJECT_ROOT / "plugins/_whats_new/webui/whats-new.html").read_text(encoding="utf-8")
    store = (PROJECT_ROOT / "plugins/_whats_new/webui/whats-new-store.js").read_text(encoding="utf-8")

    assert "What's New in Agent Zero" in html
    assert "data-modal-footer" in html
    assert "btn btn-ok" in html
    assert "btn btn-field" in html
    assert "/plugins/_whats_new/webui/whats-new-store.js" in html
    assert "/plugins/_whats_new/webui/assets" in store
    assert "Don't show this again" not in html + store

    for asset in ["parallel-subs.webm", "mcp-servers.png", "skills-scanner.png"]:
        assert asset in html + store
        assert (PROJECT_ROOT / "plugins/_whats_new/webui/assets" / asset).exists()

    assert "Parallel tool calls and subagents" in store
    assert (
        "Agent Zero can now split work across parallel tool and subagents calls and combine concurrent steps results."
        in store
    )
    assert "Redesigned MCP configuration UI" in store
    assert "Skills Scanner powered by Snyk Agent Scan" in store
    assert "Remote URL transports" in store
    assert "Raw JSON" in store
    assert "prompt-injection risks" in store
    assert "Catch risky skill instructions early" in store
    assert "Include MCP servers in the same pass" not in store


def test_whats_new_startup_trigger_is_version_gated():
    content = (
        PROJECT_ROOT / "plugins/_whats_new/extensions/webui/initFw_end/whats-new.js"
    ).read_text(encoding="utf-8")

    assert "globalThis.gitinfo?.version" in content
    assert "a0_whats_new_seen_version" in content
    assert "/plugins/_whats_new/webui/whats-new.html" in content
    assert "compareVersions" in content
    assert "shouldShowWhatsNew" in content
    assert "modal-closed" in content
    assert "markVersionSeen" in content
    assert "Don't show this again" not in content


def test_whats_new_plugin_manifest_is_always_enabled():
    manifest = (PROJECT_ROOT / "plugins/_whats_new/plugin.yaml").read_text(encoding="utf-8")

    assert "name: _whats_new" in manifest
    assert "always_enabled: true" in manifest
    assert "settings_sections: []" in manifest
