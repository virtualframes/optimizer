from __future__ import annotations
import argparse, json, os, requests
from optimizer.context_engine.context_db import append_item

GITHUB_API = "https://api.github.com"
UA = {"User-Agent":"JulesForkBot/1.0 (+virtualframes/optimizer)"}

def list_forks(repo: str, token: str | None) -> list[dict]:
    headers = dict(UA)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{GITHUB_API}/repos/{repo}/forks?per_page=100"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/name")
    args = ap.parse_args()
    token = os.getenv("GITHUBTOKEN") or os.getenv("GITHUB_TOKEN")
    forks = list_forks(args.repo, token)
    for fk in forks[:100]:
        append_item("github:fork", {"repo": args.repo, "fork": fk.get("full_name")}, ["github","fork"])
    print(json.dumps({"repo": args.repo, "forks_indexed": len(forks)}, ensure_ascii=False))