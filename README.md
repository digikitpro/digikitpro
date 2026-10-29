# DigiKitPro - Website

A static ecommerce-content site for **DigiKitPro** (Procreate brushes and digital resources).
HTML is generated from local catalog and content files; Payhip handles the actual storefront.
The catalog was initially imported from Payhip on 2026-08-11 and requires ongoing reconciliation.

Current conversion audit, local changes, limitations and next steps: **`docs/CONVERSION-AUDIT-2026-10-28.md`**. Changes in a working branch are not automatically live.

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

**Before going live:** review the configured domain and social profiles in
`tools/core.py`. `SITE_URL=https://your-domain.com python3 tools/build.py` changes
canonical, Open Graph and sitemap URLs for a local build; the deployment workflows
currently set the domain to `https://digikitpro.shop` and must also be updated if the
owner approves a domain change. Pinterest and Instagram have configured defaults;
TikTok is hidden while empty. Review profile ownership and account settings separately.

Then submit `sitemap.xml` in Google Search Console & Bing Webmaster Tools.

## 2. Content control (no HTML editing needed)

| To change… | Edit | Then run |
|---|---|---|
| Products (name, price, images, descriptions, Payhip URL, categories…) | `data/products.json` | `python3 tools/build.py` |
| **Merchandising** (product hierarchy and related products) | `data/discovery.json` | `python3 tools/build.py` |
| Free-resource exercises and comparisons | `data/free-journeys.json` | `python3 tools/build.py` |
| Blog articles | `content/blog/*.md` (front-matter + markdown) | `python3 tools/build.py` |
| Design / colors | `css/style.css` (variables at top) | `python3 tools/build.py` to refresh stylesheet fingerprint |
| Behavior (search, filters, forms) | `js/main.js` | `python3 tools/build.py` to refresh script fingerprint |
| Product image gallery (tiles, arrows, swipe, lightbox) | `js/gallery.js` (+ its rules in `css/style.css`) | Rebuild if CSS changes |
| Motion (before/after slider and scroll indicator) | `js/motion.js` + the `MOTION SYSTEM` block in `css/style.css` | `python3 tools/build.py` to refresh fingerprints |

`data/products.json` is the single source of truth - 51 products, each with
`name, slug, price, category, short, descriptionHtml, included[], features[], technical[],
requirements[], images, tags[], related[], payhipUrl, seoTitle, seoDesc, featured, free`.
Delete an entry → its pages disappear on rebuild. Add one → page, card, sitemap and search
entry are created.

**Adding a new product image:** drop WebP/JPG/PNG into `assets/products/<slug>/` and point
`images.card` / `images.main` in `data/products.json` at it (regenerate variants with any
image tool; `scraped/images.py` shows the exact pipeline used originally).

### Product image gallery (`js/gallery.js` — self-contained, no libraries)

Every product page's gallery is one module and one markup contract. It is what
makes a thumbnail click change the big image, and it is deliberately strict about
*how*: the frame's `srcset`, `sizes`, `src`, `width`, `height` and `alt` are always
rewritten together. Writing `src` alone does nothing at all while a `srcset` is
present (a matching srcset candidate always wins over `src`), which is precisely
the bug that made the tiles look dead — and why a tile must carry its own
full-size file rather than let the frame keep image #1's candidates:

```html
<div class="pdp-media" data-product-gallery>
  <figure class="gal-main">
    <img id="product-main-image" data-gallery-main src="kit.webp"
         srcset="kit-card.webp 750w, kit.webp 1160w" sizes="(min-width: 960px) 46vw, 100vw"
         width="1160" height="774" alt="…" fetchpriority="high">
  </figure>
  <div class="gal-thumbs" role="group" aria-label="Product image previews">
    <a class="gal-thumb product-gallery-thumb active" href="kit.webp" data-gallery-thumb
       data-full-image="kit.webp" data-srcset="…" data-sizes="…" data-alt="…"
       data-w="1160" data-h="774" data-pin-media="https://…/kit.webp"
       aria-label="View product image 1: …" aria-current="true">
      <img src="kit-card.webp" width="750" height="500" alt="" loading="lazy">
    </a>
    …
  </div>
</div>
```

All of it is emitted by `gallery_html()` in `tools/pages_product.py` from
`data/products.json`, so there is no per-product list and no special case: a
product with one image gets a zoomable frame and no arrows, a product with nine
gets nine tiles, and `python3 tools/build.py` keeps every page in step. Without
JavaScript, each preview links to its full-size image; single-image products
provide a full-size link as well. The module also reads older `data-gal-main` /
`data-gal-thumb` / `data-full` hooks for cached pages.

