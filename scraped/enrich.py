#!/usr/bin/env python3
"""Merge scraped store data + hand-authored enrichment -> /home/user/data/products.json"""
import json, re, os, sys, html as htmlmod
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slugs import SLUGS
from enrich_data_a import A
from enrich_data_b import B

ENRICH = {**A, **B}
CAT = json.load(open("catalog.json"))
MANIFEST = json.load(open("imgmanifest.json"))

PLANNER_IDS = {"LmOr8","bUHGy","Q2UdG","0RGu9","PwLIh","sv2ud","plxDu"}
PALETTE_IDS = {"CK2LX","BmFdZ"}

def clean_name(n):
    n = htmlmod.unescape(n or "")
    n = re.sub(r"\s+", " ", n).strip()
    return n

def _norm(t):
    return t.replace("\u2019", "'").replace("\u2018", "'").strip()

def _bullet_clean(t):
    return re.sub(r"^[\u2700-\u27BF\U0001F381\U0001F449\u2022\u25CF\u25A0\u2013\u2014\u2794\u2B50\-\*\s\uFE0F]+", "", t).strip()

BULLET_START = tuple("\u2700\u2701\u2702\u2703\u2704\u2705\u2706\u2707\u2708\u2709\u2713\u2714\u2B50\u279C\u2022\u25CF\u25A0\u2013\u2014\ufe0f\u2794-*)>▶︎✔⭐✅🎁")

