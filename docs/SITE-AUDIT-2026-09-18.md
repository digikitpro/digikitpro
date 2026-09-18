# DigiKitPro Site Audit

**Site:** https://digikitpro.shop/  
**Date:** 2026-09-18  
**Scope:** repository QA, live-page inspection, SEO, accessibility, performance, security/privacy, UX and conversion.

## Executive summary

DigiKitPro is a strong, unusually complete static commerce site. Its information architecture, semantic HTML, product data, internal links, structured data, responsive images, honest merchandising and free-to-paid value ladder are substantially better than a typical small digital-product shop. The repository's automated verification suite passes all **82 checks**, including 100 sitemap URLs, zero broken internal links, one H1 per content page, valid product checkout links and complete guide/category coverage.

The largest remaining risks are not missing pages or broken functionality. They are:

1. **No explicit consent gate before GA4 loads** — a privacy/compliance risk for visitors in consent-required jurisdictions.
2. **No configured security headers** — CSP, HSTS, Referrer-Policy, Permissions-Policy and clickjacking protection are absent from the deploy configuration.
3. **A heavy global front end** — the homepage sends about 301 KB of uncompressed HTML/CSS/first-party JS before images and analytics, with six deferred local scripts plus GA4.
4. **Weak externally visible proof** — the site makes clear product claims but has no reviews, verified buyer quotes, customer work or demonstrated brush-stroke outcomes.
5. **Unconfirmed search visibility** — a web search for the domain/brand returned no results during this audit. This is not definitive indexing evidence, but warrants immediate Search Console verification.

**Overall assessment: 8/10 foundation; 6/10 trust and conversion evidence.**

## What is working well

### Technical and QA

- All 82 repository verification checks pass.
- 104 HTML files were scanned; no missing image `alt` attributes or duplicate IDs were found.
- Zero broken internal links according to the project verifier.
- Every content page has exactly one H1.
- The XML and text sitemaps contain 100 URLs on the production domain.
- Image sitemap contains 51 product URLs and 173 full-size product images.
- Product pages retain real Payhip checkout URLs.
- Static rendering and plain links provide a strong progressive-enhancement baseline.

### SEO

- Unique page metadata, canonical URLs, Open Graph and Twitter metadata are generated.
- Organization, WebSite/SearchAction, Product/Offer, Breadcrumb and article schema are present.
- Clean category, guide, blog and product landing pages create good topical depth.
- Descriptive page copy targets user intent rather than keyword stuffing.
- `robots.txt`, sitemaps, feed and verification files are present.
- Product and educational content have clear internal-link pathways.

### Accessibility

- Skip link and semantic landmarks are present.
- Search uses a labelled modal dialog and labelled controls.
- Mobile navigation exposes `aria-expanded` and `aria-controls`.
- Decorative imagery is appropriately hidden where applicable.
- Reduced-motion behavior is documented and implemented.
- Images include dimensions, reducing layout shift.

### UX and conversion

- The hero communicates product, audience, compatibility and delivery quickly.
- “What do you create?” is a better entry point than forcing users into a 51-item catalog.
- Free packs lower purchase anxiety and create a credible value ladder.
- Products are grouped by workflow and tier.
- Copy avoids fake scarcity, invented testimonials and unverifiable counters.
- Checkout remains on Payhip, reducing the site's PCI/security burden.

## Priority findings

### P0 — Load analytics only after consent where legally required

**Evidence:** GA4 is loaded near the top of every page before visitor interaction. The privacy page discloses this and offers opt-out mechanisms, but disclosure/opt-out is not equivalent to prior consent in jurisdictions where consent is required.

**Risk:** legal/privacy exposure and avoidable visitor distrust.

**Recommendation:**

- Implement a small consent manager that defaults analytics storage to denied.
- Load or activate GA4 only after an affirmative analytics choice where required.
- Store the preference locally and provide a persistent “Cookie settings” footer link.
- Keep the no-consent experience fully functional.
- Document retention, controller/contact details and third-country processing more explicitly.

### P0 — Verify indexing and organic-search health

**Evidence:** the audit's brand/domain web search returned no results. Search APIs can be incomplete, so this should be treated as a warning rather than proof of deindexing.

**Recommendation:**

- Inspect the homepage, top category pages and flagship PDP in Google Search Console URL Inspection.
- Confirm submitted/discovered/indexed counts for `sitemap.xml`.
- Check manual actions, security issues, canonical selection and crawl stats.
- Repeat in Bing Webmaster Tools.
- Track impressions and clicks by query/page weekly; do not infer SEO health from `site:` searches alone.

### P1 — Add deployment security headers

**Evidence:** `netlify.toml` configures cache headers only.

**Missing controls:**

- `Strict-Transport-Security`
- `Content-Security-Policy`
- `Referrer-Policy`
- `X-Content-Type-Options`
- `Permissions-Policy`
- frame protection via CSP `frame-ancestors`

**Recommendation:** add headers first in report-only/test mode because GA4, Payhip, FormSubmit and on-demand Google Translate require explicit CSP allowances. A reasonable target includes `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`, `upgrade-insecure-requests`, a strict referrer policy, MIME sniffing protection, and a minimal Permissions-Policy.

