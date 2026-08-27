# DigiKitPro — Website

A complete, production-ready static ecommerce-content site for the **DigiKitPro** digital art store
(Procreate brushes & digital art resources). 100% static HTML/CSS/JS — no backend, no database,
no build dependencies. **All product data, images and prices are the real store data from
https://payhip.com/digikitpro** (scraped and verified on 2026-08-11).

---

## 1. Publish (free hosting)

The site works as-is on any static host:

| Host | How |
|---|---|
| **Netlify** | Drag-and-drop this folder onto app.netlify.com/drop |
| **Cloudflare Pages** | New project → upload assets (no build command) |
| **GitHub Pages** | Push to a repo → Settings → Pages → deploy from branch root |
| **Vercel / others** | New project → no framework preset, no build step |

Works from a subdomain, apex domain **or** a sub-path (e.g. `user.github.io/repo/`) —
all links are relative.

**Before going live:** open `tools/build.py` and set
- `SITE_URL = "https://your-domain.com"` → then run `python3 tools/build.py`
  (regenerates canonical URLs, Open Graph URLs and `sitemap.xml`)
- `SOCIAL = {...}` → your Pinterest / Instagram / TikTok URLs (hidden while empty — we never fake links)

Then submit `sitemap.xml` in Google Search Console & Bing Webmaster Tools.

## 2. Content control (no HTML editing needed)

| To change… | Edit | Then run |
|---|---|---|
| Products (name, price, images, descriptions, Payhip URL, categories…) | `data/products.json` | `python3 tools/build.py` |
| Blog articles | `content/blog/*.md` (front-matter + markdown) | `python3 tools/build.py` |
| Design / colors | `css/style.css` (variables at top) | — (no rebuild) |
| Behavior (search, filters, gallery) | `js/main.js` | — |

`data/products.json` is the single source of truth — 49 products, each with
`name, slug, price, category, short, descriptionHtml, included[], features[], technical[],
requirements[], images, tags[], related[], payhipUrl, seoTitle, seoDesc, featured, free`.
Delete an entry → its pages disappear on rebuild. Add one → page, card, sitemap and search
entry are created.

**Adding a new product image:** drop WebP/JPG/PNG into `assets/products/<slug>/` and point
`images.card` / `images.main` in `data/products.json` at it (regenerate variants with any
image tool; `scraped/images.py` shows the exact pipeline used originally).

## 3. Email capture ✅ configured

Newsletter forms (home, blog, products, freebies…) post **real submissions to
`digikitprostudio@gmail.com`** via FormSubmit — visitors never leave the page (AJAX),
and a genuine success/error message is shown for each attempt.

**One-time activation (required):** check the `digikitprostudio@gmail.com` inbox (and spam)
for an email from FormSubmit titled *"Confirm your email"* / containing an
**"Activate Form"** link — click it once. From then on, every signup arrives in
that inbox with subject **"New DigiKitPro subscriber"**.

To move to another provider later (Brevo, MailerLite, ConvertKit…): replace
`EMAIL_TO`/`EMAIL_ENDPOINT` in `tools/core.py` (via `tools/build.py`) with the
provider's form-action URL and rebuild.

> Note: browsers strip the identity of pages opened by double-clicking an HTML
> file (`file://`), so mail services refuse those submissions by design. The
> form shows an honest "offline preview" message there; signups work from the
> hosted site and from `python -m http.server`.
(ConvertKit / MailerLite / Brevo all provide one) and rebuild — forms will POST to it.
Until then, submits gracefully deep-link to the store's Freebies collection.

## 4. Structure

```
index.html  products.html  bundles.html  freebies.html  blog.html  about.html
search.html  privacy.html  terms.html  404.html
products/<slug>/index.html        × 49 product pages
blog/<slug>/index.html            × 10 articles
assets/products/<slug>/*.webp     × 174 original product images (3 size variants)
assets/img/                       brand assets (favicon / OG cover)
css/style.css  js/main.js  js/search-index.js
data/products.json                ← master product data (edit me)
content/blog/*.md                 ← article source (edit me)
tools/build.py  tools/core.py …   ← generator (run: python3 tools/build.py)
robots.txt  sitemap.xml
scraped/                          ← original scraper + Payhip source data (reference only)
```

## 5. SEO built in

Unique title/meta per page · canonicals · Open Graph + Twitter cards · Product + Offer JSON-LD
with real Payhip prices · Article schema · BreadcrumbList · Organization + WebSite (SearchAction) ·
FAQPage schema on product pages · `sitemap.xml` (69 URLs) · `robots.txt` · semantic HTML5 ·
lazy-loading responsive WebP · descriptive alt text · clean URLs.

## 6. Where the data came from

Product names, prices, file sizes, full descriptions, galleries and the Payhip URLs were taken
from the live store `payhip.com/digikitpro` on 2026-08-11 (see `scraped/catalog.json`).
Nothing is invented. If a product is added/removed in the store later, update
`data/products.json` to match. Social profile URLs are intentionally blank until configured.
