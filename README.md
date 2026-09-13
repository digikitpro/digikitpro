# DigiKitPro - Website

A complete, production-ready static ecommerce-content site for the **DigiKitPro** digital art store
(Procreate brushes & digital art resources). 100% static HTML/CSS/JS - no backend, no database,
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

Works from a subdomain, apex domain **or** a sub-path (e.g. `user.github.io/repo/`) -
all links are relative.

**Before going live:** open `tools/build.py` and set
- `SITE_URL = "https://your-domain.com"` → then run `python3 tools/build.py`
  (regenerates canonical URLs, Open Graph URLs and `sitemap.xml`)
- `SOCIAL = {...}` → your Pinterest / Instagram / TikTok URLs (hidden while empty - we never fake links)

Then submit `sitemap.xml` in Google Search Console & Bing Webmaster Tools.

## 2. Content control (no HTML editing needed)

| To change… | Edit | Then run |
|---|---|---|
| Products (name, price, images, descriptions, Payhip URL, categories…) | `data/products.json` | `python3 tools/build.py` |
| **Merchandising** (product hierarchy, who each pack is for, Brush Finder answers) | `data/discovery.json` | `python3 tools/build.py` |
| Blog articles | `content/blog/*.md` (front-matter + markdown) | `python3 tools/build.py` |
| Design / colors | `css/style.css` (variables at top) | - (no rebuild) |
| Behavior (search, filters, gallery) | `js/main.js` | - |
| Motion (reveals, hover states, before/after slider, sticky CTA) | `js/motion.js` + the `MOTION SYSTEM` block at the end of `css/style.css` | - |

`data/products.json` is the single source of truth - 51 products, each with
`name, slug, price, category, short, descriptionHtml, included[], features[], technical[],
requirements[], images, tags[], related[], payhipUrl, seoTitle, seoDesc, featured, free`.
Delete an entry → its pages disappear on rebuild. Add one → page, card, sitemap and search
entry are created.

**Adding a new product image:** drop WebP/JPG/PNG into `assets/products/<slug>/` and point
`images.card` / `images.main` in `data/products.json` at it (regenerate variants with any
image tool; `scraped/images.py` shows the exact pipeline used originally).

### Motion system (`js/motion.js` — 19 KB raw / 5.6 KB gzipped, no libraries)

The site's look is unchanged; this layer only makes it *move*. It adds: hero entrance
(headline → copy → CTAs → artwork), scroll reveals with a short stagger, hover/press
feedback on cards, categories, bundles and buttons, cursor parallax on the hero covers and
bundle tiles, a 2 px scroll-progress thread, a dismissible sticky CTA (homepage only, after
the hero, never over the footer) and the interactive **before/after slider** (homepage,
medium-width, after the free-brushes row; the slider also ships wherever a `[data-ba]`
stage is added).

Rules it keeps:

- only `opacity`, `transform`/`translate` and `clip-path` are animated, and only while an
  element is on screen (IntersectionObserver unobserves after firing);
- one shared `requestAnimationFrame` loop for every scroll-driven effect;
- `prefers-reduced-motion: reduce` → no parallax, no looping, no travel (a 200 ms fade at
  most);
- phones → shorter reveals, no cursor parallax, nothing that needs hover;
- progressive enhancement: without JS the `js-motion` class is never set, nothing is ever
  hidden, and the page works exactly as before. A 4 s failsafe removes the class if
  `js/motion.js` fails to load, and an 8 s failsafe reveals anything not yet revealed.

**Swapping the before/after artwork:** replace `assets/img/ba-before.webp` (flat base) and
`assets/img/ba-after.webp` (finished) — same size, same crop, ideally 1200×800. The current
pair is **demonstration artwork** (labelled as such in the caption); real client work with a
proper before/after will sell harder. Nothing else needs editing.

**Adding a reveal to a new component:** add the selector to *both* the `MOTION SYSTEM →
SCROLL REVEAL` list in `css/style.css` (hide rule and `.rv-in` rule — both, or specificity
will keep it invisible) and `REVEAL_SELECTORS` in `js/motion.js`.

## 3. Email capture ✅ configured

Newsletter forms (home, blog, products, freebies…) post **real submissions to
`digikitprostudio@gmail.com`** via FormSubmit - visitors never leave the page (AJAX),
and a genuine success/error message is shown for each attempt.

**One-time activation (required):** check the `digikitprostudio@gmail.com` inbox (and spam)
for an email from FormSubmit titled *"Confirm your email"* / containing an
**"Activate Form"** link - click it once. From then on, every signup arrives in
that inbox with subject **"New DigiKitPro subscriber"**.

