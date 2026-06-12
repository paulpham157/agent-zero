### parallel
run independent tool calls concurrently, or await/cancel background parallel jobs.

Use only for independent work. Each `tool_calls` item is a normal tool request object: `{ "tool_name": "...", "tool_args": { ... } }`.

Rules:
- do not use for one simple call, dependent steps, ordered steps, or shared mutable state
- never nest `parallel`
- `call_subordinate` inside `parallel` starts an isolated child chat under the parent chat, not a scheduler task
- use `wait: false` only when you will collect results later with `job_ids`
- if extras list running or ready parallel jobs, collect them before final synthesis

Args: `tool_calls`, `job_ids`, `wait` default `true`, `action` as `start|await|collect|cancel`, `timeout`.

Start and wait:
~~~json
{
  "tool_name": "parallel",
  "tool_args": {
    "tool_calls": [
      {"tool_name": "call_subordinate", "tool_args": {"message": "Research option A.", "reset": true}},
      {"tool_name": "call_subordinate", "tool_args": {"message": "Research option B.", "reset": true}}
    ],
    "wait": true
  }
}
~~~

Collect existing jobs:
~~~json
{"tool_name": "parallel", "tool_args": {"action": "await", "job_ids": ["job-id"], "timeout": 300}}
~~~