What it adds, and what it never does:
* tiles, `←`/`→` over the artwork, `ArrowLeft`/`ArrowRight`/`Home`/`End` while focus
  is inside the gallery, wrap-around at both ends, and a swipe on touch;
* a modal viewer on the big image: dark scrim, close button, arrows, `Esc`,
  click-outside, arrow keys, and the page behind it cannot scroll;
* the active tile is marked with `.active`, `aria-current="true"` and an outline, and
  the counter (`2 / 4`) is a polite live region;
* full-size images are warmed on idle after `load` (skipped on `saveData`/2G), and a
  file that fails to load puts back the image that was on screen — never a broken
  frame, never a placeholder;
* an ordinary preview click updates the frame without navigating or scrolling the
  page; modified clicks retain normal browser link behaviour. Search, filters,
  navigation, Payhip and Pinterest links remain independent. Checks 90–93 in
  `tools/verify.py` cover the module, markup contract and gallery CSS.

The behaviour, not just the markup, is policed by `tools/qa_gallery.mjs`: it loads
the real built pages, runs the real scripts in `<script>` order through jsdom (no
browser download, works offline) and tests clicks, modified clicks, arrows,
keyboard, viewer, touch and swipe, failing images, 1-image products, the separate
look-inside slider, Payhip-synced absolute image URLs and stale caches.

```bash
python3 tools/build.py            # regenerate
python3 tools/verify.py           # static checks
node tools/qa_gallery.mjs         # gallery (needs: npm i --no-save jsdom)
python3 tools/qa_form.py          # offline default form-state check, sends nothing
python3 tools/qa_assets.py        # local HTML asset references
# For Chromium regression QA, see tools/qa_conversion.mjs and tools/qa_accessibility.mjs.
```

### Motion and imagery

`js/motion.js` provides the keyboard/touch-operable before/after control and a
scroll-progress indicator. The hero copy and product artwork are visible on
first paint; hero entrance/float, decorative parallax, autoplay and the
unsolicited sticky promotional bar are not enabled. The before/after pair
(`assets/img/ba-before.webp` and `ba-after.webp`) is illustrative: do not claim
it was made with a particular pack without verifying provenance.

## 3. Email capture — not configured

`EMAIL_ENDPOINT` in `tools/core.py` is empty. The site renders free-resource
links, not a signup form; it does not send welcome messages or run an email
sequence. Direct downloads continue to be handled by Payhip, which may request
an email for delivery. A free download or order email is not marketing consent.

Before activating a future signup provider, review jurisdiction-specific
requirements, implement and test explicit opt-in/confirmation, consent records,
unsubscribe/suppression, provider responses, delivery and privacy disclosures.
The optional form template includes a consent checkbox, but changing a URL alone
is **not** a complete or tested provider integration. Never put a secret in the
static site's HTML. The audit contains a proposed sequence; no campaign is live.

## 4. Structure

```
index.html  products.html  bundles.html  freebies.html  blog.html  about.html
faq.html  contact.html  refunds.html  search.html  privacy.html  terms.html  404.html
thank-you.html              ← optional free-resource practice and comparisons (noindex)
products/<slug>/index.html        × 51 product pages
blog/<slug>/index.html            × 18 articles
category/<slug>/index.html        × 10 category landing pages
season/<slug>/index.html          × 2 seasonal hubs
guides/index.html + guides/<slug>/index.html   ← 5 buyer guides (see §9)
partner/index.html                             ← partner portal (see §10)
assets/products/<slug>/*.webp     × 174 original product images (3 size variants)
assets/img/                       brand assets (favicon / OG cover)
css/style.css  js/main.js  js/gallery.js  js/search-index.js
data/products.json                ← master product data (edit me)
data/discovery.json               ← merchandising model (edit me; see §8)
data/free-journeys.json            ← four resource-specific optional comparisons
content/blog/*.md                 ← article source (edit me)
tools/build.py  tools/core.py …   ← generator (run: python3 tools/build.py)
js/analytics.js  js/feedback.js   ← conversion layer (rebuild when fingerprinted scripts change)
robots.txt  sitemap.xml
scraped/                          ← original scraper + Payhip source data (reference only)
```

## 5. SEO built in

