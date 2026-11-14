#!/usr/bin/env python3
"""Offline tests for Merchant/Pinterest feed metadata and safe fallbacks.

Run after ``python3 tools/build.py`` (or the standalone feed builds).
These checks do not contact Google or Pinterest, validate product rights or test checkout.
"""
from __future__ import annotations

import contextlib
import csv
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
                    and float(p.get("price") or 0) > 0 and not pages_misc._google_merchant_book(p)
                    and p.get("slug") not in merchant_feed.FEED_HOLDS}
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
                and float(p.get("price") or 0) > 0 and not pages_misc._google_merchant_book(p)
                and p.get("slug") not in merchant_feed.FEED_HOLDS}

    def test_every_item_carries_a_reviewed_verified_category(self):
        nodes = merchant_feed.load_taxonomy_nodes()
        reviewed = merchant_feed.load_categories()
        items = self._feed()
        # 2026-11-10: 44 -> 47 eligible feed items after the owner-sanctioned
        # addition of three $5 Christmas brush/stamp packs to the catalog
        # (Iq8D4, AwePR, 1vTuy). The 51->54 catalog change keeps pro-sketch-
        # traditional-art-kit on hold; the hold is unchanged.
        self.assertEqual(len(items), 47)
        seen = set()
        for row in items:
            slug = row.findtext("g:id", namespaces=NS)
            value = row.findtext("g:google_product_category", namespaces=NS)
            with self.subTest(slug=slug):
                self.assertIn(value, nodes, "category id is not a verified taxonomy node")
                self.assertEqual(value, reviewed[slug]["id"])
                seen.add(value)
        self.assertGreater(len(seen), 1, "a single blanket category would misclassify the catalogue")
        held = set(merchant_feed.FEED_HOLDS)
        self.assertLessEqual(held, set(reviewed),
                             "a hold must keep its reviewed category so it is ready to re-enable")
        self.assertEqual(set(reviewed) - held, {r.findtext("g:id", namespaces=NS) for r in items})

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
            record = json.dumps(catalog[slug]).lower()
            blob = re.sub(r"[^a-z0-9]+", "", record)
            for word, digit in (("one", 1), ("two", 2), ("three", 3), ("four", 4), ("five", 5),
                                ("six", 6), ("seven", 7), ("eight", 8), ("nine", 9), ("ten", 10),
                                ("eleven", 11), ("twelve", 12), ("fifteen", 15), ("twenty", 20),
                                ("thirty", 30), ("fifty", 50), ("hundred", 100)):
                if re.search(rf"\b{word}\b", record):
                    blob += str(digit)
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
        self.assertGreaterEqual(rich_hl, 18, f"only {rich_hl}/47 reach more than 4 highlights")
        self.assertGreaterEqual(rich_dt, 14, f"only {rich_dt}/47 reach more than 5 details")

    def test_highlights_do_not_restate_the_description(self):
        """A bullet may summarise the same fact, but must not repeat the prose.

        Google asks that highlights not repeat information already submitted in
        description or product_detail. Shared nouns are unavoidable when both
        describe one product, so the enforceable rule is: no bullet may appear
        word for word in the description, and no bullet may repeat another.
        """
        from merchant_description import select_description

        def normalise(text):
            return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

        catalog = self._catalog()
        for row in self._feed():
            slug = row.findtext("g:id", namespaces=NS)
            _, description = select_description(catalog[slug])
            prose = normalise(description)
            bullets = [normalise(node.text or "") for node in row.findall("g:product_highlight", NS)]
            with self.subTest(slug=slug):
                for bullet in bullets:
                    if len(bullet) > 12:
                        self.assertNotIn(bullet, prose, f"bullet repeats the description: {bullet!r}")
                self.assertEqual(len(bullets), len(set(bullets)), "duplicate bullet on one item")

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


