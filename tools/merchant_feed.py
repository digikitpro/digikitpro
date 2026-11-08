#!/usr/bin/env python3
"""Google Merchant feed enrichment from reviewed, per-product data.

Every value emitted from here traces back to a product's own record in
``data/products.json`` plus one of two reviewed mapping files:

* ``data/merchant-categories.json`` — one Google product category per product,
  chosen by hand and checked against the official 2021-09-21 taxonomy.
  Google's taxonomy has no "digital brush" node, so downloadable creative
  assets use ``Software > Digital Goods & Currency`` (Digital Artwork /
  Document Templates) rather than the physical art-supply categories a
  default classifier tends to pick. There is deliberately no blanket
  catalogue-wide category: a product missing from the map gets no category
  and a build warning instead of a guess.
* ``data/merchant-titles.json`` — feed titles that differ from ``name``.
  Only attributes already present in that product's record are added, and
  every number in a title is verified against the record.

Highlights, detail rows and reporting labels are derived from the existing
``features`` / ``technical`` / ``requirements`` fields. Nothing is invented,
no GTIN or MPN is synthesised, and no price, URL or availability is touched.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ROOT / "data/merchant-categories.json"
TITLES = ROOT / "data/merchant-titles.json"
TAXONOMY_NODES = ROOT / "data/google-taxonomy-nodes.json"

HIGHLIGHT_MAX_CHARS = 150      # Google's per-highlight limit
HIGHLIGHT_MAX_COUNT = 10       # Google's per-item limit
DETAIL_MAX_COUNT = 8

# Human-readable names for the product classes used in the category map.
# These feed [product_type], which Google uses for its own grouping/reporting.
CLASS_LABELS = {
    "procreate_brushes": "Procreate Brushes & Stamps",
    "procreate_palettes": "Procreate Colour Palettes",
    "digital_art_assets": "Digital Art & Pattern Assets",
    "digital_planner": "Digital Planners & Journals",
    "canva_templates": "Editable Canva Templates",
}

# The owner's declared priority cluster: portrait + library + bundle value.
PRIORITY = (
    "portrait-skin-brushes-procreate",
    "portrait-mastery-kit-46-brushes",
    "ultimate-portrait-mastery-bundle",
    "master-library-2000-brushes",
    "brush-palette-bundle-160",
    "procreate-mega-bundle-650",
)

# Technical keys that are safe, buyer-relevant [product_detail] rows.
DETAIL_KEYS = {
    "Format": "Format",
    "Contents": "Contents",
    "Download": "File size",
    "Delivery": "Delivery",
}

_HEDGE = re.compile(r"\b(?:awaiting confirmation|to be confirmed|tbc)\b", re.I)


def _read(path: Path, key: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get(key), dict):
        raise ValueError(f"{path.name}: expected an object under {key!r}")
    return data[key]


def load_taxonomy_nodes(path: Path = TAXONOMY_NODES) -> dict[str, str]:
    """Official taxonomy id -> full path, vendored so QA can run offline."""
    return _read(path, "nodes")


def load_categories(path: Path = CATEGORIES, nodes: dict[str, str] | None = None) -> dict[str, dict]:
    """Reviewed category per product; fails loudly on an unverifiable entry.

    An entry is only accepted when its id exists in the vendored taxonomy
    subset, the stored path matches that node exactly, and the class is known.
    """
    nodes = load_taxonomy_nodes() if nodes is None else nodes
    out: dict[str, dict] = {}
    for slug, entry in _read(path, "categories").items():
        if not isinstance(entry, dict):
            raise ValueError(f"merchant category for {slug!r} is not an object")
        node_id = str(entry.get("id", "")).strip()
        path_text = str(entry.get("path", "")).strip()
        cls = str(entry.get("class", "")).strip()
        if node_id not in nodes:
            raise ValueError(f"merchant category for {slug!r}: id {node_id!r} is not a verified taxonomy node")
        if nodes[node_id] != path_text:
            raise ValueError(f"merchant category for {slug!r}: path does not match taxonomy node {node_id}")
        if cls not in CLASS_LABELS:
            raise ValueError(f"merchant category for {slug!r}: unknown class {cls!r}")
        out[slug] = {"id": node_id, "path": path_text, "class": cls,
                     "reason": str(entry.get("reason", "")).strip()}
    return out


def load_titles(path: Path = TITLES) -> dict[str, str]:
    return {slug: str(entry["title"]).strip()
            for slug, entry in _read(path, "titles").items()
            if isinstance(entry, dict) and str(entry.get("title", "")).strip()}


def category_for(slug: str, categories: dict[str, dict]) -> dict | None:
    return categories.get(slug)


def title_for(product: dict, titles: dict[str, str]) -> str:
    """Reviewed feed title, else the catalogue name (never a generated rewrite)."""
    return titles.get(product["slug"]) or product["name"]


def product_type(product: dict, categories: dict[str, dict], brand: str = "DigiKitPro") -> str:
    """Brand > product class > internal category, for Google's own grouping."""
    category = categories.get(product["slug"])
    parts = [brand]
    if category:
        parts.append(CLASS_LABELS[category["class"]])
    if product.get("category"):
        parts.append(str(product["category"]))
    return " > ".join(p for p in parts if p)


