#!/usr/bin/env python3
"""About, legal, search, 404, robots, sitemap, feeds, search index."""
from core import *
from pages_season import SEASON_DEFS
from datetime import datetime
from email.utils import format_datetime


def _rfc822(d):
    """Format an ISO date (YYYY-MM-DD) as an RFC-822 date for RSS pubDate."""
    try:
        return format_datetime(datetime.strptime(str(d)[:10], "%Y-%m-%d"))
    except Exception:
        return format_datetime(datetime.utcnow())


def schema_faq(faqs):
    return [{"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q,
                             "acceptedAnswer": {"@type": "Answer", "text": a}}
                            for q, a in faqs]}]


# AEO quick answers. Every answer states a fact already used elsewhere on the
# site (delivery via Payhip, .brushset requires Procreate, free packs exist),
# so no product claims or reviews are invented.
ABOUT_FAQS = [
    ("What is DigiKitPro?",
     "DigiKitPro is an independent digital art studio that creates Procreate brush sets, bundles, color palettes, planners and guides. All products are digital downloads sold through Payhip, with instant worldwide delivery and no physical shipping."),
    ("How do I receive my files after buying?",
     "Checkout is handled by Payhip. As soon as payment completes you get a download link by email and in your Payhip account. There is no shipping, so artists in any country receive the same files at the same moment."),
    ("Do DigiKitPro brushes work on Windows or Android?",
     "The .brushset brush files require the Procreate app on an iPad. Some bundles also include PNG or other files that can open in apps that support those formats. Check the product description for the file types included."),
    ("Are there free Procreate brushes?",
     "Yes. Free brush packs and a free starter eBook are listed on the Free Brushes page, and the newsletter sends free brush drops. You can start with the free fine liner set and the free chalkboard toolkit."),
    ("Which currencies and payment methods are accepted?",
     "Prices display in USD and Payhip converts the charge to your local currency at checkout. Payhip accepts PayPal, cards, Apple Pay and other supported methods."),
    ("Is DigiKitPro affiliated with Procreate or Savage Interactive?",
     "No. DigiKitPro is an independent store. Procreate is a trademark of Savage Interactive Pty Ltd, and DigiKitPro is not affiliated with or endorsed by Savage Interactive."),
    ("How do I contact DigiKitPro?",
     "Email digikitprostudio@gmail.com or use the contact form on the Payhip store. Questions about products, orders and licensing are all read and answered directly."),
]


# ── FAQ page questions ───────────────────────────────────────────────────
# Every answer restates a fact the site already commits to elsewhere
# (terms.html, privacy.html, product pages). No reviews, ratings, customer
# counts, sales figures, scarcity or deadlines are invented here.
SITE_FAQS = [
    ("What do I need to use DigiKitPro brushes?",
     "The .brushset files require the Procreate app on an iPad. Brushes are calibrated for Apple Pencil pressure and tilt. Some products are PDFs, palettes or PNG files instead; each product page lists its file types under Technical Details."),
    ("How are the files delivered?",
     "Checkout is handled by Payhip. As soon as payment completes, Payhip emails you a download link and the files also appear in your Payhip account. Delivery is instant and worldwide; nothing is physically shipped."),
    ("How do I install a .brushset file on my iPad?",
     "Get the file onto your iPad, then tap it in the Files app and choose Open in Procreate. The set installs automatically and appears in your Brushes panel. There is a full walkthrough with screenshots in the How to install Procreate brushes guide."),
    ("Can I sell artwork I make with these brushes?",
     "Yes. Finished artwork you create with these files is yours to use personally and commercially. What you may not do is resell, redistribute, copy or share the brush, palette or source files themselves, in original or modified form. The full licence is on the Terms page."),
    ("Can I get a refund?",
     "Because these are digital downloads, all sales are final once the files have been downloaded. If you hit a technical problem with a file, contact us and we will resolve it. The Refund Policy page explains this in full."),
    ("What payment methods and currencies are accepted?",
     "Prices are displayed in USD and Payhip converts the charge to your local currency at checkout. Payhip accepts PayPal, cards, Apple Pay and other supported methods."),
    ("Are there free brushes I can try first?",
     "Yes. Free brush packs and a free starter eBook are listed on the Free Brushes page, and the newsletter sends free brush drops. You can start with the free fine liner set and the free chalkboard toolkit."),
    ("Do the brushes work on Windows, Android or Photoshop?",
     "The .brushset format is specific to Procreate on iPad, so it will not load in Photoshop or on Windows and Android devices. Products that include PNG, PDF or palette files can be opened in any app that supports those formats; check the product page for what is included."),
    ("Which file do I download if a product has several ZIP parts?",
     "Download all of them. Larger libraries are split into several ZIP files purely because of file size limits, and each part contains a different set of brushes. The Technical Details on the product page state how many parts there are and the total size."),
    ("Is DigiKitPro affiliated with Procreate or Savage Interactive?",
     "No. DigiKitPro is an independent store. Procreate is a trademark of Savage Interactive Pty Ltd, and DigiKitPro is not affiliated with or endorsed by Savage Interactive."),
]


