#!/usr/bin/env python3
"""Export the 2026-10-29 editorial proposal as a reviewable product CSV.

Uses the saved *pre-rewrite* baseline, the earlier keyword map and the current
hand-authored catalog. Does not fetch Payhip or change product data. The CSV is
an audit snapshot, not independent proof of downloadable-file contents.

    python3 tools/export_product_seo.py
    python3 tools/export_product_seo.py --check   # verify existing export
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "docs/PRODUCT-BASELINE-AUDIT-2026-10-29.csv"
KEYWORDS = ROOT / "docs/PRODUCT-KEYWORD-MAP-2026-10-29.csv"
OUTPUT = ROOT / "docs/PRODUCT-SEO-REWRITE-2026-10-29.csv"
HOST = "https://digikitpro.shop"


class CopyParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)
        if tag in ("p", "li", "h2", "h3") and self.parts:
            self.parts.append("\n\n")

    def handle_data(self, data):
        self.parts.append(data)


def load_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_slug = {r["slug"]: r for r in rows}
    if len(by_slug) != len(rows):
        raise ValueError(f"Duplicate slug in {path}")
    return by_slug


def make_csv():
    products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
    baseline, keywords = load_csv(BASELINE), load_csv(KEYWORDS)
    slugs = [p["slug"] for p in products]
    if len(slugs) != len(set(slugs)) or set(slugs) != set(baseline) or set(slugs) != set(keywords):
        raise ValueError("Catalog, pre-rewrite audit and keyword map do not have identical unique slugs")

    fields = ["slug", "existing_name", "existing_url", "existing_price", "new_product_title",
              "primary_keyword", "secondary_keywords", "search_intent_hypothesis", "seo_title",
              "meta_description", "h1", "short_description", "complete_description", "description_html",
              "features", "included_items", "technical_details", "requirements", "audience",
              "main_image_url", "main_image_alt", "contextual_internal_links", "related_product_links",
              "cta_text", "cta_destination", "research_and_fact_notes"]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for p in products:
        slug, b, kw = p["slug"], baseline[p["slug"]], keywords[p["slug"]]
        url = f"{HOST}/products/{slug}/"
        if b["current_name"] != p["name"] or b["product_url"] != url or b["price_text"] != p["priceText"]:
            raise ValueError(f"Identity or price differs from baseline: {slug}")
        if b["payhip_url"] != p["payhipUrl"]:
            raise ValueError(f"Checkout destination differs from baseline: {slug}")
        parser = CopyParser()
        parser.feed(p["descriptionHtml"])
        prose = re.sub(r"\n{3,}", "\n\n", "".join(parser.parts)).strip()
        contextual = list(dict.fromkeys(urljoin(url, href) for href in parser.hrefs))
        related = [f"{HOST}/products/{s}/" for s in p.get("related", [])]
        main = p["images"]["main"]
        img = main if main.startswith(("http://", "https://")) else f"{HOST}/assets/products/{slug}/{main}"
        row = {
            "slug": slug, "existing_name": b["current_name"], "existing_url": url,
            "existing_price": b["price_text"], "new_product_title": p["pdpH1"],
            "primary_keyword": kw["primary_keyword_suggestion"],
            "secondary_keywords": kw["secondary_keyword_suggestions"],
            "search_intent_hypothesis": kw["intent_hypothesis"], "seo_title": p["seoTitle"],
            "meta_description": p["seoDesc"], "h1": p["pdpH1"], "short_description": p["short"],
            "complete_description": prose, "description_html": p["descriptionHtml"],
            "features": "\n".join(p.get("features") or []), "included_items": "\n".join(p.get("included") or []),
            "technical_details": "\n".join(p.get("technical") or []), "requirements": "\n".join(p.get("requirements") or []),
            "audience": "; ".join(p.get("perfectFor") or []), "main_image_url": img, "main_image_alt": p["alt"],
            "contextual_internal_links": "\n".join(contextual), "related_product_links": "\n".join(related),
            "cta_text": "Get Free on Payhip" if p.get("free") else "Buy on Payhip",
            "cta_destination": p["payhipUrl"], "research_and_fact_notes": kw["research_and_cannibalization_note"] +
                "; seller listing and cover are sources, not verification of delivered files or license",
        }
        writer.writerow(row)
    return output.getvalue(), len(products)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if export is missing or stale")
    args = parser.parse_args()
    text, n = make_csv()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            raise SystemExit(f"Export missing or stale: {OUTPUT}")
        print(f"PASS: {n} product SEO rows match the catalog and pre-rewrite audit")
    else:
        OUTPUT.write_text(text, encoding="utf-8", newline="")
        print(f"Wrote {n} rows: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
