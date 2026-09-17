#!/usr/bin/env python3
"""Commercial-intent buyer-guide landing pages (Phase 3 — organic traffic).

The /blog articles answer technique questions ("how do I paint skin").
The /guides pages answer shopping questions ("which procreate pencil
brushes", "which bundle should I buy"), using only the real catalog:
explicit tag-derived product selections, live prices, honest trade-offs
and a clear buying order (free first, one matched $5 kit, library when
you outgrow it).

Rules this module lives by:
  - Selections are explicit slug lists, chosen from the data/discovery.json
    tags (craft / improve / level / style / stage). The build FAILS LOUDLY
    when a referenced slug disappears, so a Payhip sync can never leave a
    silent hole on a money page — safer than keyword matching, which would
    silently drop a renamed product.
  - Nothing is fabricated: no review counts, no popularity claims, no
    strikethrough "was" pricing. Prices and contents are read from
    data/products.json at build time, so a sync keeps every number true.
  - Whole-catalog libraries (aggregate: true in discovery.json) are kept
    OUT of the guide grids — for the same reason they are excluded from
    Brush Finder ranking: they match everything, so they tell the shopper
    nothing. The Master Library appears once per page, in its own
    clearly-labelled slot (the flagship band).
  - Lifestyle products (planners, travel, Canva templates) never appear on
    these pages: they answer no brush question (owner decision 2026-09-13:
    they stay in the general catalog, but a buyer guide is a brush context).
"""
import os
from core import *
from pages_blog import load_articles  # reassigned to pages_blog.load_articles by build.py

GUIDES_DIR = "guides"

# Labels for the category cross-links used on guide pages (name shown on the
# pill). Kept here — not imported from pages_category — so the two modules
# stay decoupled and pages_category can safely import THIS module.
GUIDE_CAT_LABELS = {
    "portrait": "Portrait Brushes",
    "skin-texture": "Skin Texture",
    "line-art": "Line Art",
    "watercolor": "Watercolor",
    "anime": "Anime & Manga",
    "hair": "Hair Brushes",
    "glitter-effects": "Glitter & FX",
    "figure-drawing": "Figure Drawing",
    "traditional": "Traditional Media",
    "sketching": "Sketching",
}

# Which buyer guide(s) a category landing page should cross-link, by
# relevance. Consumed by tools/pages_category.py.
GUIDES_FOR_CATEGORY = {
    "portrait": ["procreate-texture-brushes"],
    "skin-texture": ["procreate-texture-brushes"],
    "line-art": ["procreate-pencil-brushes", "procreate-animation-brushes"],
    "watercolor": ["procreate-texture-brushes"],
    "anime": ["procreate-animation-brushes"],
    "hair": [],
    "glitter-effects": ["procreate-texture-brushes"],
    "figure-drawing": ["procreate-pencil-brushes"],
    "traditional": ["procreate-pencil-brushes", "procreate-texture-brushes"],
    "sketching": ["procreate-pencil-brushes"],
}

