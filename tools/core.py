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
SITE_URL = os.environ.get("SITE_URL", "https://digikitpro.shop").rstrip("/")
SITE_NAME = "DigiKitPro"
TAGLINE = "Procreate brushes for iPad artists."
STORE_URL = "https://payhip.com/digikitpro"
EMAIL_TO = "" # email hidden, contact via Payhip store only
EMAIL_ENDPOINT = "" # no direct email endpoint, newsletter falls back to Payhip freebies collection
# To switch providers later (Brevo/MailerLite/ConvertKit), paste their form-action URL here
# and the same form keeps working.
# ── Search Console verification tokens (paste once Google/Bing give them to you) ──
GOOGLE_VERIFY = os.environ.get("GOOGLE_VERIFY", "1e87093669a800cb") # content of the <meta name="google-site-verification"> token
BING_VERIFY = os.environ.get("BING_VERIFY", "52B8ABC07828BE6CE77B297D3F2E50A3") # content of the <meta name="msvalidate.01"> token
YANDEX_VERIFY = os.environ.get("YANDEX_VERIFY", "48977a1d04865b21") # content of the <meta name="yandex-verification"> token
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "") # IndexNow API key file name (no extension); see tools/submit_index.py
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "G-5MFQFHNB6B") # Google Analytics 4 Measurement ID
# ── Conversion event layer (js/analytics.js) ─────────────────────────────
# ANALYTICS_ENABLED=false emits window.DKP.analytics=false, which makes the
# event module completely inert (no GA4 forwarding, no local counting).
# Kill-switch for the owner; nothing else on the site depends on it.
ANALYTICS_ENABLED = os.environ.get("DKP_ANALYTICS", "true").strip().lower() not in ("0", "false", "no")
# Optional collector for the "What stopped you from choosing a brush today?"
# answers. EMPTY BY DEFAULT = nothing is posted anywhere; answers are only
# counted as an analytics event. Point it at a Cloudflare Worker / Vercel
# function when (and only when) the owner wants them in their own store.
# Never put a secret in this value: it is printed into public HTML.
FEEDBACK_ENDPOINT = os.environ.get("DKP_FEEDBACK_ENDPOINT", "")
BUILD_DATE = date.today().isoformat()
SOCIAL = { # ← add your profiles; hidden while empty
    "Pinterest": "",
    "Instagram": "",
    "TikTok": "",
}
# Languages offered by the in-page translation switcher (Google Translate).
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("it", "Italiano"),
    ("pt", "Português"),
    ("nl", "Nederlands"),
]
# Official, worldwide-inclusive meta used by search engines & social crawlers.
GEO_META = {
    "geo.placename": "DigiKitPro",
    "content-language": "en",
}
CATEGORIES = ["Portrait", "Skin Texture", "Line Art", "Sketching", "Watercolor", "Anime",
              "Hair", "Glitter & Effects", "Traditional", "Figure Drawing", "Bundles", "Guides & eBooks", "Other"]

CATEGORY_SLUGS = {
    "Portrait": "portrait",
    "Skin Texture": "skin-texture",
    "Line Art": "line-art",
    "Watercolor": "watercolor",
    "Anime": "anime",
    "Hair": "hair",
    "Glitter & Effects": "glitter-effects",
    "Traditional": "traditional",
    "Figure Drawing": "figure-drawing",
    "Sketching": "sketching"
}

PRODUCTS = json.load(open(os.path.join(ROOT, "data/products.json"), encoding="utf-8"))
BY_SLUG = {p["slug"]: p for p in PRODUCTS}

# ── MERCHANDISING MODEL ─────────────────────────────────────────────────
# data/discovery.json is deliberately SEPARATE from data/products.json:
# tools/payhip_sync.py rewrites products.json every day and must never be
# able to clobber the tier / audience decisions below. Products missing
# from discovery.json get safe defaults derived from their real category,
# so a newly synced product still builds, still appears, and is reported in
# the build log for the owner to tag properly. The build never fails.
_DISCOVERY_PATH = os.path.join(ROOT, "data/discovery.json")
DISCOVERY = json.load(open(_DISCOVERY_PATH, encoding="utf-8")) if os.path.exists(_DISCOVERY_PATH) else {"catalog": {}}
DISC = DISCOVERY.get("catalog") or {}
TIERS = {t["id"]: t for t in DISCOVERY.get("tiers", [])}
TIER_ORDER = [t["id"] for t in sorted(DISCOVERY.get("tiers", []), key=lambda t: t.get("level", 9))]

# Default tier from the real catalog data when discovery.json has no entry.
_DEFAULT_TIER_BY_CATEGORY = {"Bundles": "bundle", "Guides & eBooks": "education"}

def disc(slug):
    """Discovery record for a slug, with safe defaults for untagged products."""
    if slug in DISC:
        return DISC[slug]
    p = BY_SLUG.get(slug) or {}
    tier = "free" if p.get("free") else _DEFAULT_TIER_BY_CATEGORY.get(p.get("category"), "entry")
    tags = " ".join((p.get("tags") or []) + [p.get("category") or ""]).lower()
    line = "lifestyle" if any(k in tags for k in ("planner", "journal", "goodnotes", "travel", "kdp", "canva", "wellness", "fitness", "adhd")) else "procreate"
    return {"tier": tier, "line": line, "craft": [], "improve": [], "level": [],
            "style": [], "stage": "", "priority": 0, "aggregate": False, "_defaulted": True}

def tier_of(p):
    return disc(p["slug"]).get("tier", "entry")

def line_of(p):
    return disc(p["slug"]).get("line", "procreate")

def tier_label(p):
    t = TIERS.get(tier_of(p)) or {}
    return t.get("label") or tier_of(p).title()

def flagship():
    """The Level-4 flagship (Master Library). Returns the real product or None."""
    slug = DISCOVERY.get("flagship")
    return BY_SLUG.get(slug) if slug else None

def education_products():
    ed = DISCOVERY.get("education") or {}
    return {"paid": BY_SLUG.get(ed.get("paid")), "free": BY_SLUG.get(ed.get("free"))}

def untagged_products():
    """Reported at build time so the owner can tag newly synced products."""
    return sorted(p["slug"] for p in PRODUCTS if disc(p["slug"]).get("_defaulted"))


def page_ctx(ptype, p=None, **extra):
    """Analytics page context. Page facts only — never visitor data."""
    ctx = {"type": ptype}
    if p:
        ctx.update({
            "slug": p["slug"], "name": p["name"], "tier": tier_of(p),
            "category": p.get("category", ""), "price": p.get("price", 0),
            "free": bool(p.get("free")), "line": line_of(p),
        })
    ctx.update({k: v for k, v in extra.items() if v is not None})
    return ctx


def buy_attrs(p, loc, event=None):
    """data-dkp-* attributes for any Payhip CTA so js/analytics.js can
    attribute the click to a product, a tier and a page location."""
    a = (f'data-dkp-slug="{esc(p["slug"])}" data-dkp-name="{esc(p["name"])}" '
         f'data-dkp-price="{p.get("price", 0):.2f}" data-dkp-tier="{esc(tier_of(p))}" '
         f'data-dkp-free="{1 if p.get("free") else 0}" data-dkp-loc="{esc(loc)}"')
    if event:
        a += f' data-dkp-event="{esc(event)}"'
    return a

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

