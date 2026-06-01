from __future__ import annotations

from helpers.api import ApiHandler, Request
from plugins._oauth.helpers.route_bootstrap import is_installed
from plugins._oauth.helpers.providers import CODEX_PROVIDER_ID, provider_registry
from plugins._oauth.helpers.usage_plans import usage_plan_catalog


class Status(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict:
        del input, request
        providers = [_provider_status(provider) for provider in provider_registry().values()]
        provider_map = {provider["provider_id"]: provider for provider in providers}
        return {
            "ok": True,
            "routes_installed": is_installed(),
            "providers": providers,
            "provider_map": provider_map,
            "usage_plan_catalog": usage_plan_catalog(),
            "codex": provider_map.get(CODEX_PROVIDER_ID, {}),
        }


def _provider_status(provider) -> dict:
    try:
        return provider.status()
    except Exception as exc:
        return {
            "provider_id": str(getattr(provider, "provider_id", "")),
            "connected": False,
            "error": str(exc),
        }
