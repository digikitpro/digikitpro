#!/usr/bin/env python3
"""Homepage, products index, bundles, freebies, thank-you page.

The homepage is a result-first storefront (owner direction, 2026-09-18 exact
reorder): hero with ONE finished artwork and the trust row → before/after
visual proof directly under it → four best-seller cards ("Start With What
You Actually Need") → shop-by-workflow discovery ("What Do You Create?") →
free resources led by the Starter Guide ("Try DigiKitPro Before You Buy") →
the portrait journey ($0 → focused kit → bundle → Masterclass) → the bundle
ladder ("Want More Than One Kit?") → the Master Library feature → why
DigiKitPro → the honest community-art placeholder (empty slots, never fake
proof) → three guides → the free starter pack email CTA → footer.
Section order is pinned by tools/verify.py.

Buyer's path: see it (hero art) → believe it (before/after) → find it
(best sellers + workflow cards) → try it (free) → start it (journey) → go
deeper (bundle ladder → library) → trust it (why) → stay connected (email).

The Find My Brush Kit was removed in full on 2026-09-18 (page, both scripts,
nav entry, homepage links). The post-signup thank-you page — which used to be
built by tools/pages_finder.py because it shared a module, not because it is
finder logic — lives here now and is unchanged in behavior.
"""
from core import *

def page_head(depth, eyebrow, title, lead, crumbs_items=None, lead_html=None):
    c = crumbs(depth, crumbs_items) if crumbs_items else ""
    lead = lead_html if lead_html else f'<p class="lead">{lead}</p>' if lead else ""
    return ('<section class="page-head"><div class="wrap">' + c +
            f'<p class="eyebrow">{eyebrow}</p><h1>{title}</h1>{lead}</div></section>')

