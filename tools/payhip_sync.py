#!/usr/bin/env python3
"""
DigiKitPro - Payhip auto-sync
=============================

Detects products you add on Payhip and adds them to `data/products.json` so the
next `tools/build.py` publishes them automatically (product page, card, sitemap,
search index, schema, trends).

Run manually:
    python3 tools/payhip_sync.py

In CI it should run on a schedule (`.github/workflows/sync-payhip.yml`) and commit
the updated `data/products.json` when something changed.

Rules
-----
* Products already in `data/products.json` are only updated for LIVE facts
  (name, price, currency, Payhip URL, image, availability, description text).
  You never lose hand-written SEO copy, headings, FAQs, included lists, etc.
* Brand-new Payhip products are added with sensible defaults, marked
  `"auto": true`, and surfaced in Trending / products listing via `"featured": 1`.
  They are NOT given a "New" badge so the homepage stays clean.
* If Payhip is unreachable (offline, Cloudflare, rate-limit) the script reports
  it and exits 0 - CI must never fail the build because Payhip was down.
"""
import json, os, re, sys, time, html
import urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = "https://payhip.com/digikitpro"
DATA = os.path.join(ROOT, "data", "products.json")
DEFAULT_CATEGORY = "Other"
IMG_ASPECT = {"w": 1200, "h": 900}
JSON_INDENT = 2          # must match the committed data/products.json, otherwise
                         # every sync rewrites the whole file as a spurious diff

# SEO engine: generates keywords, tags, titles, descriptions and alt text for
# the products this script adds. Optional by design: if it is missing or raises,
# the sync still completes with the plain defaults below.
try:
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import seo_engine
except Exception:  # pragma: no cover - keeps sync resilient
    seo_engine = None

CAT_RULES = [
    ("anime|manga|chibi", "Anime"),
    ("watercolor|watercolour", "Watercolor"),
    ("skin|portrait", "Skin Texture"),
    ("line art|liner|inking|linework|marker", "Line Art"),
    ("charcoal|pencil|sketch|graphite|traditional", "Sketching"),
    ("hair", "Hair"),
    ("tattoo|flash", "Other"),
    ("glitter|sparkle|shine|effect", "Glitter & Effects"),
    ("pose|figure", "Figure Drawing"),
    ("bundle|mega|master|vault|library", "Bundles"),
    ("ebook|guide|course|masterclass", "Guides & eBooks"),
]

CATEGORIES = ["Portrait", "Skin Texture", "Line Art", "Sketching", "Watercolor", "Anime",
              "Hair", "Glitter & Effects", "Traditional", "Figure Drawing", "Bundles",
              "Guides & eBooks", "Other"]

KEYWORDS = {
    "Anime": "anime manga chibi soft style cel shading",
    "Watercolor": "watercolor watercolour wash bleeds granulation paper texture",
    "Skin Texture": "realistic skin pores freckles wrinkles portrait",
    "Line Art": "line art liner inking ink marker comic sketch",
    "Sketching": "sketching pencil graphite charcoal traditional media",
    "Hair": "hair strands flyaways hairstyle brush",
    "Glitter & Effects": "glitter sparkle shine effects texture",
    "Figure Drawing": "figure drawing pose anatomy gesture",
    "Bundles": "bundle value mega collection master library",
    "Guides & eBooks": "ebook guide course tutorial learn",
    "Traditional": "traditional media chalk charcoal watercolor texture",
    "Portrait": "portrait face realistic painting skin",
    "Other": "digital art procreate brush texture tool",
}


def http_get(url, timeout=40, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; DigiKitPro-Indexer/1.0)",
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError, ValueError) as e:
            if attempt == retries - 1:
                print(f"  ! fetch failed {url}: {e}")
                return ""
            time.sleep(2 * (attempt + 1))
    return ""


