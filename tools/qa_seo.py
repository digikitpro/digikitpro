#!/usr/bin/env python3
"""Offline SEO regression checks for the generated site.

Run after ``python3 tools/build.py``. These checks validate the markup and
local files, not Google's selected canonicals, indexing, rankings, clicks,
field performance or availability of remote resources.
"""
import json
import os
import re
from collections import defaultdict
from datetime import date
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from pages_blog import article_seo_title

ROOT = Path(__file__).resolve().parent.parent
SITE = os.environ.get("SITE_URL", "https://digikitpro.shop").rstrip("/")
SITE_PARTS = urlsplit(SITE)
SKIP = {".git", "node_modules", "docs", "content", "data", "scraped", "shots", "uploads", ".cache", "__pycache__", ".github"}
errors = []
checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles, self.h1s, self.canonicals, self.bases = [], [], [], []
        self.meta = defaultdict(list)
        self.schemas, self.times = [], []
        self.hero_src = None
        self._title = self._h1 = self._json = self._hero = False
        self._schema_text = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._title = True
            self.titles.append("")
        elif tag == "h1":
            self._h1 = True
            self.h1s.append("")
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key].append(a.get("content", ""))
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        elif tag == "base":
            self.bases.append(a.get("href", ""))
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._json = True
            self._schema_text = ""
        elif tag == "figure" and "article-hero" in a.get("class", "").split():
            self._hero = True
        elif tag == "img" and self._hero and self.hero_src is None:
            self.hero_src = a.get("src")
        elif tag == "time" and a.get("datetime"):
            self.times.append(a["datetime"])

    def handle_data(self, text):
        if self._title:
            self.titles[-1] += text
        if self._h1:
            self.h1s[-1] += text
        if self._json:
            self._schema_text += text

    def handle_endtag(self, tag):
        if tag == "title":
            self._title = False
        elif tag == "h1":
            self._h1 = False
        elif tag == "figure":
            self._hero = False
        elif tag == "script" and self._json:
            self.schemas.append(self._schema_text)
            self._json = False


def local_file(url):
    """Map a same-origin URL to the generated file; reject traversal/query."""
    u = urlsplit(url)
    if (u.scheme, u.netloc) != (SITE_PARTS.scheme, SITE_PARTS.netloc) or u.query or u.fragment:
        return None
    path = unquote(u.path).lstrip("/")
    target = ROOT / path
    if not path or u.path.endswith("/"):
        target = target / "index.html"
    target = target.resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return target


def expected_url(path):
    rel = path.relative_to(ROOT)
    if rel.name == "index.html":
        directory = rel.parent.as_posix()
        return SITE + "/" + (directory + "/" if directory != "." else "")
    return SITE + "/" + rel.as_posix()


