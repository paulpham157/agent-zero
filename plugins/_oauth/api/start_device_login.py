from __future__ import annotations

from helpers.api import ApiHandler, Request
from plugins._oauth.helpers.providers import CODEX_PROVIDER_ID, get_provider


class StartDeviceLogin(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict:
        return get_provider(CODEX_PROVIDER_ID).start_login(input, request).to_dict()
