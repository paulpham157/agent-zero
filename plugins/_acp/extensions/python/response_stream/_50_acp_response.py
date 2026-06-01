from helpers.extension import Extension
from plugins._acp.helpers import bridge


class ACPResponseStream(Extension):
    async def execute(self, parsed=None, **kwargs):
        if not self.agent or not isinstance(parsed, dict):
            return
        tool_name = parsed.get("tool_name") or parsed.get("tool")
        if tool_name != "response":
            return
        tool_args = parsed.get("tool_args") if isinstance(parsed.get("tool_args"), dict) else parsed.get("args")
        if not isinstance(tool_args, dict):
            return
        text = tool_args.get("text", tool_args.get("message", ""))
        bridge.send_agent_delta(self.agent.context.id, str(text or ""))
