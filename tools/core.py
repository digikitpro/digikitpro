#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║ DigiKitPro, static site generator ║
║ ║
║ HOW TO EDIT THE SITE ║
║ • Products → edit /data/products.json, then run: python3 tools/build.py
║ • Articles → edit/add markdown files in /content/blog/, run build ║
║ • Domain → change SITE_URL below before publishing ║
║ • Email → set EMAIL_ENDPOINT below (or data-endpoint in HTML) ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import json, os, re, shutil, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── CONFIG ──────────────────────────────────────────────────────────────
# Your final domain (no trailing slash). Can also be injected by CI via the
# SITE_URL environment variable, the GitHub workflow does this automatically.
SITE_URL = os.environ.get("SITE_URL", "https://digikitpro.com").rstrip("/")
SITE_NAME = "DigiKitPro"
TAGLINE = "Professional Procreate tools for digital artists."
STORE_URL = "https://payhip.com/digikitpro"
EMAIL_TO = "digikitprostudio@gmail.com" # ← subscriber emails are delivered to this inbox
EMAIL_ENDPOINT = f"https://formsubmit.co/{EMAIL_TO}" # FormSubmit forwards every signup (one-time activation email)
# To switch providers later (Brevo/MailerLite/ConvertKit), paste their form-action URL here
# and the same form keeps working.
# ── Search Console verification tokens (paste once Google/Bing give them to you) ──
GOOGLE_VERIFY = os.environ.get("GOOGLE_VERIFY", "") # content of the <meta name="google-site-verification"> token
BING_VERIFY = os.environ.get("BING_VERIFY", "") # content of the <meta name="msvalidate.01"> token
BUILD_DATE = "2026-08-11"
SOCIAL = { # ← add your profiles; hidden while empty
    "Pinterest": "",
    "Instagram": "",
    "TikTok": "",
}
CATEGORIES = ["Portrait", "Skin Texture", "Line Art", "Sketching", "Watercolor", "Anime",
              "Hair", "Glitter & Effects", "Traditional", "Figure Drawing", "Bundles", "Guides & eBooks", "Other"]

PRODUCTS = json.load(open(os.path.join(ROOT, "data/products.json"), encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PRODUCTS}

# ── helpers ─────────────────────────────────────────────────────────────
def esc(t): return html.escape(str(t), quote=True)

def urljoin(*parts):
    return "/".join(p.strip("/") for p in parts)

def absurl(path):
    return SITE_URL + "/" + path.lstrip("/")

def rel(depth, path):
    """Relative url from a page at `depth` dirs deep."""
    prefix = "../" * depth
    return prefix + path.lstrip("/")

def money(p): return p["priceText"]

def card_img(p):
    im = p.get("images") or {}
    return f"assets/products/{p['slug']}/{im.get('card','') }", im.get("cardW"), im.get("cardH")

# ── schema ──────────────────────────────────────────────────────────────
def schema_org_home():
    return [
      {"@context":"https://schema.org","@type":"Organization","@id":SITE_URL+"/#org",
       "name":SITE_NAME,"url":SITE_URL,"logo":absurl("assets/img/logo.svg"),
       "description":"DigiKitPro creates premium Procreate brushes and digital art resources for iPad artists.",
       "sameAs":[STORE_URL]+[v for v in SOCIAL.values() if v]},
      {"@context":"https://schema.org","@type":"WebSite","@id":SITE_URL+"/#website",
       "url":SITE_URL,"name":SITE_NAME,"publisher":{"@id":SITE_URL+"/#org"},
       "potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint",
        "urlTemplate":SITE_URL+"/search.html?q={search_term_string}"},"query-input":"required name=search_term_string"}}
    ]

def schema_product(p):
    return [{"@context":"https://schema.org","@type":"Product",
       "name":p["name"],"image":absurl(f"assets/products/{p['slug']}/{(p.get('images') or {}).get('card','')}"),
       "description":p["short"],"brand":{"@type":"Brand","name":SITE_NAME},
       "url":absurl(f"products/{p['slug']}/"),
       "offers":{"@type":"Offer","price":f"{p['price']:.2f}","priceCurrency":"USD",
                 "availability":"https://schema.org/InStock","url":p["payhipUrl"],
                 "seller":{"@type":"Organization","name":SITE_NAME}}}]

