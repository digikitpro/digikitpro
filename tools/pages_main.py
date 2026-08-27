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
        showcase += f'<figure class="hero-card h{i+1}"><img src="{asset_file(0, p["slug"], im.get("main",""))}" width="{im.get("fullW") or 1200}" height="{im.get("fullH") or 800}" alt="{esc(p["name"])}" loading="{"eager" if i==0 else "lazy"}" fetchpriority="{"high" if i==0 else "auto"}" decoding="async"><figcaption>{esc(p["name"])}</figcaption></figure>'

    freebies = [p for p in PRODUCTS if p["free"] and not p.get("comingSoon") and p["category"] != "Guides & eBooks"]
    featured = sorted([p for p in PRODUCTS if p.get("featured")], key=lambda x: x["featured"])[:8]
    bundles = [p for p in PRODUCTS if p["category"] == "Bundles"]
    bundles.sort(key=lambda p: p["price"])

    # studio eBooks, live on Payhip: free starter first, then the masterclass
    ebooks = sorted([p for p in PRODUCTS if p["category"] == "Guides & eBooks"], key=lambda x: x["price"])
    ebook_cards = ""
    for e in ebooks:
        im = e["images"]
        e_label = "Masterclass" if str(e.get("badge") or "").strip().lower() == "new" else e.get("badge")
        e_badge = ('<span class="badge badge-free">Free</span>' if e["free"]
                   else (f'<span class="badge">{esc(e_label)}</span>' if e_label else ""))
        e_cta = "Get Free ↗" if e["free"] else "Buy Now ↗"
        ebook_cards += f"""<article class="ebook-card">
  <a class="ebook-cover" href="products/{e['slug']}/">
    <img src="{asset_file(0, e['slug'], im.get('card',''))}" width="{im.get('cardW') or 1200}" height="{im.get('cardH') or 800}" alt="{esc(e['name'])}: cover" loading="lazy" decoding="async">
  </a>
  <div class="ebook-body">
    {e_badge}
    <h3>{esc(e['name'])}</h3>
    <p class="muted">{esc(e['short'])}</p>
    <div class="ebook-foot">
      <span class="price">{"Free" if e["free"] else e["priceText"]}</span>
      <a class="btn btn-gold btn-sm" href="{e['payhipUrl']}" target="_blank" rel="noopener">{e_cta}</a>
      <a class="text-link" href="products/{e['slug']}/">Details →</a>
    </div>
  </div>
</article>"""

    ebook_section = ""
    if ebooks:
        ebook_section = f"""<section class="section" id="ebooks">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">From the studio</p><h2>Learn Procreate Portraits with Our eBooks</h2></div>
        <p class="sec-note muted">Start with the free guide, then go deep with the Masterclass.</p>
      </div>
      <div class="ebook-duo">{ebook_cards}</div>
    </div>
  </section>
"""

    cat_counts = {}
    for p in PRODUCTS: cat_counts[p["category"]] = cat_counts.get(p["category"], 0) + 1
    free_n = sum(1 for p in PRODUCTS if p["free"])
    cat_chips = f'<a class="cat-pill pill-all" href="products.html">All <b>{len(PRODUCTS)}</b></a>'
    cat_chips += f'<a class="cat-pill pill-free" href="freebies.html">Free <b>{free_n}</b></a>'
    cat_chips += "".join(
        f'<a class="cat-pill" href="products.html#{cat_slug(c)}">{esc(c)} <b>{cat_counts[c]}</b></a>'
        for c in CATEGORIES if cat_counts.get(c))
    # second, identical half of the marquee track (aria-hidden, no extra tab stops)
    cat_chips_dup = cat_chips.replace('<a class="cat-pill', '<a tabindex="-1" class="cat-pill')

    bundle_cards = ""
    for p in bundles[:4]:
        im = p["images"]
        bundle_cards += f"""<a class="bundle-tile" href="products/{p['slug']}/">
  <img src="{asset_file(0, p['slug'], im.get('card',''))}"{img_srcset(0, p['slug'], im, "(min-width: 1100px) 300px, 90vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(p['name'])}" loading="lazy" decoding="async">
  <div class="bundle-tile-body">
    <span class="badge">{esc(p.get('badge') or 'Bundle')}</span>
    <h3>{esc(p['name'])}</h3>
    <p class="muted">{esc(p['assets'] or '')}</p>
    <span class="price">{p['priceText']}</span>
  </div>
</a>"""

    # ── Trending in Procreate & digital art ──────────────────────────────
    # Auto-rotating daily: keeps the homepage fresh for returning visitors and
    # crawlers while always pointing at best-sellers, bundles and freebies.
    featured_all = sorted([p for p in PRODUCTS if p.get("featured")], key=lambda x: (x["featured"], x["name"]))
    trending_pool = (featured_all + [p for p in PRODUCTS if p.get("badge")]
                     + [p for p in PRODUCTS if p["category"] == "Bundles"] + [p for p in PRODUCTS if p["free"]])
    seen, trending = set(), []
    for p in trending_pool:
        if p["slug"] not in seen:
            seen.add(p["slug"]); trending.append(p)
    if len(trending) < 4:
        trending += [p for p in PRODUCTS if p["slug"] not in seen]
    day = date.today().toordinal()
    trending = trending[day % len(trending):] + trending[:day % len(trending)]
    trending = trending[:4]
    trend_cards = product_grid(trending, 0)

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
        "DigiKitPro, Professional Procreate Tools for Artists",
        "Premium Procreate brushes and digital art resources for iPad artists: portrait, skin, line art, watercolor, anime & more. Create more. Search less.",
        SITE_URL + "/", 0, schemas=schema_org_home(), preload="assets/products/portrait-skin-brushes-procreate/portrait-skin-brushes-procreate.webp")
    html_out += header(0, active="index.html")
    html_out += f"""
<main id="main">
  <section class="hero">
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">Procreate brush studio</p>
        <h1>Professional Procreate Tools for Artists</h1>
        <p class="hero-sub">Create more. Search less. Hand-tested brushes for portraits, illustration and storytelling, built for the iPad and Apple Pencil.</p>
        <div class="hero-ctas">
          <a class="btn btn-gold" href="products.html">Explore Brushes</a>
          <a class="btn btn-line" href="#free">Get Free Brushes</a>
        </div>
        <p class="hero-meta">Instant download · Procreate 5+ · Apple Pencil ready</p>
      </div>
      <div class="hero-showcase" aria-hidden="true">{showcase}</div>
    </div>
  </section>

  {trust_band(0)}

  <section class="section" id="free">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Completely free</p><h2>Free Procreate Brushes</h2></div>
        <a class="text-link" href="freebies.html">All freebies →</a>
      </div>
      {product_grid(freebies, 0, eager_first=1)}
    </div>
  </section>

  {ebook_section}
  <section class="section section-alt">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Most loved</p><h2>Featured Brush Kits</h2></div>
        <a class="text-link" href="products.html">Browse all {len(PRODUCTS)} products →</a>
      </div>
      {product_grid(featured, 0)}
    </div>
  </section>

  <section class="section section-alt" id="trending" aria-labelledby="trending-title">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">What artists are searching</p><h2 id="trending-title">Trending in Procreate &amp; Digital Art</h2></div>
        <a class="text-link" href="products.html">Browse the full catalog →</a>
      </div>
      {trend_topics()}
      {trend_cards}
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Find your tool</p><h2>Shop by Category</h2></div>
        <a class="text-link" href="products.html">All {len(PRODUCTS)} products →</a>
      </div>
    </div>
    <div class="cat-marquee" aria-label="Browse product categories">
      <div class="cat-track">
        <div class="cat-half">{cat_chips}</div>
        <div class="cat-half" aria-hidden="true">{cat_chips_dup}</div>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">High value</p><h2>Procreate Bundles</h2></div>
        <a class="text-link" href="bundles.html">Compare bundles →</a>
      </div>
      <div class="grid bundles-grid">{bundle_cards}</div>
    </div>
  </section>

  <section class="section">
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

  <section class="section section-alt">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">The blog</p><h2>Procreate Guides & Techniques</h2></div>
        <a class="text-link" href="blog.html">All articles →</a>
      </div>
      <div class="grid arts-grid">{art_cards}</div>
    </div>
  </section>

  {newsletter(0)}
</main>
"""
    html_out += footer(0)
    write("index.html", html_out)

