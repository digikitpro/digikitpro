#!/usr/bin/env python3
"""Offline tests for Merchant feed description provenance and safe fallbacks.

Run after ``python3 tools/build.py`` (or the standalone Merchant feed build).
These checks do not contact Google, validate product rights or test checkout.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import merchant_feed
import pages_misc
from merchant_description import AI_SOURCE, load_provenance, render_description, select_description, text_hash

ROOT = Path(__file__).resolve().parent.parent
NS = {"g": "http://base.google.com/ns/1.0"}


def parse_fragment(fragment: str) -> ET.Element:
    return ET.fromstring(f'<item xmlns:g="{NS["g"]}">{fragment}</item>')


class MerchantDescriptionTests(unittest.TestCase):
    def test_known_ai_text_is_structured_and_xml_escaped(self):
        product = {"slug": "known", "short": '  Ink & "color" <detail> × café  '}
        provenance = {"known": {"short": {"source": "ai", "sha256": text_hash(product["short"])}}}
        fragment, origin = render_description(product, provenance)
        item = parse_fragment(fragment)
        self.assertEqual(origin, "ai")
        self.assertIsNone(item.find("g:description", NS))
        self.assertEqual(item.findtext("g:structured_description/g:digital_source_type", namespaces=NS), AI_SOURCE)
        self.assertEqual(item.findtext("g:structured_description/g:content", namespaces=NS), 'Ink & "color" <detail> × café')

    def test_changed_or_unlisted_text_keeps_plain_field_without_false_ai_claim(self):
        original = {"slug": "known", "short": "Original text"}
        provenance = {"known": {"short": {"source": "ai", "sha256": text_hash(original["short"])}}}
        for product in ({"slug": "known", "short": "Edited & revised"},
                        {"slug": "new", "short": "Original text"}):
            with self.subTest(product=product):
                fragment, origin = render_description(product, provenance)
                item = parse_fragment(fragment)
                self.assertEqual(origin, "unknown")
                self.assertEqual(item.findtext("g:description", namespaces=NS), product["short"])
                self.assertIsNone(item.find("g:structured_description", NS))

    def test_verified_non_ai_stays_plain_without_unknown_warning(self):
        product = {"slug": "verified", "name": "Verified", "short": "Written without generative AI",
                   "price": 7, "currency": "USD", "free": False, "category": "Other", "images": {}}
        provenance = {"verified": {"short": {"source": "non_ai", "sha256": text_hash(product["short"])}}}
        output = io.StringIO()
        with patch.object(pages_misc, "PRODUCTS", [product]), \
                patch.object(pages_misc, "load_provenance", return_value=provenance), \
                patch.object(pages_misc, "write") as write, contextlib.redirect_stdout(output):
            pages_misc.build_google_merchant_feed()
        item = ET.fromstring(write.call_args.args[1]).find("./channel/item")
        self.assertEqual(item.findtext("g:description", namespaces=NS), product["short"])
        self.assertIsNone(item.find("g:structured_description", NS))
        # A provenance warning would wrongly claim unknown AI origin; the
        # separate "no reviewed category" warning is expected for this synthetic
        # product and is checked in MerchantEnrichmentTests.
        self.assertNotIn("description provenance", output.getvalue())

    def test_fallback_origin_is_matched_to_its_actual_field(self):
        provenance = {"known": {"short": {"source": "ai", "sha256": text_hash("Same text")},
                                "seoDesc": {"source": "ai", "sha256": text_hash("SEO text")}}}
        fallback = {"slug": "known", "short": "", "seoDesc": "SEO text", "name": "Name"}
        self.assertEqual(render_description(fallback, provenance)[1], "ai")
        fallback["seoDesc"] = "Same text"
        self.assertEqual(render_description(fallback, provenance)[1], "unknown")
        self.assertEqual(select_description({"name": "Name"}), ("name", "Name"))
        with self.assertRaises(ValueError):
            select_description({})

    def test_manifest_rejects_bad_version_and_fingerprints(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            for invalid in ([], {"version": 2, "products": {}},
                            {"version": 1, "products": {"x": {"short": "bad"}}},
                            {"version": 1, "products": {"x": {"short": {"source": "ai", "sha256": "bad"}}}},
                            {"version": 1, "products": {"x": {"short": {"source": "guess", "sha256": "a" * 64}}}},
                            {"version": 1, "products": {"x": {"short": {"source": [], "sha256": "a" * 64}}}},
                            {"version": 1, "products": {"x": {"name": {"source": "ai", "sha256": "a" * 64}}}}):
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    load_provenance(path)
            path.write_text(json.dumps({"version": 1, "products": {}}), encoding="utf-8")
            self.assertEqual(load_provenance(path), {})

    def test_new_unknown_product_is_not_dropped_and_produces_warning(self):
        product = {"slug": "future-product", "name": "Future Product", "short": "New & unverified origin",
                   "price": 7, "currency": "USD", "free": False, "category": "Other", "images": {}}
        output = io.StringIO()
        with patch.object(pages_misc, "PRODUCTS", [product]), patch.object(pages_misc, "write") as write, \
                patch.dict(pages_misc.os.environ, {"GITHUB_ACTIONS": "true"}), contextlib.redirect_stdout(output):
            pages_misc.build_google_merchant_feed()
        path, xml = write.call_args.args
        self.assertEqual(path, "google-merchant-feed.xml")
        item = ET.fromstring(xml).find("./channel/item")
        self.assertEqual(item.findtext("g:id", namespaces=NS), "future-product")
        self.assertEqual(item.findtext("g:description", namespaces=NS), "New & unverified origin")
        self.assertIsNone(item.find("g:structured_description", NS))
        self.assertIn("WARNING", output.getvalue())
        self.assertIn("future-product", output.getvalue())
        self.assertIn("::warning title=Merchant description provenance::", output.getvalue())

    def test_bad_provenance_does_not_overwrite_the_feed(self):
        with patch.object(pages_misc, "load_provenance", side_effect=ValueError("bad manifest")), \
                patch.object(pages_misc, "write") as write:
            with self.assertRaises(ValueError):
                pages_misc.build_google_merchant_feed()
        write.assert_not_called()

    def test_generated_feed_matches_catalog_and_recorded_provenance(self):
        products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
        eligible = {p["slug"]: p for p in products if not p.get("comingSoon") and not p.get("free")
                    and float(p.get("price") or 0) > 0 and not pages_misc._google_merchant_book(p)}
        manifest = load_provenance()
        titles = merchant_feed.load_titles()
        items = ET.parse(ROOT / "google-merchant-feed.xml").findall("./channel/item")
        ids = [row.findtext("g:id", namespaces=NS) for row in items]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(eligible))
        self.assertTrue(manifest, "Known AI provenance should not be empty")
        for row in items:
            slug = row.findtext("g:id", namespaces=NS)
            product = eligible[slug]
            with self.subTest(slug=slug):
                field, text = select_description(product)
                self.assertTrue(text, "Description must not be empty")
                self.assertLessEqual(len(text), 5000)
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                record = manifest.get(slug, {}).get(field, {})
                known_ai = record.get("source") == "ai" and record.get("sha256") == digest
                actual_plain, actual_structured = row.findall("g:description", NS), row.findall("g:structured_description", NS)
                self.assertEqual(len(actual_plain) + len(actual_structured), 1)
                if known_ai:
                    self.assertEqual(len(actual_structured[0].findall("g:digital_source_type", NS)), 1)
                    self.assertEqual(len(actual_structured[0].findall("g:content", NS)), 1)
                    self.assertEqual(row.findtext("g:structured_description/g:digital_source_type", namespaces=NS), AI_SOURCE)
                    self.assertEqual(row.findtext("g:structured_description/g:content", namespaces=NS), text)
                else:
                    self.assertEqual(row.findtext("g:description", namespaces=NS), text)
                self.assertEqual(row.findtext("g:title", namespaces=NS),
                                 merchant_feed.title_for(product, titles))
                self.assertEqual(row.findtext("g:price", namespaces=NS),
                                 f"{float(product['price']):.2f} {product.get('currency', 'USD').upper()}")
                self.assertEqual(row.findtext("g:link", namespaces=NS), f"{pages_misc.SITE_URL}/products/{slug}/")
                self.assertTrue(row.findtext("g:image_link", namespaces=NS))
                self.assertEqual(row.findtext("g:availability", namespaces=NS), "in_stock")


class MerchantEnrichmentTests(unittest.TestCase):
    """The reviewed category/title data and the fields derived from it."""

    @staticmethod
    def _feed():
        return ET.parse(ROOT / "google-merchant-feed.xml").findall("./channel/item")

    @staticmethod
    def _catalog():
        products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
        return {p["slug"]: p for p in products if not p.get("comingSoon") and not p.get("free")
                and float(p.get("price") or 0) > 0 and not pages_misc._google_merchant_book(p)}

    def test_every_item_carries_a_reviewed_verified_category(self):
        nodes = merchant_feed.load_taxonomy_nodes()
        reviewed = merchant_feed.load_categories()
        items = self._feed()
        self.assertEqual(len(items), 45)
        seen = set()
        for row in items:
            slug = row.findtext("g:id", namespaces=NS)
            value = row.findtext("g:google_product_category", namespaces=NS)
            with self.subTest(slug=slug):
                self.assertIn(value, nodes, "category id is not a verified taxonomy node")
                self.assertEqual(value, reviewed[slug]["id"])
                seen.add(value)
        self.assertGreater(len(seen), 1, "a single blanket category would misclassify the catalogue")
        self.assertEqual(set(reviewed), {r.findtext("g:id", namespaces=NS) for r in items})

    def test_highlights_and_details_stay_inside_google_limits(self):
        for row in self._feed():
            slug = row.findtext("g:id", namespaces=NS)
            highlights = row.findall("g:product_highlight", NS)
            details = row.findall("g:product_detail", NS)
            with self.subTest(slug=slug):
                self.assertLessEqual(len(highlights), 10)
                self.assertTrue(highlights, "Google expects at least one highlight")
                for node in highlights:
                    text = (node.text or "").strip()
                    self.assertTrue(text)
                    self.assertLessEqual(len(text), 150)
                    self.assertNotRegex(text, r"(?i)awaiting confirmation|\blisted$")
                self.assertLessEqual(len(details), 8)
                for node in details:
                    name = (node.findtext("g:attribute_name", namespaces=NS) or "").strip()
                    value = (node.findtext("g:attribute_value", namespaces=NS) or "").strip()
                    self.assertTrue(name and value, "empty product_detail row")

    def test_titles_never_claim_anything_the_record_does_not_state(self):
        catalog = self._catalog()
        banned = re.compile(r"(?i)\b(?:best|cheapest|sale|discount|buy now|limited time|% off)\b")
        for row in self._feed():
            slug = row.findtext("g:id", namespaces=NS)
            title = row.findtext("g:title", namespaces=NS)
            blob = re.sub(r"[^a-z0-9]+", "", json.dumps(catalog[slug]).lower())
            with self.subTest(slug=slug):
                self.assertLessEqual(len(title), 150)
                self.assertIsNone(banned.search(title), f"promotional wording in title: {title!r}")
                for number in re.findall(r"\d[\d,]*", title):
                    self.assertIn(number.replace(",", ""), blob,
                                  f"title number {number} is not backed by the product record")

    def test_labels_segment_priority_and_price(self):
        catalog = self._catalog()
        for row in self._feed():
            slug = row.findtext("g:id", namespaces=NS)
            price = float(catalog[slug]["price"])
            with self.subTest(slug=slug):
                self.assertEqual(row.findtext("g:custom_label_2", namespaces=NS),
                                 "price_under_10" if price < 10 else "price_10_plus")
                self.assertEqual(row.findtext("g:custom_label_3", namespaces=NS) == "priority_cluster",
                                 slug in merchant_feed.PRIORITY)
                self.assertTrue(row.findtext("g:custom_label_0", namespaces=NS))


    def test_rich_product_description_coverage(self):
        """Google asks for >4 highlights and >5 details; both must keep improving."""
        items = self._feed()
        highlights = [len(r.findall("g:product_highlight", NS)) for r in items]
        details = [len(r.findall("g:product_detail", NS)) for r in items]
        # Hard floor: the specification itself requires at least 2 highlights.
        self.assertGreaterEqual(min(highlights), 2)
        self.assertGreaterEqual(min(details), 4)
        rich_hl = sum(1 for n in highlights if n > 4)
        rich_dt = sum(1 for n in details if n > 5)
        self.assertGreaterEqual(rich_hl, 18, f"only {rich_hl}/45 reach more than 4 highlights")
        self.assertGreaterEqual(rich_dt, 14, f"only {rich_dt}/45 reach more than 5 details")

    def test_highlights_do_not_restate_the_description(self):
        from merchant_description import select_description
        catalog = self._catalog()
        for row in self._feed():
            slug = row.findtext("g:id", namespaces=NS)
            _, description = select_description(catalog[slug])
            desc_words = {w for w in re.findall(r"[a-z0-9]+", description.lower()) if len(w) > 2}
            for node in row.findall("g:product_highlight", NS):
                words = {w for w in re.findall(r"[a-z0-9]+", (node.text or "").lower()) if len(w) > 2}
                if not words:
                    continue
                with self.subTest(slug=slug, highlight=node.text):
                    overlap = len(words & desc_words) / len(words)
                    self.assertLess(overlap, 0.95, f"highlight restates description: {node.text!r}")

    def test_category_loader_rejects_unverified_entries(self):
        nodes = merchant_feed.load_taxonomy_nodes()
        good = json.loads((ROOT / "data/merchant-categories.json").read_text(encoding="utf-8"))
        bad_id = {"categories": {"x": {"class": "procreate_brushes", "id": "999999",
                                       "path": nodes["500046"], "reason": "r"}}}
        bad_path = {"categories": {"x": {"class": "procreate_brushes", "id": "500046",
                                         "path": "Arts & Entertainment > Made Up", "reason": "r"}}}
        bad_class = {"categories": {"x": {"class": "mystery", "id": "500046",
                                          "path": nodes["500046"], "reason": "r"}}}
        for payload in (bad_id, bad_path, bad_class):
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                json.dump(payload, fh)
                tmp = Path(fh.name)
            with self.subTest(payload=list(payload["categories"]["x"].items())[:2]):
                with self.assertRaises(ValueError):
                    merchant_feed.load_categories(tmp, nodes)
                tmp.unlink()
        self.assertEqual(len(merchant_feed.load_categories(ROOT / "data/merchant-categories.json", nodes)),
                         len(good["categories"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