def build_misc():
    # ── CONTACT ──
    # A real, working form. It posts to the same FormSubmit endpoint as the
    # newsletter, but carries its own success copy via data-dkp-success so the
    # confirmation does not say "you're on the list" (see js/main.js).
    # It deliberately states no response time: only promise what is kept.
    contact_schemas = schema_breadcrumb([("Home", "/"), ("Contact", "/contact.html")])
    html_out = head("Contact DigiKitPro",
        "Contact DigiKitPro about a product, an order, a technical problem with a file, or licensing. Email digikitprostudio@gmail.com or use the contact form.",
        SITE_URL + "/contact.html", 0, schemas=contact_schemas)
    html_out += header(0)
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(0, [("Contact","contact.html")])}
    <p class="eyebrow">Get in touch</p>
    <h1>Contact DigiKitPro</h1>
  </div></section>
  <section class="section"><div class="wrap narrow">
    <p class="lead">Questions about a product, an order, a file that will not open, or licensing? Send a message below, or email <a href="mailto:{EMAIL_TO}">{EMAIL_TO}</a> directly.</p>
    <form class="contact-form" data-nl-form
          data-dkp-source="contact"
          data-dkp-success="Thanks, your message has been sent to {EMAIL_TO}."
          data-dkp-success-pending="Thanks, your message has been recorded and will arrive in our inbox once our email service finishes its one-time activation."
          action="{EMAIL_ENDPOINT}" method="POST">
      <input type="hidden" name="_subject" value="DigiKitPro contact form">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="{absurl('thank-you.html')}">
      <input type="hidden" name="source" value="contact">
      <div class="field">
        <label for="contact-name">Your name</label>
        <input id="contact-name" type="text" name="name" autocomplete="name" required>
      </div>
      <div class="field">
        <label for="contact-email">Your email</label>
        <input id="contact-email" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>
        <p class="field-hint muted">We reply to this address, so please double-check it.</p>
      </div>
      <div class="field">
        <label for="contact-order">Order number <span class="muted">(optional)</span></label>
        <input id="contact-order" type="text" name="order_number" autocomplete="off">
        <p class="field-hint muted">If your question is about a purchase, the Payhip receipt number helps us find it.</p>
      </div>
      <div class="field">
        <label for="contact-message">Message</label>
        <textarea id="contact-message" name="message" rows="7" required></textarea>
      </div>
      <button class="btn btn-gold btn-lg" type="submit">Send message</button>
      <p class="nl-note" data-nl-note>Your message goes straight to our inbox. We never share your address.</p>
    </form>
    <div class="prose contact-alt">
      <h2>Before you write</h2>
      <p>These answer most messages, and you will get an answer instantly:</p>
      <ul>
        <li><strong>Where are my files?</strong> Payhip emails the download link the moment payment completes, and the files are also in your Payhip account. Check your spam folder first.</li>
        <li><strong>How do I install a brushset?</strong> See <a href="blog/how-to-install-procreate-brushes/">How to install Procreate brushes</a>.</li>
        <li><strong>Can I sell what I make?</strong> Yes, finished artwork is yours to use commercially. See the <a href="terms.html">full licence</a>.</li>
        <li><strong>Refunds:</strong> see the <a href="refunds.html">Refund Policy</a>.</li>
        <li><strong>Everything else:</strong> the <a href="faq.html">FAQ</a>.</li>
      </ul>
    </div>
  </div></section>
</main>
{footer(0)}"""
    write("contact.html", html_out)

    # ── REFUND POLICY ──
    # Restates exactly what terms.html already commits to. No money-back
    # guarantee, no day count, no "hassle-free": the store does not offer those,
    # so the site does not claim them.
    refund_schemas = schema_breadcrumb([("Home", "/"), ("Refund Policy", "/refunds.html")])
    html_out = head("Refund Policy, DigiKitPro",
        "DigiKitPro refund policy for digital downloads: all sales are final once files are downloaded, and technical problems with any file are resolved.",
        SITE_URL + "/refunds.html", 0, schemas=refund_schemas)
    html_out += header(0)
    html_out += f"""