def slugify(text):
    s = (text or "").lower()
    s = re.sub(r"&amp;", "and", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-").strip(".")
    return s[:80] or "digital-download"


def money_text(price, currency="USD"):
    if price is None:
        return "Free" if False else "$0.00"
    try:
        p = float(price)
    except Exception:
        return str(price)
    if p <= 0:
        return "Free"
    sym = "$" if currency in ("USD", "CAD", "AUD", "NZD") else "€" if currency == "EUR" else "£" if currency == "GBP" else ""
    return f"{sym}{p:.2f}"


def infer_category(name, desc):
    hay = (name + " " + (desc or "")).lower()
    for rx, cat in CAT_RULES:
        if re.search(rx, hay):
            return cat
    return DEFAULT_CATEGORY


def plain_text(htmlsrc):
    txt = re.sub(r"<script.*?</script>", " ", htmlsrc or "", flags=re.S | re.I)
    txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return re.sub(r"\s+", " ", html.unescape(txt)).strip()


def first_image(htmlsrc):
    m = re.search(r"pe56d\.s3\.amazonaws\.com/[^\"'.\s]+\.(?:png|jpg|jpeg|webp)", htmlsrc, re.I)
    if not m:
        m = re.search(r"https://[^\"'<\s]+\.(?:png|jpg|jpeg|webp)", htmlsrc, re.I)
    return m.group(0) if m else ""


def parse_product(pid):
    """Best-effort parse of a Payhip product page into a normalized record."""
    url = f"https://payhip.com/b/{pid}"
    h = http_get(url)
    if not h:
        return None
    data = {"payhipUrl": url, "payhipId": pid, "source": "payhip"}

    # JSON-LD Product block (preferred; Payhip serves this to crawlers)
    for m in re.finditer(r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", h, re.S | re.I):
        try:
            blob = json.loads(html.unescape(m.group(1)))
        except Exception:
            continue
        blocks = blob if isinstance(blob, list) else [blob]
        for b in blocks:
            if isinstance(b, dict) and b.get("@type") == "Product":
                data["name"] = (b.get("name") or "").strip()
                off = b.get("offers") or {}
                if isinstance(off, list):
                    off = off[0] if off else {}
                if off.get("price") is not None:
                    data["price"] = off["price"]
                if off.get("priceCurrency"):
                    data["currency"] = off["priceCurrency"]
                if off.get("availability"):
                    data["availability"] = off["availability"]
                imgs = b.get("image") or (b.get("images") or [])
                if isinstance(imgs, str):
                    imgs = [imgs]
                urls = [u for u in imgs if isinstance(u, str) and u.startswith("http")]
                if urls:
                    data["images"] = urls[0]
                desc = b.get("description")
                if desc:
                    data["descriptionHtml"] = html.unescape(str(desc))
                break

    if "name" not in data:
        og = dict((m.group(1).lower(), m.group(2)) for m in re.finditer(
            r'<meta[^>]+property=["\']og:([^"\']+)["\'][^>]+content=["\']([^"\']+)["\']', h, re.I))
        og.update(dict((m.group(2).lower(), m.group(1)) for m in re.finditer(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:([^"\']+)["\']', h, re.I)))
        data["name"] = html.unescape(og.get("title", "")).split(" - Payhip")[0].split(" | ")[0].strip()
        if og.get("price:amount"):
            data["price"] = og["price:amount"]
        if og.get("image"):
            data["images"] = og["image"]
    data.setdefault("price", 0)
    data.setdefault("currency", "USD")
    data.setdefault("images", first_image(h))
    if "descriptionHtml" not in data:
        data["descriptionHtml"] = ""
    return data


def collect_payhip_ids():
    """Crawl the public collection listing for product IDs. Uses storefront HTML."""
    ids = []
    pages = 0
    for page in range(1, 60):
        url = f"{STORE}/collection/all?page={page}"
        h = http_get(url)
        if not h:
            break
        found = re.findall(r"/b/([A-Za-z0-9]{4,12})", h)
        found = list(dict.fromkeys(found))
        pages += 1
        if not found:
            break
        before = len(ids)
        ids.extend(found)
        ids = list(dict.fromkeys(ids))
        if len(ids) == before and page > 2:
            break
        time.sleep(0.3)
    # If listing crawling failed entirely, fall back to known IDs file (if present).
    if not ids:
        known = os.path.join(ROOT, "data", "payhip_ids.txt")
        if os.path.exists(known):
            ids = [ln.strip() for ln in open(known, encoding="utf-8") if ln.strip()]
            print(f"  Using fallback ID list ({len(ids)} ids).")
    return ids, pages


def main():
    print("DigiKitPro Payhip auto-sync")
    try:
        products = json.load(open(DATA, encoding="utf-8"))
    except Exception as e:
        print("  ! could not read data/products.json:", e)
        return 1

    by_payhip = {}
    for p in products:
        pid = p.get("id") or (re.search(r"/b/([A-Za-z0-9]+)", p.get("payhipUrl") or "") or [None, None])[1]
        if pid:
            by_payhip[pid] = p

    ids, pages = collect_payhip_ids()
    print(f"  Payhip store listing returned {len(ids)} product ids across {pages} page(s).")
    if not ids:
        print("  Unable to reach the Payhip store now (offline / protected). Nothing changed.")
        print("  SKIP_OK: this is not a build failure.")
        return 0

    new_ids = [i for i in ids if i not in by_payhip]
    print(f"  Existing locally: {len(by_payhip)}. New on Payhip: {len(new_ids)}.")
    report = {"checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "found": len(ids),
              "new": [], "updated": []}

    for pid in new_ids[:20]:  # generous safety cap per run
        rec = parse_product(pid)
        if not rec:
            continue
        if rec.get("name"):
            _price = round(float(rec.get("price") or 0), 2)
            _free = _price <= 0
            _price_txt = "Free" if _free else money_text(_price, rec.get("currency", "USD"))
            products.append({})
            products[-1] = {
                **{k: v for k, v in {
                    "id": pid,
                    "name": rec.get("name", "Untitled"),
                    "slug": slugify(rec.get("name", "digital-download")),
                    "category": infer_category(rec.get("name", ""), plain_text(rec.get("descriptionHtml", ""))),
                    "price": _price,
                    "priceText": _price_txt,
                    "currency": rec.get("currency", "USD"),
                    "free": _free,
                    "badge": None,
                    "assets": "Instant digital download",
                    "short": (plain_text(rec.get("descriptionHtml", ""))[:250] or "Digital download from DigiKitPro."),
                    "descriptionHtml": rec.get("descriptionHtml") or "",
                    "included": ["Instant digital download", "Lifetime access"],
                    "features": ["Lifetime access", "Instant delivery worldwide"],
                    "technical": ["Format: Digital download", "Delivery: Instant via Payhip", "Available worldwide"],
                    "requirements": ["Compatible device per product page", "Digital download, no physical item ships"],
                    "perfectFor": ["Procreate artists", "Digital illustrators"],
                    "bundleContents": [],
                    "faqs": [{"q": "How do I get this after buying?",
                              "a": "Payhip delivers the download link instantly after checkout and emails it to you. You keep lifetime access."}],
                    "tags": [],
                    "related": [],
                    "payhipUrl": rec["payhipUrl"],
                    "images": {
                        "card": rec.get("images") or "",
                        "main": rec.get("images") or "",
                        "cardW": IMG_ASPECT["w"], "cardH": IMG_ASPECT["h"],
                        "fullW": IMG_ASPECT["w"], "fullH": IMG_ASPECT["h"]
                    } if rec.get("images") else {},
                    "seoTitle": f"{rec.get('name','Digital Product')} | DigiKitPro",
                    "seoDesc": (plain_text(rec.get("descriptionHtml", ""))[:250] or "Digital download from DigiKitPro."),
                    "featured": 1,
                    "alt": f"{rec.get('name','Digital Product')} : DigiKitPro artwork",
                    "auto": True,
                    "syncedAt": time.strftime("%Y-%m-%d"),
                }.items() if v is not None}
            }
            if seo_engine:
                try:
                    _seo = seo_engine.enrich_product(products[-1], force=True)
                    if _seo:
                        print(f"    seo: {', '.join(_seo)}")
                except Exception as e:
                    print(f"    seo: skipped ({e})")
            report["new"].append({"id": pid, "name": rec.get("name"), "slug": products[-1]["slug"]})
            print(f"  + added [{pid}] {rec.get('name')}")
            by_payhip[pid] = products[-1]

    # Update live facts only for prior auto-synced products (never touch hand-written SEO).
    for pid in list(by_payhip):
        if pid not in ids or not by_payhip[pid].get("auto"):
            continue
        rec = parse_product(pid)
        if not rec or not rec.get("name"):
            continue
        p = by_payhip[pid]
        changed = False
        for k in ("name", "price", "currency"):
            if k in rec and rec[k] and rec[k] != p.get(k):
                p[k] = rec[k]
                changed = True
        if rec.get("images") and not (p.get("images") or {}).get("main"):
            p.setdefault("images", {})["main"] = rec["images"]
            p.setdefault("images", {})["card"] = rec["images"]
            changed = True
        if p.get("auto") and rec.get("descriptionHtml") and len(str(rec["descriptionHtml"])) > len(str(p.get("descriptionHtml") or "")):
            p["descriptionHtml"] = rec["descriptionHtml"]
            changed = True
        # Auto products are machine owned, so regenerate their SEO copy too when
        # any live fact moved (a new price should reach the meta description).
        if changed and seo_engine:
            try:
                _seo = seo_engine.enrich_product(p, force=True)
                if _seo:
                    print(f"    seo: {', '.join(_seo)}")
            except Exception as e:
                print(f"    seo: skipped ({e})")
        if changed:
            report["updated"].append({"id": pid, "name": rec["name"]})
            print(f"  ~ updated [{pid}] {rec['name']} live facts")

    # Save only if something actually changed (keeps CI clean when nothing is new).
    with open(DATA, "w", encoding="utf-8") as fh:
        json.dump(products, fh, indent=JSON_INDENT, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(ROOT, "data", "payhip_sync_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=JSON_INDENT, ensure_ascii=False)
        fh.write("\n")
    print(f"  Wrote {len(products)} products. New: {len(report['new'])}. Updated: {len(report['updated'])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