# ─────────────────────────── PRODUCTS INDEX ───────────────────────────
def build_products():
    counts = {}
    for p in PRODUCTS: counts[p["category"]] = counts.get(p["category"], 0) + 1
    featured_count = sum(1 for p in PRODUCTS if p.get("featured") or p.get("badge"))
    chips = f'<button class="chip active" type="button" data-filter="all">All ({len(PRODUCTS)})</button>'
    chips += f'<button class="chip" type="button" data-filter="__featured">Trending ({featured_count})</button>'
    chips += f'<button class="chip chip-free" type="button" data-filter="__free">Free ({sum(1 for p in PRODUCTS if p["free"])})</button>'
    for c in CATEGORIES:
        if counts.get(c):
            chips += f'<button class="chip" type="button" data-filter="{esc(c)}" id="{ "cat-"+c.replace(" ","%20") }">{esc(c)} ({counts[c]})</button>'

    ordered = sorted(PRODUCTS, key=lambda p: (0 if p["free"] else 1, -(p.get("featured") or 0), p["name"]))
    html_out = head("All Procreate Brushes & Digital Art Tools, DigiKitPro",
        f"Browse the complete DigiKitPro catalog: {len(PRODUCTS)} Procreate brush kits, bundles, palettes and digital resources, filter by category.",
        SITE_URL + "/products.html", 0,
        schemas=schema_breadcrumb([("Home","/"),("Products","/products.html")]) + schema_itemlist(PRODUCTS))
    html_out += header(0, active="products.html")
    html_out += f"""
<main id="main">
  {page_head(0, "The complete catalog", "Every Brush. Every Kit. One Store.", 
    f"All {len(PRODUCTS)} DigiKitPro products, hand-tested for Procreate on iPad. Filter by craft, or hit the free section first.",
    [("Products","products.html")])}
  {trust_band(0)}
  <section class="section">
    <div class="wrap">
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
    freebies = [p for p in PRODUCTS if p["free"]]
    html_out = head("Free Procreate Brushes, DigiKitPro Freebies",
        "Download free professional Procreate resources: 100 fine liner brushes, 20+ chalk brushes and a 1,200-swatch color vault. No cost, instant delivery.",
        SITE_URL + "/freebies.html", 0, schemas=schema_breadcrumb([("Home","/"),("Free Brushes","/freebies.html")]))
    html_out += header(0, active="freebies.html")
    cards = product_grid(freebies, 0, eager_first=1)
    html_out += f"""
