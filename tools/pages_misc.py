#!/usr/bin/env python3
"""About, legal, search, 404, robots, sitemap, feeds, search index."""
from core import *
from pages_season import SEASON_DEFS
from pages_guides import GUIDES_DIR, GUIDE_URLS, GUIDE_DEFS, GUIDES_INDEX
from pages_partner import PARTNER_DIR, PARTNER_URL
from datetime import datetime
from email.utils import format_datetime
# SEO tools ( /tools/ + /tools/canvas-calculator/ )
try:
    from pages_tools import TOOL_DEFS as _TOOL_DEFS, TOOLS_DIR as _TOOLS_DIR
except Exception:
    _TOOL_DEFS = []
    _TOOLS_DIR = "tools"


def _rfc822(d):
    """Format an ISO date (YYYY-MM-DD) as an RFC-822 date for RSS pubDate."""
    try:
        return format_datetime(datetime.strptime(str(d)[:10], "%Y-%m-%d"))
    except Exception:
        return format_datetime(datetime.utcnow())


def _is_card_or_thumb(filename):
    """True for the downscaled card/thumb crop of a product image."""
    name = (filename or "").rsplit("/", 1)[-1].lower()
    return "-card." in name or "-thumb." in name


def _fullsize_product_images(p):
    """(abs_url, title) pairs for the full-size artwork on a product page.

    Cards are deliberately excluded: they are downscaled crops of the same
    files, and submitting both offers Google duplicates. Titles come from
    the alt text already used on the page (p['alt'], then 'preview N' for
    gallery frames — same strings gallery_html() emits).
    """
    im = p.get("images") or {}
    slug = p["slug"]
    alt_main = p.get("alt") or p["name"]
    out = []

    def _loc(filename):
        if not filename or _is_card_or_thumb(filename):
            return None
        return filename if is_abs(filename) else absurl(f"assets/products/{slug}/{filename}")

    main = im.get("main") or ""
    loc = _loc(main)
    if loc:
        out.append((loc, alt_main))
    for i, g in enumerate(im.get("gallery") or [], start=1):
        loc = _loc(g.get("file") or "")
        if loc:
            out.append((loc, f"{alt_main}: preview {i}"))
    return out


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
     "DigiKitPro is an independent digital art studio offering Procreate brush sets, bundles, color palettes, planners and guides. Products are digital downloads sold through Payhip; no physical items are shipped."),
    ("How do I receive my files after buying?",
     "Payhip handles checkout and digital delivery. Check the Payhip confirmation and receipt for access details; if you need help, use the contact page."),
    ("Do DigiKitPro brushes work on Windows or Android?",
     "The .brushset brush files require the Procreate app on an iPad. Some bundles also include PNG or other files that can open in apps that support those formats. Check the product description for the file types included."),
    ("Are there free Procreate brushes?",
     "Yes. Free brush packs, a color palette collection and a free starter guide are listed on the Free Brushes page. You can start with the fine liner set or the chalkboard toolkit."),
    ("Which currencies and payment methods are accepted?",
     "Prices are listed in USD. Review the payment options, currency and total shown by Payhip before completing checkout."),
    ("Is DigiKitPro affiliated with Procreate or Savage Interactive?",
     "No. DigiKitPro is an independent store. Procreate is a trademark of Savage Interactive Pty Ltd, and DigiKitPro is not affiliated with or endorsed by Savage Interactive."),
    ("How do I contact DigiKitPro?",
     "Use the contact form on the Payhip store. You can use it for questions about products, orders and licensing."),
]


