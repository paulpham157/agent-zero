from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from plugins._document_query.helpers.fetch import FetchedDocument, fetch_public_resource
from plugins._document_query.helpers.document_query import DocumentQueryHelper
from plugins._document_query.helpers.parsers.base import BaseParser
from plugins._document_query.helpers.parsers import get_parsers_for_mimetype
from plugins._document_query.helpers.parsers.text import TextParser


ROOT = Path(__file__).resolve().parents[1]


def run_async(coro):
    with asyncio.Runner() as runner:
        return runner.run(coro)


class ParserNameShouldNotLeak(BaseParser):
    mimetypes = ["text/plain"]

    def _parse_sync(self, document: FetchedDocument, config: dict) -> str:
        return "parsed"


def test_fetch_file_detects_mimetype_and_reads_once(tmp_path):
    document = tmp_path / "notes.txt"
    document.write_text("hello\nworld\n", encoding="utf-8")

    fetched = run_async(fetch_public_resource(str(document), {}))

    assert fetched.scheme == "file"
    assert fetched.mimetype == "text/plain"
    assert fetched.local_path == str(document)
    assert fetched.text() == "hello\nworld\n"


def test_parser_registry_prefers_liteparse_for_pdf():
    parsers = get_parsers_for_mimetype("application/pdf", {"liteparse_enabled": True})

    assert [parser.__class__.__name__ for parser in parsers[:2]] == [
        "LiteParseParser",
        "PdfParser",
    ]


def test_parser_registry_can_disable_liteparse():
    parsers = get_parsers_for_mimetype("application/pdf", {"liteparse_enabled": False})

    assert parsers
    assert parsers[0].__class__.__name__ == "PdfParser"


def test_text_parser_uses_prefetched_content():
    fetched = FetchedDocument(
        uri="/tmp/example.json",
        source_uri="/tmp/example.json",
        scheme="file",
        mimetype="application/json",
        content=b'{"ok": true}',
        local_path=None,
    )

    text = run_async(TextParser().parse(fetched, {}, timeout=1))

    assert text == '{"ok": true}'


def test_compatibility_imports_point_to_plugin_classes():
    pytest.importorskip("langchain_core")

    from helpers.document_query import DocumentQueryHelper as CompatHelper
    from plugins._document_query.helpers.document_query import DocumentQueryHelper
    from plugins._document_query.tools.document_query import DocumentQueryTool
    from tools.document_query import DocumentQueryTool as CompatTool

    assert CompatHelper is DocumentQueryHelper
    assert CompatTool is DocumentQueryTool


def test_liteparse_is_installed_by_docker_and_plugin_hook_requirements():
    root_requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    plugin_requirements = (
        ROOT / "plugins" / "_document_query" / "requirements.txt"
    ).read_text(encoding="utf-8")

    assert "liteparse>=2.0.0,<3.0.0" in root_requirements
    assert plugin_requirements.strip().splitlines() == ["liteparse>=2.0.0,<3.0.0"]


def test_query_optimize_prompt_filename_is_spelled_correctly():
    prompt_dir = ROOT / "plugins" / "_document_query" / "prompts"
    helper_source = (
        ROOT / "plugins" / "_document_query" / "helpers" / "document_query.py"
    ).read_text(encoding="utf-8")

    assert (prompt_dir / "fw.document_query.optimize_query.md").exists()
    assert "fw.document_query.optimize_query.md" in helper_source


def test_parser_progress_is_user_facing_and_generic():
    fetched = FetchedDocument(
        uri="/tmp/example.txt",
        source_uri="/tmp/example.txt",
        scheme="file",
        mimetype="text/plain",
        content=b"content",
        local_path=None,
    )
    progress = []
    helper = object.__new__(DocumentQueryHelper)
    helper.config = {}
    helper.progress_callback = progress.append

    content = run_async(
        helper._parse_document(
            document=fetched,
            parsers=[ParserNameShouldNotLeak()],
            timeout=1,
            thread_offload=False,
        )
    )

    assert content == "parsed"
    assert progress == ["Parsing document content"]


def test_document_query_prompt_uses_progressive_skill_disclosure():
    from helpers.skills import find_skill

    prompt = (
        ROOT
        / "plugins"
        / "_document_query"
        / "prompts"
        / "agent.system.tool.document_query.md"
    ).read_text(encoding="utf-8")
    main_prompt = (ROOT / "prompts" / "agent.system.main.tips.md").read_text(
        encoding="utf-8"
    )
    skill = find_skill("document-query", include_content=True)

    assert skill is not None
    assert "document_query for Q&A" in main_prompt
    assert "specific code files" in main_prompt
    assert "skills_tool:load" in prompt
    assert "document-query" in prompt
    assert "document_query" in prompt
    assert "answering questions over local or remote documents" in skill.description
    assert "### Answer Questions Over A Document" in skill.content
    assert "### OCR Or Q&A Over A Document Image" in skill.content
