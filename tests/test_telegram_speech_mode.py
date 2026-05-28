import asyncio

from plugins._telegram_integration.extensions.python.process_chain_end import (
    _55_telegram_reply,
)
from plugins._telegram_integration.helpers import command_ui, speech
from plugins._telegram_integration.helpers.constants import (
    CTX_TG_BOT,
    CTX_TG_REPLY_TO,
    CTX_TG_SPEECH_ENABLED,
)


class FakeContext:
    id = "ctx-speech"

    def __init__(self):
        self.data = {}

    def get_data(self, key):
        return self.data.get(key)

    def set_data(self, key, value):
        self.data[key] = value


class FakeAgent:
    number = 0

    def __init__(self):
        self.context = FakeContext()
        self.context.data[CTX_TG_BOT] = "main"
        self.context.data[CTX_TG_REPLY_TO] = 456


def test_speech_toggle_defaults_off():
    context = FakeContext()

    text, markup = command_ui._toggle_view(context, CTX_TG_SPEECH_ENABLED, "Speech replies")

    assert "Speech replies: <b>disabled</b>" == text
    assert markup["inline_keyboard"][0][0]["callback_data"] == "tg:speech:on"
    assert markup["inline_keyboard"][0][1]["callback_data"] == "tg:speech:off"


def test_speech_text_is_cleaned_for_tts():
    cleaned = speech._speech_text(
        "**Hello** [`Agent Zero`](https://example.com)\n\n```python\nprint('skip')\n```"
    )

    assert cleaned == "Hello Agent Zero"


def test_speech_synthesis_writes_audio_attachment(monkeypatch):
    context = FakeContext()
    context.data[CTX_TG_SPEECH_ENABLED] = True
    writes = []

    class FakeRuntime:
        @staticmethod
        def is_globally_enabled():
            return True

        @staticmethod
        async def synthesize_sentences(sentences):
            assert sentences == ["Hello from Agent Zero."]
            return "UklGRg=="

    monkeypatch.setattr(speech.files, "write_file_base64", lambda path, audio: writes.append((path, audio)))
    monkeypatch.setattr(speech.files, "get_abs_path_dockerized", lambda path: f"/a0/{path}")
    monkeypatch.setitem(__import__("sys").modules, "plugins._kokoro_tts.helpers.runtime", FakeRuntime)

    path, warning = asyncio.run(speech.synthesize_attachment(context, "Hello from Agent Zero."))

    assert warning is None
    assert path.startswith("/a0/usr/uploads/telegram_speech_ctx-speech_")
    assert path.endswith(".wav")
    assert writes[0][1] == "UklGRg=="


def test_final_reply_includes_speech_attachment(monkeypatch):
    agent = FakeAgent()
    sent = []

    async def fake_synthesize(context, text):
        return "/a0/usr/uploads/reply.wav", None

    async def fake_send_reply(context, response_text, attachments, keyboard):
        sent.append(
            {
                "text": response_text,
                "attachments": attachments,
                "keyboard": keyboard,
            }
        )

    monkeypatch.setattr(_55_telegram_reply, "_extract_last_response", lambda context: "Final reply.")
    monkeypatch.setattr(speech, "synthesize_attachment", fake_synthesize)

    extension = _55_telegram_reply.TelegramAutoReply(agent=agent)
    extension._send_reply = fake_send_reply

    asyncio.run(extension.execute())

    assert sent == [
        {
            "text": "Final reply.",
            "attachments": ["/a0/usr/uploads/reply.wav"],
            "keyboard": None,
        }
    ]
    assert CTX_TG_REPLY_TO not in agent.context.data
