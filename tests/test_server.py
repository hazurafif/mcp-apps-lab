"""Smoke tests for the single mcp-apps-lab server."""

from __future__ import annotations

import json

import pytest
from fastmcp.server.providers.addressing import hash_tool

from mcp_apps_lab import mcp
from mcp_apps_lab.apps import news_app, quiz_app, weather_app
from mcp_apps_lab.apps.news import news_curator
from mcp_apps_lab.apps.quiz import take_quiz
from mcp_apps_lab.apps.weather import weather_app as weather_ui


def _text(result) -> str:
    item = result.content[0] if hasattr(result, "content") else result.contents[0]
    return item.text if hasattr(item, "text") else item.content


@pytest.mark.asyncio
async def test_llm_facing_tools() -> None:
    """The three UI entry points are the only tools advertised to the LLM."""
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert {"take_quiz", "weather_app", "news_curator"} <= names
    # Backend tools must NOT leak to the LLM.
    assert not names & {"submit_answer", "get_weather", "compile_briefing"}


@pytest.mark.asyncio
async def test_backend_tools_via_hash() -> None:
    """UIs call their backend tools under hashed names; the server routes them."""
    cases = [
        (quiz_app, "submit_answer", {"question_index": 0, "selected": 2, "correct": 2, "total_questions": 5, "current_score": 0}),
        (weather_app, "get_weather", {"city": "tokyo"}),
        (news_app, "compile_briefing", {"source": "bbc", "topic": "Energy"}),
    ]
    for app, tool_name, arguments in cases:
        digest = hash_tool(app.name, tool_name)
        result = await mcp.call_tool(f"{digest}_{tool_name}", arguments)
        assert not result.is_error
        data = json.loads(_text(result))
        assert data, tool_name


@pytest.mark.asyncio
async def test_weather_unknown_city_falls_back() -> None:
    """Unknown location names fall back to Jakarta with is_fallback flagged."""
    digest = hash_tool(weather_app.name, "get_weather")
    result = await mcp.call_tool(f"{digest}_get_weather", {"city": "london"})
    data = json.loads(_text(result))
    assert data["city"] == "jakarta"
    assert data["is_fallback"] is True


@pytest.mark.asyncio
async def test_resources() -> None:
    """news:// and weather:// resources resolve through the server."""
    feed = await mcp.read_resource("news://bloomberg/feed")
    stories = json.loads(_text(feed))
    assert stories[0]["headline"].startswith("S&P 500")

    briefing = await mcp.read_resource("news://guardian/briefing")
    assert "## " in _text(briefing)

    weather = await mcp.read_resource("weather://paris/current")
    assert json.loads(_text(weather))["city"] == "paris"


@pytest.mark.asyncio
async def test_prompts() -> None:
    prompts = await mcp.list_prompts()
    assert any(p.name == "morning-briefing" for p in prompts)
    prompt = await mcp.get_prompt("morning-briefing")
    rendered = await prompt._render(arguments={"topic": "AI & Tech"})
    assert rendered.messages and rendered.messages[0].content.text


@pytest.mark.asyncio
async def test_ui_serialization() -> None:
    """Each UI entry point renders to JSON without errors."""
    for ui, kwargs in [
        (take_quiz, {"topic": "Python"}),
        (weather_ui, {"city": "berlin"}),
        (news_curator, {"topic": "Global Markets"}),
    ]:
        app = ui(**kwargs)
        data = app.to_json()
        assert isinstance(data, dict) and data["view"]


def test_weather_ui_has_location_input() -> None:
    """The dashboard renders a free-text location input."""
    data = weather_ui(city="jakarta").to_json()

    def walk(node) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "Input":
                return True
            return any(walk(v) for v in node.values())
        if isinstance(node, list):
            return any(walk(v) for v in node)
        return False

    assert walk(data), "weather UI should contain an Input component"