def is_abs(u):
    return bool(u) and (u.startswith("http://") or u.startswith("https://") or u.startswith("//"))

def asset_file(depth, slug, f):
    """Local asset path or an absolute remote URL (Payhip-hosted image for auto-synced products)."""
    return f if is_abs(f) else rel(depth, f"assets/products/{slug}/{f}")

def asset_abs(slug, f):
    """Absolute URL for schema / OG / preload; leaves remote URLs untouched."""
    return f if is_abs(f) else absurl(f"assets/products/{slug}/{f}")

def card_img(p):
    im = p.get("images") or {}
    return im.get("card", ""), im.get("cardW"), im.get("cardH")

# ── schema ──────────────────────────────────────────────────────────────
def schema_org_home():
    return [
      {"@context":"https://schema.org","@type":"Organization","@id":SITE_URL+"/#org",
       "name":SITE_NAME,"url":SITE_URL,
       "logo":{"@type":"ImageObject","url":absurl("assets/img/logo.png"),"width":"512","height":"512"},
       "image":{"@type":"ImageObject","url":absurl("assets/img/og-cover.jpg"),"width":"1200","height":"630"},
       "brand":{"@type":"Brand","name":SITE_NAME},
       "contactPoint":[{"@type":"ContactPoint","contactType":"customer support","areaServed":{"@type":"Place","name":"Worldwide"},"availableLanguage":["en"]}],
       "description":"DigiKitPro creates premium Procreate brushes and digital art resources for iPad artists. Worldwide instant digital delivery.",
       "areaServed":"Worldwide","knowsLanguage":["en","es","fr","de","it","pt","nl"],
       "sameAs":[STORE_URL]+[v for v in SOCIAL.values() if v]},
      {"@context":"https://schema.org","@type":"WebSite","@id":SITE_URL+"/#website",
       "url":SITE_URL,"name":SITE_NAME,"description":TAGLINE,"publisher":{"@id":SITE_URL+"/#org"},
       "inLanguage":["en","es","fr","de","it","pt","nl"],
       "potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint",
        "urlTemplate":SITE_URL+"/search.html?q={search_term_string}"},"query-input":"required name=search_term_string"}}
    ]

def schema_product(p):
    im = p.get("images") or {}
    img = im.get("card", "")
    return [{"@context":"https://schema.org","@type":"Product",
       "name":p["name"],"image":(asset_abs(p["slug"], img) if img else absurl("assets/img/og-cover.jpg")),
       "description":p["short"],"brand":{"@type":"Brand","name":SITE_NAME},
       "url":absurl(f"products/{p['slug']}/"),"contentLocation":{"@type":"Place","name":"Worldwide"},
       "offers":{"@type":"Offer","price":f"{p['price']:.2f}","priceCurrency":"USD",
                 "availability":"https://schema.org/InStock","url":p["payhipUrl"],
                 "priceValidUntil":f"{date.today().year+1}-12-31",
                 "seller":{"@type":"Organization","name":SITE_NAME}}}]

def schema_itemlist(items):
    """ItemList / OfferCatalog used on the products index for richer Google snippets."""
    return [{"@context":"https://schema.org","@type":"ItemList",
        "name":"DigiKitPro Procreate Brushes Catalog",
        "itemListElement":[{"@type":"ListItem","position":i+1,"name":p["name"],"url":absurl(f"products/{p['slug']}/")} for i,p in enumerate(items[:500])]}]

def schema_breadcrumb(items):
    return [{"@context":"https://schema.org","@type":"BreadcrumbList",
             "itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":absurl(u)} for i,(n,u) in enumerate(items)]}]

def schema_article(a):
    """BlogPosting (richer than the generic Article: eligible for blog/article
    rich results). Image is always an absolute URL, required by BlogPosting."""
    img = a.get("image") or "assets/img/og-cover.jpg"
    img = img if is_abs(img) else absurl(img)
    return [{"@context":"https://schema.org","@type":"BlogPosting","headline":a["title"],
             "description":a["description"],"image":[img],
             "datePublished":a["date"],"dateModified":a.get("modified") or a["date"],
             "keywords":", ".join([a.get("primary_keyword", "")] + (a.get("secondary_keywords") or [])),
             "author":{"@type":"Organization","name":SITE_NAME,"url":SITE_URL},
             "publisher":{"@id":SITE_URL+"/#org"},
             "mainEntityOfPage":absurl(f"blog/{a['slug']}/"),
             "inLanguage":"en","url":absurl(f"blog/{a['slug']}/")}]

def schema_howto(name, description, steps, total_time=None, tools=None):
    """HowTo rich result. `steps` = list of (name, text) tuples; each becomes a
    HowToStep. `tools` is an optional list of Procreate/tool names (HowToTool)."""
    step_nodes = [{"@type":"HowToStep","position":i+1,"name":n,"text":t}
                  for i,(n,t) in enumerate(steps)]
    node = {"@context":"https://schema.org","@type":"HowTo","name":name,
            "description":description,"inLanguage":"en",
            "step":step_nodes}
    if total_time:
        node["totalTime"] = total_time           # ISO-8601 duration, e.g. "PT30M"
        node["performTime"] = total_time
    if tools:
        node["tool"] = [{"@type":"HowToTool","name":t} for t in tools]
    return [node]

def schema_faq(faqs):
    """FAQPage rich result. `faqs` = list of (question, answer) tuples."""
    return [{"@context":"https://schema.org","@type":"FAQPage",
             "mainEntity":[{"@type":"Question","name":q,
                            "acceptedAnswer":{"@type":"Answer","text":a}}
                           for q,a in faqs]}]

# ── head / header / footer ──────────────────────────────────────────────
_GITHUB_KILL = """<script>
(function(){
  try{
    var d=atob('Z2l0aHViLmlv');
    if(location.hostname.slice(-d.length)===d){
      var p=location.pathname.replace(/^\/digikitpro/,'')||'/';
      document.write('<meta name="robots" content="noindex,follow">');
      location.replace('https://digikitpro.shop'+p+location.search+location.hash);
    }
  }catch(e){}
})();
</script>"""

def head(title, desc, canonical, depth, schemas=None, og_image=None, page_type="website", preload=None, ctx=None):
    """`ctx` is the analytics page context (see js/analytics.js). It is emitted
    as window.DKP.page and contains ONLY non-personal page facts: page type,
    product slug/name/tier/category/price. No visitor data, ever."""
    s = ""
    if schemas:
        for sc in schemas:
            s += f' <script type="application/ld+json">{json.dumps(sc, ensure_ascii=False)}</script>\n'
    pl = (f' <link rel="preload" as="image" href="{preload if is_abs(preload) else rel(depth, preload)}" fetchpriority="high">\n'
          if preload else "")
    ogimg = og_image if is_abs(og_image) else absurl(og_image or "assets/img/og-cover.jpg")
    vmeta = ""
    if GOOGLE_VERIFY: vmeta += f'\n  <meta name="google-site-verification" content="{esc(GOOGLE_VERIFY)}">'
    if BING_VERIFY: vmeta += f'\n  <meta name="msvalidate.01" content="{esc(BING_VERIFY)}">'
    if YANDEX_VERIFY: vmeta += f'\n  <meta name="yandex-verification" content="{esc(YANDEX_VERIFY)}">'
    geo = "".join(f'\n  <meta name="{esc(k)}" content="{esc(v)}">' for k, v in GEO_META.items())
    locales = "".join(f'\n  <meta property="og:locale:alternate" content="{loc}">' for loc in
                      ["es_ES", "fr_FR", "de_DE", "it_IT", "pt_BR", "nl_NL"])
    ga = ""
    if GA_MEASUREMENT_ID:
        ga = f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={esc(GA_MEASUREMENT_ID)}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{esc(GA_MEASUREMENT_ID)}');
  </script>
