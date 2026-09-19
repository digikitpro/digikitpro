# DigiKitPro — Prioritized Issue Register (Baseline Audit 2026-09-19)

**Severity scale:** Critical (blocks indexing/revenue), High (significant SEO/UX risk), Medium (should fix soon), Low (polish), Info (observation).

**Effort:** XS (<1h), S (1-3h), M (half day), L (1-2 days), XL (week).

**Risk:** Low (reversible template fix), Medium (needs review), High (conversion/feed impact).

---

## Critical

### C-01 — 4 orphaned blog HTML dirs not in sitemap, with broken internal links
- **Severity:** Critical (broken links fail verify, cause crawl waste, confuse topical authority)
- **Affected URLs:**
  - `/blog/how-to-shade-face-procreate/` (on disk, not in sitemap.xml, not in sitemap.txt)
  - `/blog/procreate-layers-alpha-lock-clipping-mask/`
  - `/blog/procreate-line-art-tutorial/`
  - `/blog/procreate-mistakes-beginners/` (contains 2 broken links)
- **Evidence:**
  - `content/blog/*.md` has 18 files, but `blog/` has 22 dirs. `md_slugs` vs `html_slugs` diff = 4 extra.
  - `sitemap.xml` has 18 blog locs, not including these 4.
  - `tools/verify.py` FAIL: `0 broken internal links — 2; blog/procreate-mistakes-beginners/index.html -> ../procreate-shortcuts-gestures/; -> ../procreate-30-day-practice-plan/`
  - Those target slugs do not exist in `content/blog/` nor as HTML dirs.
- **Recommended fix:**
  - Option A (safe, recommended): Remove the 4 orphaned dirs from repo and from deployed site, OR convert them to proper md source files in `content/blog/` with frontmatter, internal links corrected, then rebuild so they are included in sitemap.xml and feed.xml.
  - Option B: If they are intended drafts from SEO-CONTENT-ROADMAP, move their content to `content/blog/*.md` with valid frontmatter (title, slug, description, date, primary_keyword, products, related), fix broken links to existing articles, then rebuild.
  - Do NOT leave indexable HTML files on disk that are not in sitemap and have broken links.
- **Effort:** S
- **Risk:** Low if removed, Medium if published (needs content quality review).
- **Safeguard:** Preserve existing 18 article URLs exactly; do not change their slugs.

### C-02 — GitHub Pages Enforce HTTPS toggle unverified
- **Severity:** Critical (causes http vs https duplicate, Search Console "Alternate page with proper canonical tag")
- **Affected URLs:** All URLs — `http://digikitpro.shop/*` serves 200 with same HTML as https if toggle off.
- **Evidence:** `SEO-CANONICAL-FIX-2026-09-19.md` documents previous check via GitHub API: `https_enforced: false` (403 when trying to set via API). Current repo still has JS guard for http→https, but server-level 301 is required.
- **Recommended fix:** Owner manual step: GitHub repo Settings → Pages → Enforce HTTPS → tick, wait for certificate active, verify `curl -I http://digikitpro.shop/` returns 301 to https. No code change needed beyond existing JS guard + Netlify redirects.
- **Effort:** XS (owner, 30 sec)
- **Risk:** Low — improves canonical consolidation.
- **Blocked:** Requires GitHub Pages admin access.

---

## High

### H-01 — Missing meta/OG image dimensions for some blog articles using fallback
- **Severity:** High (OG image validation, social sharing)
- **Affected URLs:** Blog articles where `products[]` empty or product missing — currently none, but fallback is `assets/img/og-cover.jpg` (1200x630) which is correct. However 4 orphaned drafts use product card images as OG (e.g., free-fine-liner) with width/height hardcoded as 1200x630 but actual image is 750x... May cause OG image mismatch.
- **Evidence:** In `blog/procreate-mistakes-beginners/index.html`, og:image = `https://digikitpro.shop/assets/products/free-fine-liner-brushes-100/free-fine-liner-brushes-100-card.webp` with width 1200 height 630 declared, but actual file is 750w. OG validator would flag dimension mismatch.
- **Fix:** Ensure og:image width/height reflect actual file dimensions from `images.cardW/cardH` or use main image (1400w). Update `pages_blog.py` to use actual dimensions.
- **Effort:** S
- **Risk:** Low.

### H-02 — No unique H2/H3 hierarchy validation for some product descriptions
- **Severity:** High (accessibility + SEO)
- **Affected URLs:** Product pages — `descriptionHtml` contains <h3> tags that are demoted from h2→h3 via `_demote_headings()`, but some descriptions have multiple <h3> without logical order, and some have empty <h3><br/></h3> (e.g., portrait-skin-brushes-procreate sample had `<h3><br/></h3>`).
- **Evidence:** Sample product descriptionHtml starts with `<blockquote>...` then `<h3><br/></h3><h3><strong>See the Difference</strong></h3><p><br/></p>` — empty heading + <br/> filler.
- **Fix:** Clean descriptionHtml in `data/products.json` or improve `_demote_headings()` to strip empty headings and <br/> inside headings. Add validation in seo_engine or verify.py.
- **Effort:** M
- **Risk:** Low.

