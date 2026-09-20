# DigiKitPro — Assumptions, Unavailable Data, Manual Review Items (2026-09-19)

---

## 5.1 Assumptions

### Platform & Deployment
- **A-01:** Site is hosted on GitHub Pages with custom domain digikitpro.shop, CNAME file present and tracked by git. Assumed to be primary production host.
- **A-02:** GitHub Pages Enforce HTTPS toggle was previously off (per SEO-CANONICAL-FIX-2026-09-19.md API check). Assumed still needs manual verification — we cannot call GitHub API from sandbox with admin scope.
- **A-03:** Netlify is not primary host, but netlify.toml redirects are present as fallback/documentation. Assumed harmless on GitHub Pages.
- **A-04:** Deployment via `.github/workflows/deploy.yml` is current production deployment process. Rollback via git revert.
- **A-05:** `tools/build.py` is single source of truth for generated HTML — no manual HTML edits in production. Assumed all HTML in repo root is generated.

### SEO & Content
- **A-06:** `data/products.json` contains real Payhip data from 2026-08-11 scrape, plus hand-written SEO copy. Assumed accurate and not to be invented.
- **A-07:** `data/discovery.json` merchandising model is editorial, not sales figures. Priority field is editorial weight, not popularity.
- **A-08:** Blog articles in `content/blog/*.md` are original, technique-first, 2k-3k words, with practical steps, FAQ, sources. Assumed human-written, not AI mass-produced.
- **A-09:** 4 orphaned blog HTML dirs (how-to-shade-face-procreate, procreate-layers-alpha-lock-clipping-mask, procreate-line-art-tutorial, procreate-mistakes-beginners) are leftover drafts from SEO-CONTENT-ROADMAP-2026.md Wave 1, not intended to be indexed until properly sourced as md with frontmatter. Assumed they should be removed or converted.
- **A-10:** No doorway pages, hidden SEO text, keyword stuffing, or mass thin content observed — assumed site complies with brief non-negotiables.
- **A-11:** Product schema omits aggregateRating/review intentionally to avoid fake social proof — assumed correct per honesty checks in verify.py.
- **A-12:** Sitemap.xml 99 URLs is correct count for current valid content (11 main + 10 categories + 2 seasonal + 6 guides + 1 partner + 51 products + 18 blog). Assumed 99 is baseline, not 100 (search.html removed intentionally).
- **A-13:** Search, thank-you, 404 are intentionally noindex, follow — assumed correct.

### Analytics & Pinterest
- **A-14:** GA4 measurement ID G-5MFQFHNB6B is production ID, gtag injection is correct.
- **A-15:** Pinterest catalog feeds (xml/csv) with 47 paid products are current production feeds submitted to Pinterest. Assumed valid and not to be disrupted.
- **A-16:** Pinterest verification token 990d08b5349bfcbb0171eab3d6f8f2d2 is production token.
- **A-17:** No Pinterest Tag (ads) active — dormant unless PINTEREST_TAG_ID set — assumed intentional.

### Audience & Business
- **A-18:** Primary audiences are new digital artists, Procreate beginners, students, digital portrait artists — per brief. Assumed content clusters should prioritize these.
- **A-19:** Target countries/languages: worldwide, with 7-language Google Translate switcher (en, es, fr, de, it, pt, nl). Primary language en. Assumed no hreflang needed beyond og:locale:alternate.
- **A-20:** No baseline metrics (impressions, clicks, conversions) available in sandbox — assumed to be documented separately by owner.

---

## 5.2 Unavailable Data

### Search Console / Analytics
- **U-01:** No Google Search Console access — cannot verify indexed pages, impressions, clicks, non-brand clicks, crawl errors, Core Web Vitals field data, "Alternate page with proper canonical tag" current status, or sitemap submission status.
- **U-02:** No GA4 dashboard access — cannot verify organic sessions, product-page organic sessions, assisted conversions, conversion rate, bounce rate, or baseline KPIs.
- **U-03:** No Bing Webmaster Tools access — cannot verify Bing indexing, sitemap status.
- **U-04:** No server logs — cannot verify crawl budget, bot hits, 404s in wild, redirect chains observed by crawlers.

### Pinterest
- **U-05:** No Pinterest catalog dashboard access — cannot verify feed validation, product disapprovals, Pin performance, board mapping.
- **U-06:** No Pinterest Tag data — cannot verify conversion tracking.

### Performance & Accessibility
- **U-07:** No Lighthouse / PageSpeed Insights field data — only static analysis of image optimization, lazy loading, font preload. Cannot verify LCP, CLS, INP, TTFB.
- **U-08:** No manual mobile rendering test on real devices — only viewport meta and responsive CSS analysis.
- **U-09:** No accessibility audit tool output (axe, Lighthouse a11y) — only manual check of skip link, aria labels, alt text.

### Content & Business
- **U-10:** No first-party search query data (site search logs, Payhip search) — cannot verify actual search demand.
- **U-11:** No customer feedback, support tickets, or FAQ data beyond existing faq.html — cannot verify content gaps from real user questions.
- **U-12:** No competitor analysis data — brief says do not copy competitors, but no competitor list provided.
- **U-13:** No baseline metrics for success — brief says success metrics should be agreed before launch (indexed canonical pages, impressions, qualified organic clicks, non-brand clicks, product-page organic sessions, assisted conversions, conversion rate). No baseline documented in repo.