GUIDE_DEFS = [
    {
        "slug": "procreate-starter-kits",
        "nav": "Starter Kits",
        "card_blurb": "New to Procreate? The honest buying order: free packs first, one $5 kit matched to what you draw, a library only when you outgrow it.",
        "seo_title": "Procreate Starter Kits for Beginners | DigiKitPro",
        "seo_desc": "New to Procreate? Start with genuinely free brush packs, then one $5 kit matched to what you draw. The honest buying order, with live prices.",
        "eyebrow": "Buyer's guide · Start here",
        "h1": "Procreate Starter Kits for Beginners",
        "lead": "The fastest way to waste money on Procreate brushes is to buy a giant library before you know what you draw. The order that actually works: take the free packs, learn on them, buy one $5 kit that matches your subject, and only then decide whether the Master Library earns its place. This page is that order.",
        "intro_h2": "The buying order we recommend to every beginner",
        "intro": [
            "Every product below exists at exactly the price shown, and each product page lists precisely what is inside — we do not inflate counts, and we do not run countdown timers. If you want the editorial companion to this page — what makes a beginner brush good in the first place — read <a href=\"../../blog/best-procreate-brushes-for-beginners/\">Best Procreate Brushes for Beginners</a>. This page is the shop version: what to take home, and in what order.",
            "One honest boundary worth stating up front: Procreate itself is a separate paid app for iPad, made by Savage Interactive and sold on the App Store. DigiKitPro makes brush kits and learning material <em>for</em> Procreate — no kit on this page includes the app.",
        ],
        "groups": [
            {
                "id": "free",
                "title": "Step 1 · Start free",
                "sub": "Real kits, not samples — the same file quality as the paid packs. $0, and the free guide walks you through a first portrait.",
                "slugs": ["free-fine-liner-brushes-100", "free-color-vault-1200-swatches",
                           "free-chalkboard-artists-toolkit", "procreate-starter-guide-free-ebook"],
            },
            {
                "id": "five",
                "title": "Step 2 · One $5 kit, matched to your subject",
                "sub": "Pick the one that matches what you actually draw. Skip the rest until you hit the first kit's limits — you will know when.",
                "slugs": ["portrait-skin-brushes-procreate", "anime-soft-style-studio-kit",
                           "essential-line-art-sketch-kit", "artista-studio-kit-76-brushes",
                           "organic-watercolor-80-brushes", "brush-palette-bundle-160"],
            },
        ],
        "flagship": True,
        "flagship_note": "Step 3 · Only when you work across subjects",
        "faqs": [
            ("Do I need to buy anything to start drawing in Procreate?",
             "No. The three free packs install exactly like the paid ones, and the free starter guide takes you from a blank canvas to a first structured portrait. Remember that Procreate itself is a separate paid App Store app by Savage Interactive — our kits are content for it, not the app."),
            ("What is the real difference between a $5 kit and the $19 Master Library?",
             "Depth versus breadth. A $5 kit goes deep on one subject — skin, line art, watercolour — and is the cheaper, faster answer when you know what you are making. The Master Library is 2,000+ brushes organised across every style: it makes sense once you work across subjects and would otherwise be buying several packs one by one."),
            ("Will these kits work on my iPad?",
             "Every .brushset kit requires the Procreate app on an iPad, and each product page lists its own contents, file sizes and requirements under Technical Details. Payment and delivery are handled by Payhip — instant download, with PayPal, cards and Apple Pay accepted."),
            ("Can I sell artwork I make with these brushes?",
             "Yes. Unless a product page states otherwise, purchases include a licence for personal and commercial finished artwork. What you may not do is resell or share the brush files themselves. The full licence is one page — see the Terms of Service link in the footer."),
        ],
        "guides": ["best-procreate-brushes-for-beginners", "how-to-choose-procreate-brushes",
                    "how-to-install-procreate-brushes", "procreate-canvas-size-dpi-guide"],
        "cats": [],
    },
    {
        "slug": "procreate-pencil-brushes",
        "nav": "Pencil Brushes",
        "card_blurb": "Graphite-feel sketching kits, pose stamps for honest proportions, and the clean liners to finish a pencil rough.",
        "seo_title": "Procreate Pencil Brushes & Sketching Kits | DigiKitPro",
        "seo_desc": "Procreate pencil brushes that behave like real graphite: pressure, tilt shading and honest tooth. Sketching kits from $5, plus a 100-brush free set.",
        "eyebrow": "Buyer's guide · Sketching & graphite",
        "h1": "Procreate Pencil Brushes",
        "lead": "A pencil brush is judged on three things: does it darken with pressure the way graphite does, does it shade on the tilt like the side of a lead, and does it leave honest tooth on the canvas instead of a plastic glide. These are the kits in the catalog built around those three tests — from full traditional sketchbooks down to a $0 fine-liner set.",
        "intro_h2": "What a pencil brush has to get right",
        "intro": [
            "Procreate ships with a serviceable pencil, and most artists outgrow it quickly. The difference a tuned pencil kit makes is not a bigger brush count — it is a better pressure curve. A good sketching pencil stays light at the start of the stroke so you can ghost in a gesture, darkens smoothly as you commit, and on the tilt it shades like the side of graphite rather than spraying like an airbrush.",
            "The kits below are organised by where they sit in a drawing: sketch first, block the figure, then ink over the rough. If you are unsure whether Procreate pencils suit you at all, start with the free fine-liner set — it installs exactly the same way as the paid kits, so it is a zero-cost test of the whole workflow.",
        ],
        "groups": [
            {
                "id": "graphite",
                "title": "Pencil, graphite & charcoal kits",
                "sub": "Sketch-first tools: gesture, study, value and finished drawing.",
                "slugs": ["pro-sketch-traditional-art-kit", "professional-digital-sketchbook",
                           "sketchbook-traditional-media-kit", "professional-charcoal-studio",
                           "artista-studio-kit-76-brushes"],
            },
            {
                "id": "layout",
                "title": "Figure layout stamps",
                "sub": "Block in the pose first, then draw over the top — the fastest way to keep proportions honest.",
                "slugs": ["male-pose-brushes-figure-drawing", "female-pose-brushes-figure-drawing"],
            },
            {
                "id": "ink",
                "title": "Ink over the sketch",
                "sub": "Clean liners to finish a pencil rough — including the free set.",
                "slugs": ["essential-line-art-sketch-kit", "master-line-art-vault-300",
                           "free-fine-liner-brushes-100"],
            },
        ],
        "flagship": True,
        "flagship_note": "Sketching in every style, one library",
        "faqs": [
            ("Do these pencil brushes respond to Apple Pencil tilt?",
             "Yes. The sketching kits are tuned for pressure and tilt inside Procreate, so an angled stroke shades like the side of a graphite lead instead of behaving like an airbrush. Each product page lists its own brush behaviour and file contents under Technical Details."),
            ("Is there a free pencil or ink brush I can test first?",
             "Yes — the free Fine Liner Set includes 100 liner, micron and marker brushes plus 13 paper textures for $0. It installs exactly like the paid kits, so it doubles as a compatibility test for your iPad before you spend anything."),
            ("What canvas size should I sketch on?",
             "Bigger than you think. Sketching on a small canvas and scaling the drawing up later blurs your strokes. The canvas size and DPI guide below walks through pixel dimensions for studies, prints and commissions."),
            ("Pencil first or ink first?",
             "Pencil first. A fast graphite rough under a clean ink pass is the standard sequence in this catalog, and the pose stamps exist for the step before that — blocking in the figure so the drawing starts from honest proportions."),
        ],
        "guides": ["how-to-make-digital-art-look-traditional", "procreate-canvas-size-dpi-guide",
                    "stamp-brushes-vs-painting-brushes", "procreate-blending-brushes-guide"],
        "cats": ["sketching", "traditional", "figure-drawing", "line-art"],
    },
    {
        "slug": "procreate-texture-brushes",
        "nav": "Texture Brushes",
        "card_blurb": "Skin pores, paper grain, fur, smoke and painterly surface — the finishing pass, grouped by what you are texturing.",
        "seo_title": "Procreate Texture Brushes: Skin, Grain & Fur | DigiKitPro",
        "seo_desc": "Texture brushes for Procreate that fix the flat digital look: pores, paper grain, fur, smoke and painterly surfaces. From $4, plus a free chalk set.",
        "eyebrow": "Buyer's guide · Surface & texture",
        "h1": "Procreate Texture Brushes",
        "lead": "Flat colour is the first giveaway of digital work. Texture is what fixes it — pores on skin, tooth on paper, fur on a creature, smoke in the background — but only when the brush adds surface without muddying the values underneath. These kits are built for exactly that pass, grouped by the thing you are texturing.",
        "intro_h2": "Where texture belongs in a painting",
        "intro": [
            "Texture is a finishing discipline, not a starting one. Lay it over flat colour on its own layer, keep the opacity low, and let the underlying values do the work — the moment the texture fights the colours, it is too strong. Skin pores at low opacity read as realism; the same stamp at full strength reads as dirt.",
            "The groupings below are the order working artists usually buy in. Portraits start with the skin set. Traditional-media work starts with paper grain and chalk. Painterly illustrators live in the watercolour and pastel kits. Atmosphere — smoke, sparkle, dust — is the last pass before export.",
        ],
        "groups": [
            {
                "id": "organic",
                "title": "Skin, pores & fur",
                "sub": "Organic surface for portraits and creatures.",
                "slugs": ["portrait-skin-brushes-procreate", "animal-fur-brushes-2"],
            },
            {
                "id": "paper",
                "title": "Paper grain, chalk & traditional surface",
                "sub": "Tooth and grain that make a digital stroke feel like physical media.",
                "slugs": ["sketchbook-traditional-media-kit", "pro-sketch-traditional-art-kit",
                           "premium-texture-effects-10-brushes", "free-chalkboard-artists-toolkit"],
            },
            {
                "id": "painterly",
                "title": "Painterly colour & texture",
                "sub": "Watercolour blooms, pastel dust and surface-rich paint handling.",
                "slugs": ["organic-watercolor-80-brushes", "watercolor-studio-kit-50-brushes",
                           "dreamy-pastel-art-kit", "illustration-brushes-2",
                           "japanese-watercolour-collection", "tie-dye-brushes-studio"],
            },
            {
                "id": "atmosphere",
                "title": "Atmosphere & effects",
                "sub": "The final pass: smoke, sparkle and light.",
                "slugs": ["smoke-brushes-12", "glitter-brushes-sparkle-shine-30"],
            },
        ],
        "flagship": True,
        "flagship_note": "Every texture family, one organised library",
        "faqs": [
            ("How do I add texture without muddying my colours?",
             "On its own layer, above the colour, at low opacity. Texture brushes are built to sit over base colour and respond to blend modes, so the values underneath keep doing the work. If the surface starts to look dirty, the layer is too strong — drop the opacity before you reach for a different brush."),
            ("Should I use stamp textures or painting textures?",
             "Both, for different jobs. A stamp lays a complete surface down in one tap — fast and repeatable, ideal for paper grain and canvas. A painting texture brush builds up with the stroke, which is how skin and fur stay organic. The stamp-versus-painting guide below shows where each one wins."),
            ("Is there a free texture set?",
             "Yes. The Chalkboard Artist's Toolkit is 20+ chalk brushes with real blackboard grit for $0 — a genuine kit, not a sample strip — and it installs the same way as the paid ones."),
            ("Can I use these textures in work I sell?",
             "Yes. Unless a product page states otherwise, the licence covers personal and commercial finished artwork. Reselling or sharing the brush files themselves is the one thing the licence forbids — see the Terms of Service for the full text."),
        ],
        "guides": ["how-to-create-realistic-skin-texture-in-procreate",
                    "how-to-make-digital-art-look-traditional", "procreate-blending-brushes-guide"],
        "cats": ["traditional", "skin-texture", "watercolor", "glitter-effects"],
    },
    {
        "slug": "procreate-animation-brushes",
        "nav": "Animation Brushes",
        "card_blurb": "Clean liners for readable frames, colour that stays consistent across cels, and glow FX — with an honest note on Procreate Dreams.",
        "seo_title": "Procreate Animation & Dreams Brushes | DigiKitPro",
        "seo_desc": "The brushes animation artists actually use in Procreate: clean liners for readable frames, consistent palettes, glow and smoke FX — plus an honest note on Procreate Dreams.",
        "eyebrow": "Buyer's guide · Animation",
        "h1": "Procreate Animation Brushes",
        "lead": "Animation punishes brushes that painting forgives. A lively line on a still becomes noise across twenty frames; a colour that drifts between cels reads as flicker; and every effect stroke is multiplied by days of frame count. These are the catalog tools frame-by-frame artists actually reach for — with one honest caveat, stated plainly below.",
        "intro_h2": "What frame-by-frame work demands from a brush",
        "intro": [
            "Readability beats richness. Lines have to hold a silhouette at thumbnail size on a phone screen, palettes have to survive four hundred frames without drifting, and effects — a glow pass, a smoke drift — have to be repeatable stroke after stroke, frame after frame.",
            "That is why the selection below leans on clean liners, locked-in colour and stylised shading rather than heavy realism: those are the tools that stay consistent when a shot is redrawn all week.",
        ],
        "notice": True,  # render data/discovery.json → animationNotice verbatim
        "groups": [
            {
                "id": "line",
                "title": "Clean line & silhouette",
                "sub": "Readable at thumbnail size, consistent across hundreds of frames.",
                "slugs": ["essential-line-art-sketch-kit", "master-line-art-vault-300",
                           "liner-marker-studio-39-brushes", "free-fine-liner-brushes-100"],
            },
            {
                "id": "color",
                "title": "Colour that stays consistent",
                "sub": "The same swatches on frame 1 and frame 400 — no drift, no flicker.",
                "slugs": ["free-color-vault-1200-swatches", "procreate-palettes-bundle-50"],
            },
            {
                "id": "fx",
                "title": "Style, glow & atmosphere",
                "sub": "Soft shading, glow passes and effects for the final composite.",
                "slugs": ["anime-soft-style-studio-kit", "anime-soft-style-brushes-100",
                           "glitter-brushes-sparkle-shine-30", "smoke-brushes-12",
                           "premium-texture-effects-10-brushes"],
            },
        ],
        "flagship": True,
        "flagship_note": "Line, colour and effects in one organised library",
        "faqs": [
            ("Do these brushes work in Procreate Dreams?",
             "Everything here is a Procreate .brushset, built for Procreate on iPad. Procreate Dreams can import Procreate brush files, but a brush behaves differently inside an animation timeline than on a painting canvas. Test the pipeline with the free fine-liner set before buying anything — that is what it is for."),
            ("Why do animators insist on clean liners?",
             "Because frames are viewed small and in motion. A textured, varied line that looks painterly on a poster becomes visual noise when it redraws twenty-four times a second. Clean, predictable liners keep silhouettes readable at every frame size."),
            ("Is there a free way to test the whole workflow?",
             "Yes: the free Fine Liner Set covers clean line work and the free Color Vault covers palette consistency — $0 for both, installed exactly like the paid kits. If they hold up across your test shot, the paid kits will too."),
            ("Will you make a Dreams-specific brush pack?",
             "Possibly — what gets built next is decided by what artists actually ask for. The mailing list below is where new tools are announced, and requests sent via the Payhip store contact form are read and answered."),
        ],
        "guides": ["best-procreate-brushes-for-anime", "best-procreate-brushes-for-line-art",
                    "how-to-install-procreate-brushes"],
        "cats": ["anime", "line-art"],
    },
    {
        "slug": "procreate-bundles-compared",
        "nav": "Bundles Compared",
        "card_blurb": "All six brush bundles side by side: live prices, real contents, who each one is for, and the one-pass chooser.",
        "seo_title": "Procreate Bundles Compared: Which Kit to Buy | DigiKitPro",
        "seo_desc": "Every DigiKitPro Procreate bundle side by side — live prices, real contents, who each one is for. From the $5 Starter bundle to the 2,000+ brush Master Library.",
        "eyebrow": "Buyer's guide · Bundles",
        "h1": "Procreate Bundles, Compared",
        "lead": "Six brush bundles, one page, live store prices. No \"was\" strikethroughs, no countdown timers, no invented savings — the price shown is what Payhip charges today. The right bundle is the smallest one that covers what you make; the table below is built to find it in one pass.",
        "intro_h2": "Every brush bundle, side by side",
        "intro": [],  # the comparison table takes this slot (custom renderer)
        "bundles_table": True,
        "groups": [],
        "flagship": True,
        "flagship_note": "The library the ladder climbs to",
        "faqs": [
            ("Which bundle should I buy first?",
             "The smallest one that covers your subject. New to the shop: the $5 Starter bundle patches the two things a fresh library lacks — pattern brushes and colour. Portraits are the main event: the $15 Ultimate Portrait Mastery bundle wires four kits into one workflow. You genuinely make everything: a whole-catalog library. Seasonal work: the Christmas bundle, when the season calls for it."),
            ("Master Library or Mega Bundle — what is the difference?",
             "The numbers on this page come from the product records: the Master Library is 2,000+ brushes organised into category folders — built so you stop hunting; the Mega Bundle is 650+ brushes plus paper textures in one download. Both are whole-catalog libraries; compare the itemised contents on their product pages and pick the organisation that suits how you work."),
            ("Are the big libraries just the $5 packs repackaged?",
             "We do not claim a one-to-one overlap, and you should be suspicious of any shop that does. Specialist packs go deeper on one subject; the libraries span every subject. Every product page lists exactly what is inside, so if overlap matters to you, compare contents directly before buying."),
            ("Why is there no \"save 60%\" pricing on this page?",
             "Because it would not be true. A discount claim needs a real \"was\" price, and these bundles sell at the prices shown. What is honest arithmetic is shown instead — for example the per-brush cost on the library — calculated from the product's own live price and count."),
        ],
        "guides": ["how-to-choose-procreate-brushes", "how-to-install-procreate-brushes"],
        "cats": [],
    },
]

