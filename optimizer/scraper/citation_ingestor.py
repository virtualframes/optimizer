import pathlib, json, time, hashlib, re, requests
try:
    import feedparser
except ImportError:
    feedparser=None

OUTDIR = pathlib.Path("docs/citations"); OUTDIR.mkdir(parents=True, exist_ok=True)
CITES  = OUTDIR / "sources.jsonl"
APIS   = OUTDIR / "apis.jsonl"

SOURCES = [
    "https://hnrss.org/frontpage",
    "https://www.lesswrong.com/feed.xml",
    "http://arxiv.org/rss/cs.AI",
]

def sha(x:str): return hashlib.sha256(x.encode("utf-8")).hexdigest()

def ingest():
    if not feedparser:
        print("feedparser not installed, skipping citation ingest")
        return
    added=0
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries:
                link = e.get("link","")
                if not link: continue
                rec = {"ts": time.time(), "url": link, "title": e.get("title",""), "source": url, "hash": sha(link)}
                append_jsonl(CITES, rec)
                added+=1
                probe_api(link)
        except Exception as e:
            print(f"Could not process feed {url}: {e}")

    print(f"added {added} citations")

API_HINTS = ["/openapi.json", "/swagger.json", "/.well-known/agent.json"]

def probe_api(root_url: str):
    try:
        for suffix in API_HINTS:
            u = root_url.rstrip("/") + suffix
            r = requests.get(u, timeout=4)
            if r.status_code == 200 and len(r.text) > 50:
                append_jsonl(APIS, {"ts": time.time(), "endpoint": u, "sample": r.text[:200]})
    except Exception:
        pass

def append_jsonl(path: pathlib.Path, obj: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False)+"\n")

def main(): ingest()
if __name__ == "__main__": main()