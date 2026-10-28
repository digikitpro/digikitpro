#!/usr/bin/env python3
"""Check local image/script/stylesheet references in the built HTML, offline.

Does not check CSS background URLs, external URLs, visual rendering or delivery.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "node_modules", "docs", "content", "data", "scraped", "__pycache__", "shots"}


class Assets(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.count = 0
        self.missing = []

    def handle_starttag(self, tag, attributes):
        if tag not in ("img", "source", "script", "link"):
            return
        attrs = dict(attributes)
        refs = []
        if tag in ("img", "source", "script") and attrs.get("src"):
            refs.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in ("stylesheet", "icon", "apple-touch-icon") and attrs.get("href"):
            refs.append(attrs["href"])
        if tag in ("img", "source") and attrs.get("srcset"):
            refs.extend(part.strip().split()[0] for part in attrs["srcset"].split(",") if part.strip())
        for ref in refs:
            if ref.startswith(("http:", "https:", "//", "data:", "#")):
                continue
            path = unquote(urlsplit(ref).path)
            if not path:
                continue
            self.count += 1
            target = (ROOT / path.lstrip("/") if path.startswith("/") else self.page.parent / path).resolve()
            if not target.is_file():
                self.missing.append((self.page.relative_to(ROOT), ref))


def main():
    pages, refs, missing = 0, 0, []
    for page in ROOT.rglob("*.html"):
        if any(part in SKIP for part in page.relative_to(ROOT).parts):
            continue
        if page.name.startswith(("google", "yandex")):
            continue  # search-engine ownership verification files
        parsed = Assets(page)
        parsed.feed(page.read_text(encoding="utf-8", errors="replace"))
        pages += 1
        refs += parsed.count
        missing.extend(parsed.missing)
    print(f"{pages} HTML pages; {refs} local asset references; {len(missing)} missing")
    for page, ref in missing:
        print(f"  {page}: {ref}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