### Credentials
- **U-14:** No admin access to GitHub Pages settings — cannot verify Enforce HTTPS toggle, cannot set via API (403 expected).
- **U-15:** No access to Payhip dashboard — cannot verify product prices, availability, or new products beyond public store.
- **U-16:** No access to domain DNS — cannot verify DNS verification for Search Console Domain property.

---

## 5.3 Items Requiring Manual Review

### Content & Editorial (Review Required per brief)
- **R-01:** 4 orphaned blog drafts — need owner decision: delete or publish properly with md source, frontmatter, and sitemap inclusion. If publish, need content quality review for accuracy, beginner-friendliness, practical examples, images with alt, internal links, FAQ, SEO title/desc, Article schema.
- **R-02:** Skin content cannibalization — `how-to-create-realistic-skin-in-procreate` vs `how-to-create-realistic-skin-texture-in-procreate` — need editorial review to ensure distinct intent and cross-linking.
- **R-03:** Product descriptions with empty `<h3><br/></h3>` and `<p><br/></p>` — need manual cleanup of `data/products.json` descriptionHtml.
- **R-04:** Alt text improvements for gallery images — need manual review of actual image content to write descriptive alt (e.g., "close-up of pore texture" vs "preview 1").
- **R-05:** FAQ expansion for products — only add genuine FAQs where they help reader, not filler. Need manual review of product pages for common questions.
- **R-06:** Future content opportunities from SEO-CONTENT-ROADMAP-2026.md (20 articles) — each opportunity needs manual review for search intent, target audience, existing competing coverage, content gap, relevant products, internal-link opportunities, Pinterest angle, priority, rationale, effort, risk — per brief section 8. Do not auto-publish.
- **R-07:** Guides content — 5 buyer guides are hardcoded in `pages_guides.py` with editorial copy. Need manual review for accuracy, no invented claims, honest limits.

### Technical (Safe fixes, but need review for conversion impact)
- **R-08:** GitHub Pages Enforce HTTPS toggle — owner must manually verify and enable.
- **R-09:** Search Console Domain property setup — owner must add Domain property digikitpro.shop, submit sitemap, review "Alternate page with proper canonical tag" report after HTTPS toggle.
- **R-10:** OG image dimensions fix — need to verify actual image dimensions and update head() to use correct width/height.
- **R-11:** BreadcrumbList + Organization + WebSite schemas on all pages — need to verify no duplication or conflict with existing schemas.
- **R-12:** Internal-linking engine — define relevance rules, max link density, orphan detection, manual overrides. Must not insert links merely for keyword coverage. Needs editorial approval.
- **R-13:** Image SEO — WebP only, no JPEG fallback — need to verify Pinterest and Payhip compatibility if adding fallback.

### Pinterest (Do not modify without approval)
- **R-14:** Pinterest feed — do not modify fields, destination URLs, or product inclusion without verifying catalog still validates. Any change to product URLs, prices, or images must keep feed intact.
- **R-15:** Pinterest recommendations for selected products/articles (title, description, board, image concept) — per brief section 13, generate recommendations, not automatic mass publishing. Needs manual review.

### Monitoring & Reporting
- **R-16:** Lightweight monitoring dashboard — brief says add if supported by current architecture, otherwise exportable report. Need to assess if static site can support dashboard safely (e.g., via JS reading search-index.js and checking for missing metadata) or if exportable report (e.g., JSON/CSV) is better. Avoid unnecessary dependencies.
- **R-17:** Verify.py currently expects 88 checks, but 87 passing due to broken links — need to update expected count or fix broken links before considering audit complete.

### Legal & Honesty
- **R-18:** No testimonial, review-count, star rating, customer-count, scarcity claims — verify.py checks for these patterns. Need manual review to ensure no new content introduces such claims.
- **R-19:** No fake product features, reviews, ratings, prices, availability — must preserve.

---

## 5.4 Questions for Owner (Information Required Before Implementation per brief section 17)

- **Q-01:** Website platform and theme/framework — confirmed as custom static Python generator, custom CSS — correct?
- **Q-02:** Available admin, code, hosting, analytics, Search Console access — what access can be provided for validation?
- **Q-03:** Current SEO plugins/apps — confirmed none, custom implementation — correct?
- **Q-04:** Current Pinterest catalog/feed mechanism — confirmed pinterest-feed.xml/csv generated by pages_misc.py — correct? Is feed submitted to Pinterest via Data Source?
- **Q-05:** Existing deployment and rollback process — confirmed GitHub Actions deploy.yml, rollback via git revert — correct?
- **Q-06:** Whether content publishing is in scope — are new articles from roadmap in scope, or only technical SEO engine?
- **Q-07:** Whether production changes require separate approval — per brief, do not change production code until audit approved — is this approval gate required?
- **Q-08:** Primary target countries and languages — confirmed worldwide, 7-language translate switcher — correct? Any primary target beyond en?
- **Q-09:** Current baseline metrics and business KPIs — what are baseline indexed pages, impressions, organic clicks, product-page sessions, conversions?
- **Q-10:** Success metrics — brief suggests indexed canonical pages, impressions, qualified organic clicks, non-brand clicks, product-page organic sessions, assisted conversions, conversion rate — which should be agreed before launch?

---

**Next:** Proposed SEO-engine architecture in 06.
