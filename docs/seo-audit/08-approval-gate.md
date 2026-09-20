# DigiKitPro — Approval Gate (Phase 1 Audit → Phase 2 Implementation)

**Date:** 2026-09-19  
**Branch:** arena/01a0bbfa-digikitpro  
**Status:** Audit complete, awaiting owner approval before any production code changes.

---

## 1. What Was Audited (Summary)

- Platform: Custom static Python generator, GitHub Pages, custom domain digikitpro.shop, Netlify fallback, custom CSS/JS, no framework.
- Content: 51 products, 18 md blog articles + 4 orphaned HTML drafts (22 HTML dirs committed), 10 categories, 6 guides, 2 seasonal, 11 main pages, partner portal.
- SEO: Titles, descriptions, canonicals, OG/Twitter, H1/H2, robots, breadcrumbs, structured data (Organization, WebSite, BreadcrumbList, Product, BlogPosting, FAQPage, HowTo, ItemList), sitemaps (103 URLs in current HEAD, 99 expected after cleanup), robots.txt, feed.xml, Pinterest feeds (47 products).
- Technical: HTTPS, redirects (JS guard + Netlify), 404, noindex, crawlability, pagination (none), param handling, image SEO (WebP, srcset, width/height, alt, lazy), mobile, accessibility, thin/duplicated content, internal linking, orphan pages, broken links, analytics (GA4), Pinterest catalog.
- Deployment: GitHub Actions deploy.yml + sync-payhip.yml, rollback via git.

**Audit deliverables in `docs/seo-audit/`:**
- 00-executive-summary.md
- 01-platform-and-safeguards.md
- 02-url-inventory.md
- 03-issue-register.md (prioritized with severity, URLs, evidence, fix, effort, risk)
- 04-metadata-schema-linking-gaps.md
- 05-assumptions-and-manual-review.md
- 06-proposed-architecture.md (SEO-engine architecture and implementation plan)
- 07-monitoring-report.md (lightweight monitoring report baseline)
- CHANGELOG.md
- 08-approval-gate.md (this file)

---

## 2. Critical Issues Requiring Decision

### C-01 — 4 orphaned blog HTML dirs with broken links

- **Current HEAD:** `blog/` has 22 HTML dirs committed, but `content/blog/` has only 18 md source files. Sitemap.xml in HEAD has 103 URLs (22 blog), but md source has 18. The 4 extra are:
  - `how-to-shade-face-procreate`
  - `procreate-layers-alpha-lock-clipping-mask`
  - `procreate-line-art-tutorial`
  - `procreate-mistakes-beginners` (contains 2 broken internal links to `procreate-shortcuts-gestures` and `procreate-30-day-practice-plan`)
- **Evidence:** `tools/verify.py` currently FAILs on main? Let's check — in HEAD, verify would pass if those 4 are in sitemap and have no broken links? But one has broken links, so verify FAILs 87/88 (as seen after build). In HEAD with 103 URLs, verify likely also fails due to broken links.
- **Options:**
  - **Option A (Safe, recommended for audit cleanup):** Remove the 4 orphaned HTML dirs from repo and from sitemap (revert to 99 URLs, 18 blog). This restores consistency: md source = HTML dirs = sitemap. No new content published.
  - **Option B (Publish):** Restore md source for the 4 drafts with proper frontmatter (title, slug, description, date, primary_keyword, secondary_keywords, search_intent, target_audience, tags, products, related), fix broken links, then rebuild. This would publish 4 new articles, increasing sitemap to 103 (or 103 if already) and requiring content quality review per brief section 9.
- **Decision needed:** Owner to choose A or B. If B, need to provide content for the 4 drafts or approve existing HTML content as md.

### C-02 — GitHub Pages Enforce HTTPS toggle

- **Evidence:** Previous audit (SEO-CANONICAL-FIX-2026-09-19.md) found `https_enforced: false` via GitHub API. http://digikitpro.shop/ serves 200 with same HTML as https if off, causing "Alternate page with proper canonical tag" in Search Console.
- **Fix:** Owner manual step: GitHub repo Settings → Pages → Enforce HTTPS → tick, wait for certificate active, verify `curl -I http://digikitpro.shop/` returns 301 to https. No code change needed beyond existing JS guard + Netlify redirects.
- **Blocked:** Requires GitHub Pages admin access.