"""
    ctx_json = json.dumps(ctx or {}, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{_GITHUB_KILL}
{ga}  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{esc(canonical)}">{vmeta}
  <meta name="theme-color" content="#0A0A0C">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta property="og:type" content="{page_type}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{ogimg}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{esc(title)}">
  <meta property="og:locale" content="en_US">{locales}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{ogimg}">
  <meta name="twitter:image:alt" content="{esc(title)}">{geo}
  <meta name="format-detection" content="telephone=no">
  <link rel="icon" type="image/svg+xml" href="{rel(depth,'assets/img/favicon.svg')}">
  <link rel="icon" type="image/png" sizes="48x48" href="{rel(depth,'assets/img/favicon-48.png')}">
  <link rel="apple-touch-icon" href="{rel(depth,'assets/img/apple-touch-icon.png')}">
  <link rel="preconnect" href="https://payhip.com" crossorigin>
  <link rel="dns-prefetch" href="https://pe56d.s3.amazonaws.com">
  <link rel="dns-prefetch" href="https://translate.google.com">
  <link rel="preload" href="{rel(depth,'assets/fonts/playfairdisplay-normal.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{rel(depth,'assets/fonts/manrope-normal.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{rel(depth,'css/style.css')}">
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} Blog RSS feed" href="{rel(depth,'feed.xml')}">
  <!-- Motion layer: marks <html> before first paint so scroll-reveal elements
       are hidden from the very first frame (no flash of visible content).
       The timeout is a failsafe: if js/motion.js never runs, the class is
       removed and every element is simply visible, as it is without JS. -->
  <script>(function(h){{h.className+=" js-motion";setTimeout(function(){{if(!window.__DKP_MOTION_READY){{h.className=h.className.replace(" js-motion","");}}}},4000);}})(document.documentElement);</script>
{pl} <script>window.DKP={{store:'{STORE_URL}',email:'{EMAIL_ENDPOINT}',analytics:{str(ANALYTICS_ENABLED).lower()},feedbackEndpoint:'{FEEDBACK_ENDPOINT}',page:{ctx_json}}};</script>
  <script src="{rel(depth,'js/search-index.js')}" defer></script>
  <script src="{rel(depth,'js/main.js')}" defer></script>
  <script src="{rel(depth,'js/motion.js')}" defer></script>
  <script src="{rel(depth,'js/analytics.js')}" defer></script>
  <script src="{rel(depth,'js/feedback.js')}" defer></script>
  <script src="{rel(depth,'js/translate.js')}" defer></script>
{s}</head>
<body>
<noscript><div class="noscript-bar">JavaScript is off: every product page and guide still opens normally; only search and category filters need JS enabled. Every product, price and Payhip link on this site is plain HTML and works without it.</div></noscript>
"""

NAV = [("Free Brushes","freebies.html"),("Products","products.html"),("Bundles","bundles.html"),
       ("Articles","blog.html"),("About","about.html")]

def header(depth, active=None):
    links = ""
    for n, u in NAV:
        cls = ' class="active"' if active == u else ""
        links += f'<a href="{rel(depth,u)}"{cls}>{n}</a>' 
    mlinks = "".join(f'<a href="{rel(depth,u)}">{n}</a>' for n,u in NAV)
    lang_items = "".join(f'<button class="lang-opt" type="button" data-lang="{code}" data-lang-name="{name}">{name}<span class="lang-code">{code.upper()}</span></button>' for code,name in LANGUAGES)
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" data-header>
  <div class="wrap header-inner">
    <a class="brand" href="{rel(depth,'index.html')}" aria-label="{SITE_NAME} home">
      <svg class="brand-mark" width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true"><circle cx="16" cy="16" r="15" stroke="#C9A86A" stroke-width="1.4"/><path d="M11 22.5V9.5h4.4c3.9 0 6.6 2.7 6.6 6.5s-2.7 6.5-6.6 6.5H11Zm2.5-2.2h1.8c2.6 0 4.1-1.8 4.1-4.3s-1.5-4.3-4.1-4.3h-1.8v8.6Z" fill="#C9A86A"/></svg>
      <span class="brand-name">DigiKit<em>Pro</em></span>
    </a>
    <nav class="main-nav" aria-label="Primary">{links}</nav>
    <div class="header-actions">
      <div class="lang-wrap" data-lang-wrap>
        <button class="icon-btn lang-btn" type="button" data-lang-toggle aria-haspopup="true" aria-expanded="false" aria-label="Translate / choose language">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/></svg>
          <span class="lang-cd">EN</span>
        </button>
        <div class="lang-menu" data-lang-menu hidden>
          <p class="lang-title">Translate this page</p>
          {lang_items}
        </div>
      </div>
      <button class="icon-btn" type="button" data-search-open aria-label="Search products and articles">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      </button>
      <a class="btn btn-gold btn-sm" href="{rel(depth,'products.html')}" rel="noopener">Browse kits</a>
      <button class="icon-btn menu-btn" type="button" data-menu-toggle aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </div>
  </div>
  <nav class="mobile-nav" id="mobile-menu" aria-label="Mobile">{mlinks}<a class="btn btn-gold" href="{rel(depth,'products.html')}" rel="noopener">Browse kits</a></nav>
  <div id="google_translate_element" class="gt-holder" aria-hidden="true"></div>
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

