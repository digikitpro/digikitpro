#!/usr/bin/env python3
"""Google Merchant description formatting with explicit text provenance.

The manifest records hashes and verified origins of specific catalog fields.
Unknown or changed text retains the previous plain-description behavior and
is reported to the owner; it is never silently claimed to be AI-generated.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/merchant-ai-provenance.json"
AI_SOURCE = "trained_algorithmic_media"
TRACKED_FIELDS = {"short", "seoDesc"}
ORIGINS = {"ai", "non_ai"}


def text_hash(text: str) -> str:
    """Digest exactly the stripped UTF-8 text submitted to Merchant Center."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def load_provenance(path: Path = MANIFEST) -> dict[str, dict[str, dict[str, str]]]:
    """Load and validate known text fingerprints and origins; fail on corruption."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("products"), dict):
        raise ValueError("Invalid Merchant description provenance manifest")
    for slug, fields in data["products"].items():
        if not isinstance(slug, str) or not slug or not isinstance(fields, dict) or not fields:
            raise ValueError(f"Invalid Merchant provenance entry: {slug!r}")
        for field, record in fields.items():
            if (field not in TRACKED_FIELDS or not isinstance(record, dict)
                    or set(record) != {"source", "sha256"} or not isinstance(record.get("source"), str)
                    or record["source"] not in ORIGINS or not isinstance(record.get("sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"])):
                raise ValueError(f"Invalid Merchant provenance fingerprint: {slug}/{field}")
    return data["products"]


def select_description(product: dict) -> tuple[str, str]:
    """Use the same short/SEO/name fallback order as the existing feed."""
    for field in ("short", "seoDesc", "name"):
        if product.get(field):
            return field, str(product[field]).strip()
    raise ValueError(f"Product {product.get('slug', '<unknown>')} has no description")


def render_description(product: dict, provenance: dict[str, dict[str, dict[str, str]]]) -> tuple[str, str]:
    """Return XML and the verified origin (ai, non_ai, or unknown).

    For missing or stale provenance, keep the former plain field to avoid
    removing existing/new products from the feed. The caller must warn so the
    owner can confirm the source and update the manifest where appropriate.
    """
    field, text = select_description(product)
    record = provenance.get(product.get("slug", ""), {}).get(field)
    origin = record["source"] if record and text_hash(text) == record["sha256"] else "unknown"
    escaped = html.escape(text, quote=True)
    if origin == "ai":
        return ("    <g:structured_description>\n"
                f"      <g:digital_source_type>{AI_SOURCE}</g:digital_source_type>\n"
                f"      <g:content>{escaped}</g:content>\n"
                "    </g:structured_description>"), origin
    return f"    <g:description>{escaped}</g:description>", origin
