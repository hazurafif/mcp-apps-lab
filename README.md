# mcp-apps-lab

One **FastMCP app server** (Python) — a single MCP server that hosts three
interactive Prefab apps (quiz, weather, news) plus MCP resources and prompts.
Each app tool returns a Prefab UI (buttons, cards, tabs, progress) instead of
raw JSON; any MCP host renders them, and the LLM sees a text summary.

## Apps

| App | UI tool | Backend tool | What it demonstrates |
| --- | --- | --- | --- |
| Quiz | `take_quiz` | `submit_answer` | Multi-turn state: the LLM generates questions, the user answers via buttons, each click grades through a backend tool, the final score is sent back to the conversation |
| Weather | `weather_app` | `get_weather` | Dashboard with a free-text location input (no geocoding — direct lookup, unknown names fall back to Jakarta with a toast) plus preset city buttons; every lookup goes through the host's tools/call proxy (hashed tool names — the proxy never sees the mapping) |
| News Curator | `news_curator` | `compile_briefing` | Curated financial feeds (Bloomberg, Reuters, The Guardian, BBC) in tabbed panels with a featured story, market-pulse metrics, and category-grouped headlines; the LLM can pass its own generated feed (`stories` param, grouped by `source` — falls back to built-in sample data); compiles a markdown briefing and sends it back to the conversation |

Also exposed server-side: resources (`news://{source}/feed`,
`news://{source}/briefing`, `weather://{city}/current`) and a prompt
(`morning-briefing`).

## Layout

```
src/mcp_apps_lab/
├── server.py          # the ONE FastMCP server — wires apps, tools, resources, prompts
├── apps/              # the FastMCPApp UIs (LLM-facing entry points)
│   ├── quiz.py        #   take_quiz UI
│   ├── weather.py     #   weather_app UI
│   └── news.py        #   news_curator UI
├── tools/             # backend tool functions the UIs call via the tool proxy
│   ├── quiz.py        #   submit_answer
│   ├── weather.py     #   get_weather
│   └── news.py        #   compile_briefing
├── resources/         # MCP resources over the shared data (news://, weather://)
├── prompts/           # MCP prompt templates (morning-briefing)
└── data/              # shared static data behind tools, apps, and resources
```

## Setup

```bash
uv sync          # installs the package (editable) + fastmcp[apps] + dev tools
```

## Running

### Plain streamable-HTTP server

```bash
uv run python -m mcp_apps_lab   # streamable HTTP at http://127.0.0.1:8090/mcp
                                # (MCP_APPS_LAB_PORT to override)
```

### Browser dev UI (`fastmcp dev apps`)

```bash
uv run fastmcp dev apps src/mcp_apps_lab/server.py --mcp-port 8090
```

- MCP server: `http://127.0.0.1:8090/mcp` (auto-reload on save)
- Dev UI: `http://localhost:8080` — pick `take_quiz`, `weather_app`, or
  `news_curator`, fill in arguments, and play the rendered app in a new tab
- The left inspector panel shows the JSON-RPC traffic (including the hashed
  backend-tool calls the UIs make)

## Wiring into the ai-backend-lab agent

One server, one entry — the agent sees all three UI tools plus the resources
and prompt:

```json
{
  "mcp-apps-lab": {
    "url": "http://127.0.0.1:8090/mcp",
    "transport": "streamable_http"
  }
}
```

Then ask the agent something like *"give me a quiz about Python"*, *"show me
the weather in Tokyo"*, or *"curate today's financial news"* — it calls the
UI tool, and the agent's reply streams a structured tool event the frontend
renders as the interactive app.

## How it's structured

```python
# server.py — one server, three apps as providers, plus resources & prompts
mcp = FastMCP("mcp-apps-lab", providers=[quiz_app, weather_app, news_app])
register_resources(mcp)   # news://{source}/feed, weather://{city}/current, ...
register_prompts(mcp)     # morning-briefing

# apps/weather.py — the UI app owns its backend tool
app = FastMCPApp("Weather")
app.add_tool(get_weather)          # from mcp_apps_lab.tools — hashed to this app

@app.ui()                          # LLM-facing entry point — returns a PrefabApp
def weather_app(city: str) -> PrefabApp: ...
```

- `@app.ui()` tools are the only ones advertised to the LLM; their result is a
  Prefab UI the host renders (the model sees a text summary).
- Backend tools (`tools/`) are plain functions registered with
  `app.add_tool(...)`: the renderer calls them over the MCP server under a
  hashed name (`<sha256(app+tool)>_<tool>`), so the UI can grade, look up, or
  compile without the LLM being in the loop — and the tool proxy never sees
  the mapping.
- `providers=[...]` lets one server host several apps; resources and prompts
  are registered server-side and shared.

## Adding to the lab

1. **App**: create `apps/<name>.py` (a `FastMCPApp` with an `@app.ui()`
   entry point), register its backend tool(s) from `tools/`, and add the app
   to `providers=[...]` in `server.py`.
2. **Backend tool**: add a plain function to `tools/<name>.py`; register it
   with `app.add_tool(...)` in the owning app.
3. **Resource / prompt**: add a `register(mcp)` function in
   `resources/<name>.py` / `prompts/<name>.py` and call it from the
   corresponding `register_*` in `server.py`.
4. Keep it lint-clean and tested: `uv run ruff check .` and
   `uv run pytest` (smoke tests live in `tests/test_server.py`).
