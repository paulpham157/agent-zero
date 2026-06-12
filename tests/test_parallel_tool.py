from __future__ import annotations

import time
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from helpers import parallel_tools
from helpers.tool import Response


class _FakeLogItem:
    def __init__(self, type_, heading="", content="", kvps=None, id_=None, **kwargs) -> None:
        self.type = type_
        self.heading = heading
        self.content = content
        self.kvps = dict(kvps or {})
        self.kvps.update(kwargs)
        self.id = id_

    def update(self, content=None, kvps=None, **kwargs):
        if content is not None:
            self.content = content
        if kvps:
            self.kvps.update(kvps)
        self.kvps.update(kwargs)


class _FakeLog:
    def __init__(self) -> None:
        self.items = []

    def log(self, type, heading="", content="", kvps=None, id=None, **kwargs):
        item = _FakeLogItem(type, heading, content, kvps, id, **kwargs)
        self.items.append(item)
        return item


class _FakeContext:
    def __init__(self) -> None:
        self.id = "ctx"
        self.data = {}
        self.log = _FakeLog()

    def get_data(self, key: str, recursive: bool = True):
        return self.data.get(key)

    def set_data(self, key: str, value, recursive: bool = True):
        self.data[key] = value


class _FakeAgent:
    def __init__(self) -> None:
        self.context = _FakeContext()
        self.agent_name = "A0"


def test_normalize_parallel_tool_calls_accepts_normal_tool_request_shapes() -> None:
    calls = parallel_tools.normalize_parallel_tool_calls(
        [
            {
                "tool_name": "text_editor:read",
                "tool_args": {"path": "README.md"},
            },
            {
                "tool": "scheduler",
                "args": {"method": "list_tasks"},
            },
        ]
    )

    assert calls[0].tool_name == "text_editor"
    assert calls[0].tool_args == {"path": "README.md", "action": "read"}
    assert calls[1].tool_name == "scheduler"
    assert calls[1].tool_args == {"method": "list_tasks", "action": "list_tasks"}


def test_normalize_parallel_tool_calls_rejects_nested_parallel() -> None:
    with pytest.raises(ValueError, match="cannot be nested"):
        parallel_tools.normalize_parallel_tool_calls(
            [{"tool_name": "parallel", "tool_args": {"tool_calls": []}}]
        )


@pytest.mark.asyncio
async def test_parallel_jobs_extras_lists_running_and_ready_jobs() -> None:
    agent = _FakeAgent()
    running = parallel_tools.ParallelJob(
        id="search-1234abcd",
        parent_context_id="ctx",
        index=0,
        tool_name="search_engine",
        tool_args={"query": "Agent Zero"},
        kind="tool",
        state="running",
        started_at=time.time() - 2,
    )
    ready = parallel_tools.ParallelJob(
        id="callsubordin-5678efgh",
        parent_context_id="ctx",
        index=1,
        tool_name="call_subordinate",
        tool_args={"message": "Summarize"},
        kind="subordinate",
        state="success",
        started_at=time.time() - 4,
        completed_at=time.time() - 1,
        result="done",
    )
    agent.context.set_data(
        parallel_tools.PARALLEL_JOBS_KEY,
        {running.id: running, ready.id: ready},
    )

    extras = await parallel_tools.build_parallel_jobs_extras(agent)  # type: ignore[arg-type]

    assert "search-1234abcd" in extras
    assert "callsubordin-5678efgh" in extras
    assert "ready to collect" in extras


@pytest.mark.asyncio
async def test_parallel_subordinate_jobs_are_visible_child_logs_not_scheduler_tasks(monkeypatch) -> None:
    class FakeDeferredTask:
        def __init__(self, thread_name=None) -> None:
            self.thread_name = thread_name
            self.started = None

        def start_task(self, func, *args):
            self.started = (func, args)
            return self

        def is_ready(self):
            return False

        def is_alive(self):
            return True

        def kill(self):
            pass

    monkeypatch.setattr(parallel_tools, "DeferredTask", FakeDeferredTask)
    agent = _FakeAgent()

    jobs = await parallel_tools.start_parallel_jobs(
        agent,  # type: ignore[arg-type]
        [
            parallel_tools.NormalizedToolCall(
                index=0,
                tool_name="call_subordinate",
                tool_args={
                    "profile": "developer",
                    "message": "Return ALPHA=1",
                    "reset": True,
                },
            )
        ],
    )

    assert jobs[0].kind == "subordinate"
    snapshot = parallel_tools._job_snapshot(jobs[0], include_result=False)
    assert "scheduler_task_uuid" not in snapshot
    assert agent.context.log.items[0].type == "subagent"
    assert agent.context.log.items[0].kvps == {
        "profile": "developer",
        "message": "Return ALPHA=1",
        "reset": True,
    }
    assert "id" not in agent.context.log.items[0].kvps
    assert "tool_name" not in agent.context.log.items[0].kvps
    assert "parallel_child" not in agent.context.log.items[0].kvps