<main id="main">
  {page_head(0, "$0, forever", "Free Procreate Brushes & Assets",
    "Professional-grade tools, completely free. Download instantly, keep forever, and see why thousands of artists trust DigiKitPro brushes in their daily work.",
    [("Free Brushes","freebies.html")])}
  <section class="section"><div class="wrap">{cards}</div></section>
  <section class="section section-alt"><div class="wrap narrow">
    <h2>Why we give professional tools away</h2>
    <p>Great tools shouldn't be gated. Every freebie in this collection is built to the same standard as our paid kits, hand-tuned pressure curves, real-media texture, and organized .brushset installs. If they become part of your daily workflow (we think they will), the <a href="products.html">full catalog</a> is waiting when you're ready.</p>
    <p>New here? Start with the <a href="products/free-fine-liner-brushes-100/">100-brush Fine Liner set</a>, then grab the <a href="products/free-color-vault-1200-swatches/">1,200-swatch Color Vault</a> so you never stall on color again.</p>
  </div></section>
  {newsletter(0)}
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
    <img class="fit{" contain" if (im.get("fullH") or 0) > (im.get("fullW") or 0) else ""}" src="{asset_file(0, p['slug'], im.get('main',''))}" width="{im.get('fullW') or 1200}" height="{im.get('fullH') or 800}" alt="{esc(p['name'])}" loading="lazy" decoding="async">
  </div>
  <div class="bundle-body">
    <span class="badge">{esc(p.get('badge') or 'Bundle')}</span>
    <h2>{esc(p['name'])}</h2>
    <p class="lead-sm">{esc(p['short'])}</p>
    {rows}
    <div class="bundle-cta">
      <span class="price price-lg">{p['priceText']}</span>
      <a class="btn btn-gold" href="{p['payhipUrl']}" target="_blank" rel="noopener">Buy on Payhip</a>
      <a class="text-link" href="products/{p['slug']}/">Full details →</a>
    </div>
  </div>
</article>"""
    html_out = head("Procreate Bundles, Mega Brush Collections | DigiKitPro",
        "High-value Procreate bundles: complete brush libraries, portrait workflow bundles and seasonal packs, up to 2,000+ brushes in one download.",
        SITE_URL + "/bundles.html", 0, schemas=schema_breadcrumb([("Home","/"),("Bundles","/bundles.html")]))
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