Unique title/meta per page · canonicals · Open Graph + Twitter cards · Product + Offer JSON-LD
with real Payhip prices · Article schema · BreadcrumbList · Organization + WebSite (SearchAction) ·
FAQPage schema on product pages · `sitemap.xml` · `robots.txt` · semantic HTML5 ·
lazy-loading responsive WebP · descriptive alt text · clean URLs. Structured data
and meta tags do not guarantee a particular Google result, ranking or indexing.

After building, run `python3 tools/qa_seo.py` to check generated canonicals,
indexability, HTTPS internal links, canonical homepage navigation, sitemaps,
JSON-LD, article dates and local Open Graph image sizes. The deploy and
catalog-sync workflows run this offline check before publishing; use Search
Console separately to inspect Google's selected canonicals and indexing.
For article authors, the optional `seo_title` frontmatter is an **unbranded**
human-written search title; the generator appends ` | DigiKitPro`. Set `modified`
only when the visible article has actually changed, not merely on every build.

Product pages put the offer before the gallery in source order. On phones a
small cover link leads to the full gallery; on desktop the gallery remains on
the left. The mobile navigation falls back to a native, collapsible menu without
JavaScript. GitHub Pages serves `404.html` at the missing URL: root-relative
assets and navigation work at nested paths, while the skip link stays on the
error page. Missing pages are not redirected to the homepage. The canvas
calculator's layer numbers are illustrative assumptions, not measured Procreate
limits.

## 6. Where the data came from

Product names, prices, file sizes, full descriptions, galleries and the Payhip URLs were taken
from the live store `payhip.com/digikitpro` on 2026-08-11 (see `scraped/catalog.json`).
Nothing is invented. If a product is added/removed in the store later, update
`data/products.json` to match. Social profile URLs are intentionally blank until configured.

## 7. Auto-sync from Payhip, translation & trending (v2)

- **Payhip → site:** `tools/payhip_sync.py` can detect and add new products. Existing
  product facts are updated only for records marked `auto: true`; the current 51
  manually maintained records need owner reconciliation with Payhip. Review the
  workflow and the generated diff before publishing any catalog changes.
- **International:** the header includes a 7-language Google Translate switcher and the homepage has
  a worldwide trust band. `tools/core.py` has `LANGUAGES` and `GEO_META` if you want to change them.
- **Discovery:** product cards and suggestions use catalog data and editorial
  priorities; they do not measure or claim actual search or sales popularity.
- **IndexNow:** on by default — the workflows carry a default key (public by design); the build
  writes `<key>.txt` and the deploy/sync workflows ping Bing, Yandex and Seznam. Set the repo
  variable `INDEXNOW_KEY` only to rotate it.

See `SEO-INDEXING.md` for Google Search Console + Bing Webmaster + IndexNow setup and a content
cadence that keeps the site visible on search results.


## 8. Sales engine (Phase 1) — how the new parts work

Current conversion findings and plan: **`docs/CONVERSION-AUDIT-2026-10-28.md`**.
The previous Phase-1 document `docs/AUDIT-AND-PLAN.md` is historical.

> **Historical note (2026-09-18; superseded where contradicted by the current audit):** two Phase-1 features were later RETIRED at the
> owner's request: the **Brush Finder** (`find-my-brushes.html`, `js/finder.js`,
> `js/finder-index.js`, `tools/pages_finder.py` — removed in full on 2026-09-18,
> no traces left anywhere in the build) and the visible **store email address**
> (contact now runs through the Payhip store form). The "Brush Finder" section
> below is kept for the design rationale only. The next three sections describe
> historical design, not the current page order, signup flow or deployment.

### Historical value ladder
Every product now carries a **tier** in `data/discovery.json`, and the homepage,
catalog and Brush Finder all read it:

| Level | Tier | What it is | Where it appears |
|---|---|---|---|
| 1 | `free` | Free Procreate packs | Homepage "Try Before You Buy" row, `/freebies.html` (email-first), `/thank-you.html` |
| 2 | `entry` | $4–$10 specialist packs (skin, hair, line art…) | Homepage best-seller four + portrait journey, catalog, PDPs |
| 3 | `bundle` | $8–$20 multi-kit bundles | Homepage **bundle ladder** + portrait journey, `/bundles.html` |
| 4 | `flagship` | **Master Library, 2,000+ brushes, $19** | Homepage ladder (top rung) + dedicated feature band + upgrade panel on 37 product pages |
| 5 | `education` | Free starter guide + $19 Portrait Masterclass | Homepage free row + journey (first/last step), PDPs |

### Historical homepage information architecture — 2026-09-18

