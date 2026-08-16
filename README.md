# mcp-apps-lab

One **FastMCP app server** (Python) — a single MCP server that hosts four
interactive Prefab apps (quiz, weather, news, English Duo) plus MCP
resources and prompts.
Each app tool returns a Prefab UI (buttons, cards, tabs, progress) instead of
raw JSON; any MCP host renders them, and the LLM sees a text summary.

## Apps

| App | UI tool | Backend tool | What it demonstrates |
| --- | --- | --- | --- |
| Quiz | `take_quiz` | `submit_answer` | Multi-turn state: the LLM generates questions, the user answers via buttons, each click grades through a backend tool, the final score is sent back to the conversation |
| Weather | `weather_app` | `get_weather` | Live forecast from the Open-Meteo API: free-text location input geocodes ANY city name (no fixed table — “bekasi” works), shows current conditions with the city's local time (🕐 20:31 WIB), region/country, and a 5-day forecast; unknown names fall back to Jakarta, sample data offline (LIVE/SAMPEL badge); lookups go through the host's tools/call proxy (hashed tool names — the proxy never sees the mapping) |
| News Curator | `news_curator` | `get_feed` | Live RSS feeds (Bloomberg Markets, CNBC, The Guardian Business, BBC Business) fetched through the backend tool on tab click / refresh — parsed with the stdlib, sample-data fallback when offline (LIVE/SAMPLE badge); compiles a markdown briefing and sends it back to the conversation |
| English Duo | `duo_english` | `grade_answer`, `get_profile`, `add_word` | A Duolingo-style English learning app: CEFR-graded vocabulary (A1-B2), FSRS-6 spaced-repetition cards per word, and game mechanics — XP + combo bonus, 5 hearts (mistakes cost one, daily refill), daily streak 🔥, and a Bronze→Diamond level ladder. Due reviews + new words drive each lesson; answers are graded by the backend tool which reschedules the word's card and updates the profile in SQLite |

Also exposed server-side: live resources (`news://{source}/feed`,
`news://{source}/briefing`, `weather://{city}/current`, `duo://profile`,
`duo://due`) and prompts (`morning-briefing`, `daily-english`).

## Layout

```
src/mcp_apps_lab/
├── server.py          # the ONE FastMCP server — wires apps, tools, resources, prompts
├── apps/              # the FastMCPApp UIs (LLM-facing entry points)
│   ├── quiz.py        #   take_quiz UI
│   ├── weather.py     #   weather_app UI
│   ├── news.py        #   news_curator UI
│   └── duo.py         #   duo_english UI (English Duo)
├── tools/             # backend tool functions the UIs call via the tool proxy
│   ├── quiz.py        #   submit_answer
│   ├── weather.py     #   get_weather
│   ├── news.py        #   get_feed (live RSS fetch + offline fallback)
│   └── duo.py         #   grade_answer, get_profile, add_word
├── duo/               # the English Duo engine
│   ├── store.py       #   SQLite persistence (~/.mcp-apps-lab/duo.db)
│   ├── scheduler.py   #   FSRS-6 spaced-repetition wrapper
│   ├── game.py        #   XP/combo, hearts, streak, level ladder
│   └── engine.py      #   lesson building + grading orchestration
├── resources/         # MCP resources (news://, weather://, duo://profile, duo://due)
├── prompts/           # MCP prompt templates (morning-briefing, daily-english)
└── data/              # feed definitions, offline fallback data, word bank
```

## Setup

```bash
uv sync          # installs the package (editable) + fastmcp[apps] + dev tools
```

## Configuring which tools are enabled

`config.json` at the repo root decides which UI apps (tools) the server
advertises to the LLM. Disabled apps are not registered at all — their
backend tools stay hidden too.

```json
{
  "tools": {
    "take_quiz": false,
    "weather_app": false,
    "news_curator": true,
    "duo_english": true
  }
}
```

- Keys: `take_quiz`, `weather_app`, `news_curator`, `duo_english`.
- Missing keys default to **enabled**; unknown keys are ignored.
- Lookup order: `MCP_APPS_LAB_CONFIG` env var → `./config.json` →
  `~/.mcp-apps-lab/config.json`.
- The checked-in config currently runs with **quiz and weather disabled**
  (English Duo + News Curator active); flip the booleans to re-enable.

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
- Dev UI: `http://localhost:8080` — pick `take_quiz`, `weather_app`,
  `news_curator`, or `duo_english`, fill in arguments, and play the
  rendered app in a new tab
- The left inspector panel shows the JSON-RPC traffic (including the hashed
  backend-tool calls the UIs make)

## English Duo details

State lives in a SQLite database (`~/.mcp-apps-lab/duo.db`, override with
`DUO_DB_PATH`):

- **Word bank** — 120 CEFR-graded words (A1-B2) with simple definitions and
  example sentences; the assistant can add more via the `add_word` tool.
- **Duolingo brand UI** — Nunito typeface, Duolingo palette (green `#58CC02`,
  blue `#1CB0F6`, yellow `#FFC800`, red `#FF4B4B`), rounded cards, 3D-press
  buttons, and green/red feedback banners — distinct from the generic quiz UI.
- **Spaced repetition** — one FSRS-6 card per word (`fsrs` package, the
  algorithm modern Anki uses). Correct → *Good*, wrong → *Again*; due
  reviews are served first in every lesson, new words fill the rest.
- **Game mechanics** — 10 XP per correct answer + combo bonus (capped),
  ❤️ 5 hearts (a mistake costs one; refill daily), 🔥 streak (once per day
  per completed lesson), levels 1-10 with Bronze→Diamond leagues.
- **Exercise types** — five, cycling through each lesson so it never
  feels like one quiz:
  - `mc` — “What does X mean?” multiple choice
  - `fill` — pick the word that fits a sentence blank
  - `type` — TYPE the missing word (no choices at all)
  - `order` — build the sentence by tapping scrambled word tiles
    (with a clear/undo button)
  - `flip` — flashcard: flip the card, then self-rate Again / Hard /
    Good / Easy — mapped straight onto the FSRS ratings, so reviews get
    a real difficulty signal and XP (0/8/10/12) instead of just right/wrong
- **Resources/prompts** — `duo://profile` and `duo://due` give the
  assistant live stats; the `daily-english` prompt wires it into a daily
  practice routine.

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
the weather in Tokyo"*, *"curate today's financial news"*, or *"let's do my
daily English practice"* — it calls the UI tool, and the agent's reply
streams a structured tool event the frontend renders as the interactive app.

## How it's structured

```python
# server.py — one server, apps filtered by config.json, plus resources & prompts
mcp = build_server()   # providers = apps enabled in config.json
register_resources(mcp)   # news://{source}/feed, weather://{city}/current, duo://profile, ...
register_prompts(mcp)     # morning-briefing, daily-english

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
