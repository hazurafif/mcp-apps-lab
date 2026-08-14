"""News backend tools — called by the news curator UI."""

from __future__ import annotations

from mcp_apps_lab.data.news import stories_by_source


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
    stories = stories_by_source(source)
    lines = [f"## {topic} — {source}", ""]
    for s in stories:
        lines.append(f"- **{s['headline']}** ({s['category']} · {s['minutes_ago']})")
        lines.append(f"  {s['summary']}")
    return {
        "source": source.lower(),
        "briefing": "\n".join(lines),
        "count": len(stories),
    }
