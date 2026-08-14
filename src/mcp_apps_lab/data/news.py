"""News data — curated sample feeds for Bloomberg, Reuters, The Guardian, BBC.

Links point at each outlet's real section pages so they always resolve.
Swap in live RSS/API data for production use.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict


class Story(TypedDict):
    source: NotRequired[str]  # feed id; required when the LLM supplies stories
    headline: str
    summary: NotRequired[str]
    category: str  # Markets | Economy | Technology | World | Business
    sentiment: NotRequired[str]  # positive | negative | neutral
    minutes_ago: NotRequired[str]  # display string, e.g. "12m ago"
    tickers: NotRequired[list[str]]  # market tickers (financial sources)
    url: NotRequired[str]  # section URL (links open in a new tab)


SOURCES: list[dict[str, str]] = [
    {"id": "bloomberg", "label": "Bloomberg"},
    {"id": "reuters", "label": "Reuters"},
    {"id": "guardian", "label": "The Guardian"},
    {"id": "bbc", "label": "BBC News"},
]

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


def pulse_stories(stories: list[Story]) -> dict[str, int]:
    """Count stories per category in an arbitrary feed (built-in or LLM-made)."""
    counts = {c: 0 for c in CATEGORY_ORDER}
    for story in stories:
        category = story.get("category", "Business")
        if category in counts:
            counts[category] += 1
    return counts


def pulse(source: str) -> dict[str, int]:
    """Count stories per category for a built-in source feed."""
    return pulse_stories(STORIES.get(source, []))


def stories_by_source(source: str) -> list[Story]:
    """Stories for a source, defaulting to bloomberg for unknown ids."""
    return STORIES.get(source.lower(), STORIES["bloomberg"])
