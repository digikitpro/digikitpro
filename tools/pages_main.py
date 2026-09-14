#!/usr/bin/env python3
"""Homepage, products index, bundles, freebies."""
from core import *

def page_head(depth, eyebrow, title, lead, crumbs_items=None, lead_html=None):
    c = crumbs(depth, crumbs_items) if crumbs_items else ""
    lead = lead_html if lead_html else f'<p class="lead">{lead}</p>' if lead else ""
    return ('<section class="page-head"><div class="wrap">' + c +
            f'<p class="eyebrow">{eyebrow}</p><h1>{title}</h1>{lead}</div></section>')

# ─────────────────────────── HOME ───────────────────────────
def build_home():
    byslug = BY_SLUG
    showcase_slugs = ["portrait-skin-brushes-procreate", "artista-studio-kit-76-brushes", "watercolor-studio-kit-50-brushes"]
    showcase = ""
    for i, s in enumerate(showcase_slugs):
        p = byslug[s]; im = p["images"]
        _hw, _hh = im.get("fullW") or 1200, im.get("fullH") or 800
        showcase += f'<figure class="hero-card h{i+1}" style="--hero-ar:{_hw}/{_hh}"><img src="{asset_file(0, p["slug"], im.get("main",""))}" width="{im.get("fullW") or 1200}" height="{im.get("fullH") or 800}" alt="{esc(p["name"])}" loading="{"eager" if i==0 else "lazy"}" fetchpriority="{"high" if i==0 else "auto"}" decoding="async"><figcaption>{esc(p["name"])}</figcaption></figure>'

    freebies = [p for p in PRODUCTS if p["free"] and not p.get("comingSoon") and p["category"] != "Guides & eBooks"]
    # The homepage bundle row used to be "all Bundles-category packs, cheapest
    # first", which buried the $19 Master Library under a $5 palette bundle and
    # cut it off the page entirely. It is now an explicit value ladder authored
    # in data/discovery.json -> bundleLadder.rungs (see core.bundle_ladder),
    # with the flagship library as its top rung. Seasonal packs stay in the
    # catalog and on bundles.html — nothing was deleted, only re-sequenced.

    # ── Featured Brush Kits: storefront cards, best-seller excluded ──────
    # The best-seller gets the compact spotlight above the cards; these are
    # the studio picks that fill out the catalog row. Hand-picked slugs keep
    # the row curated instead of whichever product edited its flag last.
    featured_kits = [byslug[s] for s in (
        "artista-studio-kit-76-brushes",
        "anime-soft-style-studio-kit",
        "watercolor-studio-kit-50-brushes",
    ) if s in byslug]

    # ── Popular Starting Points: the three packs new customers begin with ─
    starting_points = [byslug[s] for s in (
        "portrait-mastery-kit-46-brushes",
        "essential-line-art-sketch-kit",
        "ultimate-portrait-mastery-bundle",
    ) if s in byslug]

    # ── THE PORTRAIT LEARNING PATH ──────────────────────────────────────
    # Five steps, in the order a portrait painter actually learns them:
    #   Free Portrait Guide → Skin Brushes → Portrait Mastery Kit →
    #   Portrait Bundle → Portrait Masterclass
    # Every step is a real, live product (slugs resolved at build time; a
    # deleted product simply drops its step). CTA rule: the free step goes
    # straight to Payhip (zero friction, no email gate); paid steps go to
    # their product page, because the path's job is "understand what this
    # helps me do" before any checkout.
    path_steps = [
        ("procreate-starter-guide-free-ebook", "Step 1 · Free",
         "A visual beginner guide from a blank canvas to a structured, well-lit portrait."),
        ("portrait-skin-brushes-procreate", "Step 2 · Add texture",
         "Pores, freckles and wrinkles — the skin brushes that stop a face looking flat."),
        ("portrait-mastery-kit-46-brushes", "Step 3 · The full kit",
         "46 brushes wired into a complete portrait workflow: sketch, block, blend, texture, finish."),
        ("ultimate-portrait-mastery-bundle", "Step 4 · One checkout",
         "Four portrait kits as one workflow — skin, hair, finish and more, bought together."),
        ("procreate-portrait-masterclass-ebook", "Step 5 · The curriculum",
         "107 pages and 15 chapters: the complete portrait method, canvas to final render."),
    ]
    path_items = ""
    for i, (slug, tag, desc) in enumerate(path_steps, start=1):
        p = byslug.get(slug)
        if not p or p.get("comingSoon"):
            continue
        im = p.get("images") or {}
        img = im.get("card") or im.get("main") or ""
        if not img:
            continue
        name = p["name"].split(" (")[0]
        u = rel(0, f"products/{p['slug']}/")
        final = (i == len(path_steps))
        if p.get("free"):
            cta = f'<a class="btn btn-gold btn-sm" href="{p["payhipUrl"]}" target="_blank" rel="noopener" {buy_attrs(p, "portrait-path")}>Get Free <span class="btn-arr">↗</span></a>'
        else:
            cta = f'<a class="btn btn-line btn-sm" href="{u}" {buy_attrs(p, "portrait-path")}>View Product</a>'
        path_items += f"""<li class="path-step{' path-step--final' if final else ''}">
  <a class="path-media" href="{u}" tabindex="-1" aria-hidden="true">
    <span class="path-num">{i}</span>
    <img src="{asset_file(0, p['slug'], img)}" width="{im.get('cardW') or im.get('fullW') or 750}" height="{im.get('cardH') or im.get('fullH') or 500}" alt="" loading="lazy" decoding="async">
  </a>
  <div class="path-body">
    <p class="path-tag">{esc(tag)}</p>
    <h3><a href="{u}">{esc(name)}</a></h3>
    <p class="path-desc">{esc(desc)}</p>
    <div class="path-foot"><span class="price">{"Free" if p["free"] else esc(p["priceText"])}</span>{cta}</div>
  </div>
</li>"""
    portrait_path_section = ""
    if path_items:
        portrait_path_section = f"""<section class="section section-alt" id="portrait-path" aria-labelledby="path-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">The portrait learning path</p><h2 id="path-title">From First Portrait to Masterclass</h2></div>
        <a class="text-link" href="category/portrait/">All portrait brushes →</a>
      </div>
      <p class="sec-note muted">Five steps, in the order a portrait painter actually learns them — start free, add the tools for each stage, then take the full curriculum.</p>
      <ol class="path">{path_items}</ol>
    </div>
  </section>
"""

    bundle_ladder_section = bundle_ladder(0)

    # ── Before / After: the result, not the brushes ──────────────────────
    # Interactive comparison slider (js/motion.js + css/style.css "MOTION
    # SYSTEM"). Medium-width on purpose: it demonstrates texture, it does
    # not become another full-bleed product band. Swap
    # assets/img/ba-before.webp and ba-after.webp for real client artwork
    # whenever you like; they must stay the same size and the same crop.
    skin = byslug.get("portrait-skin-brushes-procreate")
    portrait_bundle = byslug.get("ultimate-portrait-mastery-bundle")
    skin_cta = ""
    bundle_cta = ""
    if skin:
        skin_cta = (
            f'<a class="btn btn-gold" href="products/{skin["slug"]}/" {buy_attrs(skin, "before-after")}>'
            f'Get the Skin Brushes <span class="btn-arr">·</span> {esc(skin["priceText"])}</a>'
        )
    if portrait_bundle:
        bundle_cta = (
            f'<a class="btn btn-line" href="products/{portrait_bundle["slug"]}/">'
            f'Or take the full portrait bundle →</a>'
        )
    before_after = f"""<section class="section ba-section" id="results" aria-labelledby="results-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">See what the brushes actually change</p><h2 id="results-title">Flat Painting → Finished Portrait</h2></div>
        <a class="text-link" href="products/portrait-mastery-kit-46-brushes/">See the portrait kit →</a>
      </div>
      <p class="sec-note muted">Same drawing, same lighting: the only difference is texture. Drag the divider to see what skin, hair and finish brushes actually add — pores, freckles, strand detail and the final pass that stops a portrait looking airbrushed.</p>
      <figure class="ba-figure">
        <div class="ba-stage" data-ba>
          <img class="ba-img ba-after" src="assets/img/ba-after.webp" width="1200" height="800" alt="Finished portrait: detailed skin texture, hair strands and final rendering" loading="lazy" decoding="async">
          <div class="ba-clip">
            <img class="ba-img ba-before" src="assets/img/ba-before.webp" width="1200" height="800" alt="Unfinished portrait: flat base colour with no skin texture or detail" loading="lazy" decoding="async">
          </div>
          <span class="ba-tag ba-tag-b">Before · flat base</span>
          <span class="ba-tag ba-tag-a">After · textured finish</span>
          <div class="ba-divider" role="slider" tabindex="0" aria-label="Reveal the finished portrait" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50" aria-valuetext="50% finished">
            <span class="ba-grip" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6 4 12l5 6M15 6l5 6-5 6"/></svg></span>
          </div>
          <div class="ba-sweep" aria-hidden="true"></div>
        </div>
        <figcaption class="ba-cap"><span>Drag anywhere on the image, or focus the handle and use ← →.</span><span>Demonstration artwork.</span></figcaption>
      </figure>
      <div class="ba-cta">{skin_cta}{bundle_cta}</div>
    </div>
  </section>
"""

    articles = [a for a in load_articles() if a.get("image")][:3]
    def art_card(a, depth):
        ss = img_srcset(depth, a.get("_pslug", ""), a.get("_im") or {}, "(min-width: 1100px) 370px, (min-width: 700px) 45vw, 92vw")
        return f"""<a class="art-card" href="{rel(depth, 'blog/' + a['slug'] + '/')}">
      <img class="art-img" src="{a['image'] if is_abs(a['image']) else rel(depth, a['image'])}"{ss} width="{a.get('imgW',750)}" height="{a.get('imgH',500)}" alt="{esc(a['title'])}" loading="lazy" decoding="async">
      <div class="art-body"><span class="art-cat">{esc(a['category'])}</span>
      <h3>{esc(a['title'])}</h3>
      <p class="muted">{esc(a['description'])}</p>
      <span class="text-link">Read the guide →</span></div></a>"""
    art_cards = "".join(art_card(a, 0) for a in articles)

    html_out = head(
        "DigiKitPro | Procreate Brushes for iPad Artists",
        "Hand-tested Procreate brushes for portraits, skin, line art, watercolor and anime. Instant download on iPad — free packs included.",
        SITE_URL + "/", 0, schemas=schema_org_home(), ctx=page_ctx("home"),
        preload="assets/products/portrait-skin-brushes-procreate/portrait-skin-brushes-procreate.webp")
    html_out += header(0, active="index.html")
    html_out += f"""
<main id="main">
  <!-- 1 · ARTIST-GOAL HERO: what DigiKitPro is + what YOU want to create,
       in one line. The artwork does the rest. -->
  <section class="hero">
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">DigiKitPro — a premium Procreate brush studio</p>
        <h1>Procreate brushes for the work you <em>want to create</em></h1>
        <p class="hero-sub">Portraits, skin &amp; hair, line art, anime, watercolor — hand-tested kits for every stage, from the free starter guide to the Complete Portrait Masterclass.</p>
        <div class="hero-ctas">
          <a class="btn btn-gold btn-lg" href="products.html">Shop Brushes</a>
          <a class="btn btn-line btn-lg" href="freebies.html">Start Free</a>
        </div>
        <p class="hero-meta">Instant download via Payhip · Procreate 5 or newer on iPad · Free packs included</p>
      </div>
      <div class="hero-showcase" aria-hidden="true" data-parallax="10">{showcase}</div>
    </div>
  </section>

  <!-- 2 · TRUST / VALUE STRIP: concrete catalog numbers, verifiable from
       data/products.json — never invented social proof. -->
  {trust_band(0)}

  <!-- 3 · WHAT DO YOU CREATE? routes by intent before the catalog. -->
  {craft_grid(0)}

  <!-- 4 · FREE PROCREATE BRUSHES: "Get Free" goes straight to Payhip. -->
  <section class="section" id="free">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Level 1 · Completely free</p><h2>Free Procreate Brushes</h2></div>
        <a class="text-link" href="freebies.html">All freebies →</a>
      </div>
      <p class="sec-note muted">Real kits, not samples — the same pressure tuning and file quality as the paid packs. Take them, use them, and only spend money once you know how they feel.</p>
      {product_grid(freebies, 0, eager_first=1, free_direct=True)}
    </div>
  </section>

  <!-- 5 · THE PORTRAIT LEARNING PATH: Free Portrait Guide → Skin Brushes →
       Portrait Mastery Kit → Portrait Bundle → Portrait Masterclass.
       It sits BEFORE the proof of result so a visitor reads "this can be
       learned, step by step" before "this is what it looks like when
       learned". -->
  {portrait_path_section}

  <!-- 6 · BEFORE → AFTER: the answer to "what do the brushes actually change".
       Medium-width slider, not another full-bleed product band. -->
  {before_after}

  <!-- 7 · ONE "WHERE DO I GO NEXT?" BLOCK: the two curated rows share a single
       question as their heading, so the middle of the page reads as one decision
       point instead of two rival storefronts. "Popular starting points" = the
       packs people begin with; "Studio favorites" = what we keep reaching for.
       The old "Not sure where to start?" eyebrow and the identical h2 said the
       same thing twice — the question is now the h2, the two rows answer it. -->
  <section class="section" id="starting-points" aria-labelledby="sp-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Two ways in</p><h2 id="sp-title">Not sure where to start?</h2></div>
        <a class="text-link" href="products.html">Browse the full catalog →</a>
      </div>
      <p class="sec-note muted">Pick a small, focused pack — or pick one we keep reaching for ourselves. Both rows are instant downloads you can use on your next piece.</p>
      <div class="sub-head">
        <h3>Popular starting points</h3>
      </div>
      {product_grid(starting_points, 0)}
      <div class="sub-head sub-head--row">
        <h3>Studio favorites</h3>
        <a class="text-link" href="products.html">Browse all products →</a>
      </div>
      {feature_band(0)}
      {product_grid(featured_kits, 0, classes="grid cards cards-3")}
    </div>
  </section>

  <!-- 8 · PROCREATE BUNDLES: a value ladder (Starter → Advanced → Ultimate →
       Master Library), not a tile grid ordered by price.
       data/discovery.json → bundleLadder owns the rungs. -->
  {bundle_ladder_section}

  <!-- 9 · MASTER LIBRARY: Level 4 — the ladder's top rung, broken out so the
       library gets a real argument instead of a fourth card. -->
  {flagship_band(0, bridge=True, ladder_href="#bundles")}

  <!-- 10 · WHY DIGIKITPRO -->
  <section class="section section-alt">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">Why artists choose DigiKitPro</p><h2>Tools that respect your craft</h2></div></div>
      <div class="grid why-grid">
        <div class="why"><h3>Hand-tested on real artwork</h3><p class="muted">Every brush is drawn, tuned and re-tuned on actual portrait and illustration work before release, never bulk-generated.</p></div>
        <div class="why"><h3>Organized by workflow</h3><p class="muted">Kits follow the order you actually paint in: sketch, ink, blend, texture, finish. Less hunting, more creating.</p></div>
        <div class="why"><h3>Instant, lifetime access</h3><p class="muted">Payhip delivers your .brushset seconds after checkout, with a permanent download link in your inbox.</p></div>
        <div class="why"><h3>Made for Apple Pencil</h3><p class="muted">Pressure and tilt behavior tuned for the iPad + Apple Pencil, on Procreate 5 and newer.</p></div>
      </div>
    </div>
  </section>

  <!-- 11 · ARTICLES -->
  <section class="section">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">The blog</p><h2>Procreate Guides & Techniques</h2></div>
        <a class="text-link" href="blog.html">All articles →</a>
      </div>
      <div class="grid arts-grid">{art_cards}</div>
    </div>
  </section>

  <!-- 12 · FREE BRUSH EMAIL CTA: last on the page on purpose — it is the
       low-commitment exit for a visitor who has read the pitch and still is not
       buying, and nothing competes with it after. The articles sit above it as
       free value, so the page ends on "take this" rather than "read more".

       REAL REVIEWS belongs between WHY DIGIKITPRO (10) and this block, the
       moment verifiable quotes exist. It is deliberately NOT built: no
       placeholder quotes, no star ratings, no review counts — tools/verify.py
       fails the build on invented social proof, and an empty "Reviews" heading
       is a worse signal than no heading. Add plain attributed text here when
       you have it. See README → "Social proof", docs/AUDIT-AND-PLAN.md Part 13. -->
  {newsletter(0)}

</main>
"""
    html_out += footer(0)
    write("index.html", html_out)