# ── FAQ page questions ───────────────────────────────────────────────────
# Every answer restates a fact the site already commits to elsewhere
# (terms.html, privacy.html, product pages). No reviews, ratings, customer
# counts, sales figures, scarcity or deadlines are invented here.
SITE_FAQS = [
    ("What do I need to use DigiKitPro brushes?",
     "The .brushset files require the Procreate app on an iPad. Brushes are calibrated for Apple Pencil pressure and tilt. Some products are PDFs, palettes or PNG files instead; each product page lists its file types under Technical Details."),
    ("How are the files delivered?",
     "Payhip handles checkout and digital delivery. Check the Payhip confirmation and receipt for access details; if you need help, use the contact page. No physical item is shipped."),
    ("How do I install a .brushset file on my iPad?",
     "Get the file onto your iPad, then tap it in the Files app and choose Open in Procreate. The set installs automatically and appears in your Brushes panel. There is a full walkthrough with screenshots in the How to install Procreate brushes guide."),
    ("Can I sell artwork I make with these brushes?",
     "Yes. Finished artwork you create with these files is yours to use personally and commercially. What you may not do is resell, redistribute, copy or share the brush, palette or source files themselves, in original or modified form. The full licence is on the Terms page."),
    ("Can I get a refund?",
     "Because these are digital downloads, all sales are final once the files have been downloaded. If you hit a technical problem with a file, contact us and we will resolve it. The Refund Policy page explains this in full."),
    ("What payment methods and currencies are accepted?",
     "Prices are listed in USD. Review the payment options, currency and total shown by Payhip before completing checkout."),
    ("Are there free brushes I can try first?",
     "Yes. Free brush packs, a color palette collection and a free starter guide are listed on the Free Brushes page. You can start with the fine liner set or the chalkboard toolkit."),
    ("Do the brushes work on Windows, Android or Photoshop?",
     "The .brushset format is specific to Procreate on iPad, so it will not load in Photoshop or on Windows and Android devices. Products that include PNG, PDF or palette files can be opened in any app that supports those formats; check the product page for what is included."),
    ("Which file do I download if a product has several ZIP parts?",
     "Download all of them. Larger libraries are split into several ZIP files purely because of file size limits, and each part contains a different set of brushes. The Technical Details on the product page state how many parts there are and the total size."),
    ("Is DigiKitPro affiliated with Procreate or Savage Interactive?",
     "No. DigiKitPro is an independent store. Procreate is a trademark of Savage Interactive Pty Ltd, and DigiKitPro is not affiliated with or endorsed by Savage Interactive."),
]


def _catalog_row(p):
    """One product's data for the Pinterest/Google-style product feed (CSV +
    XML share this same field set — see pinterest_feed() below). Every value
    comes straight from data/products.json; nothing is invented or estimated.
    Free items are marked out_of_stock intentionally: Pinterest catalogs are
    for items with a real checkout, and a $0 'purchase' isn't one — free
    items still get full Rich Pin treatment via product:price:amount=0.00
    on the page itself, they are just excluded from the paid catalog feed.
    """
    slug = p["slug"]
    link = absurl(f"products/{slug}/")
    im = p.get("images") or {}
    image = im.get("main") or im.get("card") or ""
    image_link = image if is_abs(image) else absurl(f"assets/products/{slug}/{image}")
    title = p["name"]
    desc = (p.get("seoDesc") or p.get("short") or p["name"]).strip()
    price = f"{p['price']:.2f} {p.get('currency', 'USD')}"
    availability = "in stock" if not p.get("free") else "out of stock"
    cat_path = " > ".join(x for x in ["DigiKitPro", p.get("category") or ""] if x)
    return {
        "id": slug,
        "title": title,
        "description": desc,
        "link": link,
        "image_link": image_link,
        "availability": availability,
        "price": price,
        "brand": "DigiKitPro",
        "condition": "new",
        # Verified Google product taxonomy leaf (id 4951, taxonomy v2021-09-21).
        # Pinterest catalog diagnostics flag anything shallower (Warning 126),
        # and the previous 3-segment value skipped the "Computer Software"
        # level, so it matched no real node at all.
        "google_product_category": "Software > Computer Software > Multimedia & Design Software > Graphic Design & Illustration Software",
        "product_type": cat_path,
        "item_group_id": p.get("category") or "",
    }


