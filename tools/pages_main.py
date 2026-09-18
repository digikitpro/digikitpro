#!/usr/bin/env python3
"""Homepage, products index, bundles, freebies, thank-you page.

The homepage is a product-first storefront (owner direction, 2026-09-18):
a short commercial hero, buying assurances, popular product cards near the
top, shop-by-workflow, the bundle ladder, the Master Library, the free
packs, the Starter Guide + Portrait Masterclass pair, the before/after
demonstration, and only then the supporting trust and educational content.
Section order is pinned by tools/verify.py.

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

    # ── Hero showcase: three real product covers (the storefront's window
    #    display). Same slugs as before the refocus — proven picks, and all
    #    three still render with un-cropped covers (object-fit:contain).
    showcase_slugs = ["portrait-skin-brushes-procreate", "artista-studio-kit-76-brushes", "watercolor-studio-kit-50-brushes"]
    showcase = ""
    for i, s in enumerate(showcase_slugs):
        p = byslug[s]; im = p["images"]
        _hw, _hh = im.get("fullW") or 1200, im.get("fullH") or 800
        showcase += f'<figure class="hero-card h{i+1}" style="--hero-ar:{_hw}/{_hh}"><img src="{asset_file(0, p["slug"], im.get("main",""))}" width="{im.get("fullW") or 1200}" height="{im.get("fullH") or 800}" alt="{esc(p["name"])}" loading="{"eager" if i==0 else "lazy"}" fetchpriority="{"high" if i==0 else "auto"}" decoding="async"><figcaption>{esc(p["name"])}</figcaption></figure>'

    # ── Popular product cards: the six packs the storefront leads with.
    #    Hand-picked slugs (the old "popular starting points" + "studio
    #    favorites" rows, merged): curated, stable, and every one of them a
    #    live product with a real price and Payhip checkout. The best seller
    #    gets the compact spotlight above the grid (see core.feature_band).
    popular = [byslug[s] for s in (
        "portrait-mastery-kit-46-brushes",
        "essential-line-art-sketch-kit",
        "artista-studio-kit-76-brushes",
        "anime-soft-style-studio-kit",
        "watercolor-studio-kit-50-brushes",
        "ultimate-portrait-mastery-bundle",
    ) if s in byslug]

    freebies = [p for p in PRODUCTS if p["free"] and not p.get("comingSoon") and p["category"] != "Guides & eBooks"]

    # ── LEARN: free starter guide → paid masterclass, side by side ───────
    # Large, un-cropped covers (object-fit:contain on a premium dark mat),
    # premium card styling, and a stronger emphasis for the paid Masterclass
    # (gold edge, wider column, primary CTA). The connector between the cards
    # is the funnel: start free, then go deeper.
    starter = byslug.get("procreate-starter-guide-free-ebook")
    master = byslug.get("procreate-portrait-masterclass-ebook")
    ebook_section = ""
    if starter and master:
        def edu_card(p, level_cls, level_label, desc, meta, cta_label, cta_href, cta_ext, cta_cls):
            im = p["images"]
            name = p["name"].split(" (")[0]
            return f"""<article class="ebook-card edu-card {level_cls}">
  <a class="ebook-cover" href="products/{p['slug']}/"{pin_attrs(p)}>
    <img src="{asset_file(0, p['slug'], im.get('card',''))}" width="{im.get('cardW') or 750}" height="{im.get('cardH') or 1000}" alt="{esc(name)}: cover" loading="lazy" decoding="async">
  </a>{pin_button(p)}
  <div class="ebook-body">
    <p class="edu-level">{esc(level_label)}</p>
    <h3>{esc(name)}</h3>
    <p class="edu-desc muted">{esc(desc)}</p>
    <div class="ebook-foot">
      <span class="price price-lg">{"Free" if p["free"] else esc(p["priceText"])}</span>
      <a class="btn {cta_cls}" href="{cta_href}"{cta_ext}>{cta_label}</a>
    </div>
    <p class="edu-meta">{esc(meta)}</p>
  </div>
