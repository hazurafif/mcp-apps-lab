"""News Curator app — live RSS feeds in tabbed panels with briefing export.

The LLM calls ``news_curator(topic)`` to launch the dashboard. Each tab
fetches its feed live through the ``get_feed`` backend tool (from
``mcp_apps_lab.tools``) over the host's tools/call proxy — the same pattern
as the weather app's city buttons. Feeds: Bloomberg Markets, CNBC Investing,
The Guardian Business, and BBC Business. If a feed can't be reached the
built-in sample data is shown (LIVE/SAMPLE badge says which), and the
compiled briefing is sent back to the LLM via ``SendMessage``.
"""

from __future__ import annotations

from fastmcp import FastMCPApp
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
    Muted,
    Row,
    Separator,
    Tab,
    Tabs,
    Text,
)
from prefab_ui.rx import ERROR, RESULT, Rx

from mcp_apps_lab.data.news import SOURCES
from mcp_apps_lab.tools.news import get_feed

app = FastMCPApp("News Curator")
app.add_tool(get_feed)

# Story slots per tab (0 = featured, 1..SLOTS-1 = regular cards).
SLOTS = 8


@app.ui()
def news_curator(topic: str = "Financial News") -> PrefabApp:
    """Launch a curated news dashboard with live RSS feeds.

    - topic: displayed in the header (e.g. "Global Markets", "AI & Tech")
      and used in the compiled briefing
    """
    briefing = Rx("briefing")
    live = Rx("live")

    def story_card(i: int, featured: bool = False) -> None:
        """Render story slot ``i`` (hidden until the feed data arrives)."""
        slot = Rx("stories")[i]
        with If(slot), Card(css_class="border-primary" if featured else None), Column(
            gap=2, css_class="p-4"
        ):
            with Row(gap=2, align="center", wrap=True):
                Muted(slot.minutes_ago)
            headline_class = "text-base" + (" text-lg" if featured else "")
            with If(slot.url):
                Link(slot.headline, href=slot.url, target="_blank", bold=True, css_class=headline_class)
            with If(~slot.url):
                Text(slot.headline, bold=True, css_class=headline_class)
            with If(slot.summary):
                Muted(slot.summary)

    def feed_actions() -> list:
        """Actions after a successful feed fetch: sync stories + briefing."""
        return [
            SetState("stories", RESULT.stories),
            SetState("briefing", RESULT.briefing),
            SetState("live", RESULT.live),
        ]

    def fetch_button(variant: str, label: str, tabs: Tabs) -> Button:
        return Button(
            label,
            variant=variant,
            on_click=CallTool(
                get_feed,
                arguments={"source": str(tabs.rx), "topic": topic},
                on_success=feed_actions(),
                on_error=ShowToast(ERROR, variant="error"),
            ),
        )

    # The first tab's feed is fetched at launch (short timeout; sample
    # fallback if the network is unreachable).
    initial = get_feed("bloomberg", topic=topic)

    with Column(gap=6, css_class="p-6 max-w-3xl") as view:
        with Column(gap=1):
            Heading("News Curator")
            Muted(f"Live headlines across {len(SOURCES)} sources — {topic}.")
            with Row(gap=2, align="center"):
                Badge(live.then("● LIVE FEED", "○ SAMPLE DATA"), variant="secondary")

        with Tabs(
            value="bloomberg",
            variant="line",
            on_change=CallTool(
                get_feed,
                arguments={"source": str(Rx("tabs")), "topic": topic},
                on_success=feed_actions(),
                on_error=ShowToast(ERROR, variant="error"),
            ),
        ) as tabs:
            for source in SOURCES:
                with Tab(source["label"], value=source["id"]), Column(gap=4):
                    Text(
                        "Top Story",
                        css_class="text-xs font-semibold uppercase tracking-wide text-muted-foreground",
                    )
                    story_card(0, featured=True)
                    for i in range(1, SLOTS):
                        story_card(i)

        Separator()

        with Column(gap=3):
            with Row(gap=2, align="center"):
                fetch_button("outline", "Refresh Feed", tabs)
                Muted("Tab clicks and refresh re-fetch the active feed.")

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
            "stories": initial["stories"],
            "briefing": initial["briefing"],
            "live": initial["live"],
        },
    )
