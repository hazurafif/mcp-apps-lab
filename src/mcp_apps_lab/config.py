"""Tool enable/disable configuration for mcp-apps-lab.

The server reads a JSON file to decide which UI apps (tools) are advertised
to the LLM. Lookup order:

1. ``MCP_APPS_LAB_CONFIG`` env var (explicit path)
2. ``./config.json`` in the working directory (repo root)
3. ``~/.mcp-apps-lab/config.json``

Example ``config.json``:

    {"tools": {"take_quiz": false, "weather_app": false,
               "news_curator": true, "duo_english": true}}

Missing keys default to enabled; unknown keys are ignored, so the schema
can grow without breaking old configs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# The LLM-facing UI tools this server can host.
UI_TOOLS = ("take_quiz", "weather_app", "news_curator", "duo_english")


def config_path() -> Path:
    """Where the config file lives, per the lookup order above."""
    env = os.environ.get("MCP_APPS_LAB_CONFIG")
    if env:
        return Path(env)
    local = Path("config.json")
    if local.is_file():
        return local
    return Path.home() / ".mcp-apps-lab" / "config.json"


def load_config(path: str | Path | None = None) -> dict:
    """Load the config, merged over defaults (all tools enabled)."""
    p = Path(path) if path else config_path()
    enabled = {name: True for name in UI_TOOLS}
    if p.is_file():
        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"invalid config file {p}: {exc}") from exc
        for name, flag in (data.get("tools") or {}).items():
            if name in enabled:
                enabled[name] = bool(flag)
    return {"tools": enabled, "path": str(p), "exists": p.is_file()}


def enabled_tools(path: str | Path | None = None) -> set[str]:
    """Names of the UI tools that should be advertised to the LLM."""
    return {name for name, on in load_config(path)["tools"].items() if on}
