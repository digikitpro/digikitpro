#!/usr/bin/env python3
"""
DigiKitPro - SEO engine
=======================

Generates the search-facing copy for products in `data/products.json`:

  * `keywords`     comma separated keyword string (export / reference)
  * `tags`         keyword list, this is what the site actually consumes
  * `seoTitle`     page <title>, capped at 60 characters
  * `seoDesc`      meta description, capped at 158 characters
  * `short`        product page blurb and card alt text
  * `alt`          descriptive image alt text

Why `tags` matters more than it looks: the builder reads it in three places.
`tools/core.py` writes it to each card's `data-tags` attribute (frontend search
and filtering), `tools/pages_category.py` uses it to decide which products
belong on a category hub, and `tools/pages_misc.py` folds it into the search
index. A product with empty tags is invisible to all three.

Design rules
------------
1. Deterministic and offline. No API key, no network, no model call. The same
   product always produces the same copy, so CI runs are reproducible and the
   daily Payhip sync can call this unattended without new secrets.
2. Hand-written copy is never overwritten. A field is only filled when it is
   missing, empty, or still holds a value this engine or `payhip_sync.py`
   generated earlier. Products marked `"auto": true` are machine owned, so
   those are regenerated freely.
3. Copy stays plain. No em dashes, no filler adjectives, no invented claims.
   Only facts already present on the product record are used.

Usage
-----
    python3 tools/seo_engine.py                 # fill gaps on auto products
    python3 tools/seo_engine.py --all           # fill gaps on every product
    python3 tools/seo_engine.py --all --dry-run # report only, write nothing
    python3 tools/seo_engine.py --check         # exit 1 if anything is missing

Called automatically by `tools/payhip_sync.py` for every new product it adds.
"""
import argparse
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "products.json")
BRAND = "DigiKitPro"

# Limits are tuned to the house style already present in data/products.json
# (titles run to 70 characters and always keep the "| DigiKitPro" suffix,
# descriptions to 165) rather than to generic SEO advice, so generated copy
# matches the hand-written records around it.
TITLE_MAX = 70
DESC_MAX = 165
SHORT_MAX = 155
ALT_MAX = 110
KEYWORD_MAX = 14

# Value payhip_sync.py falls back to when Payhip sends no description.
FALLBACK_BLURB = "Digital download from DigiKitPro."

# payhip_sync.py defaults the `assets` field to one of these when Payhip gives
# nothing specific. They describe delivery, not contents, so treating them as a
# real description of the product produces copy like "Instant digital download
# for Procreate on iPad" and adds junk keywords such as "instant".
BOILERPLATE_ASSETS = {
    "instant digital download",
    "digital download",
    "instant download",
    "download",
}


def real_assets(assets):
    """Return the assets string only when it says something about the contents."""
    a = clean(assets)
    return "" if a.lower() in BOILERPLATE_ASSETS else a

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into",
    "is", "it", "its", "of", "on", "or", "pack", "set", "that", "the", "this",
    "to", "with", "you", "your", "premium", "professional", "pro", "best",
    "new", "free", "buy", "download", "digital", "product", "collection",
}

# Category seed keywords. Order matters: earlier terms are treated as stronger
# signals and survive the cap when the keyword list is trimmed.
CATEGORY_KEYWORDS = {
    "Skin Texture": ["skin texture", "pores", "freckles", "wrinkles", "blemishes",
                     "realistic skin", "skin brushes", "blending", "portrait"],
    "Portrait": ["portrait", "face", "realistic portrait", "skin", "blending",
                 "portrait brushes", "painting"],
    "Line Art": ["line art", "liner", "inking", "ink", "linework", "comic",
                 "marker", "clean lines", "illustration"],
    "Sketching": ["sketching", "pencil", "graphite", "charcoal", "sketch",
                  "traditional media", "shading"],
    "Watercolor": ["watercolor", "watercolour", "wash", "bleeds", "granulation",
                   "paper texture", "wet media"],
    "Anime": ["anime", "manga", "chibi", "cel shading", "soft style",
              "anime brushes", "character art"],
    "Hair": ["hair", "hair strands", "flyaways", "hairstyle", "hair brushes",
             "strands", "detail"],
    "Glitter & Effects": ["glitter", "sparkle", "shine", "effects", "light effects",
                          "texture", "overlay"],
    "Traditional": ["traditional media", "chalk", "charcoal", "texture",
                    "hand drawn", "traditional art"],
    "Figure Drawing": ["figure drawing", "pose", "anatomy", "gesture",
                       "figure study", "body"],
    "Bundles": ["bundle", "mega bundle", "collection", "value pack",
                "brush bundle", "library"],
    "Guides & eBooks": ["ebook", "guide", "course", "tutorial", "learn",
                        "masterclass", "workflow"],
    "Other": ["procreate", "brushes", "textures", "digital art", "ipad"],
}

