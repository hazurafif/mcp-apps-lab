"""News Curator app — tabbed, curated feeds with briefing export.

The LLM calls ``news_curator(topic)`` to launch the dashboard — it can let
``stories=None`` (built-in sample feeds) or generate its own curated feed
and pass it in, exactly like ``take_quiz`` accepts generated questions.
Stories are grouped by their ``source`` field into tabs. Tabs switch
between Bloomberg, Reuters, The Guardian, and BBC News feeds. "Compile
Briefing" calls the ``compile_briefing`` backend tool (from
``mcp_apps_lab.tools``) through the tool proxy — passing the rendered feed
so LLM-generated stories compile correctly; the markdown draft is shown in
the UI and "Send Briefing to Chat" pushes it back to the LLM via
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
    pulse_stories,
)
from mcp_apps_lab.tools.news import compile_briefing

app = FastMCPApp("News Curator")
app.add_tool(compile_briefing)


def _group_feeds(stories: list[Story] | None) -> dict[str, list[Story]]:
    """Resolve the feeds to render: LLM-provided stories grouped by source,
    or the built-in sample feeds (normalized so every story carries its
    ``source`` key)."""
    if not stories:
        return {
            source_id: [dict(s, source=source_id) for s in feed]
            for source_id, feed in STORIES.items()
        }
    feeds: dict[str, list[Story]] = {}
    for story in stories:
        feeds.setdefault(story.get("source", "bloomberg"), []).append(dict(story))
    return feeds


@app.ui()
def news_curator(topic: str = "Financial News", stories: list[Story] | None = None) -> PrefabApp:
    """Launch a curated news dashboard.

    - topic: displayed in the header (e.g. "Global Markets", "AI & Tech")
    - stories: OPTIONAL — generate your own curated feed instead of using
      the built-in sample data. A flat list of story dicts, each with:
        - "source": feed id the story belongs to (bloomberg, reuters,
          guardian, bbc — or any other id; stories are grouped by this
          into tabs)
        - "headline": title text
        - "summary": 1-2 sentence description
        - "category": Markets, Economy, Technology, World, or Business
        - "sentiment": positive, negative, or neutral
        - "minutes_ago": e.g. "12m ago"
        - "tickers": optional list of market tickers (e.g. ["SPX"])
        - "url": optional link for the headline

      When omitted, the built-in sample feeds are shown.
    """
    briefing = Rx("briefing")
    feeds = _group_feeds(stories)
    flat_stories = [story for feed in feeds.values() for story in feed]

    def story_card(story: Story, featured: bool = False) -> None:
        """Render one story card inside the current container."""
        with Card(css_class="border-primary" if featured else None), Column(
            gap=2, css_class="p-4"
        ):
            with Row(gap=2, align="center", wrap=True):
                Badge(story.get("category", "Business"), variant="outline")
                Badge(
                    story.get("sentiment", "neutral").title(),
                    variant=SENTIMENT_VARIANTS.get(
                        story.get("sentiment", "neutral"), "secondary"
                    ),
                )
                Muted(story.get("minutes_ago", "now"))
            headline = story.get("headline", "Untitled")
            url = story.get("url")
            if url:
                Link(
                    headline,
                    href=url,
                    target="_blank",
                    bold=True,
                    css_class="text-base" + (" text-lg" if featured else ""),
                )
            else:
                Text(
                    headline,
                    bold=True,
                    css_class="text-base" + (" text-lg" if featured else ""),
                )
            if story.get("summary"):
                Muted(story["summary"])
            if story.get("tickers"):
                with Row(gap=2, wrap=True):
                    for ticker in story["tickers"]:
                        Badge(ticker, variant="secondary", css_class="font-mono")

    with Column(gap=6, css_class="p-6 max-w-3xl") as view:
        with Column(gap=1):
            Heading("News Curator")
            Muted(f"Curated headlines across {len(feeds)} sources — {topic}.")

        with Tabs(value=next(iter(feeds)), variant="line") as tabs:
            for source_id, feed in feeds.items():
                label = next(
                    (s["label"] for s in SOURCES if s["id"] == source_id),
                    source_id.title(),
                )

                with Tab(label, value=source_id), Column(gap=4):
                    # Featured story
                    Text(
                        "Top Story",
                        css_class="text-xs font-semibold uppercase tracking-wide text-muted-foreground",
                    )
                    story_card(feed[0], featured=True)

                    # Market pulse
                    counts = pulse_stories(feed)
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
                            section = [s for s in feed if s.get("category") == category]
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
                        arguments={
                            "source": str(tabs.rx),
                            "topic": topic,
                            "stories": flat_stories,
                        },
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
