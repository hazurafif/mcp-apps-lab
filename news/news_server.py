"""News Curator app — a FastMCPApp example with tabbed, curated feeds.

A financial-news dashboard with tabbed feeds for Bloomberg, Reuters, The
Guardian, and BBC News. Each feed shows a featured story, a market pulse
(row of metrics), and category-grouped headlines. The user can compile a
briefing of the active feed and send it back to the conversation via
`SendMessage` — the same multi-turn pattern as the quiz app.

How it works:
- The LLM calls `news_curator(topic)` to launch the dashboard
- Tabs switch between sources (native client-side switching)
- "Compile Briefing" calls the `compile_briefing` backend tool through the
  host's tools/call proxy (tool names are hashed server-side, like weather)
- The compiled markdown is shown in the UI; "Send Briefing to Chat" pushes
  it back to the LLM with `SendMessage`

Run with the browser dev UI (`fastmcp dev apps`):

    uv run fastmcp dev apps news/news_server.py --mcp-port 8093

Or as a plain streamable-HTTP server (no dev UI):

    uv run python news/news_server.py
    # streamable HTTP at http://127.0.0.1:8093/mcp

Wire it into the ai-backend-lab agent with:

    MCP_SERVERS_JSON='{"news":{"url":"http://127.0.0.1:8093/mcp","transport":"streamable_http"}}'
"""

from __future__ import annotations

from typing import TypedDict

from fastmcp import FastMCP, FastMCPApp
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool, SendMessage
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Button,
    Card,
    Column,
    Heading,
    If,
    Link,
    Metric,
    Muted,
    Row,
    Separator,
    Tab,
    Tabs,
    Text,
)
from prefab_ui.rx import ERROR, RESULT, Rx

app = FastMCPApp("News Curator")


class Story(TypedDict):
    headline: str
    summary: str
    category: str  # Markets | Economy | Technology | World | Business
    sentiment: str  # positive | negative | neutral
    minutes_ago: str  # display string, e.g. "12m ago"
    tickers: list[str]  # market tickers (financial sources)
    url: str  # section URL (links open in a new tab)


SOURCES: list[dict[str, str]] = [
    {"id": "bloomberg", "label": "Bloomberg"},
    {"id": "reuters", "label": "Reuters"},
    {"id": "guardian", "label": "The Guardian"},
    {"id": "bbc", "label": "BBC News"},
]