# One plain sentence of real benefit per category. Used to build descriptions.
CATEGORY_BENEFIT = {
    "Skin Texture": "Realistic pores, freckles and wrinkles for believable portraits.",
    "Portrait": "Paint believable faces with natural skin, hair and lighting.",
    "Line Art": "Crisp inking and clean linework for comics and illustration.",
    "Sketching": "Pencil, charcoal and graphite textures for natural sketches.",
    "Watercolor": "Soft washes, bleeds and granulation with real paper texture.",
    "Anime": "Cel shading, soft gradients and clean anime styling.",
    "Hair": "Strand by strand detail, flyaways and polished hairstyles.",
    "Glitter & Effects": "Sparkle, shine and light effects that layer over any artwork.",
    "Traditional": "Traditional media textures that keep a hand drawn feel.",
    "Figure Drawing": "Poses, gesture and anatomy for confident figure work.",
    "Bundles": "A full collection of brushes and textures at one low price.",
    "Guides & eBooks": "Step by step guidance you can read on any device.",
    "Other": "Extra tools and textures for everyday Procreate work.",
}

# Always useful, appended last so real product terms win the cap.
GENERIC_KEYWORDS = ["procreate", "procreate brushes", "ipad", "digital art", "brush set"]

CATEGORIES = list(CATEGORY_KEYWORDS)


# ── text helpers ─────────────────────────────────────────────────────────────

def plain_text(src):
    """Strip HTML tags and collapse whitespace to a single flat string."""
    if not src:
        return ""
    txt = re.sub(r"(?is)<(script|style).*?</\1>", " ", str(src))
    txt = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h[1-6]>", " ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def clean(s):
    """Trim, flatten whitespace, and strip trailing punctuation."""
    s = plain_text(s)
    return s.strip().strip(" ,;:.").strip()


def dedupe(items):
    """Order preserving dedupe, case insensitive on the stripped value."""
    seen, out = set(), []
    for it in items:
        it = clean(it)
        if not it:
            continue
        key = it.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def fit(text, limit, ellipsis=True):
    """Trim to `limit` characters, cutting at a word boundary."""
    text = clean(text)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rindex(" ")]
    cut = cut.rstrip(" ,;:.")
    return cut + ("\u2026" if ellipsis else "")


def first_sentence(text, limit=140):
    """First sentence of a block, trimmed to `limit` characters."""
    text = clean(text)
    if not text:
        return ""
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return fit(m.group(1) if m else text, limit)


