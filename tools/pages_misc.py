#!/usr/bin/env python3
"""About, legal, search, 404, robots, sitemap, search index."""
from core import *

def build_misc():
    # ── ABOUT ──
    html_out = head("About DigiKitPro, Premium Procreate Brush Studio",
        "DigiKitPro creates premium Procreate brushes for portrait artists, illustrators and digital painters. Every brush is hand-tested on real artwork.",
        SITE_URL + "/about.html", 0, schemas=schema_breadcrumb([("Home","/"),("About","/about.html")]))
    html_out += header(0, active="about.html")
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(0, [("About","about.html")])}
    <p class="eyebrow">The studio</p>
    <h1>About DigiKitPro</h1>
  </div></section>
  <section class="section"><div class="wrap narrow prose">
    <p class="lead"><strong>Welcome to DigiKitPro.</strong></p>
    <p>DigiKitPro creates premium Procreate brushes for portrait artists, illustrators, and digital painters. Every brush is hand-tested on real artwork before release. Whether you're sketching, painting realistic skin, or building anime characters, we make tools that feel natural under the Apple Pencil.</p>
    <h2>What we believe</h2>
    <ul>
      <li><strong>Workflow over catalog size.</strong> A kit organized around how you paint beats a thousand loose brushes.</li>
      <li><strong>Real media behavior.</strong> Bleeds, tooth, crumble and granulation, digital tools should carry the soul of physical media.</li>
      <li><strong>Honest pricing.</strong> Professional kits for the price of a coffee, and a free collection big enough to start a career with.</li>
    </ul>
    <h2>Worldwide, instant, in your language</h2>
    <p>Everything here is a digital download delivered instantly through Payhip, so artists in the <strong>United States, Canada, Europe and every other country</strong> get the same files at the same moment. There is no shipping and no physical product. Prices display in USD, and Payhip automatically converts the charge to your local currency at checkout. Use the globe button in the header to translate the whole site into English, Español, Français, Deutsch, Italiano, Português or Nederlands.</p>
    <h2 id="contact">Contact</h2>
    <p>Questions about a product, an order, or a collaboration? Email us directly at <a href="mailto:{EMAIL_TO}">{EMAIL_TO}</a> or use the contact form on our <a href="{STORE_URL}" target="_blank" rel="noopener">Payhip store</a>, we read everything.</p>
  </div></section>
  {newsletter(0)}
</main>
{footer(0)}"""
    write("about.html", html_out)

    # ── PRIVACY ──
    html_out = head("Privacy Policy, DigiKitPro", "How DigiKitPro handles your data: newsletter sign-up, purchases processed securely by Payhip, and your rights.", SITE_URL + "/privacy.html", 0)
    html_out += header(0)
    html_out += f"""
<main id="main"><section class="section"><div class="wrap narrow prose">
  {crumbs(0, [("Privacy Policy","privacy.html")])}
  <h1>Privacy Policy</h1>
  <p class="article-meta">Last updated: {BUILD_DATE}</p>
  <h2>Overview</h2>
  <p>DigiKitPro ("we", "our") operates this content website and sells digital products through Payhip. This policy explains what data we collect and why.</p>
  <h2>Data we collect</h2>
  <ul>
    <li><strong>Email address (optional):</strong> only if you subscribe to the newsletter. Used solely for product news, free asset drops and Procreate tips. Unsubscribe anytime via the link in every email.</li>
    <li><strong>Purchase data:</strong> all payments and order data are processed by Payhip on their secure checkout. We never see or store your payment card details. See Payhip's own privacy policy for how they process order data.</li>
  </ul>
  <h2>Analytics & cookies</h2>
  <p>This website is a static site. It sets no tracking cookies and includes no third-party analytics by default. If we ever add privacy-respecting analytics, this page will be updated first.</p>
  <h2>Your rights</h2>
  <p>You can request access, correction or deletion of your newsletter data at any time by contacting us via the <a href="{STORE_URL}" target="_blank" rel="noopener">store contact form</a>.</p>
</div></section></main>
{footer(0)}"""
    write("privacy.html", html_out)

    # ── TERMS ──
    html_out = head("Terms of Service, DigiKitPro", "DigiKitPro terms: digital product license, refund policy for digital downloads, and acceptable use.", SITE_URL + "/terms.html", 0)
    html_out += header(0)
    html_out += f"""
<main id="main"><section class="section"><div class="wrap narrow prose">
  {crumbs(0, [("Terms","terms.html")])}
  <h1>Terms of Service</h1>
  <p class="article-meta">Last updated: {BUILD_DATE}</p>
  <h2>Digital products</h2>
  <p>All products are digital downloads delivered instantly via Payhip. No physical goods are shipped. You are responsible for confirming app compatibility (for example, .brushset files require Procreate on iPad) before purchase.</p>
  <h2>License</h2>
  <p>Unless a product page states otherwise, purchases include a license to use the assets in your personal and commercial artwork. You may not resell, redistribute, copy or share the brush files, palettes or files themselves, in original or modified form.</p>
  <h2>Refunds</h2>
  <p>Due to the nature of digital products, all sales are final once files are downloaded. If you hit a technical problem with any file, contact us and we will resolve it.</p>
  <h2>Intellectual property</h2>
  <p>All site content, text, artwork previews and branding, belongs to DigiKitPro. Procreate is a trademark of Savage Interactive Pty Ltd; this independent store is not affiliated with or endorsed by Savage Interactive.</p>
