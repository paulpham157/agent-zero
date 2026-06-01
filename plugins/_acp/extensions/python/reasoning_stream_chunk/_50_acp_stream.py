from helpers.extension import Extension
from plugins._acp.helpers import bridge


class ACPReasoningStream(Extension):
    async def execute(self, stream_data=None, **kwargs):
        if not self.agent or not stream_data:
            return
        bridge.send_agent_thought_delta(self.agent.context.id, stream_data.get("full", ""))