### H-03 — Thin or duplicated content risk between similar blog posts
- **Severity:** High (cannibalization)
- **Affected URLs:**
  - `/blog/how-to-create-realistic-skin-in-procreate/` vs `/blog/how-to-create-realistic-skin-texture-in-procreate/` — overlapping intent (skin)
  - `/blog/best-procreate-brushes-for-line-art/` vs future `/blog/procreate-line-art-tutorial/` (orphaned)
- **Evidence:** Both skin articles target "realistic skin" — one is workflow, one is texture. Need to ensure distinct primary keywords, internal linking, and canonical differentiation. Currently both have unique titles/descriptions but share secondary keywords.
- **Fix:** Document content gap analysis, ensure each article has distinct search intent and target audience (as per brief section 8). Add cross-links and distinct H1. For future articles, check existing coverage before publishing (as required).
- **Effort:** M
- **Risk:** Medium (content strategy).

### H-04 — Search index includes orphaned drafts? Verify search-index.js
- **Severity:** High (search UX, broken links in search)
- **Affected URLs:** `/js/search-index.js` — generated from `load_articles()` which reads md only, so orphaned HTML not in search index — good. But if orphaned drafts are accessed directly, they have search overlay that will not find them? Actually search overlay uses search-index.js, so orphaned pages would not appear in search results — inconsistent.
- **Fix:** Ensure search-index.js only includes sitemap-listed URLs. Currently it does (md only). Keep it.
- **Effort:** XS
- **Risk:** Low.

---

## Medium

### M-01 — Alt text could be more descriptive for gallery thumbnails
- **Severity:** Medium (image SEO, accessibility)
- **Affected URLs:** Product pages — gallery thumbs alt = `"... thumbnail"` — accurate but repetitive. Main alt uses `p.alt` which is good: e.g., "Portrait Skin Brushes for Procreate, product preview artwork".
- **Evidence:** Sample: alt="Portrait Skin Brushes for Procreate, product preview artwork: preview 1 thumbnail" — descriptive, but could include actual content of image (e.g., "close-up of pore texture" rather than generic "preview 1").
- **Fix:** For new products, write alt that describes actual image content, not just product name. Preserve existing valid alt; improve only where generic. Document in image SEO guidelines.
- **Effort:** S per product, M for all.
- **Risk:** Low.

### M-02 — No intrinsic dimensions for some OG cover fallback
- **Severity:** Medium (CLS risk)
- **Affected URLs:** Pages using `og-cover.jpg` fallback — dimensions 1200x630 declared in OG meta but not necessarily as width/height on img tag? Actually img tags have width/height from product data. Homepage has width/height.
- **Fix:** Audit all img tags for missing width/height — sample shows 0 missing in product page, homepage has 0 missing. Good. Keep validation.
- **Effort:** XS
- **Risk:** Low.

### M-03 — No FAQPage schema on some product pages that could benefit
- **Severity:** Medium (rich results opportunity)
- **Affected URLs:** Product pages — FAQPage schema is generated only if product has `faqs[]` in products.json. Some products have faqs, some don't. Could add genuine FAQs where helpful, but only if visible on page.
- **Evidence:** Sample product has FAQPage schema (3 FAQs). Check count of products with faqs.
- **Fix:** Audit products.json faqs field — add genuine FAQs only where they help reader, not filler. Ensure visible FAQ matches schema.
- **Effort:** M
- **Risk:** Low.

### M-04 — Internal linking density and orphan-page detection missing
- **Severity:** Medium (topical authority)
- **Affected URLs:** All — no automated orphan detection beyond verify.py broken links. Guides cross-link, but blog articles related links are manual from frontmatter.
- **Evidence:** Blog md frontmatter `related[]` is manually curated, good. But no automatic detection of orphan pages (e.g., seasonal hubs only linked from footer, not from content). Could improve internal linking engine.
- **Fix:** Implement lightweight internal-linking engine (as per brief section 7) with rules for relevance, max density, manual overrides. Do not insert links merely for keyword coverage.
- **Effort:** L
- **Risk:** Medium (needs content review).

### M-05 — Missing Product schema properties: sku, mpn, etc. — but must NOT invent
- **Severity:** Medium (schema completeness vs honesty)
- **Affected URLs:** Product pages — Product schema currently has name, image, description, brand, url, contentLocation, offers (price, currency, availability, url). No sku, no aggregateRating, no review — correct per safeguard (do not invent). Should keep as is.
- **Fix:** No fix needed — document that we omit unsupported properties intentionally.
- **Effort:** XS
- **Risk:** Low.

### M-06 — No BreadcrumbList on some static pages? Check
- **Severity:** Medium
- **Affected URLs:** about.html, faq.html, contact.html etc. — check if they have BreadcrumbList schema. `pages_misc.py` likely adds breadcrumb for all? Need to verify.
- **Fix:** Ensure all indexable pages have BreadcrumbList schema.
- **Effort:** S
- **Risk:** Low.

---

## Low