def build_pinterest_feed():
    """Pinterest product-catalog data source: one row per PAID product, the
    exact fields Pinterest's catalog/data-source ingestion documents (id,
    title, description, link, image_link, availability, price, brand,
    condition, google_product_category). Free items are Rich-Pin-only (see
    _catalog_row docstring) so they are left out of this feed on purpose.

    Written as both CSV (data-source upload / spreadsheet review) and XML/RSS
    2.0 with the g: namespace (feed-URL ingestion, no re-upload needed after
    every price/catalog change — Pinterest just re-fetches the URL).
    Regenerate by re-running tools/build.py; nothing here needs manual sync.
    """
    rows = [_catalog_row(p) for p in PRODUCTS if not p.get("free")]

    # ── CSV ────────────────────────────────────────────────────────────
    cols = ["id", "title", "description", "link", "image_link", "availability",
            "price", "brand", "condition", "google_product_category",
            "product_type", "item_group_id"]

    def _csv_cell(v):
        v = str(v).replace('"', '""')
        return f'"{v}"' if ("," in v or '"' in v or "\n" in v) else v

    csv_lines = [",".join(cols)]
    for r in rows:
        csv_lines.append(",".join(_csv_cell(r[c]) for c in cols))
    write("pinterest-feed.csv", "\n".join(csv_lines) + "\n")

    # ── XML / RSS 2.0 with g: namespace (Google Shopping / Pinterest catalog format) ──
    items = []
    for r in rows:
        items.append(f"""  <item>
    <g:id>{esc(r['id'])}</g:id>
    <title>{esc(r['title'])}</title>
    <description>{esc(r['description'])}</description>
    <link>{esc(r['link'])}</link>
    <g:image_link>{esc(r['image_link'])}</g:image_link>
    <g:availability>{esc(r['availability'])}</g:availability>
    <g:price>{esc(r['price'])}</g:price>
    <g:brand>{esc(r['brand'])}</g:brand>
    <g:condition>{esc(r['condition'])}</g:condition>
    <g:google_product_category>{esc(r['google_product_category'])}</g:google_product_category>
    <g:product_type>{esc(r['product_type'])}</g:product_type>
    <g:item_group_id>{esc(r['item_group_id'])}</g:item_group_id>
  </item>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
<channel>
  <title>{esc(SITE_NAME)} product catalog</title>
  <link>{esc(SITE_URL)}</link>
  <description>Paid {esc(SITE_NAME)} products for the Pinterest product catalog / data source.</description>
{chr(10).join(items)}
</channel>
</rss>
"""
    write("pinterest-feed.xml", xml)
    print(f"Pinterest catalog feed: {len(rows)} paid products -> pinterest-feed.csv / pinterest-feed.xml")


def _google_merchant_book(p):
    """Books/eBooks are held out of the initial Merchant feed until their
    identifiers and destination eligibility have been reviewed separately.
    Google treats eBooks specially for Shopping ads; do not leak them into a
    broad automatic source just because their pages share the product schema.
    """
    return p.get("category") == "Guides & eBooks" or "ebook" in p.get("slug", "").lower()


def build_google_merchant_feed():
    """Build a dedicated Google Merchant Center XML source from the catalog.

    This is intentionally not a copy of the Pinterest feed: that feed excludes
    free items and marks them out of stock because it only covers paid Pins.
    The Merchant feed contains all currently available non-book products,
    including free downloads (price 0, in stock), while keeping product links
    on the claimed DigiKitPro domain. Ebooks are excluded pending a separate
    Google policy/identifier review.

    Only GTINs and MPNs explicitly present in products.json are emitted. When
    neither is supplied, identifier_exists=no accurately says that the catalog
    has no assigned unique item identifier; it never reuses a Payhip ID or SKU
    slug as a GTIN/MPN. Generate this file on every site build; Merchant Center
    can fetch its public URL on a schedule.
    """
    products = [p for p in PRODUCTS
                if not p.get("comingSoon") and not _google_merchant_book(p)]
    items = []
    for p in products:
        slug = p["slug"]
        product_url = absurl(f"products/{slug}/")
        im = p.get("images") or {}
        full_images = [url for url, _ in _fullsize_product_images(p)]
        if not full_images:
            fallback = im.get("main") or im.get("card") or ""
            if fallback:
                full_images = [asset_abs(slug, fallback)]
        image_url = full_images[0] if full_images else absurl("assets/img/og-cover.jpg")
        desc = (p.get("short") or p.get("seoDesc") or p["name"]).strip()
        currency = p.get("currency", "USD").upper()
        price = f"{float(p['price']):.2f} {currency}"
        gtin = str(p.get("gtin") or "").strip()
        mpn = str(p.get("mpn") or "").strip()
        brand = str(p.get("brand") or SITE_NAME).strip()
        identifier_exists = "yes" if gtin or (mpn and brand) else "no"
        product_type = " > ".join(x for x in (SITE_NAME, p.get("category", "Digital downloads")) if x)
        extra_images = "\n".join(
            f"    <g:additional_image_link>{esc(url)}</g:additional_image_link>"
            for url in full_images[1:11]
        )
        identifiers = []
        if gtin:
            identifiers.append(f"    <g:gtin>{esc(gtin)}</g:gtin>")
        if mpn:
            identifiers.append(f"    <g:mpn>{esc(mpn)}</g:mpn>")
        identifiers.append(f"    <g:identifier_exists>{identifier_exists}</g:identifier_exists>")
        items.append(f"""  <item>
    <g:id>{esc(slug)}</g:id>
    <g:title>{esc(p['name'])}</g:title>
    <g:description>{esc(desc)}</g:description>
    <g:link>{esc(product_url)}</g:link>
    <g:image_link>{esc(image_url)}</g:image_link>
{extra_images}
    <g:availability>in_stock</g:availability>
    <g:price>{esc(price)}</g:price>
    <g:brand>{esc(brand)}</g:brand>
    <g:condition>new</g:condition>
    <g:product_type>{esc(product_type)}</g:product_type>
{chr(10).join(identifiers)}
  </item>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
<channel>
  <title>{esc(SITE_NAME)} Google Merchant Center products</title>
  <link>{esc(SITE_URL)}</link>
  <description>Available DigiKitPro digital products. Product landing pages, prices and images are generated from the live catalog.</description>
{chr(10).join(items)}
</channel>
</rss>
"""
    write("google-merchant-feed.xml", xml)
    print(f"Google Merchant feed: {len(products)} available non-book products -> google-merchant-feed.xml")


def build_misc():
    # ── CONTACT ──
    # Support goes to the Payhip store; do not claim a site form is configured.
    contact_schemas = schema_breadcrumb([("Home", "/"), ("Contact", "/contact.html")])
    html_out = head("Contact DigiKitPro",
        "Contact DigiKitPro about a product, an order, a technical problem with a file, or licensing via the Payhip store.",
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
    <p class="lead">Questions about a product, an order, a file that will not open, or licensing? Contact us directly via our Payhip store — we read and reply to every message.</p>
    <div class="contact-card">
      <a class="btn btn-gold btn-lg" href="{STORE_URL}" target="_blank" rel="noopener">Contact on Payhip ↗</a>
      <p class="muted" style="margin-top:1rem">Payhip handles all orders and messaging securely. Click above to open the store contact form.</p>
    </div>
    <div class="prose contact-alt">
      <h2>Before you write</h2>
      <p>These answer most messages, and you will get an answer instantly:</p>
      <ul>
        <li><strong>Where are my files?</strong> Payhip handles delivery. Check the email address used for checkout and its spam folder; if you need help, contact the store with your order details.</li>
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
  <p class="lead">Everything sold here is a digital download. This page states the same policy as our <a href="terms.html">Terms of Service</a>, in one place so you can read it before you buy.</p>
  <h2>All sales are final once files are downloaded</h2>
  <p>Because digital files cannot be returned, all sales are final once the files have been downloaded. Please check compatibility before buying: .brushset files require the Procreate app on an iPad, and each product page lists exactly what file types are included under Technical Details.</p>
  <h2>Technical problems are resolved</h2>
  <p>If you hit a technical problem with any file, for example a download that will not complete, a corrupted file, or a brushset that will not open in Procreate, <a href="contact.html">contact us</a> and we will resolve it. Tell us which product it is and what happens when you try to open it, and include your Payhip order number if you have it.</p>
  <h2>Not sure yet? Start free</h2>
  <p>If you want to try the brushes before spending anything, the <a href="freebies.html">free brush packs</a> can help you practise importing Procreate brushsets on your iPad.</p>
  <h2>Payments and chargebacks</h2>
  <p>All payments are processed by Payhip, not by DigiKitPro. Billing questions can also be raised through your Payhip receipt.</p>
  <h2>Contact</h2>
  <p>Use the <a href="contact.html">contact page</a> or the contact form on our <a href="{STORE_URL}" target="_blank" rel="noopener">Payhip store</a>.</p>
</div></section></main>
{footer(0)}"""
    write("refunds.html", html_out)

    # ── FAQ ──
    faq_items = "".join(
        f'<details class="faq-q"><summary>{esc(q)}</summary><div class="faq-body"><p>{esc(a)}</p></div></details>'
        for q, a in SITE_FAQS)
    faq_schemas = schema_breadcrumb([("Home", "/"), ("FAQ", "/faq.html")]) + schema_faq(SITE_FAQS)
    html_out = head("FAQ, DigiKitPro Procreate Brushes",
        "Answers to common questions about DigiKitPro Procreate brushes: compatibility, delivery, installing a .brushset, the commercial licence and refunds.",
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
      <p>Use the <a href="contact.html">contact page</a> or the contact form on our <a href="{STORE_URL}" target="_blank" rel="noopener">Payhip store</a>. For the legal detail, see the <a href="terms.html">Terms</a>, the <a href="refunds.html">Refund Policy</a> and the <a href="privacy.html">Privacy Policy</a>.</p>
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
        "DigiKitPro offers Procreate brushes and digital resources for portrait artists, illustrators and digital painters.",
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
    <p>DigiKitPro offers Procreate brushes for portrait artists, illustrators and digital painters. Explore tools for sketching, skin texture, linework and other creative workflows.</p>
    <h2>What we believe</h2>
    <ul>
      <li><strong>Workflow over catalog size.</strong> A kit organized around how you paint beats a thousand loose brushes.</li>
      <li><strong>Real media behavior.</strong> Bleeds, tooth, crumble and granulation, digital tools should carry the soul of physical media.</li>
      <li><strong>Honest pricing.</strong> Professional kits for the price of a coffee, and useful free packs that let you test the quality first.</li>
    </ul>
    <h2>How a kit earns its place</h2>
    <p>Kits bring together tools for stages of making artwork: sketching, line, paint, texture, detail or finishing. Product pages state the listed files, compatibility and requirements so you can check the fit before buying.</p>
    <p>Check the product page for compatibility before buying. If a file does not install or an order is missing, use the <a href="contact.html">support page</a> with the product name and order details.</p>
    <h2>Digital products and language options</h2>
    <p>Our catalog contains digital products sold through Payhip; no physical items are shipped. Prices are listed in USD. Review the available payment methods, currency and total at checkout. Use the globe button in the header to request a translation into English, Español, Français, Deutsch, Italiano, Português or Nederlands.</p>
    <h2 id="contact">Contact</h2>
    <p>Questions about a product, an order, or a collaboration? Contact us via the form on our <a href="{STORE_URL}" target="_blank" rel="noopener">Payhip store</a> or visit our <a href="contact.html">contact page</a>.</p>
    <h2 id="faq">Quick answers</h2>
    <p>Short, direct answers to the questions artists ask most. For anything else, use the contact form on <a href="{STORE_URL}" target="_blank" rel="noopener">Payhip</a>.</p>
    {faq_html}
  </div></section>
  {newsletter(0)}
</main>
{footer(0)}"""
    write("about.html", html_out)

    # ── PRIVACY ──
    html_out = head("Privacy Policy, DigiKitPro", "How DigiKitPro handles your data: newsletter sign-up, purchases processed securely by Payhip, and your rights.", SITE_URL + "/privacy.html", 0)
    html_out += header(0)
    email_disclosure = ("If you explicitly subscribe to product news, the configured email provider receives your address and consent choice." if EMAIL_ENDPOINT else "This site currently has no newsletter signup provider. Payhip may ask for an email address when delivering a free or paid product.")
    feedback_disclosure = ("An optional feedback form may send your selected answer and any text you choose to provide to our configured feedback service." if FEEDBACK_ENDPOINT else "The optional feedback collector is not configured on this site.")
    ga_disclosure = ("<strong>Google Analytics 4:</strong> the Google tag measures page and product activity and may set cookies and process your IP address. We do not load it if your browser sends Do Not Track or Global Privacy Control, or if you opt out below. You can also use <a href=\"https://tools.google.com/dlpage/gaoptout\" rel=\"noopener\" target=\"_blank\">Google's opt-out add-on</a>." if GA_MEASUREMENT_ID and ANALYTICS_ENABLED else "<strong>Google Analytics 4:</strong> Google Analytics is not enabled in this build of the site.")
    html_out += f"""
<main id="main"><section class="section"><div class="wrap narrow prose">
  {crumbs(0, [("Privacy Policy","privacy.html")])}
  <h1>Privacy Policy</h1>
  <h2>Overview</h2>
  <p>DigiKitPro ("we", "our") operates this content website and sells digital products through Payhip. This policy explains what data we collect and why.</p>
  <h2>Data we collect</h2>
  <ul>
    <li><strong>Email and delivery details:</strong> {esc(email_disclosure)}</li>
    <li><strong>Purchase data:</strong> all payments and order data are processed by Payhip on their secure checkout. We never see or store your payment card details. See Payhip's own privacy policy for how they process order data.</li>
  </ul>
  <h2>Analytics &amp; cookies</h2>
  <p>This is a static website with no server of our own, but it is not analytics-free, and we would rather tell you plainly than imply otherwise.</p>
  <ul>
    <li>{ga_disclosure}</li>
    <li><strong>When site analytics is enabled, what we measure:</strong> page and product views, clicks on buy, free-download and optional recommendation links, and search-query length. These clicks are not proof that a purchase or download completed. Search text and URL query strings are excluded from the site's custom events. If a link has campaign tags, basic source, medium, campaign and optional content or ID labels may be sent to Google for attribution. {esc(feedback_disclosure)}</li>
    <li><strong>Advertising:</strong> the optional Pinterest advertising tag is not loaded unless configured by the site owner.</li>
    <li><strong>When measurement is enabled, a first-party summary</strong> of event counts is kept in your browser's <code>localStorage</code>; the summary itself is not uploaded. Clearing your browser data removes it.</li>
    <li><strong>Google Translate</strong> (the globe button in the header) is loaded from Google only when you choose a language. Google sets its own <code>googtrans</code> cookie to remember that choice. Do not use the button if you prefer not to contact Google.</li>
    <li><strong>Payhip</strong> handles all payments. Checkout happens on payhip.com under <a href="https://payhip.com/privacy" rel="noopener" target="_blank">Payhip's own privacy policy</a>; we never see or store your card details.</li>
  </ul>
  <p><a href="privacy.html?analytics=off#dkp-analytics=off">Turn site analytics off</a> · <a href="privacy.html?analytics=on#dkp-analytics=on">Turn site analytics back on</a>. Your choice is stored in this browser. Do Not Track and Global Privacy Control still take precedence.</p>
  <h2>Your rights</h2>
  <p>For questions or requests about data, use the <a href="contact.html">contact page</a>. For information held by Payhip, see <a href="https://payhip.com/privacy" target="_blank" rel="noopener">Payhip's privacy policy</a>.</p>
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
    html_out = head("Search, DigiKitPro", "Search all DigiKitPro Procreate brushes, bundles, freebies and articles.", SITE_URL + "/search.html", 0,
                      robots="noindex, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
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
    # GitHub Pages serves 404.html at the *requested* URL, not /404.html.
    # Use root-relative links and assets at unknown depths, but no <base>:
    # a base URL would make the #main skip link navigate to the homepage.
    html_out = head("Page not found, DigiKitPro", "That page doesn't exist, but the brushes do. Browse the full DigiKitPro catalog.", SITE_URL + "/404.html", ROOT_RELATIVE,
                      robots="noindex, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
    html_out += header(ROOT_RELATIVE)
    html_out += f"""
<main id="main"><section class="section"><div class="wrap narrow" style="text-align:center;padding:6rem 0">
  <p class="eyebrow">404</p>
  <h1>This canvas is blank.</h1>
  <p class="lead">The page you're looking for didn't make it to the final artwork.</p>
  <div class="hero-ctas" style="justify-content:center"><a class="btn btn-gold" href="/index.html">Back to Home</a><a class="btn btn-line" href="/products.html">Browse Products</a></div>
  <p>Or explore <a class="text-link" href="/freebies.html">free brushes</a> and <a class="text-link" href="/blog.html">art tutorials</a>.</p>
</div></section></main>
{footer(ROOT_RELATIVE)}"""
    write("404.html", html_out)

    # ── .nojekyll: tell GitHub Pages to serve files as-is (no Jekyll build) ──
    write(".nojekyll", "")

    # ── robots + sitemap ──
    # Three sitemaps: URL xml, URL txt, and the dedicated image sitemap
    # (full-size product artwork only — see sitemap-images.xml below).
    write("robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/sitemap.txt
Sitemap: {SITE_URL}/sitemap-images.xml
""")

    static_urls = [
        ("/", "1.0", "daily"),
        ("/products.html", "0.9", "daily"),
        ("/freebies.html", "0.9", "weekly"),
        ("/bundles.html", "0.8", "weekly"),
        ("/blog.html", "0.8", "weekly"),
        ("/about.html", "0.6", "monthly"),
        ("/faq.html", "0.6", "monthly"),
        ("/contact.html", "0.5", "monthly"),
        ("/refunds.html", "0.3", "monthly"),
        ("/privacy.html", "0.3", "monthly"),
        ("/terms.html", "0.3", "monthly"),
    ]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    for u, pr, freq in static_urls:
        sm += f" <url><loc>{SITE_URL}{u}</loc> <changefreq>{freq}</changefreq><priority>{pr}</priority></url>\n"

    for cslug in CATEGORY_SLUGS.values():
        sm += f" <url><loc>{SITE_URL}/category/{cslug}/</loc> <changefreq>weekly</changefreq><priority>0.85</priority></url>\n"

    # Seasonal hub pages (Halloween, Christmas, ...)
    for sdef in SEASON_DEFS:
        sm += f" <url><loc>{SITE_URL}/season/{sdef['slug']}/</loc> <changefreq>monthly</changefreq><priority>0.7</priority></url>\n"

    # Buyer-guide landing pages (tools/pages_guides.py) — commercial intent
    for u in [f"/{GUIDES_DIR}/"] + [f"/{u}" for u in GUIDE_URLS]:
        sm += f" <url><loc>{SITE_URL}{u}</loc> <changefreq>weekly</changefreq><priority>0.75</priority></url>\n"

    # Partner portal (tools/pages_partner.py). Deliberately the lowest
    # priority on the site: it is a page for creators who already know the
    # store, not a search-traffic landing page, and it must never outrank a
    # product or a buyer guide in the crawl budget.
    sm += f" <url><loc>{SITE_URL}{PARTNER_URL}</loc> <changefreq>monthly</changefreq><priority>0.4</priority></url>\n"

    # SEO tools (tools/pages_tools.py) — high-intent utility pages
    # /tools/ landing + individual tools like /tools/canvas-calculator/
    sm += f" <url><loc>{SITE_URL}/{_TOOLS_DIR}/</loc> <changefreq>weekly</changefreq><priority>0.8</priority></url>\n"
    for _td in _TOOL_DEFS:
            sm += f" <url><loc>{SITE_URL}/{_TOOLS_DIR}/{_td['slug']}/</loc> <changefreq>monthly</changefreq><priority>0.75</priority></url>\n"

    for p in PRODUCTS:
        slug = p["slug"]
        im = p.get("images") or {}
        img = im.get("card") or im.get("main") or ""
        img_xml = ""
        if img:
            img_loc = img if is_abs(img) else absurl(f"assets/products/{slug}/{img}")
            img_xml = f"<image:image><image:loc>{img_loc}</image:loc><image:title>{esc(p['name'])}</image:title></image:image>"
        sm += f" <url><loc>{SITE_URL}/products/{slug}/</loc> <changefreq>daily</changefreq><priority>0.8</priority>{img_xml}</url>\n"

    for a in load_articles():
        slug = a["slug"]
        img = a.get("image") or ""
        img_xml = ""
        if img:
            img_loc = img if is_abs(img) else absurl(img)
            img_xml = f"<image:image><image:loc>{img_loc}</image:loc><image:title>{esc(a['title'])}</image:title></image:image>"
        sm += f" <url><loc>{SITE_URL}/blog/{slug}/</loc> <changefreq>weekly</changefreq><priority>0.7</priority>{img_xml}</url>\n"

    sm += "</urlset>\n"
    write("sitemap.xml", sm)

    # ── Plain-text sitemap (one URL per line) ──────────────────────────────
    txt_urls = [
        SITE_URL + "/",
        SITE_URL + "/products.html",
        SITE_URL + "/freebies.html",
        SITE_URL + "/bundles.html",
        SITE_URL + "/blog.html",
        SITE_URL + "/about.html",
        SITE_URL + "/faq.html",
        SITE_URL + "/contact.html",
        SITE_URL + "/refunds.html",
        SITE_URL + "/privacy.html",
        SITE_URL + "/terms.html",
    ]
    txt_urls += [f"{SITE_URL}/category/{cslug}/" for cslug in CATEGORY_SLUGS.values()]
    txt_urls += [f"{SITE_URL}/season/{sdef['slug']}/" for sdef in SEASON_DEFS]
    txt_urls += [f"{SITE_URL}/{GUIDES_DIR}/"] + [f"{SITE_URL}/{u}" for u in GUIDE_URLS]
    txt_urls += [f"{SITE_URL}{PARTNER_URL}"]
    # SEO tools
    txt_urls += [f"{SITE_URL}/{_TOOLS_DIR}/"]
    txt_urls += [f"{SITE_URL}/{_TOOLS_DIR}/{_td['slug']}/" for _td in _TOOL_DEFS]
    txt_urls += [f"{SITE_URL}/products/{p['slug']}/" for p in PRODUCTS]
    txt_urls += [f"{SITE_URL}/blog/{a['slug']}/" for a in load_articles()]
    write("sitemap.txt", "\n".join(txt_urls) + "\n")

    # ── Image sitemap (full-size product artwork only) ───────────────────
    # Cards and thumbs are downscaled crops of the same artwork; submitting
    # both would offer Google duplicates. Titles reuse the alt text already
    # rendered on the product page (hand-written or from seo_engine.py).
    img_sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
              'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')
    n_img_pages = 0
    n_img_locs = 0
    for p in PRODUCTS:
        entries = _fullsize_product_images(p)
        if not entries:
            continue
        img_sm += f" <url><loc>{SITE_URL}/products/{p['slug']}/</loc>"
        for loc, title in entries:
            img_sm += (f"<image:image><image:loc>{esc(loc)}</image:loc>"
                       f"<image:title>{esc(title)}</image:title></image:image>")
            n_img_locs += 1
        img_sm += "</url>\n"
        n_img_pages += 1
    img_sm += "</urlset>\n"
    write("sitemap-images.xml", img_sm)
    print(f"image sitemap: {n_img_pages} pages, {n_img_locs} full-size images")

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
    # Buyer guides ride the articles index so ⌘K/search surfaces the shopping
    # pages for "pencil", "texture", "animation", "bundle", "beginner" queries.
    idx_articles += [{"t": g["h1"], "u": f"{GUIDES_DIR}/{g['slug']}/", "d": g["card_blurb"],
                      "k": (g["h1"] + " buyer guide shopping " + g["card_blurb"] + " " + g["slug"].replace("-", " ")).lower()}
                     for g in GUIDE_DEFS]
    idx_articles.append({"t": GUIDES_INDEX["h1"], "u": f"{GUIDES_DIR}/", "d": GUIDES_INDEX["lead"][:140],
                         "k": (GUIDES_INDEX["h1"] + " buyer guides shopping " + GUIDES_INDEX["seo_desc"]).lower()})
    # Tools in search index so ⌘K finds the calculator
    for _td in _TOOL_DEFS:
        idx_articles.append({"t": _td["title"], "u": f"{_TOOLS_DIR}/{_td['slug']}/", "d": _td["short"][:140],
                             "k": (_td["title"] + " " + _td["short"] + " tool calculator " + _td["slug"].replace("-", " ")).lower()})
    idx_articles.append({"t": "Procreate Tools", "u": f"{_TOOLS_DIR}/", "d": "Free interactive tools for Procreate artists", "k": "tools canvas calculator procreate"})
    js = "window.DKP_INDEX=" + json.dumps({"products": idx_products, "articles": idx_articles}, ensure_ascii=False) + ";"
    write("js/search-index.js", js)
    print("misc pages + sitemap + search index done")
