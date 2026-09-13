#!/usr/bin/env python3
"""
DigiKitPro — IndexNow auto-ping
================================

Submits only URLs whose built HTML actually changed, diffed via SHA-256
against data/indexnow-state.json.

Wired into .github/workflows/deploy.yml to run AFTER actions/deploy-pages,
so crawlers are never sent to content that is not live. Always exits 0:
a ping failure must never fail a deploy (the workflow also sets
continue-on-error).

Gated on INDEXNOW_KEY. With the variable unset this script prints a skip
message and writes nothing — dormant and harmless until the owner sets
the repo variable.

Does NOT ping the retired Google or Bing sitemap-ping endpoints. Both
have been dead for years (Google 404 since Jun 2023, Bing 410 since
May 2022) and Google does not consume IndexNow at all.

Run:
    INDEXNOW_KEY=abc123 SITE_URL=https://digikitpro.shop python3 tools/submit_index.py
"""
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(ROOT, "data", "indexnow-state.json")
KEY = os.environ.get("INDEXNOW_KEY", "").strip()
SITE = os.environ.get("SITE_URL", "https://digikitpro.shop").rstrip("/")

# Verification tokens and the 404 page are not indexable content.
_SKIP_NAMES = {"404.html"}
_SKIP_PREFIXES = ("google", "yandex")
_INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"


def _skip_file(relpath):
    name = os.path.basename(relpath)
    if name in _SKIP_NAMES:
        return True
    low = name.lower()
    return any(low.startswith(p) for p in _SKIP_PREFIXES)


def _file_to_url(relpath):
    relpath = relpath.replace("\\", "/")
    if relpath == "index.html":
        return SITE + "/"
    if relpath.endswith("/index.html"):
        return SITE + "/" + relpath[: -len("index.html")]
    return SITE + "/" + relpath


def iter_html_pages():
    """Yield (relpath, url, sha256) for every public HTML page."""
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in
                       {".git", ".github", "tools", "data", "content",
                        "docs", "scraped", "shots", "uploads", ".cache",
                        "__pycache__", "node_modules"}]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT)
            if _skip_file(rel):
                continue
            h = hashlib.sha256()
            with open(full, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 16), b""):
                    h.update(chunk)
            yield rel, _file_to_url(rel), h.hexdigest()


def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        data = json.load(open(STATE_PATH, encoding="utf-8"))
    except Exception:
        return {}
    pages = data.get("pages")
    return pages if isinstance(pages, dict) else {}


def save_state(pages):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    payload = {
        "version": 1,
        "site": SITE,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages": pages,
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False)
        f.write("\n")


def changed_urls(current, previous):
    """URLs whose SHA-256 changed, or that are new. Drops vanished pages
    from the next state without submitting a delete (IndexNow has none)."""
    out = []
    for url, digest in current.items():
        if previous.get(url) != digest:
            out.append(url)
    return out


def submit(urls):
    """POST to IndexNow. Returns True on HTTP 200/202. Never raises."""
    if not urls:
        return True
    body = json.dumps({
        "host": urllib.parse.urlparse(SITE).netloc,
        "key": KEY,
        "keyLocation": SITE + "/" + KEY + ".txt",
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        _INDEXNOW_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "DigiKitPro-IndexNow/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow submitted {len(urls)} URLs (HTTP {r.status}).")
            return r.status in (200, 202)
    except Exception as e:
        print(f"IndexNow submission failed: {e}")
        return False


def main():
    if not KEY:
        print("INDEXNOW_KEY is not set; skipping IndexNow ping (dormant).")
        return 0
    current_pages = {}
    for rel, url, digest in iter_html_pages():
        current_pages[url] = digest
    previous = load_state()
    to_ping = changed_urls(current_pages, previous)
    print(f"IndexNow: {len(current_pages)} HTML pages, {len(to_ping)} changed.")
    if not to_ping:
        print("IndexNow: nothing to submit.")
        return 0
    if submit(to_ping):
        save_state(current_pages)
        print(f"wrote {os.path.relpath(STATE_PATH, ROOT)}")
    else:
        print("IndexNow state not updated (will retry next deploy).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
