"""News Curator app — tabbed, curated financial feeds with briefing export.

The LLM calls ``news_curator(topic)`` to launch the dashboard. Tabs switch
between Bloomberg, Reuters, The Guardian, and BBC News feeds. "Compile
Briefing" calls the ``compile_briefing`` backend tool (from
``mcp_apps_lab.tools``) through the tool proxy; the markdown draft is shown
in the UI and "Send Briefing to Chat" pushes it back to the LLM via
``SendMessage`` (multi-turn, like the quiz's final score).
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
    Metric,
    Muted,
    Row,
    Separator,
    Tab,
    Tabs,
    Text,
)
from prefab_ui.rx import ERROR, RESULT, Rx

from mcp_apps_lab.data.news import (
    CATEGORY_ORDER,
    SENTIMENT_VARIANTS,
    SOURCES,
    STORIES,
    Story,
    pulse,
)
from mcp_apps_lab.tools.news import compile_briefing

app = FastMCPApp("News Curator")
app.add_tool(compile_briefing)


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
                    counts = pulse(source["id"])
                    with Row(gap=3):
                        Metric(
                            label="Markets",
                            value=counts["Markets"],
                            description="stories",
                        )
                        Metric(
                            label="Economy",
                            value=counts["Economy"],
                            description="stories",
                        )
                        Metric(
                            label="Technology",
                            value=counts["Technology"],
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
