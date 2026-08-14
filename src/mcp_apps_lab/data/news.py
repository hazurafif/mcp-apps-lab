"""News data — feed definitions and offline fallback stories.

Live feeds are fetched by ``mcp_apps_lab.tools.news``; the built-in
``STORIES`` tables below are only used when a feed can't be reached.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict


class Story(TypedDict):
    source: NotRequired[str]
    headline: str
    summary: NotRequired[str]
    category: NotRequired[str]
    sentiment: NotRequired[str]
    minutes_ago: NotRequired[str]
    tickers: NotRequired[list[str]]
    url: NotRequired[str]


# Live RSS feeds (verified working). Reuters and Bloomberg's public feeds are
# dead, so the fourth slot is CNBC Investing (free, no paywall).
SOURCES: list[dict[str, str]] = [
    {
        "id": "bloomberg",
        "label": "Bloomberg",
        "feed_url": "https://feeds.bloomberg.com/markets/news.rss",
    },
    {
        "id": "cnbc",
        "label": "CNBC",
        "feed_url": "https://www.cnbc.com/id/15839069/device/rss/rss.html",
    },
    {
        "id": "guardian",
        "label": "The Guardian",
        "feed_url": "https://www.theguardian.com/business/rss",
    },
    {
        "id": "bbc",
        "label": "BBC News",
        "feed_url": "https://feeds.bbci.co.uk/news/business/rss.xml",
    },
]

SOURCE_LABELS: dict[str, str] = {s["id"]: s["label"] for s in SOURCES}

# Offline fallback feeds — shown when a live feed can't be reached.
STORIES: dict[str, list[Story]] = {
    "bloomberg": [
        {
            "headline": "S&P 500 Futures Rise as Treasury Yields Cool Ahead of CPI Print",
            "summary": "Equity futures edged higher as bond yields pulled back, with traders positioning for a softer inflation reading that would firm up rate-cut bets.",
            "minutes_ago": "12m ago",
            "url": "https://www.bloomberg.com/markets",
        },
        {
            "headline": "Oil Slips Below $80 as OPEC+ Output Hikes Offset Red Sea Tensions",
            "summary": "Crude fell for a third session as supply from the cartel's latest quota increases outweighed shipping disruptions in the Red Sea.",
            "minutes_ago": "34m ago",
            "url": "https://www.bloomberg.com/energy",
        },
        {
            "headline": "Fed Officials Signal Patience on Rate Cuts as Inflation Cools Slowly",
            "summary": "Policymakers remain wary of easing too early, saying they need more evidence that price pressures are on a durable path to target.",
            "minutes_ago": "1h ago",
            "url": "https://www.bloomberg.com/economics",
        },
        {
            "headline": "Nvidia Suppliers Rally as AI Chip Demand Outpaces Supply",
            "summary": "Shares of equipment makers and memory vendors climbed after fresh data pointed to multi-quarter backlog growth for AI accelerators.",
            "minutes_ago": "2h ago",
            "url": "https://www.bloomberg.com/technology",
        },
        {
            "headline": "ECB Holds Rates, Keeps Door Open for September Cut",
            "summary": "The central bank left borrowing costs unchanged but softened its language, signalling a possible reduction at its next meeting.",
            "minutes_ago": "3h ago",
            "url": "https://www.bloomberg.com/economics",
        },
        {
            "headline": "Eurozone Factory Output Rebounds as Energy Costs Ease",
            "summary": "Industrial production rose for the first time in five months, easing fears that the bloc's manufacturing slump would drag on growth.",
            "minutes_ago": "5h ago",
            "url": "https://www.bloomberg.com/world",
        },
    ],
    "cnbc": [
        {
            "headline": "Gold Hits Record High as Rate-Cut Bets Weigh on Dollar",
            "summary": "Bullion touched an all-time peak as expectations of looser U.S. monetary policy weakened the dollar and lifted demand for the metal.",
            "minutes_ago": "8m ago",
            "url": "https://www.cnbc.com/markets/",
        },
        {
            "headline": "Asian Shares Climb on China Stimulus Hopes; Yen Steadies",
            "summary": "Regional equity benchmarks advanced on speculation of fresh support measures in Beijing, while the yen held gains after intervention warnings.",
            "minutes_ago": "25m ago",
            "url": "https://www.cnbc.com/markets/",
        },
        {
            "headline": "Visa, Mastercard Shares Fall on US Settlement Rules Overhaul",
            "summary": "Both card networks dropped after U.S. regulators proposed new interchange-fee rules that would cap what merchants pay on transactions.",
            "minutes_ago": "1h ago",
            "url": "https://www.cnbc.com/markets/",
        },
        {
            "headline": "Apple Supplier Foxconn Posts Record Quarterly Revenue on AI Servers",
            "summary": "The Taiwanese assembler beat expectations as cloud and AI infrastructure demand offset a slower smartphone refresh cycle.",
            "minutes_ago": "2h ago",
            "url": "https://www.cnbc.com/technology/",
        },
        {
            "headline": "UK Inflation Slips to 2.1%, Boosting Rate-Cut Expectations",
            "summary": "Consumer prices rose at the slowest pace in nearly three years, prompting markets to price in a Bank of England cut as soon as next month.",
            "minutes_ago": "4h ago",
            "url": "https://www.cnbc.com/markets/",
        },
    ],
    "guardian": [
        {
            "headline": "UK economy returns to growth as services sector rebounds",
            "summary": "Gross domestic product expanded 0.4% in the latest quarter, ending a mild technical recession and easing pressure on the chancellor.",
            "minutes_ago": "18m ago",
            "url": "https://www.theguardian.com/business/economics",
        },
        {
            "headline": "Bank of England under pressure to cut rates after inflation fall",
            "summary": "Economists say the door is open for a reduction in borrowing costs, but caution that wage growth remains too hot for comfort.",
            "minutes_ago": "1h ago",
            "url": "https://www.theguardian.com/business/economics",
        },
        {
            "headline": "AI firms face fines under UK online safety rules, minister warns",
            "summary": "Tech companies that fail to police harmful AI-generated content could face penalties of up to 10% of global turnover under new guidance.",
            "minutes_ago": "2h ago",
            "url": "https://www.theguardian.com/technology",
        },
        {
            "headline": "EU agrees landmark nature restoration law after months of delays",
            "summary": "The bloc's 27 member states finally backed a law requiring 20% of land and sea habitats to be restored by 2030, after last-minute horse-trading.",
            "minutes_ago": "3h ago",
            "url": "https://www.theguardian.com/world/europe-news",
        },
        {
            "headline": "House prices rise for fifth month as buyers shrug off mortgage costs",
            "summary": "Average asking prices hit a new high, with estate agents reporting the strongest spring market since before the pandemic.",
            "minutes_ago": "5h ago",
            "url": "https://www.theguardian.com/business/housing",
        },
    ],
    "bbc": [
        {
            "headline": "House prices: UK market picks up as rates expected to fall",
            "summary": "The biggest mortgage lender says prices rose more than expected last month, as buyers anticipate cheaper borrowing later this year.",
            "minutes_ago": "22m ago",
            "url": "https://www.bbc.com/news/business",
        },
        {
            "headline": "Supermarket price wars intensify as inflation eases",
            "summary": "The big grocers have cut the cost of hundreds of staples this month, with analysts saying margins are being sacrificed for market share.",
            "minutes_ago": "1h ago",
            "url": "https://www.bbc.com/news/business",
        },
        {
            "headline": "TikTok faces new EU probe over addictive design claims",
            "summary": "Regulators are examining whether the app's recommendation algorithms breach digital-services rules designed to protect younger users.",
            "minutes_ago": "2h ago",
            "url": "https://www.bbc.com/news/technology",
        },
        {
            "headline": "Global shipping costs soar as Red Sea diversions continue",
            "summary": "Container rates have tripled since December as carriers reroute around the Cape of Good Hope, threatening a fresh wave of goods inflation.",
            "minutes_ago": "3h ago",
            "url": "https://www.bbc.com/news/business",
        },
        {
            "headline": "Energy bills to fall as price cap drops to two-year low",
            "summary": "The regulator confirmed a further cut to the household price cap, taking the typical annual bill to its lowest level since 2022.",
            "minutes_ago": "6h ago",
            "url": "https://www.bbc.com/news/business",
        },
    ],
}


def fallback_stories(source: str, limit: int = 8) -> list[Story]:
    """Sample stories for a source (offline fallback; unknown → bloomberg)."""
    feed = STORIES.get(source.lower(), STORIES["bloomberg"])
    return [dict(s, source=source) for s in feed[:limit]]