def _clean_highlight(text: str) -> str:
    """Trim editorial hedge wording so a highlight reads like a feature."""
    text = re.sub(r"\s+", " ", str(text)).strip().rstrip(".")
    text = re.sub(r"\s+(?:listed|described)$", "", text, flags=re.I)
    return text[:1].upper() + text[1:] if text else text


def _compatibility_line(product: dict) -> str | None:
    """A precise compatibility bullet, only when the record already states it."""
    requirements = " ".join(str(r) for r in (product.get("requirements") or []))
    low = requirements.lower()
    if "procreate" in low and "ipad" in low:
        return "For iPad with the Procreate app"
    if "goodnotes" in low:
        return "Opens in GoodNotes and other PDF annotation apps"
    if "canva" in low:
        return "Requires a Canva account to edit the templates"
    return None


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def highlights(product: dict) -> list[str]:
    """[product_highlight] bullets: existing feature text, cleaned and capped.

    A feature that only restates a bullet already present (e.g. the generated
    "For Procreate on iPad" against the compatibility line) is dropped rather
    than repeated on the listing.
    """
    out: list[str] = []
    seen_words: list[set[str]] = []
    compat = _compatibility_line(product)
    if compat:
        out.append(compat)
        seen_words.append(_words(compat))
    for raw in (product.get("features") or []):
        text = _clean_highlight(raw)
        if not text or len(text) > HIGHLIGHT_MAX_CHARS or _HEDGE.search(text):
            continue
        words = _words(text)
        if not words:
            continue
        if any(words <= previous or previous <= words for previous in seen_words):
            continue
        out.append(text)
        seen_words.append(words)
    return out[:HIGHLIGHT_MAX_COUNT]


def details(product: dict) -> list[tuple[str, str]]:
    """[product_detail] rows parsed from the record's own technical lines."""
    rows: list[tuple[str, str]] = []
    for line in (product.get("technical") or []):
        line = str(line)
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key in DETAIL_KEYS and value and not _HEDGE.search(value):
            rows.append((DETAIL_KEYS[key], value))
    requires = [str(r).strip() for r in (product.get("requirements") or []) if str(r).strip()]
    if requires and len(requires[0]) <= HIGHLIGHT_MAX_CHARS:
        rows.append(("Requires", requires[0]))
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for name, value in rows:
        if name.lower() not in seen:
            seen.add(name.lower())
            unique.append((name, value))
    return unique[:DETAIL_MAX_COUNT]


def custom_labels(product: dict, categories: dict[str, dict]) -> dict[str, str]:
    """Segment labels so performance can be read by class, price and priority."""
    labels: dict[str, str] = {}
    category = categories.get(product["slug"])
    if category:
        labels["custom_label_0"] = category["class"]
    if product.get("category"):
        labels["custom_label_1"] = re.sub(r"[^a-z0-9]+", "_", str(product["category"]).lower()).strip("_")
    price = float(product.get("price") or 0)
    labels["custom_label_2"] = "price_under_10" if price < 10 else "price_10_plus"
    if product["slug"] in PRIORITY:
        labels["custom_label_3"] = "priority_cluster"
    return labels
