from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_welcome_screen_embeds_shared_new_chat_composer() -> None:
    welcome = _read("webui/components/welcome/welcome-screen.html")
    index = _read("webui/index.html")
    discovery_cards = _read(
        "plugins/_discovery/extensions/webui/welcome-actions-end/discovery-cards.html"
    )

    assert 'class="welcome-composer"' in welcome
    assert 'path="chat/attachments/inputPreview.html"' in welcome
    assert 'path="chat/input/chat-bar-input.html"' in welcome
    assert '<h2>Quick Actions</h2>' in welcome
    assert 'class="welcome-lower-grid"' in welcome
    assert 'x-extension id="welcome-actions-end"' in welcome

    assert "x-if=\"$store.welcomeStore && $store.welcomeStore.isVisible\"" in index
    assert "x-if=\"!$store.welcomeStore || !$store.welcomeStore.isVisible\"" in index
    assert "Connect Channels" in discovery_cards
    assert "oauthAccountCards" in discovery_cards
    assert "discovery-account-card" in discovery_cards
    assert "topHeroCards" not in discovery_cards
    assert "bottomHeroCards" not in discovery_cards
    assert "background: var(--color-background);" in welcome
    assert "radial-gradient" not in welcome


def test_welcome_composer_can_create_a_chat_before_sending() -> None:
    input_store = _read("webui/components/chat/input/input-store.js")
    chats_store = _read("webui/components/sidebar/chats/chats-store.js")

    assert 'return "Ask anything to start a new chat";' in input_store
    assert "if (!chatsStore.selected" in input_store
    assert "await chatsStore.newChat()" in input_store
    assert "return response.ctxid;" in chats_store
    assert 'return "arrow_forward";' in input_store


def test_welcome_composer_buttons_keep_target_geometry_without_glow() -> None:
    chat_bar = _read("webui/components/chat/input/chat-bar-input.html")
    mic_css = _read("plugins/_whisper_stt/webui/whisper-stt.css")

    assert "#send-button {\n      order: 2;\n      border-radius: 12px;" in chat_bar
    assert "background-color: #4248f1;" in chat_bar
    assert "background-color: #e67e22;" in chat_bar
    assert "linear-gradient" not in chat_bar
    assert "#microphone-button {\n  order: 1;" in mic_css
    assert "border-radius: 12px;" in mic_css
    assert "background-color: transparent;" in mic_css
    assert "#microphone-button.mic-inactive {\n  color: grey;" in mic_css
    assert "background-color: grey;" not in mic_css
    assert "#microphone-button.mic-listening {\n  color: red;" in mic_css
    assert "#microphone-button.mic-recording {\n  color: green;" in mic_css
    assert "#microphone-button.mic-activating svg" in mic_css
    assert "rgba(34, 68, 255" not in chat_bar
    assert "rgba(217, 119, 6" not in chat_bar


def test_welcome_hover_and_focus_borders_use_neutral_tokens() -> None:
    surfaces = "\n".join(
        [
            _read("webui/components/welcome/welcome-screen.html"),
            _read("webui/components/chat/input/chat-bar-input.html"),
            _read("plugins/_discovery/extensions/webui/welcome-actions-end/discovery-cards.html"),
        ]
    )

    assert "#315cf6" not in surfaces
    assert "rgba(34, 68, 255" not in surfaces
    assert "linear-gradient" not in surfaces
    assert "border-color: color-mix(in srgb, var(--color-primary" not in surfaces
    assert "border-color: var(--color-primary" not in surfaces
    assert "border-color: color-mix(in srgb, var(--color-border) 88%, var(--color-text) 12%)" in surfaces


def test_composer_uses_rubik_until_caret_enters_fenced_code() -> None:
    chat_bar = _read("webui/components/chat/input/chat-bar-input.html")
    input_store = _read("webui/components/chat/input/input-store.js")

    assert "font-family: var(--font-family-main" in chat_bar
    assert "#chat-input.is-code-context" in chat_bar
    assert "font-family: var(--font-family-code" in chat_bar
    assert "'is-code-context': $store.chatInput.isCodeContext" in chat_bar
    assert "_isCaretInsideFence(text, index)" in input_store
    assert "matches.length % 2 === 1" in input_store