GUIDES_INDEX = {
    "seo_title": "Procreate Buyer's Guides | DigiKitPro",
    "seo_desc": "Honest buyer's guides to DigiKitPro Procreate brushes: starter kits for beginners, pencil & sketching kits, texture brushes, animation tools and every bundle compared.",
    "eyebrow": "Shop by question",
    "h1": "Procreate Buyer's Guides",
    "lead": "The right kit is the one that matches what you actually make. These guides organise the catalog by the question you arrived with — every price live from the store, every product page listing exactly what is inside, and no pretend urgency anywhere.",
}

BY_GUIDE = {g["slug"]: g for g in GUIDE_DEFS}
GUIDE_URLS = [f"{GUIDES_DIR}/{g['slug']}/" for g in GUIDE_DEFS]


def _check_slug(slug, where):
    if slug not in BY_SLUG:
        raise SystemExit(f"pages_guides: unknown product slug '{slug}' in {where} — "
                         f"fix data/discovery.json / this module or the product was removed.")
    return BY_SLUG[slug]


def guide_products(g):
    """Resolved, de-duplicated product list for a guide page. Fails loudly on a
    stale slug (see module docstring)."""
    seen, out = set(), []
    for grp in g.get("groups", []):
        for slug in grp.get("slugs", []):
            p = _check_slug(slug, f"{g['slug']}")
            if slug not in seen:
                seen.add(slug)
                out.append(p)
    return out