---

## 3. Recommendations Separated per Brief Section 4

### Safe Fixes (Low-risk, reversible, template-level improvements) — Can proceed after approval

- **SF-01:** Resolve C-01 via Option A (remove orphaned HTML dirs, rebuild to 99 URLs) OR Option B (restore md source, fix broken links). Effort S, Risk Low/Medium.
- **SF-02:** Fix broken internal links in `procreate-mistakes-beginners` to point to existing articles (e.g., `procreate-canvas-size-dpi-guide`, `how-to-install-procreate-brushes`, `best-procreate-brushes-for-beginners`, `procreate-blending-brushes-guide`). Effort XS, Risk Low.
- **SF-03:** Fix OG image dimensions mismatch — ensure og:image width/height reflect actual file dimensions from products.json (e.g., card 750w vs declared 1200x630). Update `pages_blog.py` head() og_image handling. Effort S, Risk Low.
- **SF-04:** Clean empty `<h3><br/></h3>` and `<p><br/></p>` in product descriptions (`data/products.json` descriptionHtml). Effort M, Risk Low.
- **SF-05:** Add BreadcrumbList + Organization + WebSite schemas to all indexable pages (currently product pages have Product + Breadcrumb + FAQ, missing Org/WebSite). Update `core.py` head() to include Org + WebSite on all pages. Effort S, Risk Low.
- **SF-06:** Validate all img have width/height/alt, fix empty alt for bundle ladder images (currently alt="" for 4 bundle cards on homepage). Effort S, Risk Low.
- **SF-07:** Ensure sitemap.xml, sitemap.txt, sitemap-images.xml validity and inclusion of canonical indexable URLs only (currently 103 in HEAD, should be 99 after cleanup or 103 if publishing 4 drafts). Effort XS, Risk Low.

### Review Required (Content, product copy, URL behavior, feed behavior, conversion implications)

- **RR-01:** Content gap analysis for skin articles (`how-to-create-realistic-skin-in-procreate` vs `how-to-create-realistic-skin-texture-in-procreate`) — ensure distinct intent, cross-linking, no cannibalization. Effort M, Risk Medium.
- **RR-02:** Internal-linking engine implementation — define relevance rules, max link density, orphan detection, manual overrides, anchor text guidelines. Must not insert links merely for keyword coverage. Effort L, Risk Medium.
- **RR-03:** FAQ expansion for products — only where genuine FAQs help reader, not filler. Ensure visible FAQ matches FAQPage schema. Effort M, Risk Low.
- **RR-04:** Alt text improvements for gallery images — descriptive, not keyword list, preserve empty alt for decorative. Effort M, Risk Low.
- **RR-05:** Image SEO — WebP only, no JPEG fallback — verify Pinterest and Payhip compatibility if adding fallback. Effort M, Risk Low.
- **RR-06:** Content opportunities from SEO-CONTENT-ROADMAP-2026.md (20 articles) — each needs manual review for search intent, target audience, existing coverage, gap, relevant products, internal links, Pinterest angle, priority, rationale, effort, risk. Do not auto-publish. Effort XL, Risk Medium.
- **RR-07:** Guides content — 5 buyer guides hardcoded in `pages_guides.py` — need manual review for accuracy, no invented claims, honest limits. Effort M, Risk Low.
- **RR-08:** Pinterest recommendations — for selected products/articles, generate recommendations (title, description, board, image concept, cluster relationship) without mass automation. Verify destination URLs, prices, fields intact. Effort M, Risk Low.

### Blocked (Requires credentials, platform access, external approval, unavailable data)

- **B-01:** GitHub Pages Enforce HTTPS toggle — owner manual, Settings → Pages.
- **B-02:** Search Console Domain property setup — owner must add Domain property digikitpro.shop, submit https://digikitpro.shop/sitemap.xml, review "Alternate page with proper canonical tag" report after HTTPS toggle.
- **B-03:** GA4/Search Console data review — requires dashboard access, not available in sandbox.
- **B-04:** Pinterest catalog validation — requires Pinterest account access, Data Source validation.
- **B-05:** Core Web Vitals field data — requires Search Console.
- **B-06:** Payhip dashboard — requires Payhip access for price/availability verification.
- **B-07:** Domain DNS — requires DNS access for Domain property verification.

