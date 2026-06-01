from helpers.extension import Extension
from plugins._acp.helpers import bridge


class ACPToolStart(Extension):
    async def execute(self, tool_name="", tool_args=None, **kwargs):
        if not self.agent:
            return
        bridge.start_tool(self.agent.context.id, str(tool_name or ""), tool_args or {})