# ─────────────────────────── PRODUCTS INDEX ───────────────────────────
def build_products():
    counts = {}
    for p in PRODUCTS: counts[p["category"]] = counts.get(p["category"], 0) + 1
    # Owner decision (2026-09-13): planners, journals, templates and the travel
    # guide stay mixed into the single catalog. No separate filter, no separate
    # page, no note calling them out. The __procreate / __lifestyle filters are
    # still supported by js/main.js and cards still carry data-line, so adding
    # the chips back later is a one-line change here - nothing is hard to undo.
    featured_count = sum(1 for p in PRODUCTS if p.get("featured") or p.get("badge"))
    n_flagship = sum(1 for p in PRODUCTS if tier_of(p) == "flagship")
    chips = f'<button class="chip active" type="button" data-filter="all">All ({len(PRODUCTS)})</button>'
    chips += f'<button class="chip" type="button" data-filter="__featured">Featured ({featured_count})</button>'
    if n_flagship:
        chips += f'<button class="chip chip-gold" type="button" data-filter="__flagship">Master Library ({n_flagship})</button>'
    chips += f'<button class="chip chip-free" type="button" data-filter="__free">Free ({sum(1 for p in PRODUCTS if p["free"])})</button>'
    for c in CATEGORIES:
        if counts.get(c):
            chips += f'<button class="chip" type="button" data-filter="{esc(c)}" id="{ "cat-"+c.replace(" ","%20") }">{esc(c)} ({counts[c]})</button>'

    # VALUE LADDER ORDER. Was: free first, then "featured", then alphabetical —
    # which put 28 identically-priced $5 packs in one undifferentiated wall and
    # buried the flagship. Now: free (Level 1) → flagship (Level 4) → bundles
    # (Level 3) → specialist packs (Level 2) → education (Level 5) → everything
    # else, each group ordered by editorial priority then price. Same products,
    # nothing hidden, nothing removed — just an order that answers "what first?".
    _tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    _group_rank = {"free": 0, "flagship": 1, "bundle": 2, "entry": 3, "education": 4}
    ordered = sorted(PRODUCTS, key=lambda p: (
        _group_rank.get(tier_of(p), 9),
        -(disc(p["slug"]).get("priority") or 0),
        -(p.get("featured") or 0),
        p.get("price") or 0,
        p["name"]))
    html_out = head("All Procreate Brushes & Digital Art Tools | DigiKitPro",
        f"Browse the complete DigiKitPro catalog: {len(PRODUCTS)} Procreate brush kits, bundles, palettes and digital resources, filter by category.",
        SITE_URL + "/products.html", 0, ctx=page_ctx("catalog"),
        schemas=schema_breadcrumb([("Home","/"),("Products","/products.html")]) + schema_itemlist(PRODUCTS))
    html_out += header(0, active="products.html")
    html_out += f"""
<main id="main">
  {page_head(0, "The complete catalog", "Every Brush. Every Kit. One Store.", 
    f"All {len(PRODUCTS)} DigiKitPro products, hand-tested for Procreate on iPad. Ordered as a value ladder: free packs first, then the Master Library, bundles and specialist kits.",
    [("Products","products.html")])}
  {trust_band(0)}
  <section class="section">
    <div class="wrap">
      <p class="catalog-cta">Browse every kit — <a href="products.html">filter by category to find your workflow →</a></p>
      {trend_topics()}
      <div class="filter-bar" role="toolbar" aria-label="Filter products by category">{chips}</div>
      {product_grid(ordered, 0, eager_first=4)}
      <p class="muted empty-note" data-empty-note hidden>No products match this filter yet, try another category.</p>
    </div>
  </section>
  {newsletter(0)}
</main>
"""
    html_out += footer(0)
    write("products.html", html_out)