---

## 4. Proposed SEO-Engine Architecture (Summary)

**Components (detailed in 06-proposed-architecture.md):**

- **Metadata Engine (`tools/seo_metadata.py`):** Centralized SEO title, description, canonical, OG, Twitter, robots, breadcrumb with deterministic fallback rules and validation.
- **Product SEO Engine (enhanced `seo_engine.py`):** Accurate alt, Product + Breadcrumb schema with real values, gallery images in schema, relevant category/article/related-product links.
- **Internal-Linking Engine (`tools/internal_linking.py`):** Contextual, limited links with relevance mapping, max density, orphan detection, manual overrides, descriptive anchor text.
- **Content Opportunities (`data/content_opportunities.json`):** 20 opportunities with required fields, cannibalization check.
- **Article Standards:** One H1, logical H2/H3, beginner-friendly, practical examples, images with alt, contextual links, related articles, FAQ only where helpful, SEO title/desc/canonical/Article schema.
- **Image SEO:** Descriptive filenames, accurate alt, empty alt for decorative, width/height, srcset, lazy, WebP/AVIF where supported, CLS reduction.
- **Structured Data:** Organization, WebSite, BreadcrumbList on all pages, Product with real values, BlogPosting, FAQPage, HowTo, ItemList, validated.
- **Technical SEO:** Sitemap validity, robots.txt, canonicals, HTTPS, 404, noindex, crawlability, pagination, param handling, indexability of search/filter/thin pages.
- **Pinterest:** Preserve catalog/feed, generate recommendations without mass automation.
- **Monitoring:** Lightweight internal report (exportable JSON/CSV/Markdown) showing missing/duplicate/invalid metadata, missing canonical, suspicious alt, broken links, orphan pages, schema issues, thin content, pages lacking contextual links, content opportunities, cannibalization warnings.

**Implementation Order (from brief):**
1. Audit and baseline evidence — Done.
2. Present findings, risks, assumptions, architecture for approval — This gate.
3. Apply safe technical SEO fixes — Awaiting approval.
4. Implement and test metadata/product SEO engine.
5. Improve internal linking.
6. Implement and validate structured data.
7. Improve image SEO and performance.
8. Build content-cluster and opportunity system.
9. Research and publish first approved high-priority articles.
10. Produce Pinterest recommendations without mass automation.
11. Add lightweight monitoring/reporting.

---

## 5. Questions for Owner (Information Required Before Implementation)

- Q-01: Platform/theme confirmed as custom static Python generator, custom CSS — correct?
- Q-02: What admin, code, hosting, analytics, Search Console access can be provided for validation?
- Q-03: SEO plugins/apps confirmed none, custom implementation — correct?
- Q-04: Pinterest catalog/feed mechanism confirmed pinterest-feed.xml/csv generated by pages_misc.py — correct? Is feed submitted to Pinterest via Data Source?
- Q-05: Deployment and rollback confirmed GitHub Actions deploy.yml, rollback via git revert — correct?
- Q-06: Is content publishing in scope (new articles from roadmap) or only technical SEO engine?
- Q-07: Do production changes require separate approval (per brief, do not change production code until audit approved)?
- Q-08: Primary target countries/languages confirmed worldwide, 7-language translate switcher — correct? Any primary target beyond en?
- Q-09: Current baseline metrics and business KPIs — what are baseline indexed pages, impressions, organic clicks, product-page sessions, conversions?
- Q-10: Success metrics — which of indexed canonical pages, impressions, qualified organic clicks, non-brand clicks, product-page organic sessions, assisted conversions, conversion rate should be agreed before launch?

---

## 6. Decision Requested

**Owner to approve:**

- [ ] Safe fixes list (SF-01 to SF-07) — proceed after approval.
- [ ] Review required list (RR-01 to RR-08) — which are in scope and priority.
- [ ] Blocked items — owner to perform manual steps (Enforce HTTPS, Search Console Domain property, Pinterest validation).
- [ ] C-01 Option A (remove orphaned drafts) or Option B (publish properly with md source).
- [ ] Content publishing scope — are new articles from roadmap in scope?
- [ ] Success metrics agreement — which KPIs to track and baseline.

**Once approved, proceed with implementation order, with change log, testing, and validation per brief section 16.**

---

**End of approval gate.**