The order below is the merchandising decision — each section answers the one before it
(see → believe → find → try → start → go deeper → trust → learn → stay connected):

```
HEADER → HERO (one finished portrait artwork; Shop All Brushes / Try Free Brushes; trust row)
→ BEFORE → AFTER (visual proof, directly under the hero)
→ START WITH WHAT YOU ACTUALLY NEED (four best sellers: skin / mastery / line art / watercolor)
→ WHAT DO YOU CREATE? (shop-by-workflow route cards, one artwork each)
→ TRY DIGIKITPRO BEFORE YOU BUY (Starter Guide + three $0 kits, direct Payhip)
→ FROM FIRST PORTRAIT TO FINISHED PORTRAIT ($0 → $5 → $8 → $15 → $19 journey)
→ WANT MORE THAN ONE KIT? (Starter → Advanced → Ultimate → Master Library ladder)
→ ONE LIBRARY. MULTIPLE WORKFLOWS. (Master Library feature)
→ TOOLS THAT RESPECT YOUR CRAFT (four factual claims) → MADE FOR REAL ARTWORK
(honest empty slots — no fabricated proof) → LEARN PROCREATE. CREATE BETTER. (3 guides)
→ GET THE FREE STARTER PACK (email) → FOOTER
```

Section order is generated from `build_home()` in `tools/pages_main.py` and is checked
after every build by `tools/verify.py` (`homepage section order matches the
result-first brief` + `homepage closes: proof → articles → email CTA` +
`hero CTAs are Shop All Brushes + Try Free Brushes`). The same suite also
guards the Brush Finder removal (page, scripts and references all gone).
The bundle row is a **ladder**, not a tile grid: its rungs live in
`data/discovery.json → bundleLadder.rungs` (`Starter → Advanced → Ultimate →
Master Library`), while every number on a rung (price, asset count, kit list)
is read from `data/products.json`, so a Payhip sync updates it.
The homepage community-art strip is an **honest placeholder** — see "Social proof" below.

### Brush Finder — RETIRED 2026-09-18 (kept for the design rationale)
**Everything is gone**: the page, `js/finder.js`, `js/finder-index.js`, the nav
entry, the homepage links and the `tools/pages_finder.py` generator module.
The post-signup `thank-you.html` it once co-built now lives in
`tools/pages_main.py`. What follows is the design record.

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

`dkp.track(name, params)` forwards custom events to GA4 when enabled and keeps
browser-local event counts (`dkp.report()` / `dkp.clear()`). Events include
`product_view`, `free_download_click`, `product_buy_click`,
`outbound_payhip_click`, `free_next_step_click`, `free_next_step_view`,
`premium_product_click`, `kit_comparison_click` and `email_signup_request`.
Clicks and signup **requests** are not confirmed downloads, purchases or
subscriptions. The local summary is not an aggregate dashboard.

The production Google tag is not loaded on preview or localhost hosts. The tag
and local counting are disabled by `#dkp-analytics=off`, Do Not Track,
Global Privacy Control, or a build with `DKP_ANALYTICS=false` (set that GitHub
repository variable to `false` for both deployment workflows). The tag can set
cookies. DNT/GPC and opt-out are not a substitute for a jurisdiction-appropriate
consent assessment. The site's event payloads exclude query strings and search
text. The GA page URL is query-free; limited non-personal UTM campaign labels
are forwarded as separate config fields. Use no personal information in UTM
values, and verify attribution and cross-domain tracking in GA/Payhip before
relying on them. Ads click-ID attribution has not been validated.

### Pinterest — `tools/core.py` (Pinterest block)

The profile **https://www.pinterest.com/DigiKitProStudio/** is wired into every page the
build produces, so pins saved from the site always carry the right artwork, description
and destination:

