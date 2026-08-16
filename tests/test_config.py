"""Tests for the tool enable/disable config (config.json)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_apps_lab import config
from mcp_apps_lab.server import build_server


def _write(tmp_path, tools: dict) -> Path:
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"tools": tools}))
    return cfg


def test_defaults_all_enabled(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("MCP_APPS_LAB_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)  # no config.json in the cwd
    data = config.load_config()
    assert data["tools"] == {name: True for name in config.UI_TOOLS}
    assert data["exists"] is False
    assert config.enabled_tools() == set(config.UI_TOOLS)


def test_disable_merge_and_path(tmp_path, monkeypatch) -> None:
    cfg = _write(tmp_path, {"take_quiz": False, "weather_app": False})
    monkeypatch.setenv("MCP_APPS_LAB_CONFIG", str(cfg))
    data = config.load_config()
    assert data["tools"]["take_quiz"] is False
    assert data["tools"]["weather_app"] is False
    assert data["tools"]["news_curator"] is True  # untouched -> default on
    assert data["tools"]["duo_english"] is True
    assert data["exists"] is True
    assert config.enabled_tools() == {"news_curator", "duo_english"}


def test_unknown_keys_ignored(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "MCP_APPS_LAB_CONFIG", str(_write(tmp_path, {"take_quiz": False, "hack": False}))
    )
    assert config.enabled_tools() == {"weather_app", "news_curator", "duo_english"}


def test_invalid_json_raises(tmp_path, monkeypatch) -> None:
    cfg = tmp_path / "config.json"
    cfg.write_text("{not json")
    monkeypatch.setenv("MCP_APPS_LAB_CONFIG", str(cfg))
    with pytest.raises(ValueError, match="invalid config"):
        config.load_config()


@pytest.mark.asyncio
async def test_server_hides_disabled_tools(tmp_path, monkeypatch) -> None:
    """Disabled apps are not registered as providers on the server."""
    monkeypatch.setenv(
        "MCP_APPS_LAB_CONFIG", str(_write(tmp_path, {"take_quiz": False, "weather_app": False}))
    )
    server = build_server()
    names = {t.name for t in await server.list_tools()}
    assert names == {"news_curator", "duo_english"}


def test_repo_config_disables_quiz_and_weather() -> None:
    """The checked-in config disables exactly quiz + weather for now."""
    cfg = Path(__file__).parents[1] / "config.json"
    tools = json.loads(cfg.read_text())["tools"]
    assert tools["take_quiz"] is False
    assert tools["weather_app"] is False
    assert tools["news_curator"] is True
    assert tools["duo_english"] is True
