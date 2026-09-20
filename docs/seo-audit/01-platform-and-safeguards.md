# DigiKitPro SEO Engine — Phase 1 Baseline Audit
## 01. Platform, Theme, SEO, Analytics, Pinterest, Deployment

**Date:** 2026-09-19 (UTC)  
**Branch:** arena/01a0bbfa-digikitpro  
**Site:** https://digikitpro.shop/  
**Repo:** digikitpro/digikitpro (GitHub Pages)

---

### 1.1 Platform

- **Type:** 100% static HTML/CSS/JS, no backend, no database, no build dependencies beyond Python 3 stdlib.
- **Generator:** Custom Python generator in `tools/`:
  - `tools/core.py` — config, SITE_URL, head(), header(), footer(), schema builders, image helpers, canonical/OG/Twitter generation, Pinterest Rich Pins, GA injection, GitHub Pages duplicate-variant JS guard (`_GITHUB_KILL`).
  - `tools/build.py` — orchestrator calling:
    - `pages_main.py` (homepage, products index, bundles, freebies, thank-you)
    - `pages_product.py` (51 product pages)
    - `pages_blog.py` (blog index + article pages from `content/blog/*.md`)
    - `pages_category.py` (10 category hubs)
    - `pages_season.py` (2 seasonal hubs: halloween, christmas)
    - `pages_guides.py` (6 guide pages: index + 5 buyer guides)
    - `pages_partner.py` (partner portal)
    - `pages_misc.py` (static pages: about, faq, contact, refunds, privacy, terms, search, 404, sitemaps, feed.xml, search-index.js, pinterest feeds)
  - `tools/seo_engine.py` — deterministic offline SEO copy generator for `data/products.json` (seoTitle, seoDesc, short, alt, tags, keywords). Never overwrites hand-written copy unless `auto:true`.
  - `tools/payhip_sync.py` — daily auto-sync from Payhip public store, adds new products to `data/products.json`, calls seo_engine, never overwrites curated fields.
  - `tools/verify.py` — post-build verification suite (currently 88 checks expected, 87 passing due to 2 broken internal links in orphaned draft).
  - `tools/submit_index.py` — IndexNow submission, SHA-256, state in `data/indexnow-state.json`.
- **Hosting:** GitHub Pages, custom domain `digikitpro.shop` (CNAME file), plus `netlify.toml` redirects as documentation and Netlify fallback.
- **Domain handling:** JS guard in every page head handles 4 duplicate cases before any render:
  1. `*.github.io` mirror → `https://digikitpro.shop/...` + noindex
  2. `http://` on shop domain → `https://`
  3. `www.digikitpro.shop` → apex
  4. `/index.html` suffix → clean directory URL
  Server-level 301 for http/www depends on GitHub Pages **Enforce HTTPS** setting — see issue register.
- **No framework:** No Jekyll, Next.js, WordPress, Shopify. All links relative, works from subpath but deployed at apex.

### 1.2 Theme / Design System

- **CSS:** Single file `css/style.css` with variables at top, motion system block at end.
- **Fonts:** Self-hosted WOFF2: `manrope-normal.woff2`, `playfairdisplay-normal.woff2`, `playfairdisplay-italic.woff2`, preloaded.
- **JS:** 
  - `js/main.js` — search, filters, gallery, newsletter AJAX
  - `js/motion.js` — 19KB raw / 5.6KB gzipped, scroll reveals, parallax, before/after slider, sticky CTA, prefers-reduced-motion support
  - `js/analytics.js` — conversion event layer, reads `window.DKP.page` context, forwards to GA4 if enabled
  - `js/feedback.js` — "What stopped you?" prompt, dormant unless FEEDBACK_ENDPOINT set
  - `js/translate.js` — Google Translate switcher (7 languages)
  - `js/search-index.js` — generated, 37KB, product + article index for client search
- **Images:** WebP primary, card/thumb variants (750w, 1400w), srcset + sizes, width/height attributes to prevent CLS.
- **Layout:** Responsive, mobile-first, no heavy dependencies.

### 1.3 SEO Plugins / Apps

- **None** — no external SEO plugin. All SEO built into generator:
  - Unique title/meta per page
  - Canonical self-referential
  - Open Graph + Twitter cards
  - Product + Offer + BreadcrumbList + Organization + WebSite (SearchAction) + Article (BlogPosting) + FAQPage + HowTo + ItemList JSON-LD
  - sitemap.xml (99 URLs), sitemap.txt, sitemap-images.xml (51 pages, 173 images), robots.txt, feed.xml RSS
  - seo_engine.py deterministic fallbacks

### 1.4 Analytics / Search Console / Verification

- **Google Analytics 4:** `G-5MFQFHNB6B` injected via gtag.js in every head if `GA_MEASUREMENT_ID` set (env or default).
- **Google Search Console verification:** `<meta name="google-site-verification" content="1e87093669a800cb">`
- **Bing:** `msvalidate.01` = `52B8ABC07828BE6CE77B297D3F2E50A3`
- **Yandex:** `48977a1d04865b21`
- **BingSiteAuth.xml** present (86 bytes)
- **google1e87093669a800cb.html** verification file present
- **yandex_48977a1d04865b21.html** present
- **Analytics layer:** `window.DKP` object with store URL, email endpoint, analytics enabled flag, page context (type, slug, name, tier, category, price) — no PII.
- **Conversion tracking:** `data-dkp-*` attributes on buy buttons, cards, etc., used by analytics.js.

### 1.5 Pinterest Catalog / Feed Implementation

