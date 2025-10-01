from __future__ import annotations
import argparse, pathlib, time, json, feedparser, requests
from optimizer.context_engine.context_db import append_item

SOURCES = [
    ("arxiv-ai", "https://export.arxiv.org/rss/cs.AI"),
    ("hn-front", "https://hnrss.org/frontpage"),
    ("lesswrong", "https://www.lesswrong.com/feed.xml"),
]

def pull():
    out = []
    ua = {"User-Agent":"JulesCitationBot/1.0 (+virtualframes/optimizer)"}
    for name, url in SOURCES:
        try:
            r = requests.get(url, headers=ua, timeout=30)
            r.raise_for_status()
            feed = feedparser.parse(r.text)
            for e in feed.entries[:50]:
                entry = {
                    "title": e.get("title","").strip(),
                    "link": e.get("link"),
                    "published": (e.get("published") or e.get("updated") or ""),
                    "source": name
                }
                out.append(entry)
                append_item(source=f"citations:{name}", payload=entry, tags=["citation","rss"])
        except Exception:
            continue
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=150)
    args = ap.parse_args()
    items = pull()[:args.limit]
    print(json.dumps({"count":len(items)}, ensure_ascii=False))