def guide_pills(depth, current_slug=None):
    """'More buyer guides' pill row — the internal-link mesh between guides."""
    pills = "".join(
        f'<a class="trend-pill" href="../{gd["slug"]}/">{esc(gd["h1"])}</a>'
        for gd in GUIDE_DEFS if gd["slug"] != current_slug)
    all_link = (f'<a class="trend-pill" href="./">All buyer guides →</a>'
                if current_slug else "")
    return f"""<div class="trend-pills-wrap" style="margin:2.5rem 0 0">
  <p class="trend-label">More buyer guides</p>
  <div class="trend-pills">{pills}{all_link}</div>
</div>"""


def guide_pills_for_category(depth, catslug):
    """The cross-link block rendered on category landing pages."""
    slugs = [s for s in GUIDES_FOR_CATEGORY.get(catslug, []) if s in BY_GUIDE]
    if not slugs:
        return ""
    pills = "".join(f'<a class="trend-pill" href="../../{GUIDES_DIR}/{s}/">{esc(BY_GUIDE[s]["h1"])}</a>'
                    for s in slugs)
    return f"""<div class="trend-pills-wrap" style="margin:2.5rem 0 0">
  <p class="trend-label">Buyer guides for this category</p>
  <div class="trend-pills">{pills}<a class="trend-pill" href="../../{GUIDES_DIR}/">All guides →</a></div>
</div>"""