@pytest.mark.asyncio
async def test_parallel_direct_tool_jobs_log_normal_tool_metadata(monkeypatch) -> None:
    class FakeDeferredTask:
        def __init__(self, thread_name=None) -> None:
            self.thread_name = thread_name
            self.started = None

        def start_task(self, func, *args):
            self.started = (func, args)
            return self

        def is_ready(self):
            return False

        def is_alive(self):
            return True

        def kill(self):
            pass

    monkeypatch.setattr(parallel_tools, "DeferredTask", FakeDeferredTask)
    agent = _FakeAgent()

    jobs = await parallel_tools.start_parallel_jobs(
        agent,  # type: ignore[arg-type]
        [
            parallel_tools.NormalizedToolCall(
                index=0,
                tool_name="wait",
                tool_args={"seconds": 1},
            )
        ],
    )

    assert jobs[0].kind == "tool"
    assert agent.context.log.items[0].type == "tool"
    assert agent.context.log.items[0].kvps == {"seconds": 1, "_tool_name": "wait"}

    parallel_tools._finish_job(jobs[0], "success", result="done")

    assert agent.context.log.items[0].content == "done"
    assert agent.context.log.items[0].kvps == {"seconds": 1, "_tool_name": "wait"}


@pytest.mark.asyncio
async def test_parallel_tool_keeps_wrapper_out_of_visible_log() -> None:
    from tools.parallel import ParallelTool

    class HistoryAgent(_FakeAgent):
        def __init__(self) -> None:
            super().__init__()
            self.tool_results = []

        def hist_add_tool_result(self, tool_name, tool_result, **kwargs):
            self.tool_results.append((tool_name, tool_result, kwargs))

    agent = HistoryAgent()
    tool = ParallelTool(agent, "parallel", None, {}, "", None)  # type: ignore[arg-type]

    await tool.before_execution()
    await tool.after_execution(Response(message="done", break_loop=False, additional={"extra": "value"}))

    assert agent.context.log.items == []
    assert agent.tool_results == [("parallel", "done", {"extra": "value"})]


@pytest.mark.asyncio
async def test_parallel_child_contexts_are_chats_not_tasks(monkeypatch) -> None:
    from agent import AgentContext
    from initialize import initialize_agent
    from helpers import state_snapshot

    class NoTaskScheduler:
        def get_task_by_uuid(self, _task_id):
            return None

    monkeypatch.setattr(
        state_snapshot,
        "TaskScheduler",
        SimpleNamespace(get=lambda: NoTaskScheduler()),
    )

    parent_id = "ctx-par-parent"
    child_id = "ctx-par-child"
    parent = AgentContext(config=initialize_agent(), id=parent_id, name="Parent", set_current=False)
    child = AgentContext(config=initialize_agent(), id=child_id, name="Child", set_current=False)
    try:
        child.set_output_data(parallel_tools.CHILD_PARENT_CONTEXT_ID_KEY, parent.id)
        child.set_output_data(parallel_tools.CHILD_PARENT_CONTEXT_KIND_KEY, "parallel")
        child.set_output_data(parallel_tools.CHILD_PARENT_CONTEXT_LABEL_KEY, "Child task")
        child.set_output_data(parallel_tools.CHILD_PARALLEL_JOB_ID_KEY, "job-123")

        payload = await state_snapshot.build_snapshot(
            context=parent.id,
            log_from=0,
            notifications_from=0,
            timezone="UTC",
        )

        contexts_by_id = {ctx["id"]: ctx for ctx in payload["contexts"]}
        task_ids = {task["id"] for task in payload["tasks"]}
        assert parent_id in contexts_by_id
        assert child_id in contexts_by_id
        assert contexts_by_id[child_id]["parent_context_id"] == parent_id
        assert child_id not in task_ids
    finally:
        AgentContext.remove(parent_id)
        AgentContext.remove(child_id)


def test_chats_sidebar_projects_parallel_children_as_indented_accordion() -> None:
    store = (PROJECT_ROOT / "webui/components/sidebar/chats/chats-store.js").read_text(
        encoding="utf-8"
    )
    html = (PROJECT_ROOT / "webui/components/sidebar/chats/chats-list.html").read_text(
        encoding="utf-8"
    )

    assert "parent_context_id" in store
    assert "const nextExpandedParents = { ...this.expandedParents };" in store
    assert "nextExpandedParents[selectedId] === undefined" in store
    assert "nextExpandedParents[selectedId] = true;" in store
    assert "topLevelContexts()" in html
    assert "childContexts(context.id)" in html
    assert "chat-child-container" in html
    assert "keyboard_arrow_up" in html
    assert "keyboard_arrow_down" in html
    assert ".chats-config-list .chat-tree-item" in html
    assert ".chats-config-list .chat-child-list > li" in html
    assert 'x-show="$store.chats.hasChildren(context.id)"' in html
    assert "'chat-has-children': $store.chats.hasChildren(context.id)" in html
    assert ".chat-container.chat-has-children .chat-list-button" in html
    assert "left: 2px" in html
    assert "padding-left: 24px" in html
    assert "color: var(--color-text-muted)" in html
    assert "padding: 8px;" in html
