#!/usr/bin/env python3
"""Offline regression checks for buyer-guide navigation and accuracy.

Run after ``python3 tools/build.py``. These tests inspect generated pages;
passing does not verify Payhip checkout, product archives, ownership, or prices.
"""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from core import SITE_URL
from pages_guides import GUIDE_DEFS

ROOT = Path(__file__).resolve().parent.parent
TEST_ORIGIN = SITE_URL


def clean(value):
    return " ".join(value.split())


class Page(HTMLParser):
    """Collect link labels, visible guide FAQs, JSON-LD, and visible text."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.faqs = []
        self.schemas = []
        self.text = []
        self._link = None
        self._faq = None
        self._summary = False
        self._answer = False
        self._script = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href") is not None:
            self._link = [a["href"], ""]
        if tag == "details" and {"faq-item", "faq-q"} & set(a.get("class", "").split()):
            self._faq = {"q": "", "a": ""}
        elif self._faq is not None and tag == "summary":
            self._summary = True
        elif self._faq is not None and tag == "div" and "faq-body" in a.get("class", "").split():
            self._answer = True
        if tag == "script":
            self._script = {"json": a.get("type", "").lower() == "application/ld+json", "text": ""}

    def handle_data(self, data):
        if self._script is not None:
            self._script["text"] += data
            return
        self.text.append(data)
        if self._link is not None:
            self._link[1] += data
        if self._faq is not None:
            if self._summary:
                self._faq["q"] += data
            if self._answer:
                self._faq["a"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._link is not None:
            self.links.append((self._link[0], clean(self._link[1])))
            self._link = None
        if tag == "summary":
            self._summary = False
        elif tag == "div" and self._answer:
            self._answer = False
        elif tag == "details" and self._faq is not None:
            self.faqs.append((clean(self._faq["q"]), clean(self._faq["a"])))
            self._faq = None
        if tag == "script" and self._script is not None:
            if self._script["json"]:
                self.schemas.append(json.loads(self._script["text"]))
            self._script = None

    def links_named(self, label):
        return [href for href, text in self.links if text == label]


def load_page(relative_path):
    return Page((ROOT / relative_path).read_text(encoding="utf-8"))


def resolved_path(page_path, href):
    target = urlsplit(urljoin(TEST_ORIGIN + page_path, href))
    origin = urlsplit(TEST_ORIGIN)
    if (target.scheme.lower(), target.netloc.lower()) != (origin.scheme.lower(), origin.netloc.lower()):
        return None
    return target.path


class GuideAccuracyTests(unittest.TestCase):
    def assert_built_destination(self, path):
        relative = path.lstrip("/")
        target = ROOT / relative
        if path.endswith("/"):
            target /= "index.html"
        self.assertTrue(target.is_file(), f"Missing built destination for {path}")

    def test_all_guides_link_to_the_guide_index_not_themselves(self):
        for guide in GUIDE_DEFS:
            slug = guide["slug"]
            with self.subTest(guide=slug):
                page = load_page(f"guides/{slug}/index.html")
                hrefs = page.links_named("All buyer guides →")
                self.assertEqual(len(hrefs), 1)
                destination = resolved_path(f"/guides/{slug}/", hrefs[0])
                self.assertEqual(destination, "/guides/")
                self.assert_built_destination(destination)

    def test_catalog_free_portrait_guide_topic_goes_to_the_pdf_product(self):
        page = load_page("products.html")
        hrefs = page.links_named("Free portrait guide")
        self.assertEqual(len(hrefs), 1)
        destination = resolved_path("/products.html", hrefs[0])
        self.assertEqual(destination, "/products/procreate-starter-guide-free-ebook/")
        self.assert_built_destination(destination)

    def test_animation_notice_links_to_a_real_resource_not_a_phantom_signup(self):
        page = load_page("guides/procreate-animation-brushes/index.html")
        hrefs = page.links_named("Explore free resources →")
        self.assertEqual(len(hrefs), 1)
        destination = resolved_path("/guides/procreate-animation-brushes/", hrefs[0])
        self.assertEqual(destination, "/freebies.html")
        self.assert_built_destination(destination)
        self.assertFalse(urlsplit(hrefs[0]).fragment)
        visible = clean(" ".join(page.text)).lower()
        self.assertNotIn("mailing list below", visible)
        self.assertNotIn("get new procreate tool drops by email", visible)
        self.assertNotIn("if they hold up across your test shot, the paid kits will too", visible)

    def test_changed_faq_schema_matches_the_visible_questions_and_answers(self):
        filenames = [f"guides/{g['slug']}/index.html" for g in GUIDE_DEFS] + ["faq.html"]
        for filename in filenames:
            with self.subTest(page=filename):
                page = load_page(filename)
                schemas = [s for s in page.schemas if isinstance(s, dict) and s.get("@type") == "FAQPage"]
                self.assertEqual(len(schemas), 1)
                structured = [
                    (clean(q["name"]), clean(q["acceptedAnswer"]["text"]))
                    for q in schemas[0]["mainEntity"]
                ]
                self.assertTrue(page.faqs, f"No visible FAQs found on {filename}")
                self.assertEqual(page.faqs, structured)

    def test_guide_comparisons_are_catalog_snapshots_not_checkout_guarantees(self):
        for name in ("procreate-starter-kits", "procreate-bundles-compared"):
            with self.subTest(guide=name):
                page = load_page(f"guides/{name}/index.html")
                text = clean(" ".join(page.text)).lower()
                self.assertIn("prices shown reflect our catalog", text)
                self.assertIn("confirm the current total on payhip", text)
                for claim in (
                    "live store prices",
                    "the price shown is what payhip charges today",
                    "every product page lists exactly what is inside",
                    "every product below exists at exactly the price shown",
                    "whole-catalog libraries",
                ):
                    self.assertNotIn(claim, text)

    def test_beginner_guide_does_not_prescribe_a_purchase_order(self):
        page = load_page("guides/procreate-starter-kits/index.html")
        text = clean(" ".join(page.text)).lower()
        for claim in ("step 1 · start free", "step 2 · one $5 kit", "step 3 · only", "top rung of the bundle ladder"):
            self.assertNotIn(claim, text)
        self.assertIn("no paid purchase is required", text)

    def test_named_unverified_device_and_authorship_claims_are_not_reintroduced(self):
        banned = {
            "category/portrait/index.html": ("hand-crafted procreate portrait brushes", "tuned for the apple pencil with realistic pressure response"),
            "category/skin-texture/index.html": ("hand-tested for lifelike", "built specifically to work with procreate blending modes and apple pencil tilt"),
            "category/sketching/index.html": ("respond accurately to apple pencil tilt and pressure",),
            "guides/procreate-pencil-brushes/index.html": ("the sketching kits are tuned for pressure and tilt",),
            "faq.html": ("brushes are calibrated for apple pencil pressure and tilt",),
        }
        for filename, claims in banned.items():
            text = (ROOT / filename).read_text(encoding="utf-8").lower()
            for claim in claims:
                with self.subTest(page=filename, claim=claim):
                    self.assertNotIn(claim, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