# Curated sample feeds. Links point at the outlet's real section pages so
# they always resolve. Swap in live RSS/API data for production use.
STORIES: dict[str, list[Story]] = {
    "bloomberg": [
        {
            "headline": "S&P 500 Futures Rise as Treasury Yields Cool Ahead of CPI Print",
            "summary": "Equity futures edged higher as bond yields pulled back, with traders positioning for a softer inflation reading that would firm up rate-cut bets.",
            "category": "Markets",
            "sentiment": "positive",
            "minutes_ago": "12m ago",
            "tickers": ["SPX", "US10Y"],
            "url": "https://www.bloomberg.com/markets",
        },
        {
            "headline": "Oil Slips Below $80 as OPEC+ Output Hikes Offset Red Sea Tensions",
            "summary": "Crude fell for a third session as supply from the cartel's latest quota increases outweighed shipping disruptions in the Red Sea.",
            "category": "Markets",
            "sentiment": "negative",
            "minutes_ago": "34m ago",
            "tickers": ["CL1", "BZ1"],
            "url": "https://www.bloomberg.com/energy",
        },
        {
            "headline": "Fed Officials Signal Patience on Rate Cuts as Inflation Cools Slowly",
            "summary": "Policymakers remain wary of easing too early, saying they need more evidence that price pressures are on a durable path to target.",
            "category": "Economy",
            "sentiment": "neutral",
            "minutes_ago": "1h ago",
            "tickers": [],
            "url": "https://www.bloomberg.com/economics",
        },
        {
            "headline": "Nvidia Suppliers Rally as AI Chip Demand Outpaces Supply",
            "summary": "Shares of equipment makers and memory vendors climbed after fresh data pointed to multi-quarter backlog growth for AI accelerators.",
            "category": "Technology",
            "sentiment": "positive",
            "minutes_ago": "2h ago",
            "tickers": ["NVDA", "TSM", "MU"],
            "url": "https://www.bloomberg.com/technology",
        },
        {
            "headline": "ECB Holds Rates, Keeps Door Open for September Cut",
            "summary": "The central bank left borrowing costs unchanged but softened its language, signalling a possible reduction at its next meeting.",
            "category": "Economy",
            "sentiment": "neutral",
            "minutes_ago": "3h ago",
            "tickers": ["EURUSD"],
            "url": "https://www.bloomberg.com/economics",
        },
        {
            "headline": "Eurozone Factory Output Rebounds as Energy Costs Ease",
            "summary": "Industrial production rose for the first time in five months, easing fears that the bloc's manufacturing slump would drag on growth.",
            "category": "World",
            "sentiment": "positive",
            "minutes_ago": "5h ago",
            "tickers": [],
            "url": "https://www.bloomberg.com/world",
        },
    ],
    "reuters": [
        {
            "headline": "Gold Hits Record High as Rate-Cut Bets Weigh on Dollar",
            "summary": "Bullion touched an all-time peak as expectations of looser U.S. monetary policy weakened the dollar and lifted demand for the metal.",
            "category": "Markets",
            "sentiment": "positive",
            "minutes_ago": "8m ago",
            "tickers": ["XAU=", "DXY"],
            "url": "https://www.reuters.com/markets/commodities/",
        },
        {
            "headline": "Asian Shares Climb on China Stimulus Hopes; Yen Steadies",
            "summary": "Regional equity benchmarks advanced on speculation of fresh support measures in Beijing, while the yen held gains after intervention warnings.",
            "category": "Markets",
            "sentiment": "positive",
            "minutes_ago": "25m ago",
            "tickers": [".N225", "JPY="],
            "url": "https://www.reuters.com/markets/asia/",
        },
        {
            "headline": "Visa, Mastercard Shares Fall on US Settlement Rules Overhaul",
            "summary": "Both card networks dropped after U.S. regulators proposed new interchange-fee rules that would cap what merchants pay on transactions.",
            "category": "Business",
            "sentiment": "negative",
            "minutes_ago": "1h ago",
            "tickers": ["V", "MA"],
            "url": "https://www.reuters.com/business/finance/",
        },
        {
            "headline": "Apple Supplier Foxconn Posts Record Quarterly Revenue on AI Servers",
            "summary": "The Taiwanese assembler beat expectations as cloud and AI infrastructure demand offset a slower smartphone refresh cycle.",
            "category": "Technology",
            "sentiment": "positive",
            "minutes_ago": "2h ago",
            "tickers": ["2317.TW", "AAPL"],
            "url": "https://www.reuters.com/technology/",
        },
        {
            "headline": "UK Inflation Slips to 2.1%, Boosting Rate-Cut Expectations",
            "summary": "Consumer prices rose at the slowest pace in nearly three years, prompting markets to price in a Bank of England cut as soon as next month.",
            "category": "Economy",
            "sentiment": "positive",
            "minutes_ago": "4h ago",
            "tickers": ["GBP="],
            "url": "https://www.reuters.com/markets/rates-bonds/",
        },
    ],
    "guardian": [
        {
            "headline": "UK economy returns to growth as services sector rebounds",
            "summary": "Gross domestic product expanded 0.4% in the latest quarter, ending a mild technical recession and easing pressure on the chancellor.",
            "category": "Economy",
            "sentiment": "positive",
            "minutes_ago": "18m ago",
            "tickers": [],
            "url": "https://www.theguardian.com/business/economics",
        },
        {
            "headline": "Bank of England under pressure to cut rates after inflation fall",
            "summary": "Economists say the door is open for a reduction in borrowing costs, but caution that wage growth remains too hot for comfort.",
            "category": "Economy",
            "sentiment": "neutral",
            "minutes_ago": "1h ago",
            "tickers": [],
            "url": "https://www.theguardian.com/business/economics",
        },
        {
            "headline": "AI firms face fines under UK online safety rules, minister warns",
            "summary": "Tech companies that fail to police harmful AI-generated content could face penalties of up to 10% of global turnover under new guidance.",
            "category": "Technology",
            "sentiment": "negative",
            "minutes_ago": "2h ago",
            "tickers": [],
            "url": "https://www.theguardian.com/technology",
        },
        {
            "headline": "EU agrees landmark nature restoration law after months of delays",
            "summary": "The bloc's 27 member states finally backed a law requiring 20% of land and sea habitats to be restored by 2030, after last-minute horse-trading.",
            "category": "World",
            "sentiment": "positive",
            "minutes_ago": "3h ago",
            "tickers": [],
            "url": "https://www.theguardian.com/world/europe-news",
        },
        {
            "headline": "House prices rise for fifth month as buyers shrug off mortgage costs",
            "summary": "Average asking prices hit a new high, with estate agents reporting the strongest spring market since before the pandemic.",
            "category": "Business",
            "sentiment": "positive",
            "minutes_ago": "5h ago",
            "tickers": [],
            "url": "https://www.theguardian.com/business/housing",
        },
    ],
    "bbc": [
        {
            "headline": "House prices: UK market picks up as rates expected to fall",
            "summary": "The biggest mortgage lender says prices rose more than expected last month, as buyers anticipate cheaper borrowing later this year.",
            "category": "Business",
            "sentiment": "positive",
            "minutes_ago": "22m ago",
            "tickers": [],
            "url": "https://www.bbc.com/news/business",
        },
        {
            "headline": "Supermarket price wars intensify as inflation eases",
            "summary": "The big grocers have cut the cost of hundreds of staples this month, with analysts saying margins are being sacrificed for market share.",
            "category": "Business",
            "sentiment": "neutral",
            "minutes_ago": "1h ago",
            "tickers": [],
            "url": "https://www.bbc.com/news/business",
        },
        {
            "headline": "TikTok faces new EU probe over addictive design claims",
            "summary": "Regulators are examining whether the app's recommendation algorithms breach digital-services rules designed to protect younger users.",
            "category": "Technology",
            "sentiment": "negative",
            "minutes_ago": "2h ago",
            "tickers": [],
            "url": "https://www.bbc.com/news/technology",
        },
        {
            "headline": "Global shipping costs soar as Red Sea diversions continue",
            "summary": "Container rates have tripled since December as carriers reroute around the Cape of Good Hope, threatening a fresh wave of goods inflation.",
            "category": "World",
            "sentiment": "negative",
            "minutes_ago": "3h ago",
            "tickers": [],
            "url": "https://www.bbc.com/news/business",
        },
        {
            "headline": "Energy bills to fall as price cap drops to two-year low",
            "summary": "The regulator confirmed a further cut to the household price cap, taking the typical annual bill to its lowest level since 2022.",
            "category": "Business",
            "sentiment": "positive",
            "minutes_ago": "6h ago",
            "tickers": [],
            "url": "https://www.bbc.com/news/business",
        },
    ],
}

