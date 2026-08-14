"""News backend tools — live RSS fetching with offline fallback.

``get_feed`` is called by the news UI (tab clicks / refresh) through the
tool proxy. Feeds are parsed with the stdlib (no new dependencies), and any
failure falls back to the built-in sample data with ``live=False``.
"""

from __future__ import annotations

import html
import re
import urllib.request
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

from mcp_apps_lab.data.news import SOURCE_LABELS, SOURCES, Story, fallback_stories

_UA = "Mozilla/5.0 (mcp-apps-lab; personal demo)"
_FETCH_TIMEOUT = 6.0
_SUMMARY_CHARS = 240

_ATOM_NS = "{http://www.w3.org/2005/Atom}"
_CONTENT_NS = "{http://purl.org/rss/1.0/modules/content/}"

_HTML_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# Fetch + parse
# ---------------------------------------------------------------------------


def _fetch_feed(url: str) -> bytes:
    """GET an RSS feed (raises on any failure)."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": _UA,
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT) as response:
        return response.read()


def _clean_html(text: str) -> str:
    """Strip tags from feed descriptions and collapse whitespace."""
    text = html.unescape(_HTML_TAG.sub("", text or ""))
    return _WS.sub(" ", text).strip()


def _time_ago(pub: str | None) -> str:
    """Format a feed pubDate/updated stamp as a relative time (e.g. "2h ago")."""
    if not pub:
        return "now"
    try:
        dt = parsedate_to_datetime(pub)  # RFC 822 (RSS pubDate)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))  # ISO 8601 (Atom)
        except ValueError:
            return "now"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    minutes = int((datetime.now(UTC) - dt).total_seconds() // 60)
    if minutes < 1:
        return "now"
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def _parse_feed(raw: bytes, source: str, limit: int) -> list[Story]:
    """Parse RSS 2.0 (and Atom) XML into normalized Story dicts."""
    root = ET.fromstring(raw)
    items = root.findall(".//item")
    is_atom = not items
    nodes = items or root.findall(f".//{_ATOM_NS}entry")

    stories: list[Story] = []
    for node in nodes[:limit]:
        if is_atom:
            title = node.findtext(f"{_ATOM_NS}title")
            link_el = node.find(f"{_ATOM_NS}link")
            link = link_el.get("href") if link_el is not None else None
            summary = node.findtext(f"{_ATOM_NS}summary") or node.findtext(
                f"{_ATOM_NS}content"
            )
            pub = node.findtext(f"{_ATOM_NS}updated")
        else:
            title = node.findtext("title")
            link = node.findtext("link")
            summary = node.findtext("description") or node.findtext(
                f"{_CONTENT_NS}encoded"
            )
            pub = node.findtext("pubDate")

        headline = _clean_html(title or "Untitled")
        if not headline:
            continue
        summary_text = _clean_html(summary or "")
        if len(summary_text) > _SUMMARY_CHARS:
            summary_text = summary_text[:_SUMMARY_CHARS - 1].rstrip() + "…"

        stories.append(
            {
                "source": source,
                "headline": headline,
                "summary": summary_text,
                "minutes_ago": _time_ago(pub),
                "url": (link or "").strip(),
            }
        )
    return stories


# ---------------------------------------------------------------------------
# Public backend tool
# ---------------------------------------------------------------------------


def _build_briefing(
    source: str, topic: str, stories: list[Story], live: bool
) -> str:
    """Markdown summary of a feed, used by the UI and the news:// resources."""
    label = SOURCE_LABELS.get(source, source.title())
    lines = [f"## {topic} — {label}"]
    if not live:
        lines.append("_⚠ Live feed unreachable — showing sample data._")
    lines.append("")
    for s in stories:
        lines.append(f"- **{s.get('headline', 'Untitled')}** ({s.get('minutes_ago', 'now')})")
        summary = s.get("summary")
        if summary:
            lines.append(f"  {summary}")
    return "\n".join(lines)


def get_feed(source: str, topic: str = "Financial News", limit: int = 8) -> dict:
    """Fetch the latest stories for a source feed (live RSS, sample fallback).

    Args:
        source: Feed id — bloomberg, cnbc, guardian, or bbc.
        topic: Label used in the compiled briefing header.
        limit: Maximum number of stories to fetch.

    Returns a dict with:
    - source: the feed id
    - live: whether stories came from the live feed (False = sample data)
    - stories: list of story dicts (headline, summary, minutes_ago, url, ...)
    - briefing: markdown summary of the feed
    """
    feed_url = next((s["feed_url"] for s in SOURCES if s["id"] == source), None)
    live = False
    stories: list[Story]
    try:
        if feed_url is None:
            raise ValueError(f"unknown feed: {source!r}")
        parsed = _parse_feed(_fetch_feed(feed_url), source, limit)
        if parsed:
            stories, live = parsed, True
        else:
            stories = fallback_stories(source, limit)
    except Exception:
        stories = fallback_stories(source, limit)

    return {
        "source": source,
        "live": live,
        "stories": stories,
        "briefing": _build_briefing(source, topic, stories, live),
    }