<main id="main"><section class="section"><div class="wrap narrow prose">
  {crumbs(0, [("Refund Policy","refunds.html")])}
  <h1>Refund Policy</h1>
  <p class="article-meta">Last updated: {BUILD_DATE}</p>
  <p class="lead">Everything sold here is a digital download. This page states the same policy as our <a href="terms.html">Terms of Service</a>, in one place so you can read it before you buy.</p>
  <h2>All sales are final once files are downloaded</h2>
  <p>Because digital files cannot be returned, all sales are final once the files have been downloaded. Please check compatibility before buying: .brushset files require the Procreate app on an iPad, and each product page lists exactly what file types are included under Technical Details.</p>
  <h2>Technical problems are resolved</h2>
  <p>If you hit a technical problem with any file, for example a download that will not complete, a corrupted file, or a brushset that will not open in Procreate, <a href="contact.html">contact us</a> and we will resolve it. Tell us which product it is and what happens when you try to open it, and include your Payhip order number if you have it.</p>
  <h2>Not sure yet? Start free</h2>
  <p>If you want to try the brushes before spending anything, the <a href="freebies.html">free brush packs</a> are genuinely free and install exactly the same way, so you can confirm everything works on your iPad first.</p>
  <h2>Payments and chargebacks</h2>
  <p>All payments are processed by Payhip, not by DigiKitPro. Billing questions can also be raised through your Payhip receipt.</p>
  <h2>Contact</h2>
  <p>Email <a href="mailto:{EMAIL_TO}">{EMAIL_TO}</a> or use the <a href="contact.html">contact form</a>.</p>