def _faq_block(g):
    faqs = g.get("faqs") or []
    if not faqs:
        return ""
    items = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary><div class="faq-body"><p>{esc(a)}</p></div></details>'
        for q, a in faqs)
    return f"""<section class="section section-alt">
  <div class="wrap narrow">
    <div class="sec-head"><div><p class="eyebrow">Straight answers</p><h2>Common questions</h2></div></div>
    {items}
  </div>
</section>"""


def _guides_row(g, all_articles, depth):
    arts = [all_articles[s] for s in g.get("guides", []) if s in all_articles]
    if not arts:
        return ""
    cards = "".join(
        f'<a class="art-card art-card-sm" href="../../blog/{a["slug"]}/">'
        f'<div class="art-body"><span class="art-cat">{esc(a.get("category", "Guide"))}</span>'
        f'<h3>{esc(a["title"])}</h3>'
        f'<p class="muted">{esc(a.get("description", ""))}</p>'
        f'<span class="text-link">Read tutorial →</span></div></a>'
        for a in arts)
    return f"""<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">Technique &amp; tutorials</p><h2>Learn the craft behind the tools</h2></div>
      <a class="text-link" href="../../blog.html">All articles →</a>
    </div>
    <div class="grid arts-grid">{cards}</div>
  </div>
</section>"""