def schema_breadcrumb(items):
    return [{"@context":"https://schema.org","@type":"BreadcrumbList",
             "itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":absurl(u)} for i,(n,u) in enumerate(items)]}]

def schema_article(a):
    return [{"@context":"https://schema.org","@type":"Article","headline":a["title"],
             "description":a["description"],"datePublished":a["date"],"dateModified":a["date"],
             "author":{"@type":"Organization","name":SITE_NAME,"url":SITE_URL},
             "publisher":{"@id":SITE_URL+"/#org"},
             "mainEntityOfPage":absurl(f"blog/{a['slug']}/")}]

# ── head / header / footer ──────────────────────────────────────────────
def head(title, desc, canonical, depth, schemas=None, og_image=None, page_type="website", preload=None):
    s = ""
    if schemas:
        for sc in schemas:
            s += f' <script type="application/ld+json">{json.dumps(sc, ensure_ascii=False)}</script>\n'
    pl = f' <link rel="preload" as="image" href="{rel(depth, preload)}" fetchpriority="high">\n' if preload else ""
    ogimg = absurl(og_image or "assets/img/og-cover.jpg")
    vmeta = ""
    if GOOGLE_VERIFY: vmeta += f'\n <meta name="google-site-verification" content="{esc(GOOGLE_VERIFY)}">'
    if BING_VERIFY: vmeta += f'\n <meta name="msvalidate.01" content="{esc(BING_VERIFY)}">'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{esc(canonical)}">{vmeta}
  <meta name="theme-color" content="#0A0A0C">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta property="og:type" content="{page_type}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{ogimg}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{ogimg}">
  <link rel="icon" type="image/svg+xml" href="{rel(depth,'assets/img/favicon.svg')}">
  <link rel="apple-touch-icon" href="{rel(depth,'assets/img/apple-touch-icon.png')}">
  <link rel="preload" href="{rel(depth,'assets/fonts/playfairdisplay-normal.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{rel(depth,'assets/fonts/manrope-normal.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{rel(depth,'css/style.css')}">
{pl} <script>window.DKP={{store:'{STORE_URL}',email:'{EMAIL_ENDPOINT}'}};</script>
  <script src="{rel(depth,'js/search-index.js')}" defer></script>
  <script src="{rel(depth,'js/main.js')}" defer></script>
{s}</head>
<body>
<noscript><div class="noscript-bar">JavaScript is off: every product page and guide still opens normally; only search and category filters need JS enabled.</div></noscript>
"""

NAV = [("Free Brushes","freebies.html"),("Products","products.html"),("Bundles","bundles.html"),
       ("Articles","blog.html"),("About","about.html")]

def header(depth, active=None):
    links = "".join(f'<a href="{rel(depth,u)}"{" class=\"active\"" if active==u else ""}>{n}</a>' for n,u in NAV)
    mlinks = "".join(f'<a href="{rel(depth,u)}">{n}</a>' for n,u in NAV)
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" data-header>
  <div class="wrap header-inner">
    <a class="brand" href="{rel(depth,'index.html')}" aria-label="{SITE_NAME} home">
      <svg class="brand-mark" width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true"><circle cx="16" cy="16" r="15" stroke="#C9A86A" stroke-width="1.4"/><path d="M11 22.5V9.5h4.4c3.9 0 6.6 2.7 6.6 6.5s-2.7 6.5-6.6 6.5H11Zm2.5-2.2h1.8c2.6 0 4.1-1.8 4.1-4.3s-1.5-4.3-4.1-4.3h-1.8v8.6Z" fill="#C9A86A"/></svg>
      <span class="brand-name">DigiKit<em>Pro</em></span>
    </a>
    <nav class="main-nav" aria-label="Primary">{links}</nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" data-search-open aria-label="Search products and articles">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      </button>
      <a class="btn btn-gold btn-sm" href="{STORE_URL}" target="_blank" rel="noopener">Shop Now</a>
      <button class="icon-btn menu-btn" type="button" data-menu-toggle aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </div>
  </div>
  <nav class="mobile-nav" id="mobile-menu" aria-label="Mobile">{mlinks}<a class="btn btn-gold" href="{STORE_URL}" target="_blank" rel="noopener">Shop the Store</a></nav>
</header>
<div class="search-overlay" data-search-overlay hidden>
  <div class="search-panel" role="dialog" aria-modal="true" aria-label="Site search">
    <div class="search-bar">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input type="search" placeholder="Search brushes, kits, articles…" data-search-input aria-label="Search">
      <button type="button" class="icon-btn" data-search-close aria-label="Close search">✕</button>
    </div>
    <div class="search-results" data-search-results></div>
  </div>
</div>
"""