# ─────────────────────────── FREEBIES ───────────────────────────
def build_freebies():
    html_out = head("Free Procreate Brushes | DigiKitPro",
        "Download free professional Procreate resources: 100 fine liner brushes, 20+ chalk brushes and a 1,200-swatch color vault. No cost, instant delivery.",
        SITE_URL + "/freebies.html", 0, ctx=page_ctx("freebies"),
        schemas=schema_breadcrumb([("Home","/"),("Free Brushes","/freebies.html")]))
    html_out += header(0, active="freebies.html")
    html_out += f"""
<main id="main">
  {page_head(0, "$0, forever", "Free Procreate Brushes & Assets",
    "Professional-grade tools, completely free. Download instantly, keep forever, and judge the quality for yourself before you spend anything.",
    [("Free Brushes","freebies.html")])}
  {freebie_download_row(0)}
  {freebie_gate(0, source="freebies")}
  <section class="section"><div class="wrap narrow">
    <h2>Why we give professional tools away</h2>
    <p>Great tools shouldn't be gated. Every freebie in this collection is built to the same standard as our paid kits, hand-tuned pressure curves, real-media texture, and organized .brushset installs. If they become part of your daily workflow (we think they will), the <a href="products.html">full catalog</a> is waiting when you're ready.</p>
    <p>New here? Start with the <a href="products/free-fine-liner-brushes-100/">100-brush Fine Liner set</a>, then grab the <a href="products/free-color-vault-1200-swatches/">1,200-swatch Color Vault</a> so you never stall on color again.</p>
  </div></section>
</main>
"""
    html_out += footer(0)
    write("freebies.html", html_out)