# ─────────────────────────── HOME ───────────────────────────
def build_home():
    byslug = BY_SLUG

    # ── Hero artwork: ONE large finished portrait, not a wall of covers ──
    # The right half of the hero is a single piece of finished artwork (the
    # portrait painted with the best-selling skin kit) that links straight to
    # the product: what it is → who it is for → where to go next. Same image
    # as the <link rel="preload"> below, so it stays the LCP element.
    hero_p = byslug.get("portrait-skin-brushes-procreate")
    hero_art = ""
    if hero_p:
        im = hero_p["images"]
        hw, hh = im.get("fullW") or 1400, im.get("fullH") or 1766
        hero_art = (
            f'<div class="hero-showcase hero-showcase--single" data-parallax="10">'
            f'<a class="hero-card h1 hero-card--link" href="products/{hero_p["slug"]}/" '
            f'style="--hero-ar:{hw}/{hh}">'
            f'<img src="{asset_file(0, hero_p["slug"], im.get("main", ""))}" width="{hw}" height="{hh}" '
            f'alt="{esc(hero_p["name"])} — finished portrait painted with the kit" '
            f'loading="eager" fetchpriority="high" decoding="async">'
            f'<span class="hero-cap">Painted with the {esc(hero_p["name"])}<b>View the kit →</b></span>'
            f'</a></div>')

    # ── Popular: the four leading kits, one per workflow ────────────────
    # Best-seller spotlight + six-card wall became a 4-card gallery row
    # (2026-09-18 reorder): the kits a new visitor actually starts with, each
    # focused on one workflow. Cards carry View Product AND Payhip Buy Now
    # (dual_buy, entry-tier only), badges and Pinterest Save like everywhere.
    popular = [byslug[s] for s in (
        "portrait-skin-brushes-procreate",
        "portrait-mastery-kit-46-brushes",
        "essential-line-art-sketch-kit",
        "watercolor-studio-kit-50-brushes",
    ) if s in byslug]

    # ── Free row: the Starter Guide leads, then the three $0 kits ───────
    starter = byslug.get("procreate-starter-guide-free-ebook")
    freebies = [p for p in PRODUCTS if p["free"] and not p.get("comingSoon") and p["category"] != "Guides & eBooks"]
    free_row = ([starter] if starter else []) + freebies

    # ── PORTRAIT JOURNEY: $0 → focused tool → kit → bundle → Masterclass ─
    # One horizontal path on desktop, a vertical timeline on mobile. Every
    # step is a real product with its live price/assets from products.json;
    # only the stage label ("Free", "Portrait skin", ...) is merchandising
    # copy. Rung labels kept short so the progression reads at a glance.
    JOURNEY = [
        ("Free", "procreate-starter-guide-free-ebook"),
        ("Portrait skin", "portrait-skin-brushes-procreate"),
        ("Portrait workflow", "portrait-mastery-kit-46-brushes"),
        ("Complete", "ultimate-portrait-mastery-bundle"),
        ("Masterclass", "procreate-portrait-masterclass-ebook"),
    ]
    journey_steps = ""
    ji = 0
    for label, slug in JOURNEY:
        p = byslug.get(slug)
        if not p or p.get("comingSoon"):
            continue
        ji += 1
        im = p.get("images") or {}
        card = im.get("card") or im.get("main") or ""
        u = f"products/{p['slug']}/"
        name = p["name"].split(" (")[0]
        price = "Free" if p["free"] else esc(p["priceText"])
        final = slug == JOURNEY[-1][1]
        if p["free"]:
            cta = (f'<a class="btn btn-line btn-sm" href="{esc(p["payhipUrl"])}" target="_blank" rel="noopener" '
                   f'{buy_attrs(p, "journey")}>Get Free ↗</a>')
        elif final:
            cta = f'<a class="btn btn-gold btn-sm" href="{u}">Explore the Masterclass</a>'
        else:
            cta = f'<a class="btn btn-line btn-sm" href="{u}">View Product</a>'
        journey_steps += f"""<li class="journey-step{' journey-step--final' if final else ''}">
  <span class="journey-rung"><i aria-hidden="true">{ji}</i>{esc(label)}</span>
  <div class="card-img">
  <a class="journey-media" href="{u}" tabindex="-1" aria-hidden="true"{pin_attrs(p)}>
    <img src="{asset_file(0, p['slug'], card)}"{img_srcset(0, p['slug'], im, "(min-width: 1080px) 220px, 88vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="" loading="lazy" decoding="async">
  </a>{pin_button(p) if PINTEREST_URL else ""}
  </div>
  <div class="journey-body">
    <h3><a href="{u}">{esc(name)}</a></h3>
    <p class="journey-meta muted">{esc(p.get('assets') or '')}</p>
    <div class="journey-foot"><span class="price">{price}</span>{cta}</div>
  </div>
</li>"""
    journey_section = ""
    if ji >= 4:
        journey_section = f"""<section class="section section-alt" id="journey" aria-labelledby="journey-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">The portrait path</p><h2 id="journey-title">From First Portrait to Finished Portrait</h2></div>
      <a class="text-link" href="blog/procreate-portrait-workflow/">Read the portrait workflow →</a>
    </div>
    <p class="sec-note muted">A simple path from learning the basics to building a complete portrait workflow. Start free — then add the tools when your portraits ask for them.</p>
    <ol class="journey">{journey_steps}</ol>
  </div>
</section>
"""

    bundle_ladder_section = bundle_ladder(
        0, section_cls="section", eyebrow="Bundles & libraries",
        title="Want More Than One Kit?",
        lead_rest="choose the collection that fits how you create. Every rung below says "
                  "exactly what it adds and who it is for — a bigger library is not "
                  "automatically the better buy, the right rung is.")

    # ── Before / After: the visual proof, moved directly under the hero ──
    # Interactive comparison slider (js/motion.js + css/style.css "MOTION
    # SYSTEM"). The visitor sees the transformation BEFORE being asked to
    # browse a catalog. Swap assets/img/ba-before.webp / ba-after.webp for
    # real client artwork whenever you like; keep the same size and crop.
    skin = byslug.get("portrait-skin-brushes-procreate")
    portrait_bundle = byslug.get("ultimate-portrait-mastery-bundle")
    skin_cta = ""
    bundle_cta = ""
    if skin:
        skin_cta = (
            f'<a class="btn btn-gold" href="products/{skin["slug"]}/" {buy_attrs(skin, "before-after")}>'
            f'Shop the tools used in this artwork <span class="btn-arr">·</span> {esc(skin["priceText"])}</a>'
        )
    if portrait_bundle:
        bundle_cta = (
            f'<a class="btn btn-line" href="products/{portrait_bundle["slug"]}/">'
            f'Or take the full portrait bundle →</a>'
        )
    before_after = f"""<section class="section ba-section" id="results" aria-labelledby="results-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Visual proof</p><h2 id="results-title">See the difference the right tools can make</h2></div>
        <a class="text-link" href="products/portrait-mastery-kit-46-brushes/">See the portrait kit →</a>
      </div>
      <p class="sec-note muted">Same artwork — different texture, detail and finishing tools. Drag the divider to see what pores, freckles, hair strands and the final polish add, and why the finished portrait stops looking airbrushed.</p>
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
      <ol class="ba-steps" aria-label="What the tools add, in paint order">
        <li>Skin texture</li><li>Pores</li><li>Freckles</li><li>Hair</li><li>Final polish</li>
      </ol>
      <div class="ba-cta">{skin_cta}{bundle_cta}</div>
    </div>
  </section>
"""

    # ── Articles: pinned editorial order (product-adjacent guides first) ─
    _img_articles = [a for a in load_articles() if a.get("image")]
    _by_aslug = {a.get("slug"): a for a in _img_articles}
    _pinned = ("best-procreate-brushes-for-beginners",
               "best-procreate-brushes-for-line-art",
               "best-procreate-brushes-for-anime")
    articles = [_by_aslug[s] for s in _pinned if s in _by_aslug]
    for a in _img_articles:  # safety net if a pinned slug ever gets renamed
        if len(articles) >= 3:
            break
        if a not in articles:
            articles.append(a)
    articles = articles[:3]
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
        "Hand-tested Procreate brushes organized around the way you actually create — portraits, skin, line art, watercolor, anime and more. Start free, then build the toolkit you need.",
        SITE_URL + "/", 0, schemas=schema_org_home(), ctx=page_ctx("home"),
        preload="assets/products/portrait-skin-brushes-procreate/portrait-skin-brushes-procreate.webp")
    html_out += header(0, active="index.html")
    html_out += f"""
<main id="main">
  <!-- 1 · HERO: short and commercial — one value proposition, two CTAs
       (Shop All Brushes / Try Free Brushes), ONE finished artwork on the
       right, trust row under the buttons. -->
  <section class="hero">
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">Premium Procreate brushes · organized by workflow</p>
        <h1>Procreate Brushes<br>for <em>iPad Artists</em></h1>
        <p class="hero-sub">Hand-tested portrait, skin, line art, watercolor and anime kits. Instant download, lifetime access — and free packs to try before you spend a cent.</p>
        <div class="hero-ctas">
          <a class="btn btn-gold btn-lg" href="products.html">Shop All Brushes</a>
          <a class="btn btn-line btn-lg" href="freebies.html">Try Free Brushes</a>
        </div>
        <p class="hero-meta">Secure checkout via Payhip &nbsp;·&nbsp; Instant worldwide delivery &nbsp;·&nbsp; Lifetime access &nbsp;·&nbsp; Free packs, no email needed</p>
      </div>
      {hero_art}
    </div>
  </section>

  <!-- 2 · VISUAL PROOF: before → after, directly under the hero. The
       transformation comes before any catalog browsing. -->
  {before_after}

  <!-- 3 · POPULAR / BEST SELLERS: four focused kits, gallery-style cards
       with View Product + Payhip Buy Now. No spotlight wall, no ten-card
       pile — this is where "start with what you need" is answered. -->
  <section class="section" id="popular" aria-labelledby="pop-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Best sellers</p><h2 id="pop-title">Start With What You Actually Need</h2></div>
        <a class="text-link" href="products.html">Browse all {len(PRODUCTS)} products →</a>
      </div>
      <p class="sec-note muted">Focused tools for specific workflows. No giant brush pile required — every kit below is a real product with its own page, live price and Payhip checkout.</p>
      {product_grid(popular, 0, classes="grid cards cards-4", dual_buy=True)}
    </div>
  </section>

  <!-- 4 · SHOP BY WORKFLOW ("What Do You Create?"): discovery by intent,
       one artwork per route. Built from data/discovery.json + CRAFT_ART. -->
  {craft_grid(0)}

  <!-- 5 · FREE PROCREATE RESOURCES: the Starter Guide first, then the $0
       kits. "Get Free" goes straight to Payhip — generous, not a teaser. -->
  <section class="section" id="free" aria-labelledby="free-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Completely free</p><h2 id="free-title">Try DigiKitPro Before You Buy</h2></div>
        <a class="text-link" href="freebies.html">All freebies →</a>
      </div>
      <p class="sec-note muted">Try real Procreate resources before spending anything — the same pressure tuning and file quality as the paid packs. Download now, keep forever, and only spend money once you know how they feel.</p>
      {product_grid(free_row, 0, free_direct=True, classes="grid cards cards-4")}
    </div>
  </section>

  <!-- 6 · PORTRAIT JOURNEY: the portrait funnel as a path, not a pile —
       free guide → focused kit → full kit → bundle → Masterclass. -->
  {journey_section}

  <!-- 7 · PROCREATE BUNDLES ("Want More Than One Kit?"): the value ladder
       only AFTER the visitor has seen focused kits and the portrait path.
       data/discovery.json → bundleLadder owns the rungs. -->
  {bundle_ladder_section}

  <!-- 8 · MASTER LIBRARY FEATURE: the advanced option — one library, nine
       workflows as scannable chips, Compare Bundles as the second CTA. -->
  {flagship_band(0, bridge=True, ladder_href="#bundles", home=True)}

  <!-- 9 · WHY DIGIKITPRO: trust AFTER products and results, four factual
       blocks with quiet stroke icons. -->
  <section class="section" id="why" aria-labelledby="why-title">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">Why artists choose DigiKitPro</p><h2 id="why-title">Tools That Respect Your Craft</h2></div></div>
      <div class="grid why-grid">
        <div class="why"><span class="why-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20l1.4-4.3L15.6 5.5a2.05 2.05 0 0 1 2.9 0l1 1a2.05 2.05 0 0 1 0 2.9L9.3 19.6 4 20z"/><path d="m13.8 7.4 3.8 3.8"/></svg></span><h3>Hand-tested on real artwork</h3><p class="muted">Every brush is drawn, tuned and re-tuned on actual portrait and illustration work before release, never bulk-generated.</p></div>
        <div class="why"><span class="why-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 12.5 9 5 9-5"/><path d="m3 16.5 9 5 9-5"/></svg></span><h3>Organized by workflow</h3><p class="muted">Kits follow the order you actually paint in: sketch, ink, blend, texture, finish. Less hunting, more creating.</p></div>
        <div class="why"><span class="why-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v11"/><path d="m7 9.5 5 5 5-5"/><path d="M4 21h16"/></svg></span><h3>Instant, lifetime access</h3><p class="muted">Payhip delivers your .brushset seconds after checkout, with a permanent download link in your inbox.</p></div>
        <div class="why"><span class="why-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="13" height="17" rx="2.5"/><path d="m19.4 8.4 1.9 1.9a1.5 1.5 0 0 1 0 2.1l-3.9 3.9-2.3.3.3-2.3 3.9-3.9a.1.1 0 0 1 .1 0z"/></svg></span><h3>Made for Apple Pencil</h3><p class="muted">Pressure and tilt behavior tuned for the iPad + Apple Pencil, on Procreate 5 and newer.</p></div>
      </div>
    </div>
  </section>

  <!-- 10 · CUSTOMER ART / SOCIAL PROOF — honest placeholder, populated
       only with genuine, permission-granted artist work.
       STORE RULE: no invented quotes, no stock "customer" photos, no
       manufactured ratings. tools/verify.py fails the build on fabricated
       social proof (the empty .quote-slot figures below are its documented
       placeholder shape and are excluded from that scan as placeholders,
       never as proof). Until real artwork exists, the slots display the
       invitation — an empty, clearly-marked frame beats fake proof.
       TO PUBLISH A REAL PIECE: replace one .proof-slot figure with the
       artwork, the artist's own handle (with their permission) and a link
       to their profile or shop. Keep the others as slots. -->
  <section class="section section-alt" id="proof" aria-labelledby="proof-title">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">Community</p><h2 id="proof-title">Made for Real Artwork</h2></div></div>
      <p class="sec-note muted">This space is reserved for finished pieces painted with DigiKitPro kits. Nothing appears here until a real artist shares real work and says we may show it — we would rather keep it empty than fake proof. Painting with our brushes? Tag <b>@digikitprostudio</b> on Instagram or pin your work on Pinterest, and tell us we may feature it here.</p>
      <div class="grid proof-grid">
        <figure class="proof-slot quote-slot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-4.5-4.5L6 21"/></svg><b>Your artwork here</b><span>Reserved for a DigiKitPro artist — shared with permission.</span></figure>
        <figure class="proof-slot quote-slot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-4.5-4.5L6 21"/></svg><b>Your artwork here</b><span>Reserved for a DigiKitPro artist — shared with permission.</span></figure>
        <figure class="proof-slot quote-slot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-4.5-4.5L6 21"/></svg><b>Your artwork here</b><span>Reserved for a DigiKitPro artist — shared with permission.</span></figure>
      </div>
      <div class="proof-cta">
        <a class="btn btn-line btn-sm" href="{esc(INSTAGRAM_PROFILE)}" target="_blank" rel="noopener">Share on Instagram ↗</a>
        <a class="btn btn-line btn-sm" href="{esc(PINTEREST_URL)}" target="_blank" rel="noopener">Share on Pinterest ↗</a>
      </div>
    </div>
  </section>

  <!-- 11 · LEARN PROCREATE: three guides, beginners → line art → anime,
       ordered to connect naturally to the products above. -->
  <section class="section" id="articles" aria-labelledby="articles-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">The blog</p><h2 id="articles-title">Learn Procreate. Create Better.</h2></div>
        <a class="text-link" href="blog.html">All articles →</a>
      </div>
      <div class="grid arts-grid">{art_cards}</div>
    </div>
  </section>

  <!-- 12 · FREE STARTER PACK EMAIL CTA: the final invitation — one
       low-commitment exit after everything, never an aggressive popup. -->
  {newsletter(0)}

</main>
"""
    html_out += footer(0)
    write("index.html", html_out)

