#!/usr/bin/env python3
"""Homepage, products index, bundles, freebies, thank-you page.

The homepage (2026-09-19 layout): hero → before/after proof → Starter Guide
& Masterclass (ebooks, medium 3:4 covers in horizontal book cards) → best
sellers → workflow discovery → bundle ladder → Master Library → free
resources → three guides → email CTA. Community (#proof) and Why (#why) sections
removed; ebooks section placed immediately after results; Pinterest footer
band removed. Section order is pinned by tools/verify.py.

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

    bundle_ladder_section = bundle_ladder(
        0, section_cls="section", eyebrow="Bundles & libraries",
        title="Want More Than One Kit?",
        lead_rest="choose the collection that fits how you create. Every rung below says "
                  "exactly what it adds and who it is for — a bigger library is not "
                  "automatically the better buy, the right rung is.")

    # ── Before / After: the visual proof ──
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

    # ── Starter Guide & Masterclass (ebooks) — immediately after results ──
    # Two horizontal book-feature cards: medium 3:4 cover left (framed, never
    # cropped — both covers carry baked-in titles to the edge), pitch + price
    # + CTAs right. Cover flags and step labels state facts from products.json
    # only. No interior preview images on the index page (covers only).
    ebooks_section = ""
    master_p = byslug.get("procreate-portrait-masterclass-ebook")
    # starter already fetched above; reuse
    if starter and master_p:
        # Starter card
        s_im = starter.get("images") or {}
        s_card = s_im.get("card") or s_im.get("main") or ""
        s_u = f"products/{starter['slug']}/"
        # Masterclass card
        m_im = master_p.get("images") or {}
        m_card = m_im.get("card") or m_im.get("main") or ""
        m_u = f"products/{master_p['slug']}/"
        ebooks_section = f"""<section class="section" id="ebooks" aria-labelledby="ebooks-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">Learn the craft</p><h2 id="ebooks-title">Starter Guide &amp; Masterclass</h2></div>
    </div>
    <p class="sec-note muted">Structured portrait learning for Procreate artists. Start free with the essentials, or step into the full 15-chapter masterclass.</p>
    <div class="ebooks-grid">
      <article class="ebook-card edu-start">
        <a class="ebook-cover" href="{s_u}" aria-label="{esc(starter['name'])}">
          <span class="ebook-frame"><img src="{asset_file(0, starter['slug'], s_card)}"{img_srcset(0, starter['slug'], s_im, "(min-width: 640px) 195px, 130px")} width="{s_im.get('cardW') or 750}" height="{s_im.get('cardH') or 1000}" alt="{esc(starter['name'])}" loading="lazy" decoding="async"></span>
          <span class="ebook-flag flag-free">Free</span>
        </a>
        <div class="ebook-body">
          <p class="edu-level">Step 1 · Beginner · Free</p>
          <h3><a href="{s_u}">{esc(starter['name'])}</a></h3>
          <p class="edu-desc muted">{esc(starter.get('short') or "Start your first believable portrait this week — a free visual guide from blank canvas to structured head study.")}</p>
          <div class="ebook-foot">
            <p class="edu-meta">PDF eBook · instant download</p>
            <span class="price price-free">Free</span>
            <a class="btn btn-gold btn-sm" href="{esc(starter['payhipUrl'])}" target="_blank" rel="noopener" {buy_attrs(starter, "ebooks")}>Get Free ↗</a>
            <a class="text-link" href="{s_u}">View guide →</a>
          </div>
        </div>
      </article>
      <article class="ebook-card edu-deep">
        <a class="ebook-cover" href="{m_u}" aria-label="{esc(master_p['name'])}">
          <span class="ebook-frame"><img src="{asset_file(0, master_p['slug'], m_card)}"{img_srcset(0, master_p['slug'], m_im, "(min-width: 640px) 195px, 130px")} width="{m_im.get('cardW') or 750}" height="{m_im.get('cardH') or 1000}" alt="{esc(master_p['name'])}" loading="lazy" decoding="async"></span>
          <span class="ebook-flag flag-gold">15 chapters</span>
        </a>
        <div class="ebook-body">
          <p class="edu-level">Step 2 · 15 chapters · 107 pages</p>
          <h3><a href="{m_u}">{esc(master_p['name'])}</a></h3>
          <p class="edu-desc muted">{esc(master_p.get('short') or "From blank canvas to believable portrait — a repeatable workflow you can reuse on every portrait after.")}</p>
          <div class="ebook-foot">
            <p class="edu-meta">PDF eBook · 15 chapters · lifetime access</p>
            <span class="price">{esc(master_p['priceText'])}</span>
            <a class="btn btn-line btn-sm" href="{m_u}">View Masterclass</a>
            <a class="text-link" href="{esc(master_p['payhipUrl'])}" target="_blank" rel="noopener" {buy_attrs(master_p, "ebooks")}>Buy on Payhip ↗</a>
          </div>
        </div>
      </article>
    </div>
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
  <!-- HERO: short and commercial — one value proposition, two CTAs, ONE finished artwork -->
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

  <!-- VISUAL PROOF: before → after -->
  {before_after}

  <!-- STARTER GUIDE & MASTERCLASS — immediately after results -->
  {ebooks_section}

  <!-- POPULAR / BEST SELLERS -->
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

  <!-- SHOP BY WORKFLOW -->
  {craft_grid(0)}

  <!-- PROCREATE BUNDLES -->
  {bundle_ladder_section}

  <!-- MASTER LIBRARY FEATURE -->
  {flagship_band(0, bridge=True, ladder_href="#bundles", home=True)}

  <!-- FREE PROCREATE RESOURCES -->
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

  <!-- LEARN PROCREATE: three guides -->
  <section class="section" id="articles" aria-labelledby="articles-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">The blog</p><h2 id="articles-title">Learn Procreate. Create Better.</h2></div>
        <a class="text-link" href="blog.html">All articles →</a>
      </div>
      <div class="grid arts-grid">{art_cards}</div>
    </div>
  </section>

  <!-- FREE STARTER PACK EMAIL CTA -->
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
        ctx=page_ctx("thankyou"),
        robots="noindex, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
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
