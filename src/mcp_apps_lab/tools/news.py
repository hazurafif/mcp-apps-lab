"""News backend tools — called by the news curator UI."""

from __future__ import annotations

from mcp_apps_lab.data.news import Story, stories_by_source


def compile_briefing(
    source: str, topic: str = "Daily Briefing", stories: list[Story] | None = None
) -> dict:
    """Compile a markdown news briefing from a feed.

    Args:
        source: Feed id — bloomberg, reuters, guardian, or bbc.
        topic: Label to include in the briefing header.
        stories: Optional list of stories to compile. The UI passes the
            currently rendered feed here so LLM-generated feeds compile
            correctly; defaults to the built-in feed for the source.

    Returns a dict with:
    - source: the feed id
    - briefing: markdown text of the top headlines
    - count: number of stories included
    """
    if stories:
        # The UI passes all rendered feeds; keep only the active source's stories.
        feed = [s for s in stories if s.get("source", "bloomberg") == source]
    else:
        feed = stories_by_source(source)
    lines = [f"## {topic} — {source}", ""]
    for s in feed:
        lines.append(
            f"- **{s.get('headline', 'Untitled')}** "
            f"({s.get('category', 'Business')} · {s.get('minutes_ago', 'now')})"
        )
        summary = s.get("summary")
        if summary:
            lines.append(f"  {summary}")
    return {
        "source": source.lower(),
        "briefing": "\n".join(lines),
        "count": len(feed),
    }