# ───────────────────── THANK-YOU PAGE (post-signup delivery) ─────────────
# Moved here from tools/pages_finder.py on 2026-09-18 when the Brush Finder
# was removed: this page is the free-download delivery page for every email
# capture on the site (the newsletter's `_next`), not finder logic. Its two
# jobs, in this order: DELIVER the promised free files, then make ONE
# starter offer and show the flagship. Never more than one ask per level.

def _compat(p):
    """Compatibility statement, derived from the product's own requirement
    text so we never claim support that is not in the data."""
    hay = " ".join((p.get("requirements") or []) + (p.get("technical") or [])
                   + [p.get("category", ""), p.get("short", "")]).lower()
    if "goodnotes" in hay or "notability" in hay:
        return "GoodNotes, Notability & compatible PDF note apps"
    if "canva" in hay:
        return "Canva (editable templates)"
    if "procreate" in hay or "ipad" in hay:
        return "Procreate on iPad (Procreate 5 or newer)"
    if p.get("category") in ("Other", "Guides & eBooks"):
        return "See the requirements on the product page"
    return "Procreate on iPad"


def build_thanks():
    depth = 0
    freebies = [p for p in PRODUCTS if p.get("free") and not p.get("comingSoon")]
    freebies.sort(key=lambda p: -(disc(p["slug"]).get("priority") or 0))

    cards = ""
    for p in freebies:
        im = p.get("images") or {}
        card = im.get("card", "")
        cards += f'''<article class="thanks-card" data-thanks-slug="{esc(p["slug"])}">
  <a class="thanks-media" href="{rel(depth, 'products/' + p['slug'] + '/')}">
    <img src="{asset_file(depth, p['slug'], card)}"{img_srcset(depth, p['slug'], im, "(min-width: 1100px) 320px, 92vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(p.get('alt') or p['name'])}" loading="lazy" decoding="async">
  </a>
  <div class="thanks-body">
    <span class="badge badge-free">Free</span>
    <h2>{esc(p['name'])}</h2>
    <p class="muted">{esc(p.get('assets') or '')}</p>
    <a class="btn btn-gold btn-sm" href="{p['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(p, 'thanks')}>Get Free ↗</a>
  </div>
</article>'''

    # ONE starter offer: the highest-priority paid specialist pack.
    entries = [p for p in PRODUCTS
               if not p.get("free") and tier_of(p) == "entry" and line_of(p) == "procreate"]
    entries.sort(key=lambda p: -(disc(p["slug"]).get("priority") or 0))
    starter = entries[0] if entries else None
    starter_html = ""
    if starter:
        im = starter.get("images") or {}
        starter_html = f'''<section class="section section-alt" aria-labelledby="starter-title">
  <div class="wrap starter-inner">
    <div class="starter-media">
      <a href="{rel(depth, 'products/' + starter['slug'] + '/')}">
        <img src="{asset_file(depth, starter['slug'], im.get('card',''))}"{img_srcset(depth, starter['slug'], im, "(min-width: 960px) 340px, 92vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(starter.get('alt') or starter['name'])}" loading="lazy" decoding="async">
      </a>
    </div>
    <div class="starter-body">
      <p class="eyebrow">Your next step</p>
      <h2 id="starter-title">{esc(starter['name'])}</h2>
      <p class="muted">{esc(starter.get('short',''))}</p>
      <ul class="tick-list check">
        <li>{esc(starter.get('assets') or 'Complete specialist set')}</li>
        <li>{esc(_compat(starter))}</li>
        <li>Instant download, lifetime access</li>
      </ul>
      <div class="starter-cta">
        <span class="price price-lg">{esc(starter['priceText'])}</span>
        <a class="btn btn-gold" href="{starter['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(starter, 'thanks-starter')}>Buy Now ↗</a>
        <a class="text-link" href="{rel(depth, 'products/' + starter['slug'] + '/')}">See what is inside →</a>
      </div>
      <p class="muted starter-note">Not yet? No pressure at all — the free packs above are yours to keep, and the
        <a href="{rel(depth, 'products.html')}">full catalog</a> is waiting when you are ready.</p>
    </div>
  </div>
</section>'''

    html_out = head(
        "Thank You — Your Free Procreate Downloads | DigiKitPro",
        "Your free Procreate brushes are ready to download right now, plus the recommended next step for your workflow.",
        SITE_URL + "/thank-you.html", depth,
        schemas=schema_breadcrumb([("Home", "/"), ("Thank you", "/thank-you.html")]),
        ctx=page_ctx("thankyou"))
    # Thank-you pages should be reachable but not compete for ranking.
    html_out = html_out.replace(
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        '<meta name="robots" content="noindex, follow">', 1)
    html_out += header(depth)
    html_out += f"""
<main id="main">
  <section class="page-head thanks-head"><div class="wrap">
    <p class="eyebrow">You are on the list</p>
    <h1 data-thanks-title>Your free Procreate downloads are ready</h1>
    <p class="lead" data-thanks-lead>Grab them right here — no need to wait for an email. Every file below is free,
      delivered instantly by Payhip, and yours to keep.</p>
    <p class="muted thanks-mail" data-thanks-mail>We have also sent a confirmation to your inbox. If it does not appear
      in a few minutes, check spam, or just use the links below.</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="grid thanks-grid">{cards}</div>
  </div></section>

  {starter_html}

  {flagship_band(depth)}

  <section class="section"><div class="wrap narrow">
    <div class="sec-head"><div><p class="eyebrow">While you are here</p><h2>Learn the workflow</h2></div></div>
    <p class="muted">Brushes are half of it. These guides show the same tools used on finished artwork, step by step.</p>
    <ul class="thanks-links">
      <li><a href="{rel(depth,'blog/procreate-portrait-workflow/')}">The complete Procreate portrait workflow →</a></li>
      <li><a href="{rel(depth,'blog/how-to-install-procreate-brushes/')}">How to install .brushset files on iPad →</a></li>
      <li><a href="{rel(depth,'blog/how-to-choose-procreate-brushes/')}">How to choose brushes without regretting it →</a></li>
    </ul>
  </div></section>
</main>
"""
    html_out += footer(depth)

    # Tiny inline script: the only page-specific JS on the site. It reads the
    # ?lead= parameter set by the signup form and puts the promised pack first,
    # so the page matches what the visitor actually asked for.
    html_out = html_out.replace("</body>", """<script>
(function(){
  try{
    var lead=new URLSearchParams(location.search).get('lead');
    if(!lead)return;
    var card=document.querySelector('[data-thanks-slug="'+CSS.escape(lead)+'"]');
    if(card&&card.parentNode)card.parentNode.insertBefore(card,card.parentNode.firstChild);
    var t=document.querySelector('[data-thanks-title]');
    var name=card?card.querySelector('h2'):null;
    if(t&&name)t.textContent='Your download is ready: '+name.textContent;
    var m=document.querySelector('[data-thanks-mail]');
    if(m)m.hidden=true;
  }catch(e){}
})();
</script>
</body>""", 1)
    write("thank-you.html", html_out)

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
    chips += f'<button class="chip" type="button" data-filter="__under10">Under $10 ({sum(1 for p in PRODUCTS if not p["free"] and p.get("price", 0) < 10)})</button>'
    chips += f'<button class="chip" type="button" data-filter="__starter">Starter Kits ({sum(1 for p in PRODUCTS if tier_of(p) == "entry")})</button>'
    chips += f'<button class="chip" type="button" data-filter="__bundles">Bundles ({sum(1 for p in PRODUCTS if tier_of(p) == "bundle")})</button>'
    if n_flagship:
        chips += f'<button class="chip chip-gold" type="button" data-filter="__flagship">Complete Libraries ({n_flagship})</button>'
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
  <div class="bundle-media"{pin_attrs(p)}>
    <img src="{asset_file(0, p['slug'], im.get('main',''))}" width="{im.get('fullW') or 1200}" height="{im.get('fullH') or 800}" alt="{esc(p['name'])}" loading="lazy" decoding="async">{pin_button(p)}
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
  <section class="section"><div class="wrap">
    <p style="margin-bottom:1.75rem"><a class="text-link" href="guides/procreate-bundles-compared/">Compare every bundle side by side →</a></p>
  </div><div class="wrap bundle-stack">{tiles}</div></section>
  {newsletter(0)}
</main>
"""
    html_out += footer(0)
    write("bundles.html", html_out)