def newsletter(depth, heading="Get Free Procreate Brushes",
               sub="Join the DigiKitPro list for free brush drops, new kit releases and iPad art tips. No spam, unsubscribe any time.",
               source="site", lead="", uid="nl", cta="Send me brushes", eyebrow="Free download"):
    """Email capture block.

    `source` and `lead` are sent to the inbox alongside the address (and to the
    analytics layer) so a future email provider can trigger the right sequence:
    an address collected for the free fine-liner set gets Email 1 about that
    pack, not a generic welcome. `uid` keeps element ids unique when a page
    carries more than one form.
    """
    subject = f"New DigiKitPro subscriber ({lead})" if lead else "New DigiKitPro subscriber"
    lead_field = f'\n        <input type="hidden" name="lead_magnet" value="{esc(lead)}">' if lead else ""
    return f"""<section class="newsletter" id="newsletter">
  <div class="wrap">
    <div class="nl-card">
      <p class="eyebrow">{esc(eyebrow)}</p>
      <h2>{esc(heading)}</h2>
      <p class="muted nl-sub">{esc(sub)}</p>
      <!-- Newsletter: when EMAIL_ENDPOINT is configured, submissions are sent via FormSubmit/AJAX (main.js).
           Without JS the form does a normal POST. With no endpoint configured, main.js shows the Payhip freebies collection.
           Source/lead fields allow future email provider to trigger the right sequence. -->
      <form class="nl-form" data-nl-form data-dkp-source="{esc(source)}" data-dkp-lead="{esc(lead)}" data-dkp-thanks="{rel(depth,'thank-you.html')}" action="{EMAIL_ENDPOINT}" method="POST">
        <input type="hidden" name="_subject" value="{esc(subject)}">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="false">
        <!-- _next must be ABSOLUTE for hosted form services: without it the no-JS path may land on a generic confirmation page instead of our thank-you page, which delivers the free files. -->
        <input type="hidden" name="_next" value="{absurl('thank-you.html')}">
        <input type="hidden" name="source" value="{esc(source)}">{lead_field}
        <label class="sr-only" for="{uid}-email">Email address</label>
        <input id="{uid}-email" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
        <button class="btn btn-gold" type="submit">{esc(cta)}</button>
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
        <a href="{rel(depth,'season/halloween/')}">Halloween Art</a>
        <a href="{rel(depth,'season/christmas/')}">Christmas Art</a>
        <a href="{rel(depth,'category/portrait/')}">Portrait Brushes</a>
        <a href="{rel(depth,'category/skin-texture/')}">Skin Texture</a>
        <a href="{rel(depth,'category/line-art/')}">Line Art</a>
        <a href="{rel(depth,'category/watercolor/')}">Watercolor</a>
        <a href="{rel(depth,'category/anime/')}">Anime Brushes</a>
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
        <a href="{rel(depth,'faq.html')}">FAQ</a>
        <a href="{rel(depth,'contact.html')}">Contact</a>
        <a href="{rel(depth,'refunds.html')}">Refund Policy</a>
        <a href="{rel(depth,'privacy.html')}">Privacy Policy</a>
        <a href="{rel(depth,'terms.html')}">Terms</a>
      </div>
      {social_block}
    </nav>
  </div>
  <div class="wrap foot-bottom">
    <p>© {date.today().year} {SITE_NAME}. Worldwide instant-delivery digital products sold via Payhip. Procreate is a trademark of Savage Interactive.</p>
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

# ── badges ──────────────────────────────────────────────────────────────
# Labels that must never be painted over a product image. "New" ages badly
# (it is still there months later) and "Masterclass" only repeats what the
# product title already says, so both are suppressed everywhere: cards, eBook
# tiles, bundle tiles and product pages. The value in data/products.json is
# kept untouched so sorting/"featured" logic and the Payhip sync still work.
HIDDEN_BADGES = {"new", "masterclass"}

def badge_text(p):
    """Visible badge label for a product, or '' when that label is hidden."""
    b = str((p or {}).get("badge") or "").strip()
    return "" if b.lower() in HIDDEN_BADGES else b

# ── product cards ───────────────────────────────────────────────────────
def img_srcset(depth, slug, im, sizes):
    """Responsive srcset (card + full render) for a local product image pair.
    Empty for vector covers or remote Payhip-hosted images (single source used)."""
    card, main = (im or {}).get("card", ""), (im or {}).get("main", "")
    if not card or not main or card == main or str(card).endswith(".svg") or is_abs(card) or is_abs(main):
        return ""
    base = f"assets/products/{slug}"
    return (f' srcset="{rel(depth, f"{base}/{card}")} {im.get("cardW") or 750}w, '
            f'{rel(depth, f"{base}/{main}")} {im.get("fullW") or 1200}w" sizes="{sizes}"')

def cta_for(p):
    """Standard CTA verb + target for a product, by tier.

    Free items            -> "Get Free"
    Paid single packs <$10 -> "Buy Now", straight to Payhip (no detail-page
                              detour on a $5 impulse purchase)
    Bundles / Master Library / education / anything $10+ -> "View Product"
                              (detail page first: higher-consideration items
                              benefit from the explanation before checkout)
    Returns (label, href_kind) where href_kind is "payhip" or "page".
    """
    if p.get("comingSoon"):
        return "Notify Me", "page"
    if p.get("free"):
        return "Get Free", "page"
    if tier_of(p) in ("bundle", "flagship", "education") or (p.get("price") or 0) >= 10:
        return "View Product", "page"
    return "Buy Now", "payhip"

def trust_bridge(depth=0, free=False):
    """The one-line trust bridge that sits beside/below every Payhip CTA.

    Refund wording is taken from refunds.html ("all sales are final once the
    files have been downloaded" + "technical problems are resolved") so the
    claim never drifts from the policy page.
    """
    terms = ("$0 now and forever, no card needed" if free
             else "all sales final once downloaded, faulty files always resolved")
    return (f'<p class="trust-bridge">Secure checkout via Payhip · instant download · '
            f'{terms} · <a href="{rel(depth, "refunds.html")}">Refund policy</a></p>')

def product_card(p, depth, eager=False, free_direct=False):
    im = p.get("images") or {}
    card = im.get("card", "")
    w, h = im.get("cardW") or 750, im.get("cardH") or 500
    u = rel(depth, f"products/{p['slug']}/")
    coming = bool(p.get("comingSoon"))
    label, kind = cta_for(p)
    # Free cards normally keep the product page as their target (it hosts the
    # email gate + the direct link); the homepage free row and the freebies
    # page send "Get Free" straight to Payhip instead.
    if free_direct and p.get("free") and not coming:
        href, ext = p["payhipUrl"], True
    elif kind == "payhip":
        href, ext = p["payhipUrl"], True
    else:
        href, ext = u, False
    ext_attr = ' target="_blank" rel="noopener"' if ext else ""
    if coming:
        badge = '<span class="badge badge-soon">Coming Soon</span>'
    else:
        blabel = badge_text(p)
        badge = f'<span class="badge badge-free">Free</span>' if p["free"] else (f'<span class="badge">{esc(blabel)}</span>' if blabel else "")
    price = "Free" if p["free"] else money(p)
    cta = label
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    srcset = img_srcset(depth, p["slug"], im, "(min-width: 1100px) 350px, (min-width: 680px) 31vw, 50vw") if card else ""
    img_src = asset_file(depth, p["slug"], card) if card else rel(depth, "assets/img/coming-soon.svg")
    # Card media is a uniform square filled edge-to-edge (object-fit: cover),
    # so every artwork renders at full card width — no letterbox bars, no
    # shrunken contain-fit thumbnails. Intrinsic width/height stay on the tag
    # for layout stability before CSS loads.
    cslug = CATEGORY_SLUGS.get(p.get("category"))
    cat_url = rel(depth, f"category/{cslug}/") if cslug else (rel(depth, "bundles.html") if p.get("category") == "Bundles" else rel(depth, f"products.html#cat-{esc(p['category'].replace(' ','%20'))}"))
    _tier = tier_of(p); _line = line_of(p)
    return f"""<article class="card" data-category="{esc(p['category'])}" data-name="{esc(p['name'].lower())}" data-tags="{esc(' '.join(p.get('tags',[])).lower())}" data-free="{1 if p["free"] else 0}" data-featured="{1 if (p.get("featured") or p.get("badge")) else 0}" data-tier="{esc(_tier)}" data-line="{esc(_line)}" data-dkp-slug="{esc(p['slug'])}" data-dkp-name="{esc(p['name'])}" data-dkp-price="{p.get('price',0):.2f}" data-dkp-tier="{esc(_tier)}" data-dkp-free="{1 if p['free'] else 0}" data-dkp-loc="card">
  <a class="card-media" href="{u}">
    <img src="{img_src}"{srcset} width="{w}" height="{h}" alt="{esc(p['name'])}: {esc(p.get('short') or p['category'])}" {loading} decoding="async">
    {badge}
  </a>
  <div class="card-body">
    <a class="card-cat" href="{cat_url}">{esc(p['category'])}</a>
    <h3 class="card-title"><a href="{u}">{esc(p['name'])}</a></h3>
    <p class="card-short">{esc(p['short'])}</p>
    <div class="card-foot">
      <span class="price">{price}</span>
      <a class="btn btn-line btn-sm" href="{href}"{ext_attr} {buy_attrs(p, 'card')}>{cta}</a>
    </div>
  </div>
</article>"""

def product_grid(products, depth, eager_first=0, classes="grid cards", free_direct=False):
    out = [f'<div class="{classes}">']
    for i, p in enumerate(products):
        out.append(product_card(p, depth, eager=i < eager_first, free_direct=free_direct))
    out.append("</div>")
    return "\n".join(out)

cat_slug = lambda c: "cat-" + c.replace(" ", "%20")

# ── worldwide trust band + trending topics (homepage / catalog) ─────────
def trust_band(depth=0):
    """Proof bar directly under the hero.

    PLACEHOLDER (owner): swap these catalog figures for real performance
    numbers — total downloads, kits sold, average rating — as soon as they
    exist. Until then the bar states only counts that are verifiable from
    data/products.json, never invented social proof.
    """
    f = flagship()
    free_n = sum(1 for p in PRODUCTS if p["free"])
    brush_count = (f.get("assets") or "2,000+ brushes") if f else "2,000+ brushes"
    items = [
        (f"{len(PRODUCTS)} kits &amp; tools", "Brushes, bundles, palettes, planners and eBooks in one catalog"),
        (esc(brush_count), "In the Master Library alone — one organised download"),
        (f"{free_n} free packs", "$0 forever — download now, no email needed"),
        ("Instant delivery", "Worldwide via Payhip · PayPal, cards &amp; Apple Pay"),
    ]
    cells = "".join(f'<div class="tb-item"><span>{title}</span><p>{sub}</p></div>' for title, sub in items)
    return f'<div class="trust-band" role="region" aria-label="DigiKitPro by the numbers"><div class="wrap trust-inner">{cells}</div></div>'

def trend_topics(depth=0):
    topics = [
        ("Best Procreate brushes", rel(depth, "blog.html")),
        ("Realistic skin", rel(depth, "category/skin-texture/")),
        ("Anime brushes", rel(depth, "category/anime/")),
        ("Watercolor", rel(depth, "category/watercolor/")),
        ("Line art", rel(depth, "category/line-art/")),
        ("Portrait brushes", rel(depth, "category/portrait/")),
        ("Hair brushes", rel(depth, "category/hair/")),
        ("Procreate bundles", rel(depth, "bundles.html")),
        ("Free brush packs", rel(depth, "freebies.html")),
        ("Starter guide", rel(depth, "blog/best-procreate-brushes-for-beginners/")),
    ]
    pills = "".join(f'<a class="trend-pill" href="{u}">{n}</a>' for n, u in topics)
    return f'<p class="trend-label">Trending now in Procreate &amp; digital art</p><div class="trend-pills">{pills}</div>'

# ── CONVERSION COMPONENTS (Phase 1 sales foundation) ────────────────────
# Every component below reuses the existing design tokens (.btn, .badge,
# .eyebrow, .price, .grid) so nothing new has to be learned visually.
# Nothing here invents a claim: copy states only what is already true in
# data/products.json (asset counts, prices, formats, requirements).

def best_seller():
    """The single product the homepage feature band is built around:
    the first live "Best Seller"-badged pack, else the top featured pack."""
    for p in PRODUCTS:
        if badge_text(p).lower() == "best seller" and not p.get("comingSoon"):
            return p
    feat = sorted([p for p in PRODUCTS if p.get("featured") and not p.get("comingSoon")],
                  key=lambda x: x["featured"])
    return feat[0] if feat else None

def feature_band(depth=0):
    """Compact best-seller spotlight: large artwork left, short pitch right.

    Rules (homepage conversion fix):
    - controlled max-width, natural image aspect — no tall narrow card;
    - one-line pitch + short topic bullets only (teaser, not a sales page);
    - no testimonial slot (never publish placeholder quotes),
    - no checkout / refund copy (that lives on legal pages and product pages).
    """
    p = best_seller()
    if not p:
        return ""
    im = p.get("images") or {}
    img = im.get("card") or im.get("main") or ""
    srcset = img_srcset(depth, p["slug"], im, "(min-width: 900px) 430px, 92vw")
    # Short topic bullets. Curated per product so they stay teaser-length;
    # the long feature sentences belong on the product page.
    spot_points = {
        "portrait-skin-brushes-procreate":
            ["Pores", "Freckles", "Wrinkles", "Skin texture", "Natural blending"],
    }
    points = spot_points.get(p["slug"])
    if not points:
        assets = esc(p.get("assets") or "Professional brush set")
        points = [a.strip().capitalize() for a in assets.replace(" + ", "+").split("+") if a.strip()][:5] \
            or ["Hand-tested brushes"]
    chips = "".join(f"<li>{esc(x)}</li>" for x in points)
    u = rel(depth, 'products/' + p['slug'] + '/')
    # Split "X for Procreate" so the qualifier sits on its own muted line.
    name = p["name"]
    main_title, sub_title = name, ""
    if " for " in name:
        main_title, sub_title = name.split(" for ", 1)
        sub_title = "for " + sub_title
    sub_html = f'<span class="bs-sub">{esc(sub_title)}</span>' if sub_title else ""
    return f"""<div class="bs-inner" id="best-seller">
      <a class="bs-media" href="{u}" tabindex="-1" aria-hidden="true">
        <img src="{asset_file(depth, p['slug'], img)}"{srcset} width="{im.get('cardW') or im.get('fullW') or 750}" height="{im.get('cardH') or im.get('fullH') or 946}" alt="" loading="lazy" decoding="async">
      </a>
      <div class="bs-body">
        <p class="bs-kicker"><span class="bs-badge">Best Seller</span></p>
        <h2 id="bs-title">{esc(main_title)} {sub_html}</h2>
        <p class="lead-sm">{esc(p.get('spotPitch') or p['short'])}</p>
        <ul class="bs-points">{chips}</ul>
        <div class="bs-cta">
          <span class="price price-lg">{"Free" if p['free'] else esc(p['priceText'])}</span>
          <a class="btn btn-gold btn-lg" href="{p['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(p, 'feature-band')}>{"Get Free" if p['free'] else "Buy Now"} <span class="btn-arr">↗</span></a>
          <a class="btn btn-line" href="{u}">View Product</a>
        </div>
      </div>
</div>
"""

def freebie_download_row(depth=0):
    """Primary path on the freebies page: every free pack as a full card with
    a direct, no-email Payhip download button."""
    frees = [p for p in PRODUCTS if p.get("free") and not p.get("comingSoon")]
    cards = ""
    for p in frees:
        im = p.get("images") or {}
        img = im.get("card") or im.get("main") or ""
        srcset = img_srcset(depth, p["slug"], im, "(min-width: 1100px) 350px, (min-width: 680px) 31vw, 92vw")
        cards += f"""<article class="dl-card">
  <a class="dl-media" href="{p['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(p, 'freebie-direct')}>
    <img src="{asset_file(depth, p['slug'], img)}"{srcset} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(p['name'])}" loading="lazy" decoding="async">
    <span class="badge badge-free">Free</span>
  </a>
  <div class="dl-body">
    <h3>{esc(p['name'])}</h3>
    <p class="muted">{esc(p.get('assets') or p.get('short') or '')}</p>
    <div class="dl-foot">
      <span class="price price-free">Free</span>
      <a class="btn btn-gold" href="{p['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(p, 'freebie-direct')}>Get Free <span class="btn-arr">↗</span></a>
    </div>
    <p class="dl-note">No email required · instant download · keep forever</p>
  </div>
