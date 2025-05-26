# scripts/news.py
from datetime import datetime, timezone
from dateutil import parser as dateparser
import feedparser

# 1. Feeds pro Kategorie
NEWS_FEEDS = {
    "weltweit": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.reutersagency.com/feed/?best-sectors=world&post_type=best",
    ],
    "deutschland": [
        "https://www.tagesschau.de/xml/rss2",
        "https://www.spiegel.de/schlagzeilen/tops/index.rss",
    ],
    "it": [
        "https://www.heise.de/rss/heise-atom.xml",
        "https://rss.golem.de/rss.php?feed=RSS2.0",
    ],
    "it-security": [
        "https://www.heise.de/rss/heise-security-atom.xml",
        "https://threatpost.com/feed/",
    ],
}

def fetch_today_entries(feed_url: str):
    """
    Liest einen RSS-Feed ein und gibt eine Liste von (title, link)-Tuples
    für alle heute veröffentlichten Artikel zurück.
    """
    today = datetime.now(timezone.utc).date()
    feed = feedparser.parse(feed_url)
    items = []
    for e in feed.entries:
        # Datum ermitteln
        dt = None
        for attr in ("published", "updated"):
            if attr in e:
                dt = dateparser.parse(getattr(e, attr))
                break
        # Nur Artikel vom heutigen Tag
        if dt and dt.date() == today:
            items.append((e.title, e.link))
    return items

def get_news_report(category: str, max_items: int = 5) -> str:
    """
    Baut einen Report zusammen, in dem jeder Eintrag in der Form:
    
    Titel
    Link

    (Leerzeile)
    
    ausgegeben wird.
    """
    cat = category.lower()
    if cat not in NEWS_FEEDS:
        valid = ", ".join(f"`{k}`" for k in NEWS_FEEDS)
        return f"⚠️ Unbekannte Kategorie. Bitte eine von: {valid}"

    # Headlines sammeln
    entries = []
    for url in NEWS_FEEDS[cat]:
        entries.extend(fetch_today_entries(url))

    if not entries:
        return f"ℹ️ Keine News für *{cat}* heute."

    # Maximal max_items Einträge
    selected = entries[:max_items]

    # Report bauen
    report_lines = [f"*News für {cat.title()} heute:*", ""]
    for title, link in selected:
        report_lines.append(title)
        report_lines.append(link)
        report_lines.append("")  # Leerzeile nach jedem Eintrag

    # Am Ende kein doppeltes Newline
    return "\n".join(report_lines).rstrip()

# Beispiel:
# print(get_news_report("weltweit"))