To move to another provider later (Brevo, MailerLite, ConvertKit…): replace
`EMAIL_TO`/`EMAIL_ENDPOINT` in `tools/core.py` (via `tools/build.py`) with the
provider's form-action URL and rebuild.

> Note: browsers strip the identity of pages opened by double-clicking an HTML
> file (`file://`), so mail services refuse those submissions by design. The
> form shows an honest "offline preview" message there; signups work from the
> hosted site and from `python -m http.server`.
(ConvertKit / MailerLite / Brevo all provide one) and rebuild - forms will POST to it.
Until then, submits gracefully deep-link to the store's Freebies collection.

## 4. Structure

```
index.html  products.html  bundles.html  freebies.html  blog.html  about.html
search.html  privacy.html  terms.html  404.html
find-my-brushes.html        ← the Brush Finder (Level-1 conversion tool)
thank-you.html              ← post-signup delivery + first starter offer (noindex)
products/<slug>/index.html        × 51 product pages
blog/<slug>/index.html            × 16 articles
assets/products/<slug>/*.webp     × 174 original product images (3 size variants)
assets/img/                       brand assets (favicon / OG cover)
css/style.css  js/main.js  js/search-index.js
data/products.json                ← master product data (edit me)
data/discovery.json               ← merchandising model (edit me; see §8)
content/blog/*.md                 ← article source (edit me)
tools/build.py  tools/core.py …   ← generator (run: python3 tools/build.py)
js/analytics.js  js/finder.js  js/feedback.js   ← conversion layer (no build needed)
robots.txt  sitemap.xml
scraped/                          ← original scraper + Payhip source data (reference only)
```

## 5. SEO built in

Unique title/meta per page · canonicals · Open Graph + Twitter cards · Product + Offer JSON-LD
with real Payhip prices · Article schema · BreadcrumbList · Organization + WebSite (SearchAction) ·
FAQPage schema on product pages · `sitemap.xml` (76+ URLs) · `robots.txt` · semantic HTML5 ·
lazy-loading responsive WebP · descriptive alt text · clean URLs.

## 6. Where the data came from

Product names, prices, file sizes, full descriptions, galleries and the Payhip URLs were taken
from the live store `payhip.com/digikitpro` on 2026-08-11 (see `scraped/catalog.json`).
Nothing is invented. If a product is added/removed in the store later, update
`data/products.json` to match. Social profile URLs are intentionally blank until configured.

## 7. Auto-sync from Payhip, translation & trending (v2)

- **Payhip → site:** run `python3 tools/payhip_sync.py` (or install
  `docs/automation/payhip-auto-sync.yml` as `.github/workflows/sync-payhip.yml` to run it daily) to
  detect and add new products automatically. It never overwrites hand-written SEO copy.
- **International:** the header includes a 7-language Google Translate switcher and the homepage has
  a worldwide trust band. `tools/core.py` has `LANGUAGES` and `GEO_META` if you want to change them.
- **Trending:** homepage and `/products.html` build auto-rotating trending product cards + trending
  search links from `data/products.json`.
- **IndexNow:** set `INDEXNOW_KEY` as a GitHub repo variable; the build writes `<key>.txt` and the
  deploy/sync workflows ping Bing, Yandex and Seznam.

See `SEO-INDEXING.md` for Google Search Console + Bing Webmaster + IndexNow setup and a content
cadence that keeps the site visible on search results.


## 8. Sales engine (Phase 1) — how the new parts work

Full audit and the phased plan: **`docs/AUDIT-AND-PLAN.md`**.

### The value ladder
Every product now carries a **tier** in `data/discovery.json`, and the homepage,
catalog and Brush Finder all read it:

| Level | Tier | What it is | Where it appears |
|---|---|---|---|
| 1 | `free` | Free Procreate packs | Homepage §3, `/freebies.html` (email-first), `/thank-you.html` |
| 2 | `entry` | $4–$10 specialist packs (skin, hair, line art…) | Homepage §5, catalog, finder primary result |
| 3 | `bundle` | $8–$20 multi-kit bundles | Homepage §9, `/bundles.html` |
| 4 | `flagship` | **Master Library, 2,000+ brushes, $19** | Homepage §4 (dedicated band) + upgrade panel on 37 product pages |
| 5 | `education` | Free starter guide + $19 Portrait Masterclass | Homepage §7, finder cross-sell for portrait answers |

