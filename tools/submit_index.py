#!/usr/bin/env python3
"""
DigiKitPro — IndexNow submission helper
=======================================

Posts your most important URLs to Bing's IndexNow API (Bing feeds Yandex,
Seznam and others). It is the fastest free way to tell search engines when you
publish a new product. Requires:

* `INDEXNOW_KEY` env var (same as the GitHub Actions variable, e.g. "a1b2c3")
* `SITE_URL` env var (your deployed site, no trailing slash)

The key file `<key>.txt` must be reachable at the site root; tools/build.py
writes it automatically whenever `INDEXNOW_KEY` is set.

Run:
    INDEXNOW_KEY=abc123 SITE_URL=https://your-site.example python3 tools/submit_index.py
"""
import json, os, sys, urllib.request, urllib.parse
from datetime import date, timedelta

KEY = os.environ.get("INDEXNOW_KEY", "").strip()
SITE = os.environ.get("SITE_URL", "https://digikitpro.com").rstrip("/")


def top_urls():
    urls = ["/", "/products.html", "/freebies.html", "/bundles.html", "/blog.html"]
    data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "products.json")
    if os.path.exists(data):
        products = json.load(open(data, encoding="utf-8"))
        for p in products[:40]:
            urls.append(f"/products/{p['slug']}/")
    return urls


def main():
    if not KEY:
        print("INDEXNOW_KEY is not set; skipping submission.")
        return 0
    url_list = [SITE + u for u in top_urls()]
    body = json.dumps({
        "host": urllib.parse.urlparse(SITE).netloc,
        "key": KEY,
        "keyLocation": SITE + "/" + KEY + ".txt",
        "urlList": url_list,
    }).encode("utf-8")
    # IndexNow accepts a POST to api.indexnow.org (Bing + partners).
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "DigiKitPro-IndexNow/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow submitted {len(url_list)} URLs (HTTP {r.status}).")
            return 0
    except Exception as e:
        print(f"IndexNow submission failed: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
