#!/usr/bin/env python3
"""Commercial-intent buyer-guide landing pages (Phase 3 — organic traffic).

The /blog articles answer technique questions ("how do I paint skin").
The /guides pages answer shopping questions ("which procreate pencil
brushes", "which bundle should I buy"), using only the real catalog:
explicit tag-derived product selections, catalog price snapshots and honest
trade-offs. Free resources, focused packs and broader libraries are options,
not a required buying sequence.

Rules this module lives by:
  - Selections are explicit slug lists, chosen from the data/discovery.json
    tags (craft / improve / level / style / stage). The build FAILS LOUDLY
    when a referenced slug disappears, so a Payhip sync can never leave a
    silent hole on a money page — safer than keyword matching, which would
    silently drop a renamed product.
  - No fabricated review counts, popularity claims or "was" pricing. Prices
    and listed contents come from data/products.json at build time, not a live
    Payhip query. Exact files and bundle overlap still need verification.
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
        "card_blurb": "Compare free resources, focused brush packs and a broader library for your Procreate workflow. No paid purchase is required to use the free resources.",
        "seo_title": "Procreate Starter Kits for Beginners | DigiKitPro",
        "seo_desc": "Compare free Procreate resources, focused brush kits and a broader library. Choose the tools that fit your work; confirm prices on Payhip.",
        "eyebrow": "Buyer's guide · Start here",
        "h1": "Procreate Starter Kits for Beginners",
        "lead": "Choose the tools that suit what you draw: free resources, a focused brush kit or a broader library. None is a required step before another, and no paid purchase is required to use the free resources.",
        "intro_h2": "Choose the resources that fit your work",
        "intro": [
            "Prices shown reflect our catalog when the site was built; confirm the current total on Payhip before checkout. Compare the listed contents on each product page and contact the store if overlap matters. For help choosing brushes, read <a href=\"../../blog/best-procreate-brushes-for-beginners/\">Best Procreate Brushes for Beginners</a>.",
            "Procreate itself is a separate paid app for iPad, made by Savage Interactive and sold on the App Store. DigiKitPro lists brush kits and learning material <em>for</em> Procreate — no kit on this page includes the app.",
        ],
        "groups": [
            {
                "id": "free",
                "title": "Free resources",
                "sub": "Explore the free brushes, color palettes and portrait guide independently. The guide's listing says you can practise with Procreate's built-in brushes.",
                "slugs": ["free-fine-liner-brushes-100", "free-color-vault-1200-swatches",
                           "free-chalkboard-artists-toolkit", "procreate-starter-guide-free-ebook"],
            },
            {
                "id": "five",
                "title": "Focused kits for your subject",
                "sub": "Compare the listed tools for skin, line art, anime, watercolor and more. Check each product's contents and requirements before buying.",
                "slugs": ["portrait-skin-brushes-procreate", "anime-soft-style-studio-kit",
                           "essential-line-art-sketch-kit", "artista-studio-kit-76-brushes",
                           "organic-watercolor-80-brushes", "brush-palette-bundle-160"],
            },
        ],
        "flagship": True,
        "flagship_note": "Optional: explore a broader brush library",
        "faqs": [
            ("Do I need to buy a DigiKitPro kit to start drawing in Procreate?",
             "No paid DigiKitPro purchase is required to use the free resources. The free portrait guide's listing describes exercises using Procreate's built-in brushes. Procreate itself is a separate paid iPad app by Savage Interactive."),
            ("How does a focused kit compare with the Master Library?",
             "A focused kit is listed for particular tasks, such as skin or line art. The Master Library is listed as a broad collection across several drawing styles. Compare the product pages and ask the store about possible overlap before buying."),
            ("Will these kits work on my iPad?",
             "Every .brushset kit requires the Procreate app on an iPad. Check each product page for its contents and requirements. Payhip handles checkout and digital delivery; review the total and available payment options there before paying."),
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
        "card_blurb": "Explore sketching kits, pose references and liners for your Procreate workflow.",
        "seo_title": "Procreate Pencil Brushes & Sketching Kits | DigiKitPro",
        "seo_desc": "Compare Procreate pencil, sketching and line-art tools for iPad. Explore listed brush packs, pose stamps and a free fine-liner set.",
        "eyebrow": "Buyer's guide · Sketching & graphite",
        "h1": "Procreate Pencil Brushes",
        "lead": "Compare Procreate tools listed for sketching, graphite-style marks, pose references and linework. Consider the type of stroke you need as well as each kit's format and contents.",
        "intro_h2": "What to look for in a pencil brush",
        "intro": [
            "When choosing a sketching brush, consider its texture, line weight and how it responds to your hand. Brush settings and device behavior vary; check the individual product details if pressure or tilt response is important to you.",
            "The resources below cover sketching, figure references and linework. The free fine-liner set is an independent option for line art; it does not verify the behavior of every paid kit.",
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
        "flagship_note": "Optional: a broader library for varied drawing styles",
        "faqs": [
            ("Do these pencil brushes respond to Apple Pencil tilt?",
             "Brush behavior can vary with its settings and your device. Tilt response has not been independently verified for every listed kit; check the product details or contact the store if it matters to your purchase."),
            ("Is there a free pencil or ink brush I can test first?",
             "The free Fine Liner Set is listed with 100 liner and marker brushes plus 13 paper textures. It is a standalone line-art resource; it does not establish how other kits will perform."),
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
            "The groups below organize the catalog by use: skin and fur, paper and chalk, painterly marks, and atmosphere. Explore whichever tools suit your work; there is no required purchase order.",
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
        "flagship_note": "Optional: explore a broader brush library",
        "faqs": [
            ("How do I add texture without muddying my colours?",
             "Try adding texture on a separate layer at low opacity and adjust the opacity or blend mode to suit the image. Check that the values underneath still read clearly."),
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
        "card_blurb": "Explore listed line, color and effects resources, with a note on checking Procreate Dreams compatibility.",
        "seo_title": "Procreate Animation & Dreams Brushes | DigiKitPro",
        "seo_desc": "Explore Procreate liners, palettes and effects for animation artwork. Check individual file formats and Procreate Dreams compatibility.",
        "eyebrow": "Buyer's guide · Animation",
        "h1": "Procreate Animation Brushes",
        "lead": "Compare listed Procreate liners, color palettes and effects for artwork you may use in animation. Check each file's format and compatibility with your own workflow before buying.",
        "intro_h2": "Choosing tools for frame-by-frame work",
        "intro": [
            "Readable lines and a consistent color palette can help a sequence feel coherent. Test your chosen process on a short sample before committing to a longer project.",
            "The resources below are listed for linework, color and effects in Procreate. They are not sold as a dedicated Procreate Dreams brush pack; their behavior in Dreams has not been independently verified here.",
        ],
        "notice": True,  # render data/discovery.json → animationNotice verbatim
        "groups": [
            {
                "id": "line",
                "title": "Clean line & silhouette",
                "sub": "Listed line-art tools for sketches, outlines and silhouettes.",
                "slugs": ["essential-line-art-sketch-kit", "master-line-art-vault-300",
                           "liner-marker-studio-39-brushes", "free-fine-liner-brushes-100"],
            },
            {
                "id": "color",
                "title": "Colour palettes",
                "sub": "Listed Procreate swatches to organize your color choices.",
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
             "These resources are listed for Procreate on iPad and include different formats, including .brushset brushes and .swatches palettes. Their behavior in Procreate Dreams has not been independently verified here; check the current app documentation and each product's format before buying."),
            ("Why might I choose a clean liner for animation?",
             "A simpler line can help a silhouette remain readable across frames. Try both smooth and textured lines in a short sample to see what suits your style."),
            ("Are there free resources I can try?",
             "The Fine Liner Set and Color Vault are separate free resources for Procreate. Trying them does not establish compatibility or performance for other products."),
            ("Is there a Dreams-specific brush pack?",
             "A Procreate Dreams-specific brush pack is not currently listed. Contact the store with questions about formats or to share a product request."),
        ],
        "guides": ["best-procreate-brushes-for-anime", "best-procreate-brushes-for-line-art",
                    "how-to-install-procreate-brushes"],
        "cats": ["anime", "line-art"],
    },
    {
        "slug": "procreate-bundles-compared",
        "nav": "Bundles Compared",
        "card_blurb": "Compare brush bundles by their listed contents, intended uses and catalog prices; confirm the total on Payhip.",
        "seo_title": "Procreate Bundles Compared: Which Kit to Buy | DigiKitPro",
        "seo_desc": "Compare Procreate brush bundles by listed contents and use. Prices shown are catalog snapshots; confirm the total on Payhip before buying.",
        "eyebrow": "Buyer's guide · Bundles",
        "h1": "Procreate Bundles, Compared",
        "lead": "Compare the listed brush bundles by contents and intended use. Prices shown reflect our catalog when the site was built; confirm the current total on Payhip before checkout. Exact inventory and overlap have not been independently verified.",
        "intro_h2": "Every brush bundle, side by side",
        "intro": [],  # the comparison table takes this slot (custom renderer)
        "bundles_table": True,
        "groups": [],
        "flagship": True,
        "flagship_note": "Optional: explore a broader brush library",
        "faqs": [
            ("Which bundle should I choose?",
             "Choose according to the tools and subject you need. Compare the listed components, requirements and possible overlap on each product page; no bundle is a prerequisite for another."),
            ("Master Library or Mega Bundle — what is the difference?",
             "The Master Library is listed as 2,000+ brushes, while the Mega Bundle is listed as 650+ brushes and paper textures. Exact contents and overlap have not been independently verified. Contact the store if a specific set matters to your decision."),
            ("Do the large libraries overlap smaller packs?",
             "The exact overlap has not been independently confirmed. Compare the listed contents and contact the store before buying both if a file-by-file comparison matters to you."),
            ("How current are the prices shown here?",
             "The prices come from our catalog when the site was built. Confirm the current price and total on Payhip before completing a purchase."),
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
    "lead": "Explore the catalog by the question you arrived with. Compare listed contents and requirements, and confirm current prices on Payhip before checkout.",
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
    all_link = (f'<a class="trend-pill" href="{rel(depth, f"{GUIDES_DIR}/")}">All buyer guides →</a>'
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
    href = cta.get("href", "freebies.html")
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
    """Compare catalog records at build time; verify prices on Payhip and
    contents against actual files. Exclude the three 'Other'-category bundles
    (palettes, PNG pack, Canva templates) because they are not brush kits."""
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
        <thead><tr><th>Bundle</th><th>Catalog price</th><th>Listed contents</th><th>Best for</th></tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    <p class="muted">Prices and contents reflect catalog records when the site was built.
    Confirm the current total on Payhip and contact the store if exact contents or overlap matter.</p>
    <p class="muted">Not brush bundles, so not compared here: the 50-palette colour bundle, the
    Halloween PNG pack and the KDP Canva templates — they live in the
    <a href="{rel(depth, 'products.html')}">full catalog</a> and state their own formats on their product pages.</p>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap narrow prose">
    <h2>Choose by your work</h2>
    <ul>
      <li><strong>Pattern and colour</strong> — compare the listed pattern brushes and palettes in the Brush &amp; Palette Bundle.</li>
      <li><strong>Portraits</strong> — the Ultimate Portrait Mastery bundle lists four kits for line art, skin, hair and glitter. Check for overlap with any packs you already own.</li>
      <li><strong>Broader collections</strong> — compare the listed brush counts, paper textures and requirements of the Mega Bundle and Master Library; exact overlap is unconfirmed.</li>
      <li><strong>Seasonal artwork</strong> — explore the Christmas bundle if its listed contents suit your project.</li>
    </ul>
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
            # Keep the comparison link, without presenting the library as a
            # required next purchase. Omit the link on the comparison page.
            lh = None if g.get("bundles_table") else rel(depth, f"{GUIDES_DIR}/procreate-bundles-compared/")
            flag_html += flagship_band(depth, ladder_href=lh, neutral_compare=True)

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