### Brush Finder — `find-my-brushes.html`
Four questions (craft → goal → level → style) produce one recommendation.
Scoring is **relevance-first, never price-first**: craft +40, goal +30, style +15,
level +10, editorial priority ≤+5. Verified across all **1,080** answer
combinations: every one returns a result, and in **zero** of them does a
whole-catalog bundle become the primary recommendation.

`aggregate: true` in `data/discovery.json` marks the three whole-catalog
libraries (Master Library, Master Vault, Mega Bundle). They match every answer
by definition, so they are excluded from ranking and shown only in their own
labelled "Want everything?" slot — otherwise the finder would recommend the
most expensive item every single time.

The page is server-rendered first: all four questions are real radio inputs and
a "Browse by what you create" section below gives the same recommendations as
plain HTML, so it works with JavaScript off and is fully crawlable.

### Conversion events — `js/analytics.js`
One entry point, `dkp.track(name, params)`. Forwards to GA4 and keeps a
first-party count-only summary in `localStorage`. Events: `homepage_view`,
`product_view`, `category_view`, `bundle_view`, `master_library_view`,
`masterclass_view`, `free_download_click`, `email_signup`, `product_buy_click`,
`outbound_payhip_click`, `brush_finder_started`, `brush_finder_completed`,
`recommendation_clicked`, `upgrade_clicked`, `craft_card_click`, `search_query`,
`scroll_depth`, `feedback_reason`.

Debug in the browser console: `dkp.report()` · `dkp.clear()`.
Turn it off entirely: visit any page with `#dkp-analytics=off`, or build with
`DKP_ANALYTICS=false`. `Do Not Track` is honoured as a full opt-out.
No PII, no new cookies, no cross-site identifier. Disclosed in `privacy.html`.

### Freebie funnel
`freebies.html` leads with an email gate; the direct Payhip link stays visible
underneath so a promised free file is never held hostage. On a real provider
response `js/main.js` sends the visitor to `thank-you.html?lead=<slug>`, which
puts the pack they asked for first, links every free download directly, then
makes **one** starter offer and shows the Master Library.

To wire a real email sequence (MailerLite / Brevo / ConvertKit), set
`EMAIL_ENDPOINT` in `tools/core.py` to the provider's form-action URL and
rebuild. The 5-email sequence is specified in `docs/AUDIT-AND-PLAN.md` §9.
No API key ever goes in frontend code.

### "What stopped you from choosing a brush today?" — `js/feedback.js`
Product/catalog pages only, after ≥60 % scroll **and** ≥25 s, and never once a
visitor has clicked a buy link. Once per visit; dismissed means never again.
Every answer returns something useful to the visitor (Finder, bundles, guides).
Fires `feedback_reason`. To collect answers in your own store, set the
`DKP_FEEDBACK_ENDPOINT` build variable — empty by default, so nothing is posted
anywhere until you point it at a Cloudflare Worker or Vercel function.

### Owner decisions currently in force (2026-09-13)

- **Email:** FormSubmit → `digikitprostudio@gmail.com`. No ESP yet, so there is
  no automated drip — but `thank-you.html` delivers every free file directly and
  makes the starter offer, so the funnel works. The `source` and `lead_magnet`
  fields are already captured on every form, so connecting MailerLite/Brevo later
  is a one-line `EMAIL_ENDPOINT` swap plus building the sequence in the ESP.
- **Catalog:** planners, journals, templates and the travel guide stay **mixed
  into the single catalog**. No separate filter or page. They are excluded from
  *brush* recommendations only because they carry no craft/goal tags in
  `data/discovery.json` — tag one and it becomes recommendable, no code change.
- **Analytics:** GA4 `G-5MFQFHNB6B` stays on, disclosed accurately in
  `privacy.html`, with `#dkp-analytics=off` and Do Not Track both honoured.

Full rationale and the review point for the catalog decision:
`docs/AUDIT-AND-PLAN.md` → "OWNER DECISIONS".

### Adding a product
`tools/payhip_sync.py` still owns `data/products.json` and is untouched. A new
product with no `discovery.json` entry gets safe defaults (tier from its
category, `line` inferred from its tags), still builds, still sells, and is
listed in the build log:

```
NOTICE: 1 product(s) are missing an entry in data/discovery.json …
```

Tag it properly when you see that notice so the Brush Finder can recommend it.

### Build determinism
The homepage used to rotate its "Trending" section by calendar day, so every
deploy rewrote the homepage and handed Google a different page on each crawl.
That is gone: two consecutive builds of all 108 generated files are now
**byte-identical**. The section is now "Popular Starting Points", ordered by
the editorial priority you set in `data/discovery.json` — and it no longer
claims to reflect search demand, because nothing on a static site measures that.