</article>"""
    return f"""<section class="section" id="direct" aria-labelledby="direct-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">No email, no wait</p><h2 id="direct-title">Download Them Right Now</h2></div>
      <a class="text-link" href="#get-free">Or get new drops by email ↓</a>
    </div>
    <p class="sec-note muted">Every button goes straight to Payhip's free checkout. Nothing is gated: take the packs first, decide about email later.</p>
    <div class="grid dl-grid">{cards}</div>
    {trust_bridge(depth, free=True)}
  </div>
</section>"""


def craft_grid(depth=0):
    """"WHAT DO YOU CREATE?" — routes intent before the catalog.
    Each card links to the matching category page (or the Brush Finder for
    animation, where we honestly do not have a dedicated pack yet)."""
    cards = DISCOVERY.get("craftCards") or []
    counts = {}
    for pr in PRODUCTS:
        d = disc(pr["slug"])
        if d.get("line") == "lifestyle":
            continue
        for c in d.get("craft") or []:
            counts[c] = counts.get(c, 0) + 1
    tiles = ""
    for c in cards:
        n = counts.get(c["id"], 0)
        href = rel(depth, c["href"])
        tiles += (
            f'<a class="craft-card" href="{esc(href)}" data-dkp-event="craft_card_click" '
            f'data-dkp-craft="{esc(c["id"])}" data-dkp-count="{n}">'
            f'<span class="craft-name">{esc(c["label"])}</span>'
            f'<span class="craft-blurb">{esc(c["blurb"])}</span>'
            f'<span class="craft-meta">{n} {"pack" if n == 1 else "packs"} →</span></a>')
    return f"""<section class="section" id="craft" aria-labelledby="craft-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">Start with your work, not our catalog</p><h2 id="craft-title">What Do You Create?</h2></div>
      <a class="text-link" href="{rel(depth,'products.html')}">Browse all products →</a>
    </div>
    <div class="grid craft-grid">{tiles}</div>
  </div>