@lru_cache(maxsize=None)
def image_size(path):
    """Read PNG, JPEG or WebP dimensions with stdlib; None for other formats."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:2] == b"\xff\xd8":
        pos = 2
        sof = set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0))
        while pos + 3 < len(data):
            if data[pos] != 0xFF:
                pos += 1
                continue
            while pos < len(data) and data[pos] == 0xFF:
                pos += 1
            if pos >= len(data):
                break
            marker = data[pos]
            pos += 1
            if marker in (0x01, 0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                continue
            length = int.from_bytes(data[pos:pos + 2], "big")
            if length < 2 or pos + length > len(data):
                break
            if marker in sof and length >= 7:
                return int.from_bytes(data[pos + 5:pos + 7], "big"), int.from_bytes(data[pos + 3:pos + 5], "big")
            pos += length
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        pos = 12
        while pos + 8 <= len(data):
            chunk = data[pos:pos + 4]
            length = int.from_bytes(data[pos + 4:pos + 8], "little")
            body = data[pos + 8:pos + 8 + length]
            if chunk == b"VP8X" and len(body) >= 10:
                return 1 + int.from_bytes(body[4:7], "little"), 1 + int.from_bytes(body[7:10], "little")
            if chunk == b"VP8L" and len(body) >= 5 and body[0] == 0x2F:
                bits = int.from_bytes(body[1:5], "little")
                return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
            if chunk == b"VP8 " and len(body) >= 10 and body[3:6] == b"\x9d\x01\x2a":
                return int.from_bytes(body[6:8], "little") & 0x3FFF, int.from_bytes(body[8:10], "little") & 0x3FFF
            pos += 8 + length + (length % 2)
    return None


def main():
    check(SITE_PARTS.scheme == "https" and bool(SITE_PARTS.netloc), "SITE_URL must use HTTPS")
    html_files = sorted(p for p in ROOT.rglob("*.html")
                        if not SKIP.intersection(p.relative_to(ROOT).parts)
                        and not p.name.lower().startswith(("google", "yandex")))
    pages = {}
    titles, descriptions = defaultdict(list), defaultdict(list)
    article_count = howto_count = 0
    for path in html_files:
        rel = path.relative_to(ROOT).as_posix()
        parser = Page()
        parser.feed(path.read_text(encoding="utf-8"))
        pages[path.resolve()] = parser
        canonical = expected_url(path)
        check(parser.canonicals == [canonical], f"{rel}: expected one self-canonical {canonical}, got {parser.canonicals}")
        check(len(parser.titles) == 1 and bool(parser.titles[0].strip()), f"{rel}: missing/duplicate title")
        check(len(parser.meta["description"]) == 1 and bool(parser.meta["description"][0].strip()), f"{rel}: missing/duplicate description")
        check(len(parser.h1s) == 1 and bool(parser.h1s[0].strip()), f"{rel}: expected one nonempty h1")
        check(len(parser.meta["robots"]) == 1, f"{rel}: expected one robots directive")
        if len(parser.titles) == 1:
            titles[parser.titles[0]].append(rel)
            check(parser.meta["og:title"] == parser.titles, f"{rel}: Open Graph title differs from title")
        if len(parser.meta["description"]) == 1:
            descriptions[parser.meta["description"][0]].append(rel)
            check(parser.meta["og:description"] == parser.meta["description"], f"{rel}: Open Graph description differs")
        check(parser.meta["og:url"] == [canonical], f"{rel}: Open Graph URL differs from canonical")

        images = parser.meta["og:image"]
        widths, heights = parser.meta["og:image:width"], parser.meta["og:image:height"]
        check(len(images) == 1 and urlsplit(images[0]).scheme == "https", f"{rel}: expected one HTTPS Open Graph image")
        check(len(widths) <= 1 and len(heights) <= 1 and len(widths) == len(heights), f"{rel}: incomplete image dimensions")
        if len(images) == len(widths) == len(heights) == 1:
            image = local_file(images[0])
            if image is not None:
                size = image_size(image)
                check(size is not None, f"{rel}: missing or unsupported local Open Graph image {image}")
                check(size is not None and (str(size[0]), str(size[1])) == (widths[0], heights[0]),
                      f"{rel}: Open Graph dimensions {widths}x{heights} do not match {size}")

        schemas = []
        for source in parser.schemas:
            try:
                node = json.loads(source)
                if isinstance(node, dict):
                    schemas.append(node)
                else:
                    check(False, f"{rel}: JSON-LD block is not an object")
            except json.JSONDecodeError as exc:
                check(False, f"{rel}: invalid JSON-LD: {exc}")
        articles = [s for s in schemas if s.get("@type") == "BlogPosting"]
        if rel.startswith("blog/") and rel.endswith("/index.html"):
            article_count += 1
            check(len(articles) == 1, f"{rel}: expected one BlogPosting")
            if len(articles) == 1:
                article = articles[0]
                check(article.get("url") == canonical and article.get("mainEntityOfPage") == canonical, f"{rel}: article URL differs from canonical")
                check(len(parser.h1s) == 1 and article.get("headline") == parser.h1s[0], f"{rel}: article headline differs from h1")
                check(article.get("description") in parser.meta["description"], f"{rel}: article description differs")
                check(bool(parser.times) and article.get("datePublished") == parser.times[0] and article.get("dateModified") == parser.times[-1], f"{rel}: article dates differ from visible dates")
                try:
                    published = date.fromisoformat(article.get("datePublished", ""))
                    modified = date.fromisoformat(article.get("dateModified", ""))
                    check(modified >= published, f"{rel}: modification date precedes publication")
                except ValueError:
                    check(False, f"{rel}: invalid article date")
                hero = urljoin(canonical, parser.hero_src) if parser.hero_src else None
                check((hero is not None and article.get("image") == [hero]) or (hero is None and "image" not in article),
                      f"{rel}: article image is not the visible full-size hero")
        for howto in (s for s in schemas if s.get("@type") == "HowTo"):
            howto_count += 1
            check(bool(howto.get("step")), f"{rel}: HowTo has no steps")
            check(not any(key in howto for key in ("tool", "totalTime", "performTime")), f"{rel}: unverified required tools or time in HowTo")

    for title, paths in titles.items():
        check(len(paths) == 1, f"duplicate title {title!r}: {paths}")
    for description, paths in descriptions.items():
        check(len(paths) == 1, f"duplicate description {description!r}: {paths}")

    sitemap_path = ROOT / "sitemap.xml"
    root = ET.parse(sitemap_path).getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [e.text for e in root.findall("s:url/s:loc", namespace)]
    check(bool(urls), "XML sitemap is empty")
    check(len(urls) == len(set(urls)), "XML sitemap has duplicate URLs")
    for url in urls:
        target = local_file(url or "")
        check(target is not None and target.is_file(), f"sitemap URL has no local file: {url}")
        page = pages.get(target)
        check(page is not None, f"sitemap URL has no parsed page: {url}")
        if page is not None:
            check(page.canonicals == [url], f"sitemap URL differs from canonical: {url}")
            check(all("noindex" not in value.lower() for value in page.meta["robots"]), f"sitemap includes a noindex page: {url}")
    text_urls = {line.strip() for line in (ROOT / "sitemap.txt").read_text(encoding="utf-8").splitlines() if line.strip()}
    check(text_urls == set(urls), "text sitemap and XML sitemap differ")
    image_ns = {**namespace, "image": "http://www.google.com/schemas/sitemap-image/1.1"}
    image_root = ET.parse(ROOT / "sitemap-images.xml").getroot()
    image_count = 0
    for entry in image_root.findall("s:url", image_ns):
        page_url = entry.findtext("s:loc", namespaces=image_ns)
        check(page_url in urls, f"image sitemap page is absent from XML sitemap: {page_url}")
        for image_url in (e.text for e in entry.findall("image:image/image:loc", image_ns)):
            image_count += 1
            parts = urlsplit(image_url or "")
            check(parts.scheme == "https" and bool(parts.netloc), f"image sitemap has invalid URL: {image_url}")
            if parts.netloc == SITE_PARTS.netloc:
                local_image = local_file(image_url)
                check(local_image is not None and local_image.is_file(), f"image sitemap local asset is missing: {image_url}")
    check(image_count > 0, "image sitemap is empty")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    check(f"Sitemap: {SITE}/sitemap.xml" in robots, "robots.txt does not advertise XML sitemap")
    check(not re.search(r"^\s*Disallow:\s*/\s*$", robots, re.I | re.M), "robots.txt globally disallows crawling")
    for noindex in ("404.html", "search.html", "thank-you.html"):
        page = pages[(ROOT / noindex).resolve()]
        check(any("noindex" in r.lower() for r in page.meta["robots"]), f"{noindex}: expected noindex")
        check(expected_url(ROOT / noindex) not in urls, f"{noindex}: noindex page appears in sitemap")
    error_page = pages[(ROOT / "404.html").resolve()]
    check(error_page.bases == ["/"], "404.html needs a root base for arbitrary nested URLs")
    check("location.replace(p +" not in (ROOT / "404.html").read_text(encoding="utf-8"), "404.html must not retry unknown paths")

    check(article_seo_title({"title": "An unusually long article title without any natural break that should remain whole"}).startswith("An unusually long article title without any natural break that should remain whole"), "long title was cut mid-word")
    check(article_seo_title({"title": "Long title: supporting detail that can be omitted", "seo_title": "A helpful short title"}) == "A helpful short title | DigiKitPro", "manual search title override failed")
    hair = pages[(ROOT / "blog/how-to-paint-realistic-hair-in-procreate/index.html").resolve()]
    check(hair.titles == ["How to Paint Realistic Hair in Procreate | DigiKitPro"], "hair article search title regressed")

    print(f"SEO QA: {checks} checks across {len(html_files)} pages, {len(urls)} sitemap URLs, {image_count} sitemap images, {article_count} articles and {howto_count} HowTo blocks")
    if errors:
        for error in errors[:50]:
            print("  FAIL:", error)
        if len(errors) > 50:
            print(f"  ... {len(errors) - 50} more failures")
        print(f"FAILED: {len(errors)} checks")
        return 1
    print("PASS: local markup and crawlability invariants (not a Google indexing or ranking test)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