def _cat_pills(g, depth):
    slugs = [c for c in g.get("cats", []) if c in GUIDE_CAT_LABELS]
    if not slugs:
        return ""
    pills = "".join(f'<a class="trend-pill" href="../../category/{c}/">{esc(GUIDE_CAT_LABELS[c])}</a>'
                    for c in slugs)
    return f"""<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="trend-pills-wrap">
      <p class="trend-label">Browse the matching brush categories</p>
      <div class="trend-pills">{pills}</div>
    </div>
  </div>
</section>"""


def _notice_block():
    """The animation honesty notice, verbatim from data/discovery.json (the same
    copy the Brush Finder was built around). If the owner edits it there, every
    surface that quotes it updates together."""
    n = DISCOVERY.get("animationNotice") or {}
    title, body, cta = n.get("title"), n.get("body"), n.get("cta") or {}
    if not (title and body):
        return ""
    href = cta.get("href", "freebies.html#newsletter")
    link = (f'<p><a class="btn btn-line" href="../../{esc(href)}">{esc(cta.get("label", "Tell us"))} →</a></p>'
            if cta.get("label") else "")
    return f"""<section class="section">
  <div class="wrap narrow prose">
    <h2>{esc(title)}</h2>
    <p>{esc(body)}</p>
    {link}
  </div>
</section>"""


