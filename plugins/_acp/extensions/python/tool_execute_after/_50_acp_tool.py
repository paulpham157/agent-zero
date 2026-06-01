from helpers.extension import Extension
from plugins._acp.helpers import bridge


class ACPToolFinish(Extension):
    async def execute(self, response=None, tool_name="", **kwargs):
        if not self.agent:
            return
        bridge.finish_tool(self.agent.context.id, str(tool_name or ""), response)