### L-01 — Meta title length: some titles >60 chars (house style allows 70)
- **Severity:** Low
- **Affected URLs:** Product pages — seoTitle capped at 70 chars per seo_engine.py (house style). Example: "Portrait Skin Brushes for Procreate: 19 Realistic Brushes | DigiKitPro" = 68 chars — within 70, but >60. Current limit is intentional to match existing catalog.
- **Fix:** Keep 70 char limit as per existing style, but validate that no title exceeds 70. Document fallback rule.
- **Effort:** XS
- **Risk:** Low.

### L-02 — Meta description length: capped at 165 (house style)
- **Severity:** Low
- **Affected URLs:** All — seoDesc capped at 165, slightly over generic 155-160 but matches existing. Validate.
- **Fix:** Keep, document.
- **Effort:** XS

### L-03 — No WebP/AVIF fallback for older browsers? Currently WebP only
- **Severity:** Low
- **Affected URLs:** All images — WebP only, no <picture> fallback. Modern browsers support WebP, but older Safari may need fallback. However product images are WebP only.
- **Fix:** Consider <picture> with JPEG fallback only if supported without harming feeds. Currently feeds use WebP which Pinterest supports. Keep as is, document risk.
- **Effort:** M
- **Risk:** Low.

### L-04 — No explicit width/height for some decorative images? Check
- **Severity:** Low
- **Affected URLs:** Homepage ba-before/ba-after have width/height 1200x800 — good.
- **Fix:** Keep.

### L-05 — No structured data for Organization on all pages? Actually present on homepage only? Check core.py head() includes Organization schema via SITE_URL+/#org? Need to verify.
- **Severity:** Low
- **Affected URLs:** All pages should have Organization + WebSite schemas via head()? Check sample product page had Product + Breadcrumb + FAQ, but not Organization? Actually Organization is referenced via publisher @id in BlogPosting, but not as standalone on product pages. Should add Organization + WebSite on all pages for consistency.
- **Fix:** Ensure Organization + WebSite schemas present on all indexable pages, not just homepage.
- **Effort:** S
- **Risk:** Low.

### L-06 — No sitemap lastmod update for orphaned drafts
- **Severity:** Low
- **Affected URLs:** Orphaned drafts have old lastmod? Not in sitemap, so irrelevant.
- **Fix:** Remove or properly add.

---

## Info / Observations

### I-01 — IndexNow enabled, key file present?
- **Evidence:** `INDEXNOW_KEY` env may be set via GitHub variable, key file `<key>.txt` should be in root after build. Check if file exists in repo? `ls *.txt` shows sitemap.txt only, no key file — because INDEXNOW_KEY not set in this sandbox. In production, deploy workflow writes key file via build.py if INDEXNOW_KEY env present.
- **Action:** Document that IndexNow is on by default, key is public, not secret.

### I-02 — Payhip sync adds products as featured/trending
- **Evidence:** `payhip_sync.py` adds new products as featured so they appear near top, but not labeled "New". Good.
- **Action:** No change.

### I-03 — No doorway pages, no hidden SEO text, no keyword stuffing observed
- **Evidence:** All content visible, no hidden divs, no stuffed meta keywords.
- **Action:** Keep.

### I-04 — No mass-published thin content
- **Evidence:** 18 articles, each 2k-3k words, technique-first, with practical steps, FAQ, sources.
- **Action:** Keep high standard for future articles.

### I-05 — No fake reviews, ratings, prices, availability
- **Evidence:** Product schema omits aggregateRating/review, prices from products.json match Payhip.
- **Action:** Preserve.

---

## Prioritized Action Order (for approval gate)

**Safe fixes (low-risk, reversible, template-level):**
- Remove orphaned blog HTML dirs OR convert to proper md source (C-01) — requires decision.
- Fix broken internal links in procreate-mistakes-beginners (C-01) — point to existing articles: procreate-canvas-size-dpi-guide, how-to-install-procreate-brushes, best-procreate-brushes-for-beginners, procreate-blending-brushes-guide.
- Ensure og:image dimensions match actual file (H-01).
- Clean empty <h3><br/></h3> in product descriptions (H-02).
- Ensure BreadcrumbList + Organization + WebSite schemas on all indexable pages (M-06, L-05).
- Validate all img have width/height, alt (M-01, M-02).

**Review required (content, product copy, URL behavior, feed, conversion):**
- Content gap analysis for skin articles (H-03) — decide if new articles cannibalize.
- Internal-linking engine implementation (M-04) — define relevance rules, max density, manual overrides.
- FAQPage expansion for products (M-03) — only where genuine FAQs help.
- Image alt improvements (M-01) — descriptive, not keyword list.

**Blocked (requires credentials, platform access, external approval, unavailable data):**
- GitHub Pages Enforce HTTPS toggle (C-02) — owner must do in Settings → Pages.
- Search Console Domain property + sitemap submission — owner must add Domain property digikitpro.shop, submit https://digikitpro.shop/sitemap.xml.
- GA4/Search Console data review — requires dashboard access, not available in sandbox.
- Pinterest catalog validation in Pinterest dashboard — requires Pinterest account access.
- Core Web Vitals field data — requires Search Console.

---

**Next:** Metadata/schema/internal-linking gap report in 04.