| Piece | Where it comes from | What it does |
|---|---|---|
| Profile URL | `PINTEREST_PROFILE` in `tools/core.py` (override: `PINTEREST_URL`) | Footer follow link + CTA band, Organization schema `sameAs`, `og:see_also` |
| Domain claim | `PINTEREST_VERIFY` (default `990d08b5349bfcbb0171eab3d6f8f2d2`) | `<meta name="p:domain_verify" …>` on every page — claim the website once in Pinterest settings and every pin of a digikitpro.shop URL credits the account |
| Save button | `pin_button()` in `tools/core.py` | Red "📌 Save" control on every product image — product cards/listing pages, homepage ladder, best-seller band, bundle panels, eBook covers, freebie cards, product-page gallery, upgrade panel. Links open Pinterest's pin composer pre-filled |
| Pin data | `pin_attrs()` | `data-pin-description` / `data-pin-url` / `data-pin-media` on each image, so Pinterest's own save button and browser extension pin the product page, not a bare image |
| Rich Pins | `head()` when `ctx.type == "product"` and paid | `og:type=product` + `product:price:amount`, `product:price:currency=USD`, `product:availability=instock`, `product:brand` — prices come from `data/products.json`, never estimated. Validate once at pinterest.com/rich-pins |
| Share row | `share_buttons()` | Pinterest Pin + Facebook + X + WhatsApp on every product page ("Save this artwork to Pinterest") and every article ("Share this guide") |
| Pinterest Tag | `PINTEREST_TAG_ID` (repo variable / env, **off by default**) | Loads `pintrk` `load` + `page` + the `<noscript>` pixel only when an ID is set. No ID = no Pinterest request beyond the save button script |

Editorial plan and the 30-day posting calendar: **`docs/PINTEREST-30-DAY-PLAN.md`**.

### Google Merchant Center — `google-merchant-feed.xml`

`tools/build.py` generates a dedicated scheduled-fetch feed at
`https://digikitpro.shop/google-merchant-feed.xml`; it is not the Pinterest feed
and does not connect to or modify a Merchant Center account. The initial source
includes available non-book products (including free downloads), links to
DigiKitPro product pages, and excludes the two eBooks pending a separate policy
review. Setup steps, shipping/market prerequisites, and the catalog's identifier
caveat are in **`docs/GOOGLE-MERCHANT.md`**.

### Free-resource journeys

`freebies.html` and the free product pages keep their direct Payhip links.
Each of the four resources has a relevant, optional exercise and comparison
configured in `data/free-journeys.json`. The visible "After downloading" link
opens `thank-you.html?lead=<slug>` if the visitor chooses it; this page is not
an automatic Payhip redirect and does not prove a download or signup. An unknown
slug or JavaScript-disabled browser sees all four suggestions. No email sequence
is running.

### Feedback prompt

`js/feedback.js` is not included in generated pages while
`DKP_FEEDBACK_ENDPOINT` is empty. A future collector needs a separate review of
consent, security, accessibility and provider delivery before enabling it.

### Historical catalog and analytics notes

Planners, journals, templates and the travel guide remain in the catalog.
The GA measurement ID remains configured; verify consent, account settings and
cross-domain measurement before drawing conclusions from reports. Older
strategy documents are historical and can describe retired functionality.

### Social proof — the "Made for Real Artwork" placeholder
The homepage carries a **Made for Real Artwork** strip between "Why DigiKitPro" and
the guides: three clearly-marked empty slots (`.proof-slot quote-slot`) that invite
artists to share finished pieces. It deliberately contains **no quotes, no names,
no artwork and no counts** — an honest frame is a better trust signal than fake
proof, and `tools/verify.py` fails the build if fabricated testimonial copy,
star ratings or review counts appear anywhere in generated HTML (the empty
`.quote-slot` figures are its documented placeholder shape and are excluded
from that scan as placeholders, never as proof).

When a real artist shares real work (tagged post, direct message, email — with
permission), replace one slot in `build_home()` in `tools/pages_main.py` with the
piece as plain attributed text: the artwork, their own handle, what they used.
Do **not** add an aggregate star rating unless the rating is hosted and
verifiable by Google, and expect `python3 tools/verify.py` to fail any check that
looks manufactured — that is the guard doing its job, not a bug to switch off.

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
That is gone: two consecutive builds on the same date and with the same inputs are
**byte-identical** (some generated RSS/audit metadata can change with the date). The section is now "Popular Starting Points", ordered by
the editorial priority you set in `data/discovery.json` — and it no longer
claims to reflect search demand, because nothing on a static site measures that.

## 9. Buyer guides — `/guides/` (Phase 3, commercial-intent SEO)

Five landing pages that answer **shopping** queries the technique articles
don't cover — built by `tools/pages_guides.py` from explicit, tag-derived
product selections:

| Page | URL | It answers |
|---|---|---|
| Starter Kits | `guides/procreate-starter-kits/` | "what should a beginner buy first?" — free packs → one $5 kit → library |
| Pencil Brushes | `guides/procreate-pencil-brushes/` | "procreate pencil brushes" — graphite/charcoal kits, pose stamps, ink liners |
| Texture Brushes | `guides/procreate-texture-brushes/` | "procreate texture brushes" — skin/fur, paper grain, painterly, atmosphere |
| Animation Brushes | `guides/procreate-animation-brushes/` | "procreate dreams brushes" — liners, palettes, FX + the honest Dreams notice |
| Bundles Compared | `guides/procreate-bundles-compared/` | "which procreate bundle?" — all 6 real brush bundles side by side, live data |

