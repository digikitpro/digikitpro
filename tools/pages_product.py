#!/usr/bin/env python3
"""Individual product pages."""
import re
from core import *

def _demote_headings(htmlsrc):
    """h2->h3, h1->h3 inside shop copy (page already has h1/h2 structure)."""
    htmlsrc = re.sub(r"<h2(\s[^>]*)?>", r"<h3\1>", htmlsrc or "", flags=re.I)
    htmlsrc = re.sub(r"</h2>", "</h3>", htmlsrc, flags=re.I)
    htmlsrc = re.sub(r"<h1(\s[^>]*)?>", r"<h3\1>", htmlsrc, flags=re.I)
    htmlsrc = re.sub(r"</h1>", "</h3>", htmlsrc, flags=re.I)
    return htmlsrc

def gallery_html(p):
    im = p["images"]
    slug = p["slug"]
    main = im["main"]
    items = [(main, im.get("fullW"), im.get("fullH"), p["name"])]
    for g in im.get("gallery", []):
        items.append((g["file"], g.get("w"), g.get("h"), f'{p["name"]}: preview {items and len(items)}'))
    if not items: return "", ""
    first = items[0]
    srcset = img_srcset(2, slug, im, "(min-width: 960px) 46vw, 100vw")
    main_fig = f"""<figure class="gal-main">
      <img data-gal-main src="{asset_file(2, slug, first[0])}"{srcset} width="{first[1] or 1200}" height="{first[2] or 800}" alt="{esc(first[3])}" fetchpriority="high" decoding="async">
    </figure>"""
    thumbs = ""
    if len(items) > 1:
        btns = []
        for i, (f, w, h, alt) in enumerate(items):
            g = next((x for x in ([{"file": main, "card": im.get("card")}] + im.get("gallery", [])) if x["file"] == f), None)
            th = g.get("card", f) if g else f
            btns.append(f'<button class="gal-thumb{" active" if i==0 else ""}" type="button" data-gal-thumb data-full="{asset_file(2, slug, f)}" data-alt="{esc(alt)}" data-w="{w or 1200}" data-h="{h or 800}" aria-label="View image {i+1}"><img src="{asset_file(2, slug, th)}" width="{g.get("cardW") or 150}" height="{g.get("cardH") or 100}" alt="{esc(alt)} thumbnail" loading="lazy" decoding="async"></button>')
        thumbs = f'<div class="gal-thumbs">{"".join(btns)}</div>'
    return main_fig + thumbs, (first[0] if is_abs(first[0]) else absurl(f"assets/products/{slug}/{first[0]}"))

def faq_html(p):
    if not p.get("faqs"): return ""
    items = "".join(f"""<details class="faq-item">
      <summary>{esc(f['q'])}</summary>
      <div class="faq-body"><p>{esc(f['a'])}</p></div>
    </details>""" for f in p["faqs"])
    return f"""<section class="psec" aria-labelledby="p-faq"><h2 id="p-faq">FAQ</h2>{items}</section>"""

def li_block(title, items, cls="check"):
    if not items: return ""
    lis = "".join(f"<li>{esc(i)}</li>" for i in items)
    tid = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return f"""<section class="psec" aria-labelledby="p-{tid}"><h2 id="p-{tid}">{esc(title)}</h2><ul class="tick-list {cls}">{lis}</ul></section>"""

def tech_block(p):
    """Technical Details as a key/value spec table (colon items become rows)."""
    items = p.get("technical")
    if not items: return ""
    rows = ""
    for i in items:
        k, sep, v = i.partition(":")
        if sep and v.strip():
            rows += f"<tr><th>{esc(k.strip())}</th><td>{esc(v.strip())}</td></tr>\n"
        else:
            rows += f'<tr><td colspan="2">{esc(i)}</td></tr>\n'
    return ("""<section class="psec" aria-labelledby="p-tech">"""
            """<h2 id="p-tech">Technical Details</h2>"""
            f'<table class="spec-table">{rows}</table></section>')