def _bundles_comparison(depth):
    """The honest side-by-side. Every cell is read from the product record at
    build time (name, priceText, assets, perfectFor) — nothing typed by hand,
    so a Payhip sync keeps the table true. Excludes the three 'Other'-category
    bundles (palettes, PNG pack, Canva templates): they are not brush kits and
    comparing them with brushes would be marketing, not information."""
    rows = [p for p in PRODUCTS if p.get("category") == "Bundles"]
    rows.sort(key=lambda p: (p.get("price") or 0, p["name"]))
    body = ""
    for p in rows:
        u = rel(depth, f"products/{p['slug']}/")
        best_for = ", ".join((p.get("perfectFor") or [])[:2]) or p.get("short") or ""
        seasonal = ' <span class="muted">· seasonal</span>' if "christmas" in p["slug"] or "halloween" in p["slug"] else ""
        body += (f'<tr><td><a href="{u}"><strong>{esc(p["name"])}</strong></a>{seasonal}</td>'
                 f'<td class="price">{esc(p["priceText"])}</td>'
                 f'<td>{esc(p.get("assets") or "—")}</td>'
                 f'<td>{esc(best_for)}</td></tr>')
    return f"""<section class="section">
  <div class="wrap">
    <div class="table-wrap">
      <table>
        <thead><tr><th>Bundle</th><th>Price</th><th>What you get</th><th>Best for</th></tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    <p class="muted">Not brush bundles, so not compared here: the 50-palette colour bundle, the
    Halloween PNG pack and the KDP Canva templates — they live in the
    <a href="{rel(depth, 'products.html')}">full catalog</a> and state their own formats on their product pages.</p>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap narrow prose">
    <h2>How to choose in one pass</h2>
    <ol>
      <li><strong>New to the shop</strong> — start at the bottom rung. The $5 Starter bundle patches the two gaps every fresh library has: pattern brushes and colour.</li>
      <li><strong>Portraits are the main thing</strong> — the Ultimate Portrait Mastery bundle wires four portrait kits into a single line → skin → hair → finish workflow.</li>
      <li><strong>You genuinely make everything</strong> — a whole-catalog library. The Master Library is the organised one; the Mega Bundle is the one that adds paper textures.</li>
      <li><strong>Holiday work</strong> — the Christmas bundle earns its place when the season calls, and goes back in the drawer after.</li>
    </ol>
  </div>
</section>"""


def build_guide_index(depth=1):
    gs = GUIDES_INDEX
    cards = "".join(
        f'<a class="art-card" href="{g["slug"]}/">'
        f'<div class="art-body"><span class="art-cat">{esc(g["nav"])}</span>'
        f'<h3>{esc(g["h1"])}</h3>'
        f'<p class="muted">{esc(g["card_blurb"])}</p>'
        f'<span class="text-link">Open the guide →</span></div></a>'
        for g in GUIDE_DEFS)
    schemas = schema_breadcrumb([("Home", "/"), ("Buyer Guides", f"/{GUIDES_DIR}/")])
    html_out = head(gs["seo_title"], gs["seo_desc"], absurl(f"{GUIDES_DIR}/"), depth,
                    schemas=schemas, ctx=page_ctx("guide", slug="index"))
    html_out += header(depth, active="products.html")
    html_out += f"""
<main id="main">
  <section class="page-head">
    <div class="wrap">
      {crumbs(depth, [("Buyer Guides", GUIDES_DIR + "/")])}
      <p class="eyebrow">{esc(gs["eyebrow"])}</p>
      <h1>{esc(gs["h1"])}</h1>
      <p class="lead">{esc(gs["lead"])}</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="grid arts-grid">{cards}</div>
    </div>
  </section>
  {newsletter(depth, source="guides", lead="buyer-guides", uid="gd")}
</main>
"""
    html_out += footer(depth)
    write(f"{GUIDES_DIR}/index.html", html_out)