- **Profile:** `https://www.pinterest.com/DigiKitProStudio/` + Instagram `https://www.instagram.com/digikitprostudio/`
- **Domain verification:** `<meta name="p:domain_verify" content="990d08b5349bfcbb0171eab3d6f8f2d2"/>`
- **Rich Pins:** Product pages that are paid carry `product:price:amount`, `product:price:currency`, `product:availability`, `product:brand` meta. `og:see_also` points to Pinterest, `pinterest-rich-pin=true`.
- **Save buttons:** `.pin-btn` links to `https://www.pinterest.com/pin/create/button/?url=...&media=...&description=...` — no pinit.js widget (avoids DOM scanning overlay).
- **Image pin attributes:** `data-pin-description`, `data-pin-url`, `data-pin-media` on gallery images.
- **Catalog feeds:**
  - `pinterest-feed.xml` (43KB, 47 paid products) — RSS with `g:` namespace, fields: id, title, description, link, image_link, availability, price, brand, condition, google_product_category, product_type, item_group_id.
  - `pinterest-feed.csv` (24KB, same 47 products) — CSV variant.
  - Generated by `pages_misc.py` from `data/products.json` where `free==false`, uses live price, canonical URL, main image absolute URL.
  - Destination URLs are canonical `https://digikitpro.shop/products/<slug>/` — intact.
- **Pinterest Tag:** Dormant unless `PINTEREST_TAG_ID` env set — no Pinterest requests made by default.
- **Safeguard:** Pinterest catalog must not be disrupted — feeds must continue to validate after any SEO changes.

### 1.6 Deployment Process

- **Primary:** `.github/workflows/deploy.yml`
  - Triggers on push to main, manual dispatch
  - Sets `SITE_URL: https://digikitpro.shop`
  - Runs `python3 tools/build.py`
  - Deploys via `actions/deploy-pages`
  - Then pings IndexNow if `INDEXNOW_KEY` set (continue-on-error, after deploy)
  - Permissions `contents: write`, `pages: write`, `id-token: write`
- **Secondary:** `.github/workflows/sync-payhip.yml`
  - Daily cron + manual
  - Runs `payhip_sync.py` + `build.py`, commits new products if found
  - Also pings IndexNow after build
  - Passes `PARTNER_SIGNUP_URL`, `SITE_URL`, `INDEXNOW_KEY` env
- **Rollback:** Git revert or re-deploy previous commit via GitHub Pages — all generated files are in repo root, no build artifacts elsewhere.
- **Local build:** `python3 tools/build.py` + `python3 tools/verify.py` — no npm, no bundler.
- **Netlify:** `netlify.toml` contains 301 redirects for http→https, www→apex, /*/index.html→/*/ — harmless on GitHub Pages, active if ever connected to Netlify.

### 1.7 Current Data Inventory

- **Products:** 51 in `data/products.json`, each with `name, slug, price, category, short, descriptionHtml, included[], features[], technical[], requirements[], images, tags[], related[], payhipUrl, seoTitle, seoDesc, featured, free, alt, keywords, spotPitch`. Single source of truth.
- **Discovery / Merchandising:** `data/discovery.json` — tier (free/entry/bundle/flagship/education), line (procreate/assets/lifestyle), craft, improve, level, style, stage, priority, aggregate flag. Separate from products.json so sync never clobbers merchandising.
- **Blog:** 18 markdown files in `content/blog/*.md` with frontmatter: title, slug, description, date, modified, category, howto, totaltime, primary_keyword, secondary_keywords, search_intent, target_audience, tags, products[], related[]. Plus 4 orphaned HTML dirs without md source (see issue register).
- **Categories:** 10 — portrait, skin-texture, line-art, watercolor, anime, hair, glitter-effects, traditional, figure-drawing, sketching (from CATEGORY_SLUGS).
- **Guides:** 5 buyer guides + index = 6 pages, defined in `pages_guides.py` with hardcoded slugs: procreate-starter-kits, procreate-pencil-brushes, procreate-texture-brushes, procreate-animation-brushes, procreate-bundles-compared.
- **Season:** 2 — halloween, christmas.
- **Static:** about, faq, contact, refunds, privacy, terms, search, 404, thank-you, products.html, freebies.html, bundles.html, blog.html, guides/index, partner/index, index.html.

### 1.8 Non-Negotiable Safeguards Checklist

- [x] Preserve all existing product URLs: `/products/<slug>/` — generator uses slug from products.json, never changes for SEO.
- [x] Preserve article URLs: `/blog/<slug>/` — from markdown slug.
- [x] Preserve category URLs: `/category/<slug>/`
- [x] Preserve redirects: JS guard + Netlify redirects must remain.
- [x] Preserve canonical behavior: self-canonical, no param canonicalization beyond search.
- [x] Preserve analytics/tracking: GA ID, DKP context, data-dkp attributes must remain.
- [x] Preserve structured-commerce data: Product/Offer JSON-LD uses real price, availability from products.json.
- [x] Preserve Pinterest catalog: feed generation must remain, fields intact, destination URLs unchanged.
- [x] Do not remove valid metadata without documenting reason.
- [x] Do not invent product features, reviews, ratings, prices, availability — all from products.json/Payhip.
- [x] Do not keyword-stuff, copy competitors, create doorway pages, hide SEO text, mass-publish thin content.
- [x] Do not change production code until audit approved — this phase is audit only.
- [x] Use reversible changes and maintain change log — future changes to be logged in `docs/seo-audit/`.

### 1.9 Access Limitations

- No live Search Console, GA4 dashboard, or server log access in this sandbox — only site-side implementation visible.
- No ability to verify GitHub Pages Enforce HTTPS toggle live — must be checked via GitHub API or manual owner step (see SEO-CANONICAL-FIX-2026-09-19.md).
- No Core Web Vitals field data — only lab indicators from static analysis.
- No Pinterest catalog validation beyond file syntax.

---

**Next:** URL and template inventory in 02.