def tokenize(text):
    """Lowercase word tokens with stopwords and noise removed."""
    words = re.findall(r"[a-z][a-z&-]{1,}", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


# ── field generators ─────────────────────────────────────────────────────────

def gen_keywords(name, category, desc="", assets="", extra=None):
    """Build the keyword list for a product, strongest signals first."""
    cat = category if category in CATEGORY_KEYWORDS else "Other"

    # 1. Category seeds, but only those genuinely supported by the product text.
    _assets = real_assets(assets)
    hay = " ".join([name or "", _assets, desc or ""]).lower()
    matched = [k for k in CATEGORY_KEYWORDS[cat] if k.lower() in hay]

    # 2. Meaningful words straight out of the product name.
    name_terms = tokenize(name)[:6]

    # 3. Terms from the assets line, e.g. "19 professional brushes".
    asset_terms = tokenize(_assets)[:3]

    # 4. A handful of descriptive words from the description body.
    desc_terms = []
    for w in tokenize(desc):
        if w in ("procreate", "brush", "brushes", "ipad", "texture", "textures"):
            continue
        if w not in desc_terms:
            desc_terms.append(w)
        if len(desc_terms) >= 4:
            break

    ordered = dedupe(
        list(extra or [])
        + matched
        + name_terms
        + asset_terms
        + [cat.lower()]
        + desc_terms
        + GENERIC_KEYWORDS
    )
    return ordered[:KEYWORD_MAX]


def gen_seo_title(name, category, desc=""):
    """Page title.

    The "| DigiKitPro" suffix is kept whenever possible because every hand
    written record in the catalogue has it. Only an extremely long product name
    gets trimmed, and the brand still survives the trim.
    """
    name = clean(name)
    branded = f"{name} | {BRAND}"
    if len(branded) <= TITLE_MAX:
        return branded
    budget = TITLE_MAX - len(BRAND) - 3          # room for " | " plus brand
    return f"{fit(name, budget, ellipsis=False)} | {BRAND}"


def gen_short(name, category, desc="", assets=""):
    """Product page blurb. Doubles as card alt text via tools/core.py."""
    cat = category if category in CATEGORY_KEYWORDS else "Other"
    name = clean(name)
    benefit = CATEGORY_BENEFIT[cat]

    _assets = real_assets(assets)
    if _assets:
        text = f"{name} gives you {_assets.lower()}. {benefit}"
    else:
        text = f"{name}. {benefit}"

    # A real first sentence from the seller beats our boilerplate.
    real = first_sentence(desc, 120)
    if real and len(real) > 40:
        text = f"{name}: {real}"
    return fit(text, SHORT_MAX)


def gen_seo_desc(name, category, desc="", assets="", price_text="", free=False):
    """Meta description, capped at 158 characters."""
    cat = category if category in CATEGORY_KEYWORDS else "Other"
    name = clean(name)
    benefit = CATEGORY_BENEFIT[cat]
    what = real_assets(assets) or f"{cat} brushes"

    tail = "Free instant download." if free else (
        f"Instant download, {price_text}." if price_text else "Instant digital download."
    )
    # Reserve room for the price and call to action first: a truncated price
    # reads worse than a trimmed benefit sentence.
    budget = DESC_MAX - len(tail) - 1
    for cand in (
        f"{name}: {what} for Procreate on iPad. {benefit}",
        f"{name}: {what} for Procreate on iPad.",
        f"{name}: {what} for Procreate.",
        f"{name}: {what}.",
        f"{name}.",
    ):
        if len(cand) <= budget:
            return f"{cand} {tail}"
    return f"{fit(f'{name}: {what}', budget, ellipsis=False)}. {tail}"


def gen_alt(name, category, desc=""):
    """Image alt text. Descriptive, no keyword stuffing."""
    cat = category if category in CATEGORY_KEYWORDS else "Other"
    text = f"{clean(name)} for Procreate, {CATEGORY_BENEFIT[cat].rstrip('.').lower()}"
    return fit(text, ALT_MAX)


# ── record level API ─────────────────────────────────────────────────────────

def should_fill(p, field, force=False):
    """True when a field is safe to (re)generate.

    Hand-written copy is protected: for a product that is not auto synced we
    only step in when the field is empty or still holds a generated placeholder.
    """
    if force:
        return True
    v = p.get(field)
    if v in (None, "", [], {}):
        return True
    # Products added by payhip_sync.py are machine owned.
    if p.get("auto"):
        return True
    name = clean(p.get("name", ""))
    if field == "seoTitle" and clean(v) == f"{name} | {BRAND}":
        return True
    if field in ("seoDesc", "short") and clean(v) == FALLBACK_BLURB.rstrip("."):
        return True
    return False


def enrich_product(p, force=False):
    """Fill every SEO field that is safe to fill. Returns list of changed fields."""
    name = clean(p.get("name", ""))
    category = p.get("category") or "Other"
    desc = plain_text(p.get("descriptionHtml") or "")
    assets = clean(p.get("assets") or "")
    price_text = clean(p.get("priceText") or "")
    free = bool(p.get("free"))

    changed = []

    if should_fill(p, "tags", force):
        kws = gen_keywords(name, category, desc, assets,
                           extra=list(p.get("tags") or []))
        if kws and list(p.get("tags") or []) != kws:
            p["tags"] = kws
            changed.append("tags")

    if should_fill(p, "keywords", force) or not p.get("keywords"):
        kws = p.get("tags") or gen_keywords(name, category, desc, assets)
        val = ", ".join(kws)
        if val and p.get("keywords") != val:
            p["keywords"] = val
            changed.append("keywords")

    if should_fill(p, "seoTitle", force):
        val = gen_seo_title(name, category, desc)
        if val and p.get("seoTitle") != val:
            p["seoTitle"] = val
            changed.append("seoTitle")

    if should_fill(p, "seoDesc", force):
        val = gen_seo_desc(name, category, desc, assets, price_text, free)
        if val and p.get("seoDesc") != val:
            p["seoDesc"] = val
            changed.append("seoDesc")

    if should_fill(p, "short", force):
        val = gen_short(name, category, desc, assets)
        if val and p.get("short") != val:
            p["short"] = val
            changed.append("short")

    if should_fill(p, "alt", force):
        val = gen_alt(name, category, desc)
        if val and p.get("alt") != val:
            p["alt"] = val
            changed.append("alt")

    return changed


def missing_fields(p):
    """Fields that are empty and would be filled by a run."""
    gaps = []
    for f in ("tags", "keywords", "seoTitle", "seoDesc", "short", "alt"):
        if not p.get(f):
            gaps.append(f)
    return gaps


# ── CLI ──────────────────────────────────────────────────────────────────────

def load():
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


def save(products):
    with open(DATA, "w", encoding="utf-8") as fh:
        json.dump(products, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser(description="Generate SEO copy for DigiKitPro products.")
    ap.add_argument("--all", action="store_true",
                    help="fill gaps on every product, not just auto synced ones")
    ap.add_argument("--force", action="store_true",
                    help="regenerate fields even when they already hold copy")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any product is missing SEO fields")
    args = ap.parse_args()

    products = load()

    if args.check:
        bad = [(p.get("slug") or p.get("id"), missing_fields(p))
               for p in products if missing_fields(p)]
        for slug, gaps in bad:
            print(f"  missing {', '.join(gaps)}: {slug}")
        if bad:
            print(f"{len(bad)} product(s) missing SEO fields")
            return 1
        print(f"all {len(products)} products have complete SEO fields")
        return 0

    touched = 0
    fields = 0
    for p in products:
        if not args.all and not p.get("auto"):
            continue
        changed = enrich_product(p, force=args.force)
        if changed:
            touched += 1
            fields += len(changed)
            print(f"  {p.get('slug') or p.get('id')}: {', '.join(changed)}")

    mode = "dry run" if args.dry_run else "updated"
    print(f"SEO engine: {touched} product(s), {fields} field(s) {mode}.")
    if not args.dry_run and touched:
        save(products)
        print(f"wrote {os.path.relpath(DATA, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