# Category display order within a feed
CATEGORY_ORDER = ["Markets", "Economy", "Technology", "World", "Business"]

SENTIMENT_VARIANTS = {
    "positive": "success",
    "negative": "destructive",
    "neutral": "secondary",
}


def _pulse(source: str) -> dict[str, int]:
    """Count stories per category for a source (used for the metric row)."""
    counts = {c: 0 for c in CATEGORY_ORDER}
    for story in STORIES.get(source, []):
        counts[story["category"]] += 1
    return counts


# ---------------------------------------------------------------------------
# Backend tool — compile a briefing of a feed (callable by the LLM or the UI)
# ---------------------------------------------------------------------------


@app.tool()
def compile_briefing(source: str, topic: str = "Daily Briefing") -> dict:
    """Compile a markdown news briefing from a source's curated feed.

    Args:
        source: Feed id — bloomberg, reuters, guardian, or bbc.
        topic: Label to include in the briefing header.

    Returns a dict with:
    - source: the feed id
    - briefing: markdown text of the top headlines
    - count: number of stories included
    """
    stories = STORIES.get(source.lower(), [])
    lines = [f"## {topic} — {source}", ""]
    for s in stories:
        lines.append(f"- **{s['headline']}** ({s['category']} · {s['minutes_ago']})")
        lines.append(f"  {s['summary']}")
    return {
        "source": source.lower(),
        "briefing": "\n".join(lines),
        "count": len(stories),
    }


