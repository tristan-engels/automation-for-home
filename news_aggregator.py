#!/usr/bin/env python3
import feedparser
from datetime import datetime, timezone
from dateutil import parser as dateparser
from rich.console import Console
from rich.panel import Panel

console = Console()

# 1. RSS-Feeds gruppiert nach Kategorie
FEEDS = {
    "🌐 Weltweit": [
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.reutersagency.com/feed/?best-sectors=world&post_type=best",
    ],
    "🇩🇪 Deutschland": [
        "https://www.tagesschau.de/xml/rss2",
        "https://www.spiegel.de/schlagzeilen/tops/index.rss",
    ],
    "💻 IT": [
        "https://www.heise.de/rss/heise-atom.xml",
        "https://rss.golem.de/rss.php?feed=RSS2.0",
    ],
    "🔒 IT-Security": [
        "https://www.heise.de/rss/heise-security-atom.xml",
        "https://threatpost.com/feed/",
    ],
}

def fetch_today_entries(url):
    """Liest einen RSS-Feed ein und gibt nur die Einträge von heute zurück."""
    feed = feedparser.parse(url)
    today = datetime.now(timezone.utc).date()
    entries = []
    for e in feed.entries:
        # Manche Feeds liefern e.published, manche e.updated
        dt = None
        for attr in ("published", "updated"):
            if attr in e:
                dt = dateparser.parse(getattr(e, attr))
                break
        if not dt:
            continue
        if dt.date() == today:
            entries.append({"title": e.title, "link": e.link})
    return entries

def build_briefing():
    """Sammelt alle News pro Kategorie."""
    briefing = {}
    for category, urls in FEEDS.items():
        cat_entries = []
        for url in urls:
            cat_entries += fetch_today_entries(url)
        # Optional: auf maximal 5 Headlines pro Kategorie kürzen
        briefing[category] = cat_entries[:5]
    return briefing

def print_briefing(briefing):
    """Schöne Ausgabe mit Rich."""
    for category, entries in briefing.items():
        if not entries:
            text = "[i]Keine neuen Artikel heute[/i]"
        else:
            lines = "\n".join(f"- [link={e['link']}]{e['title']}[/]" for e in entries)
            text = lines
        console.print(Panel(text, title=category, expand=False))

if __name__ == "__main__":
    briefing = build_briefing()
    print_briefing(briefing)