</div></section></main>
{footer(0)}"""
    write("refunds.html", html_out)

    # ── FAQ ──
    faq_items = "".join(
        f'<details class="faq-q"><summary>{esc(q)}</summary><div class="faq-body"><p>{esc(a)}</p></div></details>'
        for q, a in SITE_FAQS)
    faq_schemas = schema_breadcrumb([("Home", "/"), ("FAQ", "/faq.html")]) + schema_faq(SITE_FAQS)
    html_out = head("FAQ, DigiKitPro Procreate Brushes",
        "Answers to common questions about DigiKitPro Procreate brushes: compatibility, instant delivery, installing a .brushset, the commercial licence and refunds.",
        SITE_URL + "/faq.html", 0, schemas=faq_schemas)
    html_out += header(0)
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(0, [("FAQ","faq.html")])}
    <p class="eyebrow">Answers</p>
    <h1>Frequently asked questions</h1>
  </div></section>
  <section class="section"><div class="wrap narrow">
    <p class="lead">Compatibility, delivery, installing, licensing and refunds. If your question is not here, <a href="contact.html">send us a message</a>.</p>
    <div class="faq-list">{faq_items}</div>
    <div class="prose">
      <h2>Still stuck?</h2>
      <p>Email <a href="mailto:{EMAIL_TO}">{EMAIL_TO}</a> or use the <a href="contact.html">contact form</a>. For the legal detail, see the <a href="terms.html">Terms</a>, the <a href="refunds.html">Refund Policy</a> and the <a href="privacy.html">Privacy Policy</a>.</p>
    </div>
  </div></section>
  {newsletter(0)}
</main>
{footer(0)}"""
    write("faq.html", html_out)

    # ── ABOUT ──
    faq_html = "".join(f"<div class=\"faq-item\"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>" for q, a in ABOUT_FAQS)
    about_schemas = schema_breadcrumb([("Home", "/"), ("About", "/about.html")]) + schema_faq(ABOUT_FAQS)
    html_out = head("About DigiKitPro, Premium Procreate Brush Studio",
        "DigiKitPro creates premium Procreate brushes for portrait artists, illustrators and digital painters. Every brush is hand-tested on real artwork.",
        SITE_URL + "/about.html", 0, schemas=about_schemas)
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
    <h2 id="faq">Quick answers</h2>
    <p>Short, direct answers to the questions artists ask most. For anything else, email us at <a href="mailto:{EMAIL_TO}">{EMAIL_TO}</a>.</p>
    {faq_html}
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
  <h2>Analytics &amp; cookies</h2>
  <p>This is a static website with no server of our own, but it is not analytics-free, and we would rather tell you plainly than imply otherwise.</p>
  <ul>
    <li><strong>Google Analytics 4</strong> is loaded on every page to measure which products and guides are useful. Google may set cookies and process your IP address for this. You can block it with any tracker blocker, by enabling your browser's <em>Do Not Track</em> setting (this site honours it and stops sending), or by using Google's own <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener" target="_blank">opt-out add-on</a>.</li>
    <li><strong>What we measure:</strong> page and product views, clicks on "buy" and "download" links, which Brush Finder answers lead to a recommendation, and the answer you give to the optional "what stopped you from choosing a brush today?" prompt. <strong>We do not record your name, your email address, or anything you type</strong> — search queries are measured by length only.</li>
    <li><strong>DigiKitPro sets no advertising cookies and no cross-site identifier.</strong> There is no retargeting, no ad pixel and no data broker sharing.</li>
    <li><strong>A first-party summary</strong> of your visit (counts only) is kept in your browser's <code>localStorage</code> so the site can avoid asking you the same optional question twice. It never leaves your device unless you send a form. Clearing your browser data removes it.</li>
    <li><strong>Google Translate</strong> (the globe button in the header) is loaded from Google only when you choose a language. Google sets its own <code>googtrans</code> cookie to remember that choice. Do not use the button if you prefer not to contact Google.</li>
    <li><strong>FormSubmit</strong> delivers newsletter and free-download requests to our inbox. It sees the email address you type and the page you sent it from.</li>
    <li><strong>Payhip</strong> handles all payments. Checkout happens on payhip.com under <a href="https://payhip.com/privacy" rel="noopener" target="_blank">Payhip's own privacy policy</a>; we never see or store your card details.</li>
  </ul>
  <p>You can switch our own measurement off completely by visiting any page with <code>#dkp-analytics=off</code> in the address, which sets an opt-out in your browser.</p>
  <h2>Your rights</h2>
  <p>You can request access, correction or deletion of your newsletter data at any time by emailing <a href="mailto:{EMAIL_TO}">{EMAIL_TO}</a> or using the <a href="{STORE_URL}" target="_blank" rel="noopener">store contact form</a>. Every email we send contains a one-click unsubscribe link.</p>
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

    # ── .nojekyll: tell GitHub Pages to serve files as-is (no Jekyll build) ──
    write(".nojekyll", "")

    # ── robots + sitemap ──
    write("robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/sitemap.txt
""")

    static_urls = [
        ("/", "1.0", "daily"),
        ("/find-my-brushes.html", "0.9", "weekly"),
        ("/products.html", "0.9", "daily"),
        ("/freebies.html", "0.9", "weekly"),
        ("/bundles.html", "0.8", "weekly"),
        ("/blog.html", "0.8", "weekly"),
        ("/about.html", "0.6", "monthly"),
        ("/faq.html", "0.6", "monthly"),
        ("/contact.html", "0.5", "monthly"),
        ("/search.html", "0.5", "weekly"),
        ("/refunds.html", "0.3", "monthly"),
        ("/privacy.html", "0.3", "monthly"),
        ("/terms.html", "0.3", "monthly"),
    ]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    for u, pr, freq in static_urls:
        sm += f" <url><loc>{SITE_URL}{u}</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>{freq}</changefreq><priority>{pr}</priority></url>\n"

    for cslug in CATEGORY_SLUGS.values():
        sm += f" <url><loc>{SITE_URL}/category/{cslug}/</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>weekly</changefreq><priority>0.85</priority></url>\n"

    # Seasonal hub pages (Halloween, Christmas, ...)
    for sdef in SEASON_DEFS:
        sm += f" <url><loc>{SITE_URL}/season/{sdef['slug']}/</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n"

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

    # ── Plain-text sitemap (one URL per line) ──────────────────────────────
    txt_urls = [
        SITE_URL + "/",
        SITE_URL + "/find-my-brushes.html",
        SITE_URL + "/products.html",
        SITE_URL + "/freebies.html",
        SITE_URL + "/bundles.html",
        SITE_URL + "/blog.html",
        SITE_URL + "/about.html",
        SITE_URL + "/faq.html",
        SITE_URL + "/contact.html",
        SITE_URL + "/search.html",
        SITE_URL + "/refunds.html",
        SITE_URL + "/privacy.html",
        SITE_URL + "/terms.html",
    ]
    txt_urls += [f"{SITE_URL}/category/{cslug}/" for cslug in CATEGORY_SLUGS.values()]
    txt_urls += [f"{SITE_URL}/season/{sdef['slug']}/" for sdef in SEASON_DEFS]
    txt_urls += [f"{SITE_URL}/products/{p['slug']}/" for p in PRODUCTS]
    txt_urls += [f"{SITE_URL}/blog/{a['slug']}/" for a in load_articles()]
    write("sitemap.txt", "\n".join(txt_urls) + "\n")

    # ── RSS 2.0 feed of the blog articles ──────────────────────────────────
    articles = load_articles()
    rss_items = ""
    for a in articles:
        link = absurl(f"blog/{a['slug']}/")
        desc = esc(a.get("description", ""))
        rss_items += f"""    <item>
      <title>{esc(a['title'])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <description>{desc}</description>
      <pubDate>{_rfc822(a.get('date', BUILD_DATE))}</pubDate>
    </item>
"""
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_NAME} Blog</title>
    <link>{SITE_URL}/blog.html</link>
    <description>Technique-first Procreate tutorials and digital art guides from {SITE_NAME}.</description>
    <language>en-us</language>
    <lastBuildDate>{_rfc822(BUILD_DATE)}</lastBuildDate>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
{rss_items}  </channel>
</rss>
"""
    write("feed.xml", rss)

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