</div></section></main>
{footer(0)}"""
    write("terms.html", html_out)

    # ── SEARCH page (fallback target for SearchAction/schema) ──
    html_out = head("Search, DigiKitPro", "Search all DigiKitPro Procreate brushes, bundles, freebies and articles.", SITE_URL + "/search.html", 0)
    html_out += header(0)
    html_out += f"""
<main id="main"><section class="section"><div class="wrap">
  <h1>Search DigiKitPro</h1>
  <p class="lead">Type to search every product and guide.</p>
  <div class="search-page-box">
    <input type="search" id="search-page-input" placeholder="Try: skin, watercolor, anime, free…" aria-label="Search products and articles" data-search-page-input>
  </div>
  <div data-search-page-results></div>
</div></section></main>
{footer(0)}"""
    write("search.html", html_out)

    # ── 404 ──
    html_out = head("Page not found, DigiKitPro", "That page doesn't exist, but the brushes do. Browse the full DigiKitPro catalog.", SITE_URL + "/404.html", 0)
    html_out += header(0)
    html_out += f"""
<main id="main"><section class="section"><div class="wrap narrow" style="text-align:center;padding:6rem 0">
  <p class="eyebrow">404</p>
  <h1>This canvas is blank.</h1>
  <p class="lead">The page you're looking for didn't make it to the final artwork.</p>
  <div class="hero-ctas" style="justify-content:center"><a class="btn btn-gold" href="index.html">Back to Home</a><a class="btn btn-line" href="products.html">Browse Products</a></div>
</div></section></main>
  <script>
  // GitHub Pages serves this file for unknown URLs. Many "not found" hits are just
  // directory-style links missing their trailing slash; retry that form silently.
  (function () {{
    var p = location.pathname;
    if (location.protocol !== "file:" && /\\/[^\\/\\.]+$/.test(p) && p.length > 1) {{
      location.replace(p + "/" + location.search + location.hash);
    }}
  }})();
  </script>
{footer(0)}"""
    write("404.html", html_out)

    # ── robots + sitemap ──
    write("robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
""")

    static_urls = [
        ("/", "1.0", "daily"),
        ("/products.html", "0.9", "daily"),
        ("/freebies.html", "0.9", "weekly"),
        ("/bundles.html", "0.8", "weekly"),
        ("/blog.html", "0.8", "weekly"),
        ("/about.html", "0.6", "monthly"),
        ("/search.html", "0.5", "weekly"),
        ("/privacy.html", "0.3", "monthly"),
        ("/terms.html", "0.3", "monthly"),
    ]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    for u, pr, freq in static_urls:
        sm += f" <url><loc>{SITE_URL}{u}</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>{freq}</changefreq><priority>{pr}</priority></url>\n"

    for cslug in CATEGORY_SLUGS.values():
        sm += f" <url><loc>{SITE_URL}/category/{cslug}/</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>weekly</changefreq><priority>0.85</priority></url>\n"

    for p in PRODUCTS:
        slug = p["slug"]
        im = p.get("images") or {}
        img = im.get("card") or im.get("main") or ""
        img_xml = ""
        if img:
            img_loc = img if is_abs(img) else absurl(f"assets/products/{slug}/{img}")
            img_xml = f"<image:image><image:loc>{img_loc}</image:loc><image:title>{esc(p['name'])}</image:title></image:image>"
        sm += f" <url><loc>{SITE_URL}/products/{slug}/</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>daily</changefreq><priority>0.8</priority>{img_xml}</url>\n"

    for a in load_articles():
        slug = a["slug"]
        img = a.get("image") or ""
        img_xml = ""
        if img:
            img_loc = img if is_abs(img) else absurl(img)
            img_xml = f"<image:image><image:loc>{img_loc}</image:loc><image:title>{esc(a['title'])}</image:title></image:image>"
        sm += f" <url><loc>{SITE_URL}/blog/{slug}/</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority>{img_xml}</url>\n"

    sm += "</urlset>\n"
    write("sitemap.xml", sm)

    # IndexNow key file (Bing/Yandex/Seznam instant indexing). Only written when
    # INDEXNOW_KEY env var / GitHub Actions variable is configured.
    if INDEXNOW_KEY:
        write(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)
        print(f"wrote IndexNow key file: {INDEXNOW_KEY}.txt")

    # ── search index (lean, served as window.DKP_INDEX) ──
    idx_products = []
    for p in PRODUCTS:
        im = p.get("images") or {}
        card = im.get("card", "")
        idx_products.append({
            "t": p["name"], "u": f"products/{p['slug']}/", "c": p["category"],
            "p": p["priceText"], "s": p["short"][:140],
            "img": card if is_abs(card) else f"assets/products/{p['slug']}/{card}",
            "k": " ".join([p["name"], p["category"], " ".join(p.get("tags", [])), p.get("assets") or "",
                            "free" if p["free"] else "", "bundle" if p["category"] == "Bundles" else ""]).lower(),
            "free": p["free"],
        })
    idx_articles = [{"t": a["title"], "u": f"blog/{a['slug']}/", "d": a["description"], "k": (a["title"] + " " + a.get("category","") + " " + a["description"]).lower()} for a in load_articles()]
    js = "window.DKP_INDEX=" + json.dumps({"products": idx_products, "articles": idx_articles}, ensure_ascii=False) + ";"
    write("js/search-index.js", js)
    print("misc pages + sitemap + search index done")