def extract_sections(html):
    """Line-based zone extraction from store copy: {included[], features[], requirements[]}."""
    res = {"included": [], "features": [], "requirements": []}
    if not html: return res
    soup = BeautifulSoup(html, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    lines = []
    for el in soup.find_all(["h1","h2","h3","h4","h5","p","li"]):
        for ln in el.get_text("", strip=False).split("\n"):
            ln = re.sub(r"\s+", " ", ln).strip()
            if ln: lines.append((ln, el.name == "li"))
    zone = None
    for raw, is_li in lines:
        txt = _norm(raw); low = txt.lower()
        if len(txt) < 130:
            if re.search(r"(what'?s|whats|what is)\s*(included|inside)|included in (your|the)|what you (will )?(get|receive)|here'?s what makes|(files?|contents)( included| include)?:?$|formats? included", low):
                zone = "included"; continue
            if re.search(r"^(⭐ )?key features:?$|^(why|game[- ]?changer|must[- ]?have|benefits)", low):
                zone = "features"; continue
            if re.search(r"^(requirements?|compatible with|what you.?ll need|you will need)", low):
                zone = "requirements"; continue
            if re.search(r"^(perfect for|technical|note|important|faq|how to|ideal for|tips|installation|terms|>>|who)", low) or re.match(r"^[\d]+\.\s", low):
                zone = None; continue
        if zone and len(txt) < 300:
            looks_bullet = is_li or raw.lstrip().startswith(BULLET_START) or (zone == "included" and len(txt) < 160) or (zone != "included" and len(txt) < 140)
            if looks_bullet:
                t = _bullet_clean(raw).lstrip("*").strip()
                if 2 < len(t) and t not in res[zone] and not re.search(r"click|add to cart|buy now", t, re.I):
                    res[zone].append(t)
    for k in res:
        res[k] = res[k][:14]
    return res

def clean_marketing_ctas(html):
    """Remove 'Click Add to Cart' style paragraphs (Payhip-specific CTAs)."""
    if not html: return html
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.find_all(["p","h2","h3"]):
        t = _norm(el.get_text(" ", strip=True)).lower()
        if re.search(r"click [\"']?(add to cart|buy now|download now)", t) or t.startswith("\U0001F449"):
            el.decompose()
    return soup.decode_contents()

def extract_included(html):
    return extract_sections(html)["included"]

def image_block(manifest_entry):
    imgs = manifest_entry.get("images", [])
    if not imgs: return None
    main = imgs[0]
    return {
        "card": f"{main['base']}-card.webp" if "-card" in main["variants"] else f"{main['base']}.webp",
        "main": f"{main['base']}.webp",
        "mainW": main["variants"]["-full" if "-full" in main["variants"] else "" ]["w"] if main["variants"].get("-full") or main["variants"].get("") else None,
        "cardW": main["variants"].get("-card", {}).get("w"),
        "cardH": main["variants"].get("-card", {}).get("h"),
        "fullW": main["variants"].get("-full", main["variants"].get("", {})).get("w"),
        "fullH": main["variants"].get("-full", main["variants"].get("", {})).get("h"),
        "gallery": [
            {"file": f"{im['base']}.webp",
             "card": f"{im['base']}-card.webp" if "-card" in im["variants"] else f"{im['base']}.webp",
             "w": im["variants"].get("-full", im["variants"].get("", {})).get("w"),
             "h": im["variants"].get("-full", im["variants"].get("", {})).get("h"),
             "cardW": im["variants"].get("-card", {}).get("w"),
             "cardH": im["variants"].get("-card", {}).get("h")}
            for im in imgs[1:]
        ],
    }

STORE_FAQ = [
  {"q": "How will I receive my files?",
   "a": "Immediately after checkout on Payhip you are redirected to a download page, and you also receive an automated email with a permanent download link."},
  {"q": "What is the refund policy?",
   "a": "Due to the nature of digital products, all sales are final once files are downloaded. If you run into any technical issue, contact DigiKitPro and it will be resolved."},
]

out = []
order = list(SLUGS.keys())
for pid in order:
    if pid not in CAT: continue
    cat = CAT[pid]
    en = ENRICH.get(pid, {})
    slug = SLUGS[pid]
    name = en.get("name") or clean_name(cat.get("name"))
    price = float(cat.get("price") or 0)
    free = bool(en.get("free")) or price == 0
    files = [re.sub(r"\s+", " ", f).strip() for f in cat.get("files", []) if f.strip()]

    # technical details
    if pid in PLANNER_IDS: fmt = "Hyperlinked PDF"
    elif pid in PALETTE_IDS: fmt = ".swatches (Procreate color palettes)"
    elif pid in ("SWUCM","oKdcU"): fmt = "PNG (300 DPI)" if pid=="SWUCM" else "PNG illustrations & patterns"
    elif pid == "jFL0I": fmt = "Editable Canva templates"
    elif pid == "BG7ob": fmt = "PDF travel guide"
    else: fmt = ".brushset (Procreate)"
    technical = [f"Format: {fmt}"]
    if en.get("assets"): technical.append(f"Contents: {en['assets']}")
    if files: technical.append("Download: " + " + ".join(files))
    technical.append("Delivery: Instant digital download via Payhip")
    if pid not in PLANNER_IDS and pid not in PALETTE_IDS and pid not in ("SWUCM","oKdcU","jFL0I","BG7ob"):
        technical.append("Designed for Apple Pencil pressure & tilt")

    # requirements
    if pid in ("Q2UdG","PwLIh"):
        req = ["iPad or tablet with a PDF annotation app (GoodNotes, Notability or similar)", "Digital download — no physical item ships"]
    elif pid in PLANNER_IDS:
        req = ["A tablet or computer with a PDF annotation/note-taking app", "Digital download — no physical item ships"]
    elif pid == "BG7ob":
        req = ["Any device with a PDF reader", "Digital download — no physical item ships"]
    elif pid == "jFL0I":
        req = ["A free Canva account to edit templates", "Digital download — no physical item ships"]
    elif pid in ("SWUCM","oKdcU"):
        req = ["Any design software that opens PNG files", "Digital download — no physical item ships"]
    elif pid in PALETTE_IDS:
        req = ["iPad with the Procreate app", "Digital download — no physical item ships"]
    else:
        req = ["iPad with the Procreate app (not compatible with Photoshop or other apps)", "Apple Pencil recommended for pressure & tilt control", "Digital download — no physical item ships"]

    sections = extract_sections(cat.get("descriptionHtml"))
    included = en.get("included") or sections["included"]
    EXTRA_INCLUDED = {
      "procreate-mega-bundle-650": [
        "24 complete Procreate brush sets in one mega kit",
        "650+ brushes plus paper textures made for iPad",
        "Brush sets covering every style in the DigiKitPro catalog at release",
        "Installation guide included on the product page",
      ],
      "illustration-brushes-2": [
        "15 authentic textured illustration brushes",
        "5 beautiful Procreate color palettes",
        "Pressure-sensitive brushes suited to hand lettering",
        "Instant .zip download",
      ],
    }
    EXTRA_INCLUDED.setdefault("ultimate-fitness-planner", [
        "Personalized goal-setting pages",
        "Workout schedules and progress trackers",
        "Meal planning pages",
        "Habit trackers",
        "Self-care reminders",
      ])
    if not included and slug in EXTRA_INCLUDED:
        included = EXTRA_INCLUDED[slug]
    if not en.get("features") and sections["features"]:
        en = {**en, "features": sections["features"]}
    if sections["requirements"] and pid not in PLANNER_IDS:
        req = sections["requirements"][:8]
    compat_q = "an iPad with the Procreate app" if pid not in PLANNER_IDS|PALETTE_IDS and pid not in {"SWUCM","oKdcU","jFL0I","BG7ob"} else "the app or software listed in the requirements above"
    faqs = [{"q": f"What do I need to use this product?",
             "a": f"You need {compat_q}. Full requirements are listed above on this page."}] + STORE_FAQ

    rec = {
        "id": pid,
        "name": name,
        "slug": slug,
        "category": en.get("category", "Other"),
        "price": price,
        "priceText": "Free" if free else f"${price:0.2f}",
        "currency": "USD",
        "free": free,
        "badge": en.get("badge") or ("Free" if free else ("Bundle" if en.get("category")=="Bundles" else None)),
        "assets": en.get("assets"),
        "short": en.get("short", ""),
        "descriptionHtml": clean_marketing_ctas(cat.get("descriptionHtml", "")),
        "included": included,
        "features": en.get("features", []),
        "technical": technical,
        "requirements": req,
        "perfectFor": en.get("perfectFor", []),
        "bundleContents": en.get("bundleContents"),
        "faqs": faqs,
        "tags": en.get("tags", []),
        "related": en.get("related", []),
        "payhipUrl": cat["payhipUrl"],
        "images": image_block(MANIFEST.get(pid, {})),
        "seoTitle": en.get("seoTitle") or f"{name} | DigiKitPro",
        "seoDesc": (en.get("seoDesc") or en.get("short",""))[:160],
        "featured": en.get("featured", 0),
        "alt": f"{name} — product preview artwork",
    }
    out.append(rec)

os.makedirs("/home/user/data", exist_ok=True)
json.dump(out, open("/home/user/data/products.json","w",encoding="utf-8"), indent=1, ensure_ascii=False)
missing_img = [r["slug"] for r in out if not r["images"]]
missing_short = [r["slug"] for r in out if not r["short"]]
missing_inc = [r["slug"] for r in out if not r["included"]]
print("products:", len(out))
print("missing images:", missing_img)
print("missing short:", missing_short)
print("missing included:", missing_inc)
print("free:", [r["slug"] for r in out if r["free"]])
print("bundles:", [r["slug"] for r in out if r["category"]=="Bundles"])
