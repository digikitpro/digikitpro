#!/usr/bin/env python3
"""Offline regression checks for the product SEO review snapshot (54 products).

Run after tools/build.py and tools/export_product_seo.py. These assertions do
not inspect delivered archives, verify licenses, contact Payhip, measure field
performance or establish Google indexing/rankings.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import merchant_feed  # noqa: E402
from seo_engine import should_fill  # noqa: E402
from export_product_seo import make_csv  # noqa: E402


class ProductPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main_alt = None
        self.thumb_alts = []
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img" and a.get("id") == "product-main-image":
            self.main_alt = a.get("alt")
        if tag == "a":
            if "data-gallery-thumb" in a:
                self.thumb_alts.append(a.get("data-alt"))
            if a.get("href"):
                self.hrefs.append(a["href"])


def load_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
    baseline = load_csv(ROOT / "docs/PRODUCT-BASELINE-AUDIT-2026-10-29.csv")
    records = {r["slug"]: r for r in baseline}
    sheet_path = ROOT / "docs/PRODUCT-SEO-REWRITE-2026-10-29.csv"
    expected_sheet, expected_count = make_csv()
    failures = []
    checks = 0

    def check(ok, message):
        nonlocal checks
        checks += 1
        if not ok:
            failures.append(message)

    # Catalog expanded 2026-11-10 with three Christmas SKUs (owner-sanctioned
    # addition, listed in the PR for this change): Iq8D4 Christmas Sweater Knit
    # Pattern Brushes, AwePR Christmas Tree Stamp Brushes, 1vTuy Hand-Drawn
    # Christmas Stamp Brushes. The 2026-10-29 snapshot CSVs were EXTENDED with
    # matching new rows; the original 51 rows are byte-identical to the dated
    # snapshot. Re-pin alongside verify.py and the baseline CSVs.
    check(len(products) == 54 == len(records) == expected_count, "Snapshot must cover 54 unique products")
    check(sheet_path.is_file() and sheet_path.read_text(encoding="utf-8") == expected_sheet,
          "Product SEO CSV missing or stale")
    for field in ("pdpH1", "seoTitle", "seoDesc", "short", "alt"):
        values = [p.get(field, "").strip() for p in products]
        check(all(values) and len(set(values)) == len(values), f"Missing or duplicate {field}")

    by_slug = {p["slug"]: p for p in products}
    for p in products:
        slug, old = p["slug"], records.get(p["slug"], {})
        for field, before in (("id", "id"), ("name", "current_name"), ("payhipUrl", "payhip_url"),
                              ("priceText", "price_text")):
            check(str(p.get(field, "")) == old.get(before, ""), f"{slug}: {field} differs from baseline")
        check(str(bool(p.get("free"))).lower() == old.get("is_free", "").lower(), f"{slug}: free flag changed")
        check(f"assets/products/{slug}/{p['images']['main']}" == old.get("main_image"), f"{slug}: cover changed")
        original_gallery = json.loads(old.get("gallery_images", "[]"))
        check(p["images"].get("gallery", []) == original_gallery, f"{slug}: gallery records changed")
        check(not should_fill(p, "seoTitle") and not should_fill(p, "seoDesc"), f"{slug}: SEO sync overwrite risk")
        check(len(re.findall(r"<p>", p.get("descriptionHtml", ""))) >= 3, f"{slug}: incomplete description")
        check(len(p.get("features", [])) >= 2 and len(p.get("included", [])) >= 1, f"{slug}: missing product details")
        links = re.findall(r'href="../../products/([^/]+)/"', p.get("descriptionHtml", ""))
        check(bool(links) and all(x in by_slug and x != slug for x in links), f"{slug}: no valid contextual product link")
        check(all(x in by_slug and x != slug for x in p.get("related", [])), f"{slug}: invalid related item")
        page = ROOT / "products" / slug / "index.html"
        check(page.is_file(), f"{slug}: built page missing")
        if page.is_file():
            parsed = ProductPage()
            markup = page.read_text(encoding="utf-8")
            parsed.feed(markup)
            check(not re.search(r"instant (?:digital )?(?:download|delivery)|download instantly|lifetime access|keep forever|save 80%", markup, re.I),
                  f"{slug}: unverified delivery or savings promise reintroduced")
            check(parsed.main_alt == p.get("alt"), f"{slug}: main image alt not rendered")
            check(p["payhipUrl"] in parsed.hrefs, f"{slug}: direct checkout link missing")
            if p["images"].get("gallery"):
                check(len(parsed.thumb_alts) == 1 + len(p["images"]["gallery"]), f"{slug}: gallery count changed")
                for index, gallery in enumerate(p["images"]["gallery"], 2):
                    wanted = gallery.get("alt") or f"{p['name']} product image {index}"
                    check(len(parsed.thumb_alts) >= index and parsed.thumb_alts[index - 1] == wanted,
                          f"{slug}: gallery image {index} inherited incorrect cover description")

    # Counts for these two products were confirmed against their Payhip
    # listings on 2026-11-08 (source of truth for delivered contents):
    #   https://payhip.com/b/b70QE (Essential Line Art & Sketch Kit) states
    #     "43 professional brushes + 1 bonus texture brush": 14 PENCIL,
    #     12 LINERS, 7 INK, 6 DETAILERS, 3 SKETCH TOOLS + 1 BONUS TEXTURE.
    #   https://payhip.com/b/2h0iG (Ultimate Portrait Mastery Bundle) states
    #     "252+ professional assets" across 4 kits (43 + 19 + 160 + 30 = 252).
    # The copy must state the confirmed counts; the old "disputed count" ban
    # and mandatory "awaiting confirmation" caveat were retired with them.
    confirmed_counts = {
        "essential-line-art-sketch-kit": ("43", "14", "12", "7", "6", "3", "bonus"),
        "ultimate-portrait-mastery-bundle": ("252+", "43", "19", "160", "30"),
    }
    for slug, needles in confirmed_counts.items():
        text = " ".join(str(by_slug[slug].get(k, "")) for k in
                        ("assets", "short", "descriptionHtml", "included", "features", "technical", "bundleContents"))
        check(not re.search(r"awaiting confirmation|await confirmation|count (?:is )?(?:un)?confirmed|total (?:asset|brush) count unconfirmed|to be confirmed|\btbc\b", text, re.I),
              f"{slug}: stale unconfirmed-count hedge reintroduced")
        for needle in needles:
            check(needle in text, f"{slug}: confirmed count {needle!r} missing (source: Payhip listing)")
    for slug in ("anime-soft-style-studio-kit", "anime-soft-style-brushes-100"):
        check("overlap" in by_slug[slug]["descriptionHtml"].lower(), f"{slug}: no overlap caveat")
    for slug in ("mindfulness-system-planner", "wellness-journal-2026"):
        check("personal use only" in by_slug[slug]["descriptionHtml"].lower(), f"{slug}: personal-use note lost")
    paid_palettes = (ROOT / "products/procreate-palettes-bundle-50/index.html").read_text(encoding="utf-8")
    check("Complete your order on Payhip and save the files to your iPad." in paid_palettes,
          "Paid palette installation describes a free download")

    ns = {"g": "http://base.google.com/ns/1.0"}
    pinterest_rows = load_csv(ROOT / "pinterest-feed.csv")
    check(len(pinterest_rows) == sum(not p.get("free") for p in products), "Pinterest paid product coverage changed")
    check(all("google_product_category" not in row for row in pinterest_rows), "Pinterest has blanket Google category")
    pin_xml = ET.parse(ROOT / "pinterest-feed.xml")
    check(not pin_xml.findall(".//g:google_product_category", ns), "Pinterest XML has blanket Google category")
    merchant = ET.parse(ROOT / "google-merchant-feed.xml")
    merchant_ids = {x.text for x in merchant.findall(".//g:id", ns)}
    check(not any(p["slug"] in merchant_ids for p in products if p.get("free")), "Free download sent to Merchant source")
    check("morocco-7-day-itinerary" not in merchant_ids, "PDF travel guide sent to common Merchant source")

    # Merchant categories must be reviewed per product and verified against the
    # official taxonomy subset: no blanket category, no unlisted node, and no
    # product silently shipped without one. Digital downloads belong under
    # Software > Digital Goods & Currency, not a physical art-supply node.
    reviewed = merchant_feed.load_categories()
    merchant_cats = {}
    for item in merchant.findall(".//item", ns):
        slug = item.findtext("g:id", namespaces=ns)
        value = item.findtext("g:google_product_category", namespaces=ns)
        check(value is not None, f"{slug}: no Google product category")
        merchant_cats[slug] = value
    check(len(set(merchant_cats.values())) > 1, "blanket Google category applied to the whole feed")
    check(len(merchant_cats) == len(merchant_ids), "Merchant category coverage differs from item count")
    for slug, value in merchant_cats.items():
        entry = reviewed.get(slug)
        check(entry is not None, f"{slug}: no reviewed category in data/merchant-categories.json")
        if entry:
            check(value == entry["id"], f"{slug}: feed category {value} != reviewed {entry['id']}")
            check(not entry["path"].startswith("Arts & Entertainment"),
                  f"{slug}: physical arts-and-crafts category used for a digital download")
            check(entry["reason"].strip(), f"{slug}: category has no recorded reason")

    if failures:
        print(f"FAILED: {len(failures)} of {checks} editorial checks")
        for failure in failures[:40]:
            print(" -", failure)
        return 1
    print(f"PASS: {checks} editorial checks across {len(products)} products; files, purchases and rankings not tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