Plus `guides/index.html` as the hub. Contract (enforced by `tools/verify.py`,
checks 63–70):

- **Selections are explicit slug lists** in `GUIDE_DEFS`, chosen from the
  `data/discovery.json` tags. The build **fails loudly** on a stale slug, so a
  Payhip sync can never leave a silent hole on a money page.
- **No aggregates in the grids** — whole-catalog libraries match everything, so
  they would tell the shopper nothing; the Master Library appears once per
  page in its clearly-labelled flagship band.
- **No lifestyle products** (planners, travel, Canva templates) — buyer guides
  are a brush context (owner decision: they stay in the general catalog).
- **Nothing invented** — prices, asset counts and bundle rows are read from
  `data/products.json` at build time; no "was" strikethroughs, no countdowns,
  no fake urgency (also guarded by the honesty checks).
- Every guide carries BreadcrumbList + ItemList + FAQPage JSON-LD, cross-links
  its sibling guides, the matching `/category/` pages and the technique
  articles, and is in the sitemap, the search index and the footer.

To edit a guide: change `GUIDE_DEFS` in `tools/pages_guides.py` (copy,
groups, FAQs, cross-links) and run `python3 tools/build.py`.
`GUIDES_FOR_CATEGORY` in the same file controls which buyer guides each
category landing page cross-links.

## 10. Partner portal — `/partner/` (affiliate program front door)

One generated page (`partner/index.html`, built by `tools/pages_partner.py`)
that does the public half of the partner program. The private half — tracked
links, click/sale reporting, payout — stays in **Payhip's own affiliate
system**, because Payhip already takes every payment and delivers every file
for this store. So the page has **no login, no accounts and no commission
ledger**, and it never renders numbers it cannot keep true.

What it contains:

| Block | What it does |
|---|---|
| Program status + CTA | Invite-only vs. open, driven by one variable (below) |
| Four steps | Apply → get tracked links → share → get paid by Payhip |
| Share kit | 3 free packs + 5 paid kits: real cover art, real one-line copy, live price, product URL, Payhip checkout URL and absolute artwork URL, all read from `data/products.json` at build time |
| Promotion rules | Do / do-not list. Extends the site's own fabrication rules to partners: no invented reviews, ratings, sales totals, earnings promises or fake scarcity |
| Partner FAQ | 10 questions, also emitted as `FAQPage` JSON-LD (+ `BreadcrumbList`) |

**The one knob — `PARTNER_SIGNUP_URL`.** Payhip → Dashboard → **Marketing →
Affiliates** hands out a single sign-up link. Set it as a repository variable
(**Settings → Secrets and variables → Actions → Variables → New variable**,
name `PARTNER_SIGNUP_URL`) and both workflows pass it to the build: the
primary CTA becomes the real application form. Left empty, the page says the
program is invite-only and routes applicants to the Payhip store contact form.
`EMAIL_ENDPOINT` is unset, and actual message routing has not been verified. It never renders a dead button.

Contract (enforced by `tools/verify.py`, checks 71–80):

- Share-kit slugs are **explicit lists** (`PARTNER_FREE_SLUGS` /
  `PARTNER_PAID_SLUGS`) and the build **fails loudly** on a stale slug — a
  Payhip rename can never leave a hole in a page partners copy links from.
- Prices, Payhip URLs and cover images come from `data/products.json`, so the
  daily sync keeps the kit truthful with no edit here.
- No commission rate or earnings figure may appear (a rate is agreed per
  partner and paid by Payhip, so any number printed here could only be wrong).
- The page is linked from the **footer of every generated page**, is in
  `sitemap.xml` + `sitemap.txt` (priority 0.4 — it is for creators who already
  know the store, and must never outrank a product or a buyer guide), and is
  deliberately **not** in the site search index: a shopper searching "brushes"
  should not get an affiliate page.

To edit the copy: `tools/pages_partner.py` holds the steps, rules, FAQs and
the "who this kit is for" angles; `PARTNER_*_SLUGS` holds the kit. Then
`python3 tools/build.py`. Styles are the `pt-*` block at the end of
`css/style.css`.