def build_guides():
    all_articles = {a["slug"]: a for a in load_articles()}
    build_guide_index(depth=1)
    for g in GUIDE_DEFS:
        slug = g["slug"]
        depth = 2
        if g.get("bundles_table"):
            # the comparison page's listed items are the real brush bundles
            prods = [p for p in PRODUCTS if p.get("category") == "Bundles"]
        else:
            prods = guide_products(g)

        schemas = schema_breadcrumb([
            ("Home", "/"),
            ("Buyer Guides", f"/{GUIDES_DIR}/"),
            (g["h1"], f"/{GUIDES_DIR}/{slug}/"),
        ])
        if prods:
            schemas += schema_itemlist(prods)
        if g.get("faqs"):
            schemas += schema_faq(g["faqs"])

        # intro prose (skipped for the bundles page — its slot is the table)
        intro_html = ""
        if g.get("intro"):
            paras = "\n".join(f"    <p>{t}</p>" for t in g["intro"])  # intro copy is trusted markup
            intro_html = f"""<section class="section">
  <div class="wrap narrow prose">
    <h2>{esc(g["intro_h2"])}</h2>
{paras}
  </div>
</section>"""

        # product groups
        groups_html = ""
        for i, grp in enumerate(g.get("groups", [])):
            gprods = [_check_slug(s, f"{slug}:{grp['id']}") for s in grp["slugs"]]
            alt = ' section-alt' if i % 2 == 1 else ""
            sub = f'<p class="muted" style="max-width:56ch;margin:-0.75rem 0 1.75rem">{esc(grp["sub"])}</p>' if grp.get("sub") else ""
            groups_html += f"""<section class="section{alt}" id="{esc(grp['id'])}">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">{esc(g["nav"])}</p><h2>{esc(grp["title"])}</h2></div></div>
    {sub}
    {product_grid(gprods, depth, eager_first=2 if i == 0 else 0)}
  </div>
</section>
"""

        notice_html = _notice_block() if g.get("notice") else ""
        table_html = _bundles_comparison(depth) if g.get("bundles_table") else ""

        flag_html = ""
        if g.get("flagship"):
            note = g.get("flagship_note")
            if note:
                flag_html += f"""<section class="section" style="padding-bottom:0">
  <div class="wrap narrow"><p class="eyebrow" style="margin-bottom:0.5rem">{esc(note)}</p></div>
</section>
"""
            # "top rung of the ladder" link — pointless when it points at the
            # page it sits on, so the comparison page renders without it.
            lh = None if g.get("bundles_table") else rel(depth, f"{GUIDES_DIR}/procreate-bundles-compared/")
            flag_html += flagship_band(depth, ladder_href=lh)

        html_out = head(g["seo_title"], g["seo_desc"], absurl(f"{GUIDES_DIR}/{slug}/"), depth,
                        schemas=schemas, ctx=page_ctx("guide", slug=slug, category=g["nav"]))
        html_out += header(depth, active="products.html")
        html_out += f"""
<main id="main">
  <section class="page-head">
    <div class="wrap">
      {crumbs(depth, [("Buyer Guides", f"{GUIDES_DIR}/"), (g["h1"], f"{GUIDES_DIR}/{slug}/")])}
      <p class="eyebrow">{esc(g["eyebrow"])}</p>
      <h1>{esc(g["h1"])}</h1>
      <p class="lead">{esc(g["lead"])}</p>
      {guide_pills(depth, current_slug=slug)}
    </div>
  </section>

  {intro_html}
  {table_html}
  {groups_html}
  {notice_html}
  {flag_html}
  {_faq_block(g)}
  {_guides_row(g, all_articles, depth)}
  {_cat_pills(g, depth)}
  {newsletter(depth, source="guide", lead=slug, uid="gd")}
</main>
"""
        html_out += footer(depth)
        write(f"{GUIDES_DIR}/{slug}/index.html", html_out)

    print(f"Built buyer guides: index + {len(GUIDE_DEFS)} landing pages under /{GUIDES_DIR}/")
