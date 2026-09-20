# DigiKitPro SEO Engine — Phase 1 Baseline Audit Executive Summary

**Date:** 2026-09-19  
**Branch:** arena/01a0bbfa-digikitpro  
**Site:** https://digikitpro.shop/  
**Auditor:** Arena AI Agent (Phase 1 — Audit only, no implementation)

---

## Objective (from brief)

Build a scalable, maintainable SEO system that increases qualified organic traffic and converts relevant visitors (new digital artists, Procreate beginners, students, digital portrait artists). Improve visitor experience as well as search visibility. Not mass-produced blog posts or speculative SEO changes.

---

## What Was Audited

- **Platform:** Custom static Python generator (tools/build.py), GitHub Pages hosting, custom domain, Netlify fallback, no framework, custom CSS/JS.
- **Content:** 51 products, 18 blog articles (md source) + 4 orphaned HTML drafts, 10 categories, 6 guides, 2 seasonal, 11 main pages, partner portal.
- **SEO:** Titles, descriptions, canonicals, OG/Twitter, H1/H2, robots, breadcrumbs, structured data (Organization, WebSite, BreadcrumbList, Product, BlogPosting, FAQPage, HowTo, ItemList), sitemaps (99 URLs), robots.txt, feed.xml, Pinterest feeds (47 products).
- **Technical:** HTTPS, redirects (JS guard + Netlify), 404, noindex, crawlability, pagination (none), param handling, image SEO (WebP, srcset, width/height, alt, lazy), mobile, accessibility, thin/duplicated content, internal linking, orphan pages, broken links, analytics (GA4 G-5MFQFHNB6B), Pinterest catalog, verification tokens.
- **Deployment:** GitHub Actions deploy.yml + sync-payhip.yml, rollback via git.

---

## Key Findings

### Critical (must fix before proceeding)

1. **4 orphaned blog HTML dirs not in sitemap with broken internal links** — `how-to-shade-face-procreate`, `procreate-layers-alpha-lock-clipping-mask`, `procreate-line-art-tutorial`, `procreate-mistakes-beginners` exist on disk but have no md source, not in sitemap.xml, and one contains 2 broken links to non-existent articles (`procreate-shortcuts-gestures`, `procreate-30-day-practice-plan`). Causes verify.py FAIL (87/88).
2. **GitHub Pages Enforce HTTPS toggle unverified** — previously `https_enforced: false` per SEO-CANONICAL-FIX doc, causes http vs https duplicate and Search Console "Alternate page with proper canonical tag". Requires owner manual toggle in Settings → Pages.

### High

- OG image dimensions mismatch for orphaned drafts (750w card image declared as 1200x630).
- Empty `<h3><br/></h3>` and `<p><br/></p>` in some product descriptions.
- Potential cannibalization between `realistic-skin` workflow vs texture articles.
- Search index correctly excludes orphaned drafts, but orphaned pages would not appear in search if accessed directly.

### Medium

- Alt text for gallery thumbnails generic ("preview N") — could be more descriptive.
- No BreadcrumbList + Organization + WebSite schemas on all pages (product pages have Product + Breadcrumb + FAQ, missing Org/WebSite).
- No contextual internal-linking engine — related links are manual frontmatter, not inline contextual with relevance rules, max density, orphan detection.
- Product schema image array could include all gallery images, not just main.
- FAQPage could be expanded where genuine FAQs help, but only if visible.

### Low / Info

- Title length 70 chars (house style) slightly over generic 60 but consistent.
- Description length 165 chars (house style) slightly over 155-160 but consistent.
- WebP only, no JPEG fallback — modern, Pinterest supports WebP, low risk.
- No fake reviews, ratings, scarcity, doorway, hidden text, keyword stuffing observed — good.
- No mass thin content — 18 articles technique-first, 2k-3k words.

---

## Deliverables Produced (Phase 1)

1. **01-platform-and-safeguards.md** — Platform, theme, SEO plugins, analytics, Pinterest, deployment, safeguards checklist, access limitations.
2. **02-url-inventory.md** — Complete URL and template inventory (99 sitemap URLs, 51 products, 18+4 blog, 10 categories, 6 guides, 2 seasonal, etc.), robots.txt, sitemap details, duplicate variant handling, navigation.
3. **03-issue-register.md** — Prioritized issue register with severity, affected URLs, evidence, recommended fix, effort, risk, separated into Safe fixes / Review required / Blocked.
4. **04-metadata-schema-linking-gaps.md** — Gap report for titles, descriptions, canonicals, OG/Twitter, H1/H2, robots, breadcrumbs, structured data, internal linking, Pinterest feed, image SEO.
5. **05-assumptions-and-manual-review.md** — Assumptions, unavailable data (Search Console, GA4, server logs, Pinterest dashboard, Core Web Vitals, etc.), manual review items, questions for owner.
6. **06-proposed-architecture.md** — Proposed SEO-engine architecture and implementation plan with components (metadata engine, product SEO engine, internal-linking engine, content opportunities, article standards, image SEO, structured data, technical SEO, Pinterest, monitoring dashboard), implementation order, testing criteria, files to change, risks.
7. **00-executive-summary.md** — This summary.

All in `docs/seo-audit/`.

---

## Safeguards Compliance