def newsletter(depth, heading="Get Free Procreate Brushes", sub="Join the DigiKitPro list for free brush drops, new kit releases and iPad art tips. No spam, unsubscribe any time."):
    return f"""<section class="newsletter" id="newsletter">
  <div class="wrap">
    <div class="nl-card">
      <p class="eyebrow">Free download</p>
      <h2>{esc(heading)}</h2>
      <p class="muted nl-sub">{esc(sub)}</p>
      <!-- REAL CAPTURE: submissions are emailed to {EMAIL_TO} via FormSubmit
           (main.js posts with AJAX; without JS the form does a normal POST).
           One-time activation: FormSubmit emails {EMAIL_TO}, click "Activate" once
           and every signup afterwards lands directly in that inbox. -->
      <form class="nl-form" data-nl-form action="{EMAIL_ENDPOINT}" method="POST">
        <input type="hidden" name="_subject" value="New DigiKitPro subscriber">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="false">
        <label class="sr-only" for="nl-email">Email address</label>
        <input id="nl-email" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
        <button class="btn btn-gold" type="submit">Send me brushes</button>
        <p class="nl-note" data-nl-note>No spam. Unsubscribe anytime.</p>
      </form>
      <p class="nl-caption">Prefer to grab them now? <a href="{rel(depth,'freebies.html')}">Browse the free brush packs</a>.</p>
    </div>
  </div>
</section>
"""

def footer(depth):
    social = "".join(f'<a href="{v}" target="_blank" rel="noopener">{k}</a>' for k, v in SOCIAL.items() if v)
    social_block = f'<p class="foot-label">Follow</p><div class="foot-links">{social}</div>' if social else ""
    return f"""
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="foot-brand">
      <a class="brand" href="{rel(depth,'index.html')}"><span class="brand-name">DigiKit<em>Pro</em></span></a>
      <p class="muted">{TAGLINE}</p>
      <p class="foot-label">Store</p>
      <div class="foot-links"><a href="{STORE_URL}" target="_blank" rel="noopener">Payhip ↗</a></div>
    </div>
    <nav aria-label="Footer shop">
      <p class="foot-label">Shop</p>
      <div class="foot-links">
        <a href="{rel(depth,'freebies.html')}">Free Brushes</a>
        <a href="{rel(depth,'products.html')}">All Products</a>
        <a href="{rel(depth,'bundles.html')}">Bundles</a>
        <a href="{rel(depth,'products.html#cat-Portrait')}">Portrait Brushes</a>
        <a href="{rel(depth,'products.html#cat-Line%20Art')}">Line Art</a>
      </div>
    </nav>
    <nav aria-label="Footer learn">
      <p class="foot-label">Learn</p>
      <div class="foot-links">
        <a href="{rel(depth,'blog.html')}">Articles</a>
        <a href="{rel(depth,'blog/best-procreate-brushes-for-portraits/')}">Best Portrait Brushes</a>
        <a href="{rel(depth,'blog/how-to-create-realistic-skin-in-procreate/')}">Realistic Skin Guide</a>
        <a href="{rel(depth,'about.html')}">About</a>
      </div>
    </nav>
    <nav aria-label="Footer legal">
      <p class="foot-label">Company</p>
      <div class="foot-links">
        <a href="{rel(depth,'about.html#contact')}">Contact</a>
        <a href="{rel(depth,'privacy.html')}">Privacy Policy</a>
        <a href="{rel(depth,'terms.html')}">Terms</a>
      </div>
      {social_block}
    </nav>
  </div>
  <div class="wrap foot-bottom">
    <p>© {date.today().year} {SITE_NAME}. Digital products sold via Payhip. Procreate is a trademark of Savage Interactive.</p>
  </div>
</footer>
</body>
</html>
"""