# ─────────────────────────── BUNDLES ───────────────────────────
def build_bundles():
    bundles = [p for p in PRODUCTS if p["category"] == "Bundles"]
    order = ["master-library-2000-brushes", "procreate-mega-bundle-650", "master-vault-1000-brushes",
             "ultimate-portrait-mastery-bundle", "brush-palette-bundle-160", "christmas-brushes-bundle"]
    bundles.sort(key=lambda p: order.index(p["slug"]) if p["slug"] in order else 99)
    tiles = ""
    for p in bundles:
        im = p["images"]
        rows = ""
        if p.get("bundleContents"):
            for b in p["bundleContents"]:
                rows += f"<li><span>{esc(b['name'])}</span><span class=\"muted\">{esc(b['count'])}</span></li>"
            rows = f'<ul class="bundle-list">{rows}</ul>'
        tiles += f"""<article class="bundle-panel">
  <div class="bundle-media">
    <img src="{asset_file(0, p['slug'], im.get('main',''))}" width="{im.get('fullW') or 1200}" height="{im.get('fullH') or 800}" alt="{esc(p['name'])}" loading="lazy" decoding="async">
  </div>
  <div class="bundle-body">
    <span class="badge">{esc(badge_text(p) or 'Bundle')}</span>
    <h2>{esc(p['name'])}</h2>
    <p class="lead-sm">{esc(p['short'])}</p>
    {rows}
    <div class="bundle-cta">
      <span class="price price-lg">{p['priceText']}</span>
      <a class="btn btn-gold" href="products/{p['slug']}/">View Product</a>
      <a class="text-link" href="{p['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(p, 'bundles-page')}>Buy on Payhip ↗</a>
    </div>
    {trust_bridge(0)}
  </div>
</article>"""
    html_out = head("Procreate Bundles | DigiKitPro",
        "High-value Procreate bundles: complete brush libraries, portrait workflow bundles and seasonal packs, up to 2,000+ brushes in one download.",
        SITE_URL + "/bundles.html", 0, ctx=page_ctx("bundles"),
        schemas=schema_breadcrumb([("Home","/"),("Bundles","/bundles.html")]))
    html_out += header(0, active="bundles.html")
    html_out += f"""
<main id="main">
  {page_head(0, "Best value", "Procreate Bundles",
    "Complete libraries at a fraction of their combined price. One download, every tool, lifetime access, the fastest way to build a professional brush library.",
    [("Bundles","bundles.html")])}
  <section class="section"><div class="wrap bundle-stack">{tiles}</div></section>
  {newsletter(0)}
</main>
"""
    html_out += footer(0)
    write("bundles.html", html_out)