def build_product_pages():
    for p in PRODUCTS:
        slug = p["slug"]; depth = 2
        im = p["images"]
        gal, og_img = gallery_html(p)
        schemas = schema_product(p) + schema_breadcrumb([("Home","/"),("Products","/products.html"),(p["name"], f"/products/{slug}/")])
        schemas += [{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in p.get("faqs",[])]}] if p.get("faqs") else schemas

        href_cc = f'https://creativecommons.org'
        features = li_block("Why You'll Love It", p.get("features"), cls="gold")
        included = li_block("What's Included", p.get("included"))
        technical = tech_block(p)
        requirements = li_block("Requirements", p.get("requirements"), cls="plain")
        whofor = ""
        if p.get("perfectFor"):
            chips = "".join(f'<span class="tag">{esc(t)}</span>' for t in p["perfectFor"])
            whofor = f"""<section class="psec" aria-labelledby="p-for"><h2 id="p-for">Who It's For</h2><div class="tag-row">{chips}</div></section>"""
        desc = _demote_headings(p.get("descriptionHtml", ""))
        desc_sec = f"""<section class="psec richtext" aria-labelledby="p-about"><h2 id="p-about">About This Product</h2><div class="prose">{desc}</div></section>""" if desc.strip() else ""

        bundle_block = ""
        if p.get("bundleContents"):
            rows = "".join(f'<li><span>{esc(b["name"])}</span><span class="muted">{esc(b["count"])}</span></li>' for b in p["bundleContents"])
            bundle_block = f"""<section class="psec" aria-labelledby="p-bundle"><h2 id="p-bundle">Inside the Bundle</h2><ul class="bundle-list">{rows}</ul></section>"""

        related = [BY_SLUG[r] for r in p.get("related", []) if r in BY_SLUG] or [x for x in PRODUCTS if x["category"] == p["category"] and x["slug"] != slug][:4]
        related = related[:4]
        rel_grid = product_grid(related, depth)

        # related guides (articles that teach with this product)
        try:
            arts = [a for a in load_articles() if slug in (a.get("products") or [])]
        except NameError:
            arts = []
        rel_arts = ""
        if arts:
            links = "".join(f'<a class="text-link" href="../../blog/{a["slug"]}/">{esc(a["title"])}</a>' for a in arts[:4])
            rel_arts = f"""<section class="psec" aria-labelledby="p-guides">
      <div class="sec-head"><div><p class="eyebrow">Learn the technique</p><h2 id="p-guides">Related Guides</h2></div></div>
      <div class="rel-arts">{links}</div>
    </section>"""

        coming = bool(p.get("comingSoon"))
        cta_label = "View on Store" if coming else ("Download Free" if p["free"] else "Buy Now")
        price_html = '<span class="price price-free">Free</span>' if p["free"] else f'<span class="price price-lg">{p["priceText"]}</span>'
        if coming:
            price_html += '<span class="price-note muted"> · at launch</span>'
        if coming:
            badge = '<span class="badge badge-soon">Coming Soon</span>'
        else:
            _blabel = badge_text(p)
            badge = f'<span class="badge">{esc(_blabel)}</span>' if _blabel and not p["free"] else ('<span class="badge badge-free">Free</span>' if p["free"] else "")
        trust_items = (["Launches soon, right here on Payhip", "Newsletter subscribers get it first", "Procreate on iPad recommended"]
                       if coming else
                       ["Instant download via Payhip", "Lifetime access",
                        'Procreate on iPad required' if p['category'] not in ('Other', 'Guides & eBooks') else 'See requirements below'])
        trust = "".join(f"<li>{t}</li>" for t in trust_items)
        get_copy = ("Launches soon on our Payhip store. Join the newsletter below and you will be the first to know."
                    if coming else "Secure checkout on Payhip. Instant delivery to your email.")

        # badge chips row (status - assets - category), like the reference design
        status_chip = ('<span class="meta-chip soon">Coming Soon</span>' if coming else
                       ('<span class="meta-chip free">Free</span>' if p["free"] else
                        (f'<span class="meta-chip gold">{esc(badge_text(p))}</span>' if badge_text(p) else "")))
        assets_chip = f'<span class="meta-chip">{esc(p["assets"])}</span>' if p.get("assets") else ""
        cat_chip = (f'<a class="meta-chip cat" href="../../products.html#cat-{p["category"].replace(" ", "%20")}">'
                    f'{esc(p["category"])}</a>')
        chips_html = status_chip + assets_chip + cat_chip
        caption = ("Launches soon · Newsletter subscribers get it first · Opens the store in a new tab"
                   if coming else "Secure checkout on Payhip · Instant download · Opens in a new tab")
        cta_label_long = "Get Free Download" if p["free"] and not coming else cta_label
        buy_panel = f"""<div class="buy-panel">
          <div class="buy-top"><span class="buy-label">Price</span>{price_html}</div>
          <a class="btn btn-gold btn-lg" href="{p['payhipUrl']}" target="_blank" rel="noopener">{cta_label_long} <span class="btn-arr">↗</span></a>
          <p class="buy-cap">{caption}</p>
        </div>"""

        _og_img = asset_abs(slug, im.get("card", "")) if im.get("card", "") else absurl("assets/img/og-cover.jpg")
        _preload = asset_abs(slug, im.get("main", "")) if im.get("main", "") else None
        html_out = head(p["seoTitle"], p["seoDesc"], absurl(f"products/{slug}/"), depth,
                        schemas=schemas, og_image=_og_img, page_type="product", preload=_preload)
        html_out += header(depth, active="products.html")
        html_out += f"""
<main id="main">
  <div class="wrap">
    {crumbs(depth, [("Products","products.html"),(p["name"], f"products/{slug}/")])}
    <article class="pdp">
      <div class="pdp-media">{gal}</div>
      <div class="pdp-info">
        <div class="chip-row">{chips_html}</div>
        <h1>{esc(p['name'])}</h1>
        <p class="pdp-short">{esc(p['short'])}</p>
        {buy_panel}
        <ul class="pdp-trust">{trust}</ul>
      </div>
    </article>

    {features}
    {bundle_block}
    {included}
    {desc_sec}
    {technical}
    {requirements}
    {whofor}
    {faq_html(p)}
    {rel_arts}

    <section class="psec pdp-cta" aria-labelledby="p-get">
      <div>
        <h2 id="p-get">Get This Product</h2>
        <p class="muted">{get_copy}</p>
      </div>
      <a class="btn btn-gold btn-lg" href="{p['payhipUrl']}" target="_blank" rel="noopener">{cta_label} <span class="btn-arr">↗</span></a>
    </section>

    <section class="psec" aria-labelledby="p-related">
      <div class="sec-head"><div><p class="eyebrow">You may also like</p><h2 id="p-related">Related Products</h2></div></div>
      {rel_grid}
    </section>
  </div>
  {newsletter(depth)}
</main>
"""
        html_out += footer(depth)
        write(f"products/{slug}/index.html", html_out)

# category landing stub pages for breadcrumbs/SEO (products.html handles filtering)