class PinterestCategoryTests(unittest.TestCase):
    """Pinterest GPC values cover the paid catalog and match the taxonomy."""

    def test_every_paid_item_has_a_verified_category_in_csv_and_xml(self):
        products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
        paid = {p["slug"]: p for p in products if not p.get("free")}
        categories = merchant_feed.load_pinterest_categories()
        nodes = merchant_feed.load_taxonomy_nodes()
        with (ROOT / "pinterest-feed.csv").open(encoding="utf-8", newline="") as fh:
            csv_rows = list(csv.DictReader(fh))
        csv_by_id = {row.get("id"): row for row in csv_rows}
        xml_items = ET.parse(ROOT / "pinterest-feed.xml").findall("./channel/item")
        xml_by_id = {row.findtext("g:id", namespaces=NS): row for row in xml_items}

        self.assertEqual(set(csv_by_id), set(paid))
        self.assertEqual(set(xml_by_id), set(paid))
        self.assertEqual(set(categories), set(paid), "every paid Pinterest item needs one reviewed mapping")
        self.assertIn("google_product_category", csv_rows[0])
        self.assertGreater(len({row.get("google_product_category") for row in csv_rows}), 1,
                           "do not apply one blanket category to unlike products")
        for slug in paid:
            with self.subTest(slug=slug):
                expected = categories[slug]["id"]
                csv_value = csv_by_id[slug].get("google_product_category", "").strip()
                xml_values = xml_by_id[slug].findall("g:google_product_category", NS)
                self.assertEqual(csv_value, expected)
                self.assertIn(csv_value, nodes)
                self.assertEqual(len(xml_values), 1)
                self.assertEqual(xml_values[0].text, expected)
                self.assertEqual(xml_values[0].text, csv_value)
        self.assertEqual(categories["morocco-7-day-itinerary"]["id"], "543542")
        self.assertEqual(categories["procreate-portrait-masterclass-ebook"]["id"], "543542")

    def test_pinterest_category_extras_reject_bad_taxonomy_entries(self):
        nodes = merchant_feed.load_taxonomy_nodes()
        invalid_payloads = (
            {"categories": {"extra": {"id": "999999", "path": nodes["543542"], "reason": "reviewed"}}},
            {"categories": {"extra": {"id": "543542", "path": "Media > Books > Made Up", "reason": "reviewed"}}},
            {"categories": {"extra": {"id": "543542", "path": nodes["543542"], "reason": ""}}},
            {"categories": {"portrait-skin-brushes-procreate": {
                "id": "543542", "path": nodes["543542"], "reason": "duplicate mapping"}}},
        )
        for payload in invalid_payloads:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                json.dump(payload, fh)
                tmp = Path(fh.name)
            try:
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    merchant_feed.load_pinterest_categories(tmp)
            finally:
                tmp.unlink()


class FeedHoldTests(unittest.TestCase):
    """Products paused from the Google feed must be deliberate and documented.

    Any hold in merchant_feed.FEED_HOLDS is buyer-protective: it keeps a
    known-broken deliverable away from Google until the owner resolves it.
    A hold without an audit reference is a silent editorial choice and fails.
    """

    def test_holds_are_audit_referenced_and_excluded(self):
        items = self._feed()
        ids = {row.findtext("g:id", namespaces=NS) for row in items}
        for slug, why in merchant_feed.FEED_HOLDS.items():
            self.assertNotIn(slug, ids, f"held product {slug} still appears in the feed")
            self.assertGreaterEqual(len(why.split()), 8,
                                    f"hold for {slug} lacks a documented reason")
            self.assertRegex(why, r"(?i)(audit|merchant|feed|zip|archive|cover|verif)",
                             f"hold for {slug} does not cite the blocker")

    def test_held_product_keeps_its_pdp(self):
        """The hold is a feed pause, not a delisting: organic page must exist."""
        for slug in merchant_feed.FEED_HOLDS:
            pdp = ROOT / "products" / slug / "index.html"
            self.assertTrue(pdp.is_file(), f"held product {slug} lost its landing page")

    def test_feed_carries_no_internal_audit_language(self):
        xml = (ROOT / "google-merchant-feed.xml").read_text(encoding="utf-8")
        # Tight list on purpose. Highlight caveats on unconfirmed-count
        # products ("exactly confirmed in the text listing" style) are the
        # owner-approved transitional state from PR #77, tracked as register
        # item D; they are not re-introduced by this test's mercy. The phrases
        # banned here are audit-workroom language in ALL cases.
        banned = (
            "owner verification", "owner verify", "owner to confirm", "need owner",
            "unverified", " audit ", "internal note", "do not ship",
            "awaiting confirmation", "to be confirmed",
        )
        low = xml.lower()
        for phrase in banned:
            self.assertNotIn(phrase, low, f"internal audit language leaked into the feed: {phrase!r}")

    @staticmethod
    def _feed():
        return ET.parse(ROOT / "google-merchant-feed.xml").findall("./channel/item")


if __name__ == "__main__":
    unittest.main(verbosity=2)