### P1 — Reduce global JS and CSS cost

**Evidence (raw/uncompressed):**

- `index.html`: 84.8 KB
- `css/style.css`: 101.8 KB
- first-party JS loaded on homepage: about 115 KB
- combined HTML/CSS/first-party JS: about 301 KB before images and GA4
- `search-index.js`: 38.2 KB and loaded globally
- six first-party scripts are loaded on the homepage

The primary hero image is a reasonable 175 KB WebP, and the two preloaded fonts total 63 KB. The concern is less one catastrophic asset than cumulative global work.

**Recommendation:**

1. Load the search index only when search opens or on the dedicated search page.
2. Load feedback only where the prompt can appear.
3. Load translation code only after the language control is activated.
4. Split page-specific CSS or remove unused selectors after coverage testing.
5. Minify generated HTML/CSS/JS in production while preserving source files.
6. Re-run Lighthouse on mobile after each change and monitor LCP, INP and CLS with field data.

### P1 — Add authentic proof and result-oriented media

**Evidence:** product cards and PDPs primarily demonstrate packaging/cover art. Automated checks intentionally confirm there are no fabricated reviews, but the current result is little third-party proof.

**Recommendation:**

- Add optional, data-driven slots for verified buyer quotes and customer artwork.
- Collect explicit publication permission and disclose whether products were gifted.
- Prioritize brush-stroke sheets, zoomed texture samples and finished-art examples.
- For major kits, show a concise “which brush made which result” panel.
- Never display empty stars, fake counts or generic unattributed praise.

### P2 — Simplify homepage choice density

The homepage has a sound sequence, but it is long and offers many category/product exits. Mobile visitors may understand the promise yet postpone selection.

**Recommendation:** keep one primary goal per section, reduce repeated card-level Pinterest actions on mobile, and test a shorter route:

1. workflow choice,
2. three free starters,
3. three best paid starting points,
4. flagship comparison,
5. proof,
6. education/email.

Use GA4 funnel events to validate rather than redesigning from preference.

### P2 — Improve cache strategy clarity

`/assets/*` receives a one-year immutable cache policy. This is safe only if changed asset URLs are fingerprinted or renamed. Product image filenames appear stable.

**Recommendation:** either fingerprint all immutable assets during generation or remove `immutable`/shorten max-age for stable product-image URLs. CSS is query-versioned; apply an equally reliable strategy to images and other replaceable media.

### P2 — Tighten structured-data language claims

The pages are authored in English and machine translation is activated client-side, while WebSite/Organization schema lists seven languages. Machine-translated UI availability is not the same as separately localized, indexable versions.

**Recommendation:** keep `inLanguage` as `en` until real localized URLs/pages exist. Do not add `hreflang` without distinct localized canonical pages.

### P3 — Repository/deployment efficiency

The deploy artifact is about 37 MB across 610 files, which is reasonable. However, generated HTML repeats a substantial common head/header/footer and many scripts. This is acceptable for static hosting but makes broad changes noisy.

**Recommendation:** retain generator ownership, add deterministic build checks in CI, and compare generated output after every source change. Do not hand-edit generated HTML.

## Suggested 30-day plan

### Week 1 — Risk and measurement

- Verify indexation and canonical selection in Google/Bing webmaster tools.
- Implement consent-aware analytics.
- Add tested security headers.
- Capture baseline mobile Lighthouse and Core Web Vitals data.

### Week 2 — Performance

- Lazy-load search index, translation and feedback code.
- Audit unused CSS and minify production output.
- Confirm hero LCP image sizing and responsive delivery on 360–430 px screens.

### Week 3 — Trust

- Publish stroke/output galleries for the top five revenue products.
- Add honest proof architecture and a permission-based customer-art submission flow.
- Clarify support response expectations and refund limitations at the decision point.

### Week 4 — Conversion experiments

- Measure homepage workflow click-through, PDP checkout clicks and Payhip purchase completion.
- Test one shorter homepage variant or one flagship comparison change at a time.
- Segment freebie → paid behavior without collecting unnecessary personal data.

## Acceptance criteria for the next audit

- Analytics does not transmit before the applicable consent state permits it.
- Security-header scan reports HSTS, CSP, Referrer-Policy, MIME protection and Permissions-Policy.
- Search Console confirms the homepage and priority commercial pages are indexed.
- Mobile Lighthouse is captured in a reproducible environment; no regression in accessibility/SEO.
- Search/translation/feedback code is not downloaded until needed.
- Top five PDPs include real result media; any testimonials have attribution and permission.
- All repository verification checks continue to pass.

## Audit limitations

- The live page was retrievable and inspectable, but the sandbox command-line TLS client could not complete a direct handshake, so live response headers and transfer compression could not be independently verified from `curl`.
- Chromium was not installed in the environment; therefore this pass does not claim measured Lighthouse scores, visual-regression results, keyboard-only browser testing or screen-reader output.
- No private analytics, Search Console, Payhip conversion or revenue data was available. Conversion recommendations are hypotheses to validate with real funnel data.
