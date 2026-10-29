#!/usr/bin/env python3
"""
DigiKitPro — IndexNow auto-ping
================================

Submits changed, indexable HTML URLs, diffed via SHA-256 against
data/indexnow-state.json. The public /tools/ pages are included. Generic
robots noindex/none pages are excluded from routine updates; a previously
tracked indexable URL is notified on becoming noindex or disappearing, with
retries until the notification is accepted.

The deploy workflow runs this AFTER actions/deploy-pages. A ping failure must
never fail a deploy (the workflow also sets continue-on-error).

Normal submissions are gated on INDEXNOW_KEY. With the variable unset the
script skips without writing; --dry-run can preview the changes without a key.

Does NOT ping the retired Google or Bing sitemap-ping endpoints. Both
have been dead for years (Google 404 since Jun 2023, Bing 410 since
May 2022) and Google does not consume IndexNow at all.

Run:
    python3 tools/submit_index.py --dry-run  # preview only; no key needed
    INDEXNOW_KEY=abc123 SITE_URL=https://digikitpro.shop python3 tools/submit_index.py
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

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


class RobotsMetaParser(HTMLParser):
    """Read actual generic robots meta elements, not strings in scripts/comments."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.noindex = False
        self.inert_element = None
        self.template_depth = 0

    def handle_starttag(self, tag, attrs):
        # HTMLParser already treats script/style as raw text. These elements
        # can also contain inactive or literal markup rather than page metadata.
        if self.inert_element:
            if self.inert_element == "template" and tag == "template":
                self.template_depth += 1
            return
        if tag in {"template", "textarea", "title"}:
            self.inert_element = tag
            self.template_depth = 1 if tag == "template" else 0
            return
        if tag != "meta":
            return
        attrs = dict(attrs)
        if (attrs.get("name") or "").strip().lower() != "robots":
            return
        # Keep a value such as "max-image-preview: none" attached to its
        # directive, rather than mistaking the value for a standalone "none".
        directives = re.findall(
            r"([a-z][a-z0-9_-]*)(?:\s*:\s*[^,\s]+)?",
            attrs.get("content") or "",
            flags=re.IGNORECASE,
        )
        if {directive.lower() for directive in directives} & {"noindex", "none"}:
            self.noindex = True

    def handle_endtag(self, tag):
        if tag == self.inert_element:
            if tag == "template":
                self.template_depth -= 1
                if self.template_depth:
                    return
            self.inert_element = None


def is_noindex(html):
    parser = RobotsMetaParser()
    parser.feed(html)
    parser.close()
    return parser.noindex


def _raise_walk_error(error):
    # A partially unreadable tree must not be recorded as a complete state.
    raise error


def _iter_html_with_indexability():
    """Yield (relpath, url, sha256, is_noindex) for public HTML files."""
    for dirpath, dirnames, filenames in os.walk(ROOT, onerror=_raise_walk_error):
        dirnames[:] = sorted(d for d in dirnames if d not in
                            {".git", ".github", "data", "content", "docs",
                             "scraped", "shots", "uploads", ".cache",
                             "__pycache__", "node_modules"})
        for name in sorted(filenames):
            if not name.endswith(".html"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT)
            if _skip_file(rel):
                continue
            with open(full, "rb") as f:
                data = f.read()
            yield (rel, _file_to_url(rel), hashlib.sha256(data).hexdigest(),
                   is_noindex(data.decode("utf-8", errors="replace")))


def iter_html_pages():
    """Yield (relpath, url, sha256) for indexable public HTML pages."""
    for rel, url, digest, noindex in _iter_html_with_indexability():
        if not noindex:
            yield rel, url, digest


def load_state():
    """Read v1 or v2 state; v1 may contain previously submitted noindex pages."""
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"version": 0, "pages": {}}
    except (OSError, ValueError) as error:
        raise ValueError("Cannot read IndexNow state; refusing to submit") from error
    if (not isinstance(data, dict) or not isinstance(data.get("pages"), dict)
            or data.get("version") not in (1, 2)
            or not all(isinstance(url, str) and isinstance(digest, str)
                       for url, digest in data["pages"].items())):
        raise ValueError("Invalid or unsupported IndexNow state; refusing to submit")
    if data.get("site") not in (None, SITE):
        return {"version": 0, "pages": {}}
    # Never put another host's URL into a removal notification if a state
    # file was malformed or created without a site field.
    data["pages"] = {url: digest for url, digest in data["pages"].items()
                     if url.startswith(SITE + "/")}
    return data


def save_state(pages):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    payload = {
        "version": 2,
        "site": SITE,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages": pages,
    }
    # Replace atomically so a write failure cannot truncate the last state.
    fd, temporary = tempfile.mkstemp(prefix=".indexnow-state-", suffix=".tmp",
                                     dir=os.path.dirname(STATE_PATH))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=False)
            f.write("\n")
        os.replace(temporary, STATE_PATH)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def changed_urls(current, previous):
    """Return new indexable URLs and URLs whose SHA-256 changed."""
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
            if r.status in (200, 202):
                print(f"IndexNow submitted {len(urls)} URLs (HTTP {r.status}).")
                return True
            print(f"IndexNow submission not accepted (HTTP {r.status}).")
            return False
    except Exception as e:
        print(f"IndexNow submission failed: {e}")
        return False


def collect_changes():
    current_pages = {}
    for _rel, url, digest, noindex in _iter_html_with_indexability():
        if not noindex:
            current_pages[url] = digest
    state = load_state()
    previous = state["pages"]
    to_ping = changed_urls(current_pages, previous)

    # V2 tracks only indexable pages. A previously tracked URL that no longer
    # qualifies is either newly noindex or absent from the built tree; notify
    # it once after deployment. V1 also tracked noindex pages, so we cannot
    # safely infer transitions or deletions during migration from V1.
    if state.get("version") == 2:
        to_ping.extend(sorted(set(previous) - set(current_pages)))
    return state, current_pages, to_ping


def main(dry_run=False, check_pending=False):
    if not KEY and not dry_run:
        if check_pending:
            print("false")
        else:
            print("INDEXNOW_KEY is not set; skipping IndexNow ping (dormant).")
        return 0
    state, current_pages, to_ping = collect_changes()
    if check_pending:
        # Used by the daily sync to queue a post-deployment retry when needed.
        print("true" if to_ping else "false")
        return 0
    print(f"IndexNow: {len(current_pages)} indexable HTML pages, "
          f"{len(to_ping)} URLs to notify.")
    if dry_run:
        for url in to_ping:
            print(url)
        print("Dry run: no submission or state changes.")
        return 0
    if not to_ping:
        if state.get("version") != 2 or current_pages != state["pages"]:
            save_state(current_pages)
            print("IndexNow: refreshed state; nothing to submit.")
        else:
            print("IndexNow: nothing to submit.")
        return 0
    if submit(to_ping):
        save_state(current_pages)
        print(f"wrote {os.path.relpath(STATE_PATH, ROOT)}")
    else:
        print("IndexNow state not updated (will retry next deploy).")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notify IndexNow about changed pages.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview URLs without sending or writing")
    mode.add_argument("--check-pending", action="store_true",
                      help="print true/false without sending or writing (requires a key)")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run, check_pending=args.check_pending))