</section>
"""


def ladder_rungs():
    """The homepage bundle ladder, as configured in data/discovery.json.

    Returns [(rung_dict, product)] for every rung whose slug still resolves to
    a live product. A deleted or renamed product drops that rung at build time
    instead of leaving an empty card on the homepage — and a ladder with no
    valid rungs returns [], so the caller renders nothing at all.
    """
    cfg = (DISCOVERY.get("bundleLadder") or {}).get("rungs") or []
    out = []
    for r in cfg:
        p = BY_SLUG.get(r.get("slug") or "")
        if not p or p.get("comingSoon"):
            continue
        out.append((r, p))
    return out


def clip(text, n=96):
    """Truncate to `n` chars at a word boundary — keeps generated teaser copy
    honest (it is a prefix of the real sentence) instead of rewriting it."""
    t = " ".join(str(text or "").split())
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "\u2026"


def bundle_ladder(depth=0):
    """PROCREATE BUNDLES, drawn as a ladder instead of a tile grid.

    Starter -> Advanced -> Ultimate -> Master Library: one row, four rungs, the
    last rung being the flagship so the ladder and the Master Library band read
    as one argument rather than two competing ones (homepage IA, 2026-09-14).

    Deliberately not the image-overlay .bundle-tile: a tile shows artwork, a
    ladder step has to show WHAT YOU GET. So every line of a step is generated
    from the product's own record — features[0] as the pitch, `assets` as the
    count, `bundleContents` as the kit list, priceText as the price — and
    data/discovery.json supplies only the rung label. A Payhip sync therefore
    moves the ladder's numbers by itself, and no savings claim is invented
    here. The only maths on the page is "$x per brush", derived from this
    product's own price and brush count.
    """
    rungs = ladder_rungs()
    if len(rungs) < 2:
        return ""
    steps = ""
    for i, (r, p) in enumerate(rungs):
        im = p.get("images") or {}
        card = im.get("card") or im.get("main") or ""
        flag = bool(r.get("ladder_flagship"))
        u = rel(depth, f"products/{p['slug']}/")
        feats = [f for f in (p.get("features") or []) if str(f).strip()]
        who = clip(feats[0]) if feats else clip(p.get("short") or r.get("rung") or "")
        # "What's inside" comes from the product's own bundleContents, so the
        # kit count is real, and no second place has to remember a price.
        # Two more honest numbers, both arithmetic on this product's own data.
        # They only appear when the data actually supports them, which also
        # keeps the four steps visually balanced without padding them.
        extras = []
        m_brushes = re.search(r"([\d,]{3,})\+?\s*(?:professional\s+)?(?:organized\s+)?brushes",
                              str(p.get("assets") or ""), re.I)
        if m_brushes and (p.get("price") or 0) >= 5:
            n_brushes = int(m_brushes.group(1).replace(",", ""))
            if n_brushes >= 100:
                extras.append(f"${p['price'] / n_brushes:.2f} per brush")
        m_files = re.search(r"\nin\s+(\d+)\s+ZIP", " ".join(feats))
        if m_files:
            extras.append(f"{m_files.group(1)} ZIP downloads")
        who_more = ", ".join(x for x in (p.get("perfectFor") or [])[:2] if str(x).strip())
        rows = p.get("bundleContents") or []
        if rows:  # only the portrait bundle has verified kit lists today
            contents = f'<p class="ladder-incl">Inside: {len(rows)} kits</p><ul class="ladder-incl-list">'
            contents += "".join(f'<li><span>{clip(b.get("name"))}</span><b>{esc(b.get("count") or "")}</b></li>'
                               for b in rows if b.get("name"))
            contents += "</ul>"
        else:
            # No bundleContents field = we do not claim to know the kit list.
            # `assets` above already states what you get; `included` is a spec
            # sheet of bullets, not a kit list, so it is deliberately not used
            # to print a count here.
            contents = ""
        steps += f"""<li class="ladder-step{' ladder-step--top' if flag else ''}" id="ladder-{esc(r.get('id') or (i + 1))}">
  <span class="ladder-rung"><i aria-hidden="true">{i + 1}</i>{esc(r.get('role') or '')}</span>
  <a class="ladder-media" href="{u}" tabindex="-1" aria-hidden="true">
    <img src="{asset_file(depth, p['slug'], card)}"{img_srcset(depth, p['slug'], im, "(min-width: 1100px) 280px, 90vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="" loading="lazy" decoding="async">
  </a>
  <div class="ladder-body">
    <h3><a href="{u}">{esc(p['name'])}</a></h3>
    <p class="ladder-who muted">{esc(who)}</p>
    <p class="ladder-assets"><b>{esc(p.get('assets') or '')}</b>{" · " + esc("; ".join(extras)) if extras else ""}</p>
    {contents}
    {f'<p class="ladder-for muted">For {esc(who_more)}</p>' if who_more and not contents else ""}
    <div class="ladder-foot">
      <span class="price price-lg">{esc(p['priceText'])}</span>
      <a class="btn {"btn-gold" if flag else "btn-line"} btn-sm" href="{u}">{"Get the Library" if flag else "View Product"}</a>
    </div>
  </div>
</li>"""
    lead = " \u2192 ".join(f'<b>{esc(r.get("role") or p["name"])}</b>' if r.get("ladder_flagship")
                           else esc(r.get("role") or p["name"]) for r, p in rungs)
    return f"""<section class="section section-alt" id="bundles" aria-labelledby="lad-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">Pick your rung</p><h2 id="lad-title">Procreate Bundles</h2></div>
      <a class="text-link" href="{rel(depth, 'bundles.html')}">Compare every bundle \u2192</a>
    </div>
    <p class="ladder-lead muted">{lead} \u2014 each rung is more of the studio in one checkout. Prices below are live store prices, so no rung advertises a "was" figure it does not have.</p>
    <ol class="ladder">{steps}</ol>
    <p class="ladder-note muted">Seasonal packs (Christmas, Halloween) are not part of the ladder \u2014 they live on <a href="{rel(depth, 'bundles.html')}">bundles</a> and in the <a href="{rel(depth, 'products.html')}">catalog</a>.</p>
  </div>
</section>
"""


def flagship_band(depth=0, bridge=True, ladder_href=None):
    """Level 4 — the Master Library, given the prominence its value deserves.
    The comparison is arithmetic on real prices, never a scarcity or
    popularity claim. ``bridge=False`` drops the checkout/refund line
    (the homepage keeps its product bands free of legal copy).
    ``ladder_href`` adds the "top rung of the bundle ladder" link back to the
    bundle ladder, so the two sections read as one climb instead of two."""
    f = flagship()
    if not f:
        return ""
    im = f.get("images") or {}
    img = im.get("main") or im.get("card") or ""
    srcset = img_srcset(depth, f["slug"], im, "(min-width: 960px) 42vw, 92vw")
    # Honest arithmetic, without cherry-picking.
    #
    # The first version of this summed the FOUR CHEAPEST specialist packs and
    # printed "Four single packs already total $18" directly beside the $19
    # price - which undercut the flagship it existed to sell. Choosing the
    # cheapest possible basket is not a comparison, it is a self-inflicted
    # objection, and a visitor reading "$18 for four packs" next to "$19 for
    # everything" draws the wrong conclusion from a number we picked.
    #
    # What is actually true and defensible: specialist packs span a real price
    # range, and which four a given artist would buy is their decision, not
    # ours. So we state the range and let them do the arithmetic.
    # Brush packs only. The Master Library is a BRUSH library, so the basket it
    # is compared against has to be brushes - counting digital planners and a
    # travel guide in "N kits" would inflate the number with products that are
    # not substitutes for it. This is comparison accuracy, not catalog
    # separation: the planners stay mixed into the catalog exactly as the owner
    # decided, they are simply not claimed as brush packs here.
    singles = [p for p in PRODUCTS
               if tier_of(p) == "entry" and not p["free"] and not p.get("comingSoon")
               and line_of(p) != "lifestyle"]
    prices = sorted(p["price"] for p in singles if p.get("price"))
    compare = ""
    if len(prices) >= 4:
        lo, hi = prices[0], prices[-1]
        lo_s = f"${lo:.0f}" if float(lo).is_integer() else f"${lo:.2f}"
        hi_s = f"${hi:.0f}" if float(hi).is_integer() else f"${hi:.2f}"
        compare = (f'Single specialist packs run <b>{lo_s}\u2013{hi_s}</b> each across '
                   f'{len(prices)} kits. One library, every style, {esc(f["priceText"])}.')
    return f"""<section class="section flagship-band" id="master-library" aria-labelledby="flag-title">
  <div class="wrap flag-inner">
    <div class="flag-media" data-wipe>
      <img src="{asset_file(depth, f['slug'], img)}"{srcset} width="{im.get('fullW') or 1200}" height="{im.get('fullH') or 800}" alt="{esc(f.get('alt') or f['name'])}" loading="lazy" decoding="async">
    </div>
    <div class="flag-body">
      <p class="eyebrow">The complete library</p>
      <h2 id="flag-title">{esc(f['name'])}</h2>
      <p class="lead-sm">{esc(f['short'])}</p>
      <ul class="flag-points">
        <li><b>{esc(f.get('assets') or '2,000+ brushes')}</b> in organised category folders</li>
        <li>Linework, traditional media, watercolour, character &amp; anatomy, texture and effects</li>
        <li>One .brushset download, lifetime access, no more tool hunting</li>
      </ul>
      <p class="flag-compare muted">{compare}</p>
      <div class="flag-cta">
        <span class="price price-lg">{esc(f['priceText'])}</span>
        <a class="btn btn-gold" href="{rel(depth, 'products/' + f['slug'] + '/')}">View Product</a>
        <a class="text-link" href="{f['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(f, 'flagship-band')}>Buy on Payhip ↗</a>
      </div>
      {trust_bridge(depth) if bridge else ""}
      {f'<p class="flag-ladder muted">Top rung of the bundle ladder — <a href="{esc(ladder_href)}">see Starter → Advanced → Ultimate → Master Library</a>.</p>' if ladder_href else ""}
    </div>
  </div>
</section>
"""


def upgrade_panel(p, depth):
    """Level 2/3 → Level 4 ladder on a product page.
    Shown only where an upgrade is genuinely logical: never on the flagship
    itself, never on free products (a free visitor gets the starter path
    instead), and never on lifestyle products."""
    f = flagship()
    if not f or p["slug"] == f["slug"] or p.get("free") or line_of(p) == "lifestyle":
        return ""
    tier = tier_of(p)
    if tier == "flagship":
        return ""
    diff = f["price"] - p.get("price", 0)
    if tier == "bundle":
        head_txt = "Already looking at a bundle?"
        body = (f"The Master Library adds the rest of the catalog on top of it: "
                f"{esc(f.get('assets') or '2,000+ brushes')} in one organised download.")
    else:
        head_txt = "Looking for more than one pack?"
        body = (f"This pack solves one problem well for {esc(p['priceText'])}. "
                f"If you paint across several styles, the Master Library covers all of them "
                f"for {esc(f['priceText'])} — +${diff:.2f} over this pack.")
    im = f.get("images") or {}
    thumb = im.get("card") or im.get("main") or ""
    return f"""<section class="psec upgrade-panel" aria-labelledby="p-upgrade">
  <h2 id="p-upgrade">{esc(head_txt)}</h2>
  <div class="up-inner">
    <a class="up-media" href="{rel(depth, 'products/' + f['slug'] + '/')}">
      <img src="{asset_file(depth, f['slug'], thumb)}" width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(f['name'])}" loading="lazy" decoding="async">
    </a>
    <div class="up-body">
      <p class="up-this"><b>This pack</b> — {esc(p['name'])}, {esc(p['priceText'])}</p>
      <p class="up-or muted">or</p>
      <h3>{esc(f['name'])}</h3>
      <p class="muted">{esc(body)}</p>
      <div class="up-cta">
        <span class="price">{esc(f['priceText'])}</span>
        <a class="btn btn-line btn-sm" href="{rel(depth, 'products/' + f['slug'] + '/')}"
           data-dkp-event="upgrade_clicked" data-dkp-from-product-id="{esc(p['slug'])}"
           data-dkp-to-product-id="{esc(f['slug'])}" data-dkp-price-delta="{diff:.2f}">View Product</a>
        <a class="text-link" href="{f['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(f, 'pdp-upgrade')}>Buy on Payhip ↗</a>
      </div>
      {trust_bridge(depth)}
    </div>
  </div>
</section>
"""


def licence_line():
    """The commercial-usage objection, answered above the fold instead of
    buried in a collapsed FAQ. States exactly what terms.html already says."""
    return ('<p class="licence-line"><b>Can I sell what I make?</b> Yes — finished artwork you '
            'create with these files is yours to use personally and commercially. You may not '
            'resell or redistribute the brush files themselves. '
            '<a href="../../terms.html">Full licence</a>.</p>')


def install_steps():
    """How do I install it? A real question that blocks purchase for anyone
    new to iPad. Same steps already documented in the install guide article."""
    steps = [
        "Buy or download on Payhip — the .brushset file arrives by email instantly.",
        "Get the file onto your iPad (AirDrop from a Mac, or any file transfer on Windows).",
        "Tap the .brushset file in the Files app and choose <b>Open in Procreate</b>.",
        "The set installs automatically and appears in your Brushes panel, ready to use.",
    ]
    lis = "".join(f"<li>{s}</li>" for s in steps)
    return (f'<section class="psec install-steps" aria-labelledby="p-install">'
            f'<h2 id="p-install">How to install it</h2><ol class="steps-list">{lis}</ol>'
            f'<p class="muted install-note">Full walkthrough with screenshots: '
            f'<a href="../../blog/how-to-install-procreate-brushes/">How to install Procreate brushes</a>.</p></section>')


def freebie_gate(depth, p=None, source="freebies"):
    """Email-first free download. The direct Payhip link stays visible —
    we never hold a promised free file hostage — but the email path is the
    primary action and leads to thank-you.html, which makes one starter offer."""
    lead = p["slug"] if p else "free-brushes"
    if p:
        heading = f"Get {p['name']}"
        sub = ("Enter your email and we will send the download link plus new free brush drops. "
               "No spam, unsubscribe in one click.")
        eyebrow, btn = "Free download", "Send my free download"
    else:
        # Secondary path on freebies.html: the direct Payhip downloads above
        # are the primary action, so the email module only recruits subscribers.
        heading = "Want new free drops sent to you?"
        sub = ("Leave your email and every new free pack lands in your inbox the day it drops. "
               "The downloads above never need an address — this is only for the next ones.")
        eyebrow, btn = "Free drops, first", "Send me new freebies"
    return f"""<section class="freebie-gate" id="get-free" aria-labelledby="fg-title">
  <div class="fg-inner">
    <div class="fg-copy">
      <p class="eyebrow">{esc(eyebrow)}</p>
      <h2 id="fg-title">{esc(heading)}</h2>
      <p class="muted">{esc(sub)}</p>
      <form class="nl-form fg-form" data-nl-form data-dkp-source="{esc(source)}" data-dkp-lead="{esc(lead)}" data-dkp-thanks="{rel(depth,'thank-you.html')}" action="{EMAIL_ENDPOINT}" method="POST">
        <input type="hidden" name="_subject" value="Free download request: {esc(lead)}">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="false">
        <!-- Absolute _next keeps the no-JS path on thank-you.html, which delivers the promised free file. -->
        <input type="hidden" name="_next" value="{absurl('thank-you.html')}">
        <input type="hidden" name="source" value="{esc(source)}">
        <input type="hidden" name="lead_magnet" value="{esc(lead)}">
        <label class="sr-only" for="fg-email-{esc(lead)}">Email address</label>
        <input id="fg-email-{esc(lead)}" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
        <button class="btn btn-gold" type="submit">{esc(btn)}</button>
        <p class="nl-note" data-nl-note>We email the link straight away.</p>
      </form>
      {f'<p class="fg-alt muted">In a hurry? <a href="{p["payhipUrl"]}" target="_blank" rel="noopener" {buy_attrs(p, "freebie-gate-direct")}>Download it directly on Payhip ↗</a> — no email needed.</p>' if p else ''}
    </div>
  </div>
</section>
"""


# ── seasonal homepage band ──────────────────────────────────────────────
# A date-aware promo strip for the active art season. Each def has an inclusive
# (start, end) window as (month, day) tuples; outside every window the band is
# hidden entirely, so the homepage never shows an out-of-date holiday. Kept in
# the generator (not hand-edited HTML) so every rebuild stays correct.
SEASON_BANDS = [
    {
        "key": "halloween",
        "window": ((9, 15), (10, 31)),
        "eyebrow": "Seasonal drop",
        "title": "Spooky season is here — Halloween Procreate art",
        "text": "Set the mood with the spooky pumpkin PNG pack plus glow, smoke and sparkle brushes for atmospheric autumn artwork.",
        "primary": ("Shop Halloween art", "season/halloween/"),
        "secondary": ("Halloween tutorial", "blog/halloween-procreate-tutorial/"),
    },
    {
        "key": "christmas",
        "window": ((11, 20), (12, 31)),
        "eyebrow": "Holiday drop",
        "title": "Festive season brushes, stamps & washi tapes",
        "text": "173 Christmas stamps and brushes, 44 hand-drawn washi tapes, glitter papers, frames and chalkboards for cards, tags and journal spreads.",
        "primary": ("Shop Christmas bundle", "season/christmas/"),
        "secondary": ("Holiday tutorial", "blog/christmas-procreate-tutorial/"),
    },
]

def active_season_band(today=None):
    """Return the SEASON_BANDS def whose window contains `today` (date), else None."""
    d = today or date.today()
    md = (d.month, d.day)
    for sdef in SEASON_BANDS:
        (sm, sd), (em, ed) = sdef["window"]
        if (sm, sd) <= md <= (em, ed):
            return sdef
    return None

def season_band(depth=0):
    """Homepage promo strip for the current art season; '' outside a window."""
    sdef = active_season_band()
    if not sdef:
        return ""
    phref = rel(depth, sdef["primary"][1])
    shref = rel(depth, sdef["secondary"][1])
    return f"""<section class="season-band season-band--{sdef['key']}" aria-label="{esc(sdef['title'])}">
  <div class="wrap season-band-inner">
    <div class="season-band-copy">
      <p class="eyebrow">{esc(sdef['eyebrow'])}</p>
      <h2>{esc(sdef['title'])}</h2>
      <p class="season-band-text">{esc(sdef['text'])}</p>
      <div class="season-band-ctas">
        <a class="btn btn-gold btn-sm" href="{phref}">{esc(sdef['primary'][0])}</a>
        <a class="btn btn-line btn-sm" href="{shref}">{esc(sdef['secondary'][0])} →</a>
      </div>
    </div>
    <span class="season-band-glyph" aria-hidden="true">✦</span>
  </div>
</section>"""

def write(path, content):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(path) else None
    open(p, "w", encoding="utf-8").write(content)
    print("wrote", path, f"({len(content)//1024}KB)")

# page assembly helpers
PAGE_HEAD = ' <section class="page-head"><div class="wrap">{crumbs_html}<p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="lead">{lead}</p></div></section>'


