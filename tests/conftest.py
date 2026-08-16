"""Test bootstrap: the server must see ALL apps enabled.

The repo's ``config.json`` disables ``take_quiz`` and ``weather_app``, but
the smoke tests exercise every app. Point ``MCP_APPS_LAB_CONFIG`` at an
all-enabled temp config before anything imports ``mcp_apps_lab`` (config is
read at import time in ``server.py``).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

_ALL_ENABLED = Path(tempfile.mkdtemp(prefix="mcp-apps-lab-test-")) / "config.json"
_ALL_ENABLED.write_text(
    json.dumps(
        {
            "tools": {
                "take_quiz": True,
                "weather_app": True,
                "news_curator": True,
                "duo_english": True,
            }
        }
    )
)
os.environ["MCP_APPS_LAB_CONFIG"] = str(_ALL_ENABLED)
