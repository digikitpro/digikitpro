#!/usr/bin/env python3
"""Read-only landing-page audit for every Google Merchant feed item.

Checks the things an auditor can actually verify offline: that the page exists,
is indexable, states the same price and availability as the feed, carries a
usable main image, links to checkout, and has substantive description text.
It does not contact Google, Payhip, or the live site, and it changes nothing.

Usage: python3 tools/audit_merchant_landing.py [--csv PATH]
"""
from __future__ import annotations

import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {"g": "http://base.google.com/ns/1.0"}
TAG = re.compile(r"<[^>]+>")

sys.path.insert(0, str(ROOT / "tools"))
import merchant_feed  # noqa: E402


def text_of(html: str) -> str:
    return re.sub(r"\s+", " ", TAG.sub(" ", html)).strip()


def one(pattern: str, html: str, flags=re.S) -> str | None:
    m = re.search(pattern, html, flags)
    return m.group(1).strip() if m else None


def check_item(item: ET.Element, catalog: dict, categories: dict) -> dict:
    slug = item.findtext("g:id", namespaces=NS)
    product = catalog[slug]
    feed_price = item.findtext("g:price", namespaces=NS)
    row = {"id": slug, "feed_price": feed_price, "issues": []}

    page = ROOT / "products" / slug / "index.html"
    row["page_exists"] = page.is_file()
    if not row["page_exists"]:
        row["issues"].append("landing page file missing")
        return row
    html = page.read_text(encoding="utf-8")
    visible = text_of(html)
    # The preview-host guard writes a robots meta string inside <script>; only
    # a real <head> meta tag counts as a noindex.
    head_meta = re.sub(r"<script.*?</script>", " ", html, flags=re.S)

    robots = one(r'<meta name="robots" content="([^"]*)"', head_meta) or ""
    row["robots"] = robots or "(none)"
    if "noindex" in robots.lower():
        row["issues"].append("landing page is noindex")

    canonical = one(r'<link rel="canonical" href="([^"]*)"', html) or ""
    row["canonical_ok"] = canonical.rstrip("/") == f"https://digikitpro.shop/products/{slug}"
    if not row["canonical_ok"]:
        row["issues"].append(f"canonical mismatch: {canonical}")

    title = one(r"<title>(.*?)</title>", html) or ""
    h1 = one(r"<h1[^>]*>(.*?)</h1>", html)
    row["title"] = title
    row["h1"] = text_of(h1) if h1 else ""
    if not h1:
        row["issues"].append("no H1")
    if len(title) > 70:
        row["issues"].append(f"title {len(title)} chars")

    # Price consistency: the page must show the same amount the feed submits.
    price_text = re.escape(f"{float(product['price']):.2f}")
    schema_price = one(r'"price"\s*:\s*"?([0-9.]+)"?', html)
    row["schema_price"] = schema_price or ""
    row["price_in_text"] = bool(re.search(re.escape(product.get("priceText") or ""), visible))
    if not row["price_in_text"]:
        row["issues"].append("catalog price not found in page text")
    if schema_price and abs(float(schema_price) - float(product["price"])) > 0.001:
        row["issues"].append(f"structured-data price {schema_price} != catalog {product['price']}")

    row["availability_in_schema"] = one(r'"availability"\s*:\s*"([^"]*)"', html) or ""
    feed_avail = item.findtext("g:availability", namespaces=NS) or ""
    if "InStock" not in row["availability_in_schema"] and feed_avail == "in_stock":
        row["issues"].append("feed says in_stock but structured data does not")

    # Main image: exists on disk, has a real size, and is the one the feed sends.
    image_link = item.findtext("g:image_link", namespaces=NS) or ""
    rel = image_link.replace("https://digikitpro.shop/", "")
    image_path = ROOT / rel
    row["image_ok"] = image_path.is_file()
    row["image_kb"] = round(image_path.stat().st_size / 1024) if row["image_ok"] else 0
    if not row["image_ok"]:
        row["issues"].append(f"image_link file missing: {rel}")
    row["additional_images"] = len(item.findall("g:additional_image_link", NS))

    # Checkout path: a Payhip link must be reachable from the page.
    row["payhip_link"] = "payhip.com" in html
    if not row["payhip_link"]:
        row["issues"].append("no Payhip checkout link on page")

    # Description substance (visible product copy, links excluded).
    paras = re.findall(r"<p[^>]*>(.*?)</p>", html, re.S)
    body_words = sum(len(text_of(p).split()) for p in paras)
    row["body_words"] = body_words
    if body_words < 80:
        row["issues"].append(f"thin page copy ({body_words} words in <p>)")

    row["highlights"] = len(item.findall("g:product_highlight", NS))
    row["details"] = len(item.findall("g:product_detail", NS))
    if row["highlights"] < 5:
        row["issues"].append(f"{row['highlights']} highlights (rich PDP asks >4)")
    if row["details"] < 6:
        row["issues"].append(f"{row['details']} detail rows (rich PDP asks >5)")
    if slug not in categories:
        row["issues"].append("no reviewed Google category")
    return row


def main() -> int:
    catalog = {p["slug"]: p for p in json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))}
    categories = merchant_feed.load_categories()
    items = ET.parse(ROOT / "google-merchant-feed.xml").findall("./channel/item")
    rows = [check_item(item, catalog, categories) for item in items]

    out = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--csv" else None
    if out:
        fields = ["id", "feed_price", "page_exists", "robots", "canonical_ok", "title", "h1",
                  "schema_price", "price_in_text", "availability_in_schema", "image_ok",
                  "image_kb", "additional_images", "payhip_link", "body_words",
                  "highlights", "details", "issues"]
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: ("; ".join(v) if isinstance(v, list) else v) for k, v in row.items()})

    bad = [r for r in rows if r["issues"]]
    print(f"Landing audit: {len(rows)} items, {len(bad)} with at least one issue")
    counts: dict[str, int] = {}
    for row in bad:
        for issue in row["issues"]:
            key = re.sub(r"[\d,.]+", "N", issue).split(":")[0]
            counts[key] = counts.get(key, 0) + 1
    for key, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>2}  {key}")
    if out:
        print(f"csv -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