</article>"""
        starter_card = edu_card(
            starter, "edu-start", "Free · Start here",
            "The free Portrait Starter Guide — a structured introduction to Procreate portrait basics on a blank canvas.",
            "PDF eBook · instant download · $0 forever",
            "Get Free Guide ↗", starter["payhipUrl"], ' target="_blank" rel="noopener" ' + buy_attrs(starter, "edu-duo"), "btn-line")
        master_card = edu_card(
            master, "edu-deep", "Premium · Full workflow",
            "The Complete Procreate Portrait Masterclass — 107 pages, 15 chapters, full portrait workflow from blank canvas to finished believable portrait.",
            "PDF eBook · 107 pages · 15 chapters · $19",
            "Explore the Masterclass", f"products/{master['slug']}/", "", "btn-gold btn-lg")
        # ── homepage Look Inside preview (real interiors when present) ──────
        import os as _os
        _look_dir = _os.path.join(ROOT, "assets/products/procreate-portrait-masterclass-ebook")
        _look_files = []
        if _os.path.isdir(_look_dir):
            for _f in sorted(_os.listdir(_look_dir)):
                if _f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) and (_f in ("0.jpg","1.jpg","2.jpg","3.jpg","4.jpg","0.png","1.png","2.png","3.png","4.png") or _f.startswith("look-")):
                    if _f.startswith("procreate-portrait-masterclass"):
                        continue
                    _look_files.append(_f)
        if _look_files:
            _look_note = f"Real page spreads from inside the book — {len(_look_files)} interior pages now live in <a href=\"products/{master['slug']}/#look-inside\">Look Inside</a> on the Masterclass page."
            _look_preview = "<div class=\"look-home-preview\">" + "".join(f'<a href="products/{master["slug"]}/#look-inside" aria-label="Look inside — {esc(_f)}"><img src="assets/products/procreate-portrait-masterclass-ebook/{esc(_f)}" alt="Masterclass interior — {esc(_f)}" loading="lazy" decoding="async" width="260" height="346"></a>' for _f in _look_files[:5]) + "</div>"
        else:
            _look_note = "Start with the free guide. Then learn the complete workflow — real page spreads from inside the book below (4 real interior images coming soon)."
            _look_preview = ""
        ebook_section = f"""<section class="section section-alt" id="ebooks" aria-labelledby="edu-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Learn the craft</p><h2 id="edu-title">Learn Procreate Portraits</h2></div>
        <p class="sec-note muted">{_look_note}</p>
      </div>
      <div class="ebook-duo">{starter_card}<div class="edu-link" aria-hidden="true"><span class="edu-arrow">→</span><span class="edu-label">then go deeper</span></div>{master_card}</div>
      {_look_preview}
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
        <div><p class="eyebrow">See the difference</p><h2 id="results-title">See the difference the right tools can make</h2></div>
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
        "Hand-tested Procreate brushes organized around the way you actually create — portraits, skin, line art, watercolor, anime and more. Start free, then build the toolkit you need.",
        SITE_URL + "/", 0, schemas=schema_org_home(), ctx=page_ctx("home"),
        preload="assets/products/portrait-skin-brushes-procreate/portrait-skin-brushes-procreate.webp")
    html_out += header(0, active="index.html")
    html_out += f"""
<main id="main">
  <!-- 1 · HERO: short and commercial — one value proposition, two CTAs
       (Shop All Brushes / Try Free Brushes), the window-display covers. -->
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
      <div class="hero-showcase" aria-hidden="true" data-parallax="10">{showcase}</div>
    </div>
  </section>

  <!-- 2 · BUYING ASSURANCES: checkout, delivery, access, free packs —
       statements the store already makes, verifiable in-repo. -->
  {trust_band(0)}

  <!-- 3 · POPULAR: best-seller spotlight + the six packs the store leads
       with. Products lead: a storefront shows the goods before the story. -->
  <section class="section" id="popular" aria-labelledby="pop-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Start here</p><h2 id="pop-title">Popular Procreate Brushes</h2></div>
        <a class="text-link" href="products.html">Browse all {len(PRODUCTS)} products →</a>
      </div>
      <p class="sec-note muted">The packs painters reach for first — real kits from the full catalog, each with its own product page, live price and Payhip checkout.</p>
      {feature_band(0)}
      {product_grid(popular, 0, eager_first=1, classes="grid cards cards-3")}
    </div>
  </section>

  <!-- 4 · SHOP BY WORKFLOW: route by the artist's intent, not our file
       structure. Cards are generated from data/discovery.json. -->
  {craft_grid(0)}

  <!-- 5 · PROCREATE BUNDLES: a value ladder (Starter → Advanced → Ultimate
       → Master Library), not a tile grid ordered by price.
       data/discovery.json → bundleLadder owns the rungs; the heading link
       goes to the full side-by-side comparison guide. -->
  {bundle_ladder_section}

  <!-- 6 · MASTER LIBRARY: the ladder's top rung, broken out so the library
       gets a real argument instead of a fourth card. -->
  {flagship_band(0, bridge=True, ladder_href="#bundles")}

  <!-- 7 · FREE PROCREATE BRUSHES: "Get Free" goes straight to Payhip. -->
  <section class="section" id="free">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Completely free</p><h2>Free Procreate Brushes</h2></div>
        <a class="text-link" href="freebies.html">All freebies →</a>
      </div>
      <p class="sec-note muted">Try the tools before you buy anything. Real kits, not samples — the same pressure tuning and file quality as the paid packs. Download now, keep forever, and only spend money once you know how they feel.</p>
      {product_grid(freebies, 0, eager_first=1, free_direct=True, classes="grid cards cards-3")}
    </div>
  </section>

  <!-- 8 · LEARN PROCREATE PORTRAITS: free starter guide → paid masterclass,
       side by side. Large covers, premium cards, the paid Masterclass gets
       the stronger emphasis. -->
  {ebook_section}

  <!-- 9 · BEFORE → AFTER: the answer to "what do the brushes actually
       change". Medium-width slider, not another full-bleed product band. -->
  {before_after}

  <!-- 10 · WHY DIGIKITPRO: supporting trust content, after the products. -->
  <section class="section section-alt" id="why" aria-labelledby="why-title">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">Why artists choose DigiKitPro</p><h2 id="why-title">Tools that respect your craft</h2></div></div>
      <div class="grid why-grid">
        <div class="why"><h3>Hand-tested on real artwork</h3><p class="muted">Every brush is drawn, tuned and re-tuned on actual portrait and illustration work before release, never bulk-generated.</p></div>
        <div class="why"><h3>Organized by workflow</h3><p class="muted">Kits follow the order you actually paint in: sketch, ink, blend, texture, finish. Less hunting, more creating.</p></div>
        <div class="why"><h3>Instant, lifetime access</h3><p class="muted">Payhip delivers your .brushset seconds after checkout, with a permanent download link in your inbox.</p></div>
        <div class="why"><h3>Made for Apple Pencil</h3><p class="muted">Pressure and tilt behavior tuned for the iPad + Apple Pencil, on Procreate 5 and newer.</p></div>
      </div>
    </div>
  </section>

  <!-- 11 · ARTICLES: supporting educational content. -->
  <section class="section" id="articles" aria-labelledby="articles-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">The blog</p><h2 id="articles-title">Procreate Guides & Techniques</h2></div>
        <a class="text-link" href="blog.html">All articles →</a>
      </div>
      <div class="grid arts-grid">{art_cards}</div>
    </div>
  </section>

  <!-- 12 · FREE BRUSH EMAIL CTA: last on the page on purpose — it is the
       low-commitment exit for a visitor who has read the pitch and still is
       not buying, and nothing competes with it after. The articles sit
       above it as free value, so the page ends on "take this" rather than
       "read more".

       REAL REVIEWS belongs between WHY DIGIKITPRO (10) and this block, the
       moment verifiable quotes exist. It is deliberately NOT built: no
       placeholder quotes, no star ratings, no review counts — tools/verify.py
       fails the build on invented social proof, and an empty "Reviews"
       heading is a worse signal than no heading. Add plain attributed text
       here when you have it. See README → "Social proof", docs/AUDIT-AND-PLAN.md Part 13. -->
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
