from __future__ import annotations

from copy import deepcopy
from typing import Any

CODEX_PROVIDER_ID = "codex_oauth"
GITHUB_COPILOT_PROVIDER_ID = "github_copilot_oauth"
CLAUDE_CODE_PROVIDER_ID = "claude_code_oauth"
GEMINI_API_PROVIDER_ID = "gemini_api_oauth"
GEMINI_CODE_ASSIST_PROVIDER_ID = "gemini_code_assist_oauth"
XAI_GROK_PROVIDER_ID = "xai_grok_oauth"


USAGE_PLAN_CATALOG: dict[str, dict[str, Any]] = {
    CODEX_PROVIDER_ID: {
        "provider_id": CODEX_PROVIDER_ID,
        "display_name": "OpenAI Codex",
        "implemented": True,
        "plans": [
            {"id": "free", "label": "Free", "billing": "$0/month", "usage": "Quick coding tasks with plan-specific limits."},
            {"id": "go", "label": "Go", "billing": "$8/month", "usage": "Lightweight coding tasks."},
            {"id": "plus", "label": "Plus", "billing": "$20/month", "usage": "Focused coding sessions, latest Codex models, and credit extension."},
            {"id": "pro", "label": "Pro", "billing": "From $100/month", "usage": "Higher Codex limits than Plus, including Pro tiers."},
            {"id": "business", "label": "Business", "billing": "Pay as you go", "usage": "Standard or usage-based Codex seats, credits, admin controls, and no training by default."},
            {"id": "enterprise_edu", "label": "Enterprise / Edu", "billing": "Contact sales", "usage": "Enterprise controls, priority processing, audit and usage monitoring."},
            {"id": "api_key", "label": "API Key", "billing": "Token-based API pricing", "usage": "CLI, SDK, or IDE automation without ChatGPT cloud features."},
        ],
        "notes": [
            "Codex is included across ChatGPT Free, Go, Plus, Pro, Business, Edu, and Enterprise plans.",
            "The Pro 2x/boost promotion ended on 2026-05-31.",
            "API-key usage is separate from ChatGPT subscription usage and may receive delayed access to some new Codex models.",
        ],
        "sources": [
            {"label": "OpenAI Codex pricing", "url": "https://developers.openai.com/codex/pricing"},
            {"label": "Using Codex with your ChatGPT plan", "url": "https://help.openai.com/en/articles/11369540"},
        ],
    },
    GITHUB_COPILOT_PROVIDER_ID: {
        "provider_id": GITHUB_COPILOT_PROVIDER_ID,
        "display_name": "GitHub Copilot",
        "implemented": True,
        "plans": [
            {"id": "free", "label": "Copilot Free", "billing": "Free", "usage": "Entry Copilot access with monthly completion limits."},
            {"id": "student", "label": "Copilot Student", "billing": "Free for eligible users", "usage": "Student-entitled Copilot access."},
            {"id": "pro", "label": "Copilot Pro", "billing": "$10/month", "usage": "Individual Copilot access with paid entitlements."},
            {"id": "pro_plus", "label": "Copilot Pro+", "billing": "$39/month", "usage": "Larger individual AI-credit pool."},
            {"id": "max", "label": "Copilot Max", "billing": "$100/month", "usage": "Highest individual monthly AI-credit allowance and priority model access."},
            {"id": "business", "label": "Copilot Business", "billing": "$19/seat/month", "usage": "Team and organization plan with centralized management."},
            {"id": "enterprise", "label": "Copilot Enterprise", "billing": "$39/seat/month", "usage": "Enterprise Cloud plan with larger AI-credit pool and enterprise controls."},
        ],
        "notes": [
            "AI-credit availability and model access can differ by seat and organization policy.",
            "GitHub docs list new signup pauses for several Copilot plans beginning in April 2026.",
            "Beginning 2026-06-01, GitHub docs describe Copilot Max as upgrade-only for users with existing Copilot plans.",
        ],
        "sources": [
            {"label": "GitHub Copilot plans", "url": "https://docs.github.com/en/copilot/get-started/plans"},
        ],
    },
    CLAUDE_CODE_PROVIDER_ID: {
        "provider_id": CLAUDE_CODE_PROVIDER_ID,
        "display_name": "Claude Code",
        "implemented": False,
        "plans": [
            {"id": "pro", "label": "Pro", "billing": "Subscription", "usage": "Shared Claude and Claude Code usage limits."},
            {"id": "max_5x", "label": "Max 5x", "billing": "Subscription", "usage": "Higher included usage than Pro."},
            {"id": "max_20x", "label": "Max 20x", "billing": "Subscription", "usage": "Highest individual Claude Code subscription allocation."},
            {"id": "team", "label": "Team", "billing": "Seat-based subscription", "usage": "Claude Code included with every Team seat; premium seats add more usage."},
            {"id": "enterprise_premium", "label": "Enterprise Premium", "billing": "Seat-based subscription", "usage": "Enterprise seat type with Claude Code access."},
            {"id": "enterprise_usage_based", "label": "Enterprise usage-based", "billing": "API-rate consumption", "usage": "Usage billed by consumption instead of per-seat caps."},
        ],
        "notes": [
            "Claude subscription usage and Anthropic API-key billing are distinct systems.",
            "An ANTHROPIC_API_KEY can make Claude Code use API billing instead of subscription allocation.",
        ],
        "sources": [
            {"label": "Claude Code with Pro or Max", "url": "https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan"},
            {"label": "Claude Code with Team or Enterprise", "url": "https://support.claude.com/en/articles/11845131-use-claude-code-with-your-team-or-enterprise-plan"},
        ],
    },
    GEMINI_API_PROVIDER_ID: {
        "provider_id": GEMINI_API_PROVIDER_ID,
        "display_name": "Google Gemini API",
        "implemented": True,
        "plans": [
            {"id": "oauth_cloud_project", "label": "OAuth Cloud project", "billing": "Google Cloud project", "usage": "Official OAuth access using a user-provided Google Cloud OAuth client."},
            {"id": "api_key", "label": "API key", "billing": "Gemini API pricing", "usage": "Standard Gemini API key access through Google AI Studio or Google Cloud."},
            {"id": "vertex_ai", "label": "Vertex AI", "billing": "Google Cloud", "usage": "Enterprise Gemini API access through Vertex AI projects and IAM."},
        ],
        "notes": [
            "Gemini API OAuth requires the Google Generative Language API to be enabled on the user's Cloud project.",
            "OAuth Gemini API usage is separate from Antigravity, Gemini Code Assist, Gemini CLI, Google AI Pro, and Google AI Ultra subscription quotas.",
            "A quota project may be required so Google can attribute billing and quota to the correct Cloud project.",
        ],
        "sources": [
            {"label": "Gemini API OAuth", "url": "https://ai.google.dev/gemini-api/docs/oauth"},
            {"label": "Gemini OpenAI compatibility", "url": "https://ai.google.dev/gemini-api/docs/openai"},
            {"label": "Gemini API billing", "url": "https://ai.google.dev/gemini-api/docs/billing"},
        ],
    },
    GEMINI_CODE_ASSIST_PROVIDER_ID: {
        "provider_id": GEMINI_CODE_ASSIST_PROVIDER_ID,
        "display_name": "Google Gemini / Antigravity",
        "implemented": False,
        "implementation_status": "metadata_only",
        "plans": [
            {"id": "individual", "label": "Antigravity Individual", "billing": "$0/month", "usage": "Baseline Antigravity quota, unlimited tab completions, and CLI access."},
            {"id": "google_ai_pro", "label": "Google AI Pro", "billing": "Subscription", "usage": "More generous Antigravity rate limits and AI credit overages."},
            {"id": "google_ai_ultra", "label": "Google AI Ultra", "billing": "Subscription", "usage": "Highest Antigravity quota, highest weekly limits, and third-party model access."},
            {"id": "organization", "label": "Organization plan", "billing": "Google Cloud", "usage": "Gemini Enterprise Agent Platform access, Cloud project integration, and consumption pricing."},
            {"id": "code_assist_standard", "label": "Gemini Code Assist Standard", "billing": "Google Cloud subscription", "usage": "Organization plan for code assistance, agent mode, and Gemini CLI quotas."},
            {"id": "code_assist_enterprise", "label": "Gemini Code Assist Enterprise", "billing": "Google Cloud subscription", "usage": "Enterprise plan with customization and broader Google Cloud integrations."},
            {"id": "gemini_api_oauth", "label": "Gemini API OAuth", "billing": "Google Cloud project", "usage": "Official third-party OAuth path with a user-provided Google Cloud OAuth client."},
        ],
        "provider_modes": [
            {
                "id": "gemini_api_oauth",
                "label": "Gemini API OAuth",
                "allowed": True,
                "status": "implemented",
                "note": "Implemented as the separate Google Gemini API OAuth provider. It requires a user-configured Google Cloud OAuth client and does not spend Antigravity or Google AI subscription quota.",
            },
            {
                "id": "antigravity_subscription_oauth",
                "label": "Antigravity subscription OAuth",
                "allowed": False,
                "status": "not_implemented",
                "note": "Google Antigravity terms prohibit using third-party tools to access the Antigravity service through its OAuth flow.",
            },
        ],
        "notes": [
            "Official Gemini API OAuth requires a Google Cloud OAuth client and is separate from Google AI Pro, Google AI Ultra, Antigravity, Gemini Code Assist, and Gemini CLI quotas.",
            "Antigravity and Gemini Code Assist subscription OAuth are metadata-only here because Google does not authorize third-party tools to access the service through those product OAuth flows.",
            "Gemini CLI quotas are provided by Gemini Code Assist editions and shared with Code Assist agent mode; the CLI can also use a Gemini API key for pay-as-you-go usage.",
        ],
        "sources": [
            {"label": "Google Antigravity terms", "url": "https://antigravity.google/terms"},
            {"label": "Google Antigravity plans", "url": "https://antigravity.google/docs/plans?id=GoogleAntigravity"},
            {"label": "Google Antigravity pricing", "url": "https://antigravity.google/pricing?app=antigravity"},
            {"label": "Gemini Code Assist overview", "url": "https://developers.google.com/gemini-code-assist/docs/overview"},
            {"label": "Gemini Code Assist quotas", "url": "https://developers.google.com/gemini-code-assist/resources/quotas"},
            {"label": "Gemini CLI", "url": "https://developers.google.com/gemini-code-assist/docs/gemini-cli"},
            {"label": "Gemini API OAuth", "url": "https://ai.google.dev/gemini-api/docs/oauth"},
        ],
    },
    XAI_GROK_PROVIDER_ID: {
        "provider_id": XAI_GROK_PROVIDER_ID,
        "display_name": "xAI Grok",
        "implemented": True,
        "plans": [
            {"id": "free", "label": "Free", "billing": "$0/month", "usage": "Grok app access with free limits."},
            {"id": "supergrok_lite", "label": "SuperGrok Lite", "billing": "Subscription", "usage": "Intermediate Grok app limits."},
            {"id": "supergrok", "label": "SuperGrok", "billing": "$30/month", "usage": "Higher app limits, Grok 4 model, connectors, image and video generation."},
            {"id": "supergrok_heavy", "label": "SuperGrok Heavy", "billing": "Subscription", "usage": "Highest individual Grok app tier."},
            {"id": "business", "label": "Business", "billing": "Team plan", "usage": "Team seats, billing, role-based access, and admin controls."},
            {"id": "enterprise", "label": "Enterprise", "billing": "Contact sales", "usage": "Custom rate limits, SSO, SCIM, data residency, and volume pricing."},
            {"id": "api_credits", "label": "API credits", "billing": "Prepaid/usage credits", "usage": "xAI API access after account setup and credit loading."},
        ],
        "notes": [
            "xAI API billing is separate from Grok app subscriptions unless xAI explicitly entitles the account.",
            "The API quickstart uses API keys from the xAI console and requires loading credits.",
        ],
        "sources": [
            {"label": "xAI pricing", "url": "https://x.ai/pricing"},
            {"label": "xAI API quickstart", "url": "https://docs.x.ai/developers/quickstart"},
        ],
    },
}


def usage_plan_catalog() -> dict[str, dict[str, Any]]:
    return deepcopy(USAGE_PLAN_CATALOG)


def usage_plan_entry(provider_id: str) -> dict[str, Any]:
    return deepcopy(USAGE_PLAN_CATALOG.get(provider_id, {}))


def usage_plans_for(provider_id: str) -> list[dict[str, Any]]:
    entry = usage_plan_entry(provider_id)
    plans = entry.get("plans", [])
    return plans if isinstance(plans, list) else []


def usage_plan_notes_for(provider_id: str) -> list[str]:
    entry = usage_plan_entry(provider_id)
    notes = entry.get("notes", [])
    return notes if isinstance(notes, list) else []


def usage_plan_sources_for(provider_id: str) -> list[dict[str, str]]:
    entry = usage_plan_entry(provider_id)
    sources = entry.get("sources", [])
    return sources if isinstance(sources, list) else []