def breadcrumbs(depth, items):
    els = [f'<a href="{rel(depth,"index.html")}">Home</a>']
    for name, u in items[:-1]:
        els.append(f'<a href="{rel(depth,u)}">{esc(name)}</a>')
    els.append(f'<span aria-current="page">{esc(items[-1][0])}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span class="crumb-sep">/</span>'.join(els).replace("</span>","</span>",1) + "</nav>"

def crumbs(depth, items):
    links = [f'<a href="{rel(depth,"index.html")}">Home</a>']
    for name, u in items[:-1]:
        links.append(f'<a href="{rel(depth,u)}">{esc(name)}</a>')
    links.append(f'<span aria-current="page">{esc(items[-1][0])}</span>')
    inner = '<svg class="crumb-ic" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>'.join(links)
    return f'<nav class="crumbs" aria-label="Breadcrumb">{inner}</nav>'

# ── product cards ───────────────────────────────────────────────────────
def img_srcset(depth, slug, im, sizes):
    """Responsive srcset (card + full render) for a product image pair. Empty for vector covers."""
    card, main = (im or {}).get("card", ""), (im or {}).get("main", "")
    if not card or not main or card == main or str(card).endswith(".svg"):
        return ""
    base = f"assets/products/{slug}"
    return (f' srcset="{rel(depth, f"{base}/{card}")} {im.get("cardW") or 750}w, '
            f'{rel(depth, f"{base}/{main}")} {im.get("fullW") or 1200}w" sizes="{sizes}"')

def product_card(p, depth, eager=False):
    im = p.get("images") or {}
    card = im.get("card", "")
    w, h = im.get("cardW") or 750, im.get("cardH") or 500
    u = rel(depth, f"products/{p['slug']}/")
    coming = bool(p.get("comingSoon"))
    if coming:
        badge = '<span class="badge badge-soon">Coming Soon</span>'
    else:
        badge = f'<span class="badge badge-free">Free</span>' if p["free"] else (f'<span class="badge">{esc(p["badge"])}</span>' if p.get("badge") else "")
    price = "Free" if p["free"] else money(p)
    cta = "Notify Me" if coming else ("Get Free" if p["free"] else "View Product")
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    fit = " contain" if (im.get("cardH") or 0) > (im.get("cardW") or 0) else ""
    srcset = img_srcset(depth, p["slug"], im, "(min-width: 1100px) 350px, (min-width: 680px) 31vw, 50vw")
    return f"""<article class="card" data-category="{esc(p['category'])}" data-name="{esc(p['name'].lower())}" data-tags="{esc(' '.join(p.get('tags',[])).lower())}" data-free="{1 if p["free"] else 0}">
  <a class="card-media" href="{u}">
    <img class="fit{fit}" src="{rel(depth, f"assets/products/{p['slug']}/{card}")}"{srcset} width="{w}" height="{h}" alt="{esc(p['name'])}: {esc(p.get('short') or p['category'])}" {loading} decoding="async">
    {badge}
  </a>
  <div class="card-body">
    <a class="card-cat" href="{rel(depth,'products.html')}#cat-{esc(p['category'].replace(' ','%20'))}">{esc(p['category'])}</a>
    <h3 class="card-title"><a href="{u}">{esc(p['name'])}</a></h3>
    <p class="card-short">{esc(p['short'])}</p>
    <div class="card-foot">
      <span class="price">{price}</span>
      <a class="btn btn-line btn-sm" href="{u}">{cta}</a>
    </div>
  </div>
</article>"""

def product_grid(products, depth, eager_first=0, classes="grid cards"):
    out = [f'<div class="{classes}">']
    for i, p in enumerate(products):
        out.append(product_card(p, depth, eager=i < eager_first))
    out.append("</div>")
    return "\n".join(out)

cat_slug = lambda c: "cat-" + c.replace(" ", "%20")

def write(path, content):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(path) else None
    open(p, "w", encoding="utf-8").write(content)
    print("wrote", path, f"({len(content)//1024}KB)")

# page assembly helpers
PAGE_HEAD = ' <section class="page-head"><div class="wrap">{crumbs_html}<p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="lead">{lead}</p></div></section>'