# ---------------------------------------------------------------------------
# UI entry point — the LLM calls this with a topic to launch the dashboard
# ---------------------------------------------------------------------------


@app.ui()
def news_curator(topic: str = "Financial News") -> PrefabApp:
    """Launch a curated news dashboard.

    - topic: displayed in the header (e.g. "Global Markets", "AI & Tech")
    """
    briefing = Rx("briefing")

    def story_card(story: Story, featured: bool = False) -> None:
        """Render one story card inside the current container."""
        with Card(css_class="border-primary" if featured else None), Column(
            gap=2, css_class="p-4"
        ):
            with Row(gap=2, align="center", wrap=True):
                Badge(story["category"], variant="outline")
                Badge(
                    story["sentiment"].title(),
                    variant=SENTIMENT_VARIANTS[story["sentiment"]],
                )
                Muted(story["minutes_ago"])
            Link(
                story["headline"],
                href=story["url"],
                target="_blank",
                bold=True,
                css_class="text-base" + (" text-lg" if featured else ""),
            )
            Muted(story["summary"])
            if story["tickers"]:
                with Row(gap=2, wrap=True):
                    for ticker in story["tickers"]:
                        Badge(ticker, variant="secondary", css_class="font-mono")

    with Column(gap=6, css_class="p-6 max-w-3xl") as view:
        with Column(gap=1):
            Heading("News Curator")
            Muted(
                f"Curated headlines from Bloomberg, Reuters, The Guardian, and BBC — {topic}."
            )

        with Tabs(value="bloomberg", variant="line") as tabs:
            for source in SOURCES:
                stories = STORIES[source["id"]]

                with Tab(source["label"], value=source["id"]), Column(gap=4):
                    # Featured story
                    Text(
                        "Top Story",
                        css_class="text-xs font-semibold uppercase tracking-wide text-muted-foreground",
                    )
                    story_card(stories[0], featured=True)

                    # Market pulse
                    pulse = _pulse(source["id"])
                    with Row(gap=3):
                        Metric(
                            label="Markets",
                            value=pulse["Markets"],
                            description="stories",
                        )
                        Metric(
                            label="Economy",
                            value=pulse["Economy"],
                            description="stories",
                        )
                        Metric(
                            label="Technology",
                            value=pulse["Technology"],
                            description="stories",
                        )

                    # Category-grouped feed
                    with Column(gap=3):
                        for category in CATEGORY_ORDER:
                            section = [s for s in stories if s["category"] == category]
                            if not section:
                                continue
                            with Column(gap=2):
                                Separator()
                                Text(
                                    category,
                                    css_class="text-xs font-semibold uppercase tracking-wide text-muted-foreground",
                                )
                                for story in section:
                                    story_card(story)

        Separator()

        # Compile a briefing of the active feed and push it back to the LLM
        with Column(gap=3):
            with Row(gap=2, align="center"):
                Button(
                    "Compile Briefing",
                    variant="default",
                    on_click=CallTool(
                        compile_briefing,
                        arguments={"source": str(tabs.rx), "topic": topic},
                        on_success=[
                            SetState("briefing", RESULT.briefing),
                            ShowToast(
                                "Briefing compiled — review below, then send it to the chat."
                            ),
                        ],
                        on_error=ShowToast(ERROR, variant="error"),
                    ),
                )
                Muted("Turns the active feed into markdown you can send to the chat.")

            with If(briefing), Card(), Column(gap=3, css_class="p-4"):
                Text(
                    "Briefing Draft",
                    css_class="text-sm font-semibold text-muted-foreground",
                )
                Text(briefing, css_class="whitespace-pre-line text-sm")
                Button(
                    "Send Briefing to Chat",
                    variant="default",
                    on_click=SendMessage(
                        f"📰 News briefing ({topic} · {tabs.rx}):\n{briefing}",
                    ),
                )

    return PrefabApp(
        view=view,
        state={
            "briefing": "",
        },
    )


mcp = FastMCP("News Curator Server", providers=[app])

if __name__ == "__main__":
    # Port 8093: keeps clear of the quiz app (:8091), the plain weather
    # demo server (:8094), and the weather app (:8095).
    mcp.run(transport="http", host="127.0.0.1", port=8093)