- No production code changed during audit — only documentation added in `docs/seo-audit/`.
- All existing product, article, category, Pinterest, redirect URLs preserved.
- No metadata removed without documenting reason.
- No invented product features, reviews, ratings, prices, availability.
- No keyword stuffing, doorway pages, hidden SEO text, mass thin content.
- Reversible changes and change log to be maintained in future phases.

---

## Approval Gate (per brief section 4)

**Safe fixes (low-risk, reversible, template-level):**
- Remove or convert orphaned blog HTML dirs, fix broken internal links.
- Fix OG image dimensions.
- Clean empty headings in product descriptions.
- Add BreadcrumbList + Organization + WebSite schemas to all indexable pages.
- Validate all img have width/height/alt.

**Review required (content, product copy, URL behavior, feed, conversion):**
- Content gap analysis for skin articles, future roadmap articles.
- Internal-linking engine with relevance rules, max density, orphan detection, manual overrides.
- FAQ expansion for products where genuine.
- Alt text improvements.
- Pinterest recommendations.

**Blocked (requires credentials, platform access, external approval, unavailable data):**
- GitHub Pages Enforce HTTPS toggle (owner manual).
- Search Console Domain property + sitemap submission.
- GA4/Search Console data review.
- Pinterest catalog validation.
- Core Web Vitals field data.

**Proceed only with approved or clearly safe fixes.**

---

## Proposed Architecture Highlights

- **Metadata Engine (`seo_metadata.py`):** Centralized SEO title, description, canonical, OG, Twitter, robots, breadcrumb with deterministic fallback rules and validation for missing/duplicated/overlong/suspicious values.
- **Product SEO Engine (enhanced `seo_engine.py`):** Accurate alt, Product + Breadcrumb schema with real values only, gallery images in schema, relevant category/article/related-product links, related recommendations.
- **Internal-Linking Engine (`internal_linking.py`):** Contextual, limited links among products/articles/categories with relevance mapping, max density, orphan detection, manual overrides, descriptive anchor text.
- **Content Opportunities (`content_opportunities.json`):** 20 opportunities from roadmap with required fields (topic, primary keyword, intent, audience, related terms, existing coverage, gap, relevant products, internal links, Pinterest angle, priority, rationale, effort, risk), cannibalization check.
- **Article Standards:** One H1, logical H2/H3, beginner-friendly, practical examples, images with alt, contextual links, related articles, FAQ only where helpful, SEO title/desc/canonical/Article schema, human-readable.
- **Image SEO:** Descriptive filenames, accurate alt, empty alt for decorative, width/height, srcset, lazy, WebP/AVIF where supported without harming feeds, CLS reduction.
- **Structured Data:** Organization, WebSite, BreadcrumbList on all pages, Product with real values, BlogPosting, FAQPage only when visible FAQs, HowTo, ItemList, validated.
- **Technical SEO:** Sitemap validity, robots.txt, canonicals, HTTPS, 404, noindex, crawlability, pagination, param handling, indexability of search/filter/thin pages. No URL changes without migration plan and approval.
- **Pinterest:** Preserve catalog/feed, generate recommendations (title, desc, board, image concept, cluster relationship) without mass automation, verify destination URLs/prices/fields intact.
- **Monitoring:** Lightweight internal report (or exportable JSON/CSV/Markdown) showing missing/duplicate/invalid metadata, missing canonical, suspicious alt, broken links, orphan pages, schema issues, thin content, pages lacking contextual links, content opportunities, cannibalization warnings. Avoid unnecessary dependencies.

---

## Implementation Order (per brief)

1. Audit and baseline evidence — **Done.**
2. Present findings, risks, assumptions, architecture for approval — **This audit.**
3. Apply safe technical SEO fixes — **Awaiting approval.**
4. Implement and test metadata/product SEO engine.
5. Improve internal linking.
6. Implement and validate structured data.
7. Improve image SEO and performance.
8. Build content-cluster and opportunity system.
9. Research and publish first approved high-priority articles.
10. Produce Pinterest recommendations without mass automation.
11. Add lightweight monitoring/reporting.

---

## Testing & Acceptance Criteria (for future phases)

- Homepage, representative product pages, categories, blog, articles render correctly.
- Mobile layouts usable.
- Existing product, article, category, Pinterest, redirect URLs still work.
- Sitemap and robots.txt valid.
- Canonicals correct and self-consistent.
- Structured data valid and matches visible content.
- Metadata unique for representative page types.
- Product schema no fabricated properties.
- Analytics, tracking, Pinterest catalog intact.
- No new broken links, noindex mistakes, redirect chains, performance regressions.
- Verify.py passes all checks.
- Record test URLs, results, validation output, unresolved risks.

---

## Remaining Opportunities & Next Steps

- Owner reviews audit deliverables.
- Owner approves safe fixes, decides on orphaned drafts (delete or publish properly), provides baseline metrics and success metrics agreement.
- Owner performs manual steps: Enforce HTTPS toggle, Search Console Domain property + sitemap submission, Pinterest catalog validation.
- Proceed with safe fixes, then metadata engine, internal linking, structured data, image SEO, content clusters, Pinterest recommendations, monitoring — per order, with approval at each stage.

---

## Risks, Limitations, Unavailable Access

- No Search Console, GA4, server logs, Pinterest dashboard, Core Web Vitals field data — only site-side implementation.
- No admin access to GitHub Pages, Payhip, domain DNS, Pinterest account.
- 4 orphaned drafts with broken links must be resolved before audit can be considered fully green (verify.py currently 87/88).

---

**End of executive summary.**
