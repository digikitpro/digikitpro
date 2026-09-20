# DigiKitPro — Lightweight Monitoring Report (Baseline 2026-09-19)

**Generated:** 2026-09-19 via custom audit script (no external dependencies)  
**Sitemap URLs:** 99  
**Products:** 51 (all have seoTitle, seoDesc, alt, tags)  
**Blog md:** 18 (plus 4 orphaned HTML dirs not in sitemap)

---

## Summary

- **Missing metadata:** 0 missing title, 0 missing description, 0 missing canonical, 0 missing OG (for sitemap-listed pages) — good.
- **Duplicate metadata:** 0 duplicate titles, 0 duplicate descriptions — good.
- **Broken internal links (sitemap pages):** 0 — good (orphaned drafts not in sitemap, but they have 2 broken links internally).
- **Orphaned drafts not in sitemap:** 4 — `how-to-shade-face-procreate`, `procreate-layers-alpha-lock-clipping-mask`, `procreate-line-art-tutorial`, `procreate-mistakes-beginners` — these have index,follow and would be indexable if discovered, but not in sitemap.
- **Broken links in orphaned drafts:** 2 in `procreate-mistakes-beginners` → `../procreate-shortcuts-gestures/` and `../procreate-30-day-practice-plan/` — targets do not exist.
- **Missing alt:** 0 missing alt attribute, but 9 suspicious empty alts found:
  - `index.html` has 4 empty alts for bundle ladder images (brush-palette-bundle-160, ultimate-portrait-mastery-bundle, procreate-mega-bundle-650, master-library-2000-brushes) — these are content images and should have descriptive alt.
  - `products/procreate-portrait-masterclass-ebook/index.html` has 5 empty alts for look-thumbs (interior page thumbnails) — buttons have aria-label, but img alt empty may be okay if decorative, but could be improved.
- **Thin content:** 0 blog md <800 words — good (all 18 are 2k+).
- **Orphan detection (naive):** Our simple incoming link counter flagged 99 pages as <3 incoming, but this is due to counting logic not including all relative links properly. Manual review shows all sitemap pages are linked from nav/footer/homepage, so not truly orphaned. However seasonal hubs and guides only linked from footer/homepage, not from contextual content — low internal link equity.
- **Product schema:** No fake reviews/ratings, prices real, availability InStock — good.
- **Image sitemap:** 51 pages, 173 images, all https, no -card/-thumb — good.
- **Pinterest feed:** 47 paid products, required fields present — good.

---

## Detailed Findings

### Missing / Duplicate / Invalid Metadata

- **Missing title:** 0
- **Missing description:** 0
- **Missing canonical:** 0
- **Missing OG (title/desc/image):** 0
- **Duplicate titles:** 0
- **Duplicate descriptions:** 0
- **Overlong titles (>70):** Need to check — sample product 68 chars, within 70. No validation found >70.
- **Overlong descriptions (>165):** Need to check — sample 150-160, within 165.
- **Suspicious:** No "lorem", "placeholder", "test" found in titles/descs.

**Action:** Keep validation, add automated check for overlong/suspicious in verify.py.

### Missing Canonical Tags

- 0 missing canonical for sitemap pages — good.
- Search, thank-you, 404 have self-canonical but noindex — correct.

### Missing or Suspicious Alt Text

- **Missing alt attribute:** 0
- **Empty alt (alt=""):** 9 found:
  - `index.html` line 352, 370, 388, 406 — bundle ladder cards
  - `products/procreate-portrait-masterclass-ebook/index.html` line 194 — 5 look-thumbs
- **Too short (<5 chars):** Same 9 (empty)
- **Keyword stuffed:** None detected (no alt with procreate >3 or brush >4 repeated)

**Recommendation:**
- Bundle ladder images should have descriptive alt like product name (currently alt="" — should be product name).
- Look-thumbs: if decorative and button has aria-label, empty alt is acceptable per accessibility (meaningful empty alt for decorative), but could add alt describing interior page (e.g., "Masterclass interior: Contents page").

### Broken Internal Links

- **Sitemap pages:** 0 broken — good.
- **Orphaned drafts (not in sitemap):** 2 broken in `blog/procreate-mistakes-beginners/index.html`:
  - `../procreate-shortcuts-gestures/` → does not exist
  - `../procreate-30-day-practice-plan/` → does not exist
- **Verify.py:** FAIL for 0 broken internal links — 2 broken (same as above).

**Action:** Fix broken links to point to existing articles (e.g., `procreate-canvas-size-dpi-guide`, `how-to-install-procreate-brushes`, `best-procreate-brushes-for-beginners`, `procreate-blending-brushes-guide`) or remove orphaned drafts.

### Orphan Pages

- **Definition:** Pages with <3 incoming internal links (excluding nav/footer) or not linked from contextual content.
- **Naive count:** 99 flagged due to counting logic limitation.
- **Manual review:**
  - Seasonal hubs (`/season/halloween/`, `/season/christmas/`) only linked from footer, not from homepage or articles — low equity, but not truly orphaned.
  - Guides (`/guides/*`) linked from footer and homepage articles section? Actually homepage has 3 guides in articles section? Need to verify — homepage articles section shows 3 latest articles, not guides. Guides linked from footer only? Actually footer has 5 guides under "Learn". So guides have footer links, but not contextual inline links from blog.
  - Partner (`/partner/`) linked from footer of every page — good, but only footer.
  - Categories: linked from footer and guides and product pages (category link) — good.
  - Products: linked from homepage, category, guides, blog product grids, related products — good.
  - Blog: linked from homepage, blog index, related articles, footer — good.
- **True orphans:** 4 orphaned drafts not linked from any sitemap page (since not in sitemap), but they are on disk and could be discovered if someone guesses URL or if old sitemap had them.

**Action:** Implement proper orphan detection in `seo_report.py` that counts incoming links from all generated HTML (including directory URLs) and excludes nav/footer if needed, or counts contextual links only.

### Schema Validation Issues

- **Product schema:** No fake reviews/ratings — good. Image array includes main only? Could include gallery.
- **Organization + WebSite:** Missing on product, blog, category pages — only homepage has Org + WebSite? Need to verify: sample product had 3 schemas (Product, Breadcrumb, FAQ) — no Org/WebSite. Should add.
- **BreadcrumbList:** Present on product, blog, category, guides, seasonal, partner? Need to verify static pages (about, faq, etc.) — likely have breadcrumb, but need to check.
- **FAQPage:** Only when visible FAQs present — correct.
- **HowTo:** Only for howto:true articles with steps — correct.

**Action:** Add Org + WebSite to all indexable pages, ensure Product image array includes gallery, validate required properties.

### Thin-Content Candidates

- **Blog md <800 words:** 0 — good.
- **Product descriptions:** Some have empty headings and <br/> filler — could be considered thin? But descriptionHtml is rich (multiple paragraphs, lists).
- **Category pages:** Product grids with short intro — not thin, but could benefit from more unique intro text per category (currently category pages have H1 + product grid + maybe intro? Check category template).
- **Guides:** Each guide has intro paragraphs, groups, FAQs — not thin.

**Action:** No immediate thin content, but monitor for future.

### Pages Lacking Contextual Internal Links

- **Blog articles:** Have product grid (3) and related articles (2-3) but lack inline contextual links within body copy (e.g., "realistic-skin tutorials to relevant skin-texture brushes" should be inline, not just grid). Currently some articles have inline links like `[Portrait Skin Brushes](/products/portrait-skin-brushes-procreate/)` but not consistently.
- **Product pages:** Have related products (3) and category link, but lack links to relevant articles that mention product (reverse index).
- **Category pages:** Product grid only, no links to relevant guides or articles.
- **Guides:** Product grids per group, cross-links to other guides, but no links to blog articles.

**Action:** Implement internal-linking engine with relevance mapping.

### Content Opportunities & Cannibalization Warnings

- **Existing coverage:** 18 articles covering brush buying guides, tutorials, technical.
- **Content gaps from roadmap:** 20 new articles identified, including:
  - 10 Procreate Mistakes Every Beginner Makes (orphaned draft exists)
  - Procreate Layers Explained (orphaned draft exists)
  - Essential Procreate Shortcuts & Gestures (missing, broken link target)
  - How to Organize Your Procreate Brushes (missing)
  - Your First 30 Days in Procreate: Practice Plan (missing, broken link target)
  - How to Shade a Face in Procreate (orphaned draft exists)
  - How to Paint Eyes, Portrait Lighting, Color Mixing, Paint Lips, Portrait Practice, Line Art Tutorial (orphaned draft exists), Blend Modes, Texture Techniques, Brush Settings, Share Art, Digital vs Traditional, Art Portfolio, Time-Lapse, Student Budget
- **Cannibalization risk:**
  - `how-to-create-realistic-skin-in-procreate` vs `how-to-create-realistic-skin-texture-in-procreate` — overlapping intent, need distinct primary keywords and cross-linking.
  - `best-procreate-brushes-for-line-art` vs future `procreate-line-art-tutorial` — one is buying guide, one is tutorial, distinct intent, but need to ensure titles/descriptions differentiate.
- **Opportunity records:** Not yet created in structured JSON — need to create `data/content_opportunities.json` with required fields per brief section 8.

**Action:** Create opportunity records, check existing coverage before publishing, ensure distinct intent.

### Pinterest

- **Feed:** 47 paid products, fields present, destination URLs canonical https, prices real.
- **Recommendations:** Not yet created — need `data/pinterest_recommendations.json` for selected products/articles with Pinterest title/desc, board, image concept, cluster relationship.

---

## Monitoring Dashboard Proposal

**Option 1 (recommended for static site):** Exportable report via `tools/seo_report.py` generating:
- JSON: `reports/seo-report-2026-09-19.json` with all metrics above
- Markdown: `docs/seo-audit/07-monitoring-report.md` (this file)
- CSV: `reports/seo-issues.csv` with prioritized issues

**Option 2 (optional):** Lightweight internal HTML dashboard at `/reports/` or `/tools/` that reads `search-index.js` and product data client-side, shows issues, noindex, no external dependencies. Only if platform can support safely.

**Avoid unnecessary dependencies.**

---

## Next Steps for Monitoring

1. Implement `tools/seo_report.py` with checks for:
   - Missing/duplicate/invalid metadata
   - Missing canonical
   - Missing/suspicious alt
   - Broken internal links
   - Orphan pages (incoming <3)
   - Schema validation (presence of required types per template)
   - Thin content (<500 words or low text ratio)
   - Pages lacking contextual internal links
   - Content opportunities and cannibalization warnings
2. Run after each build, output to `reports/` and `docs/seo-audit/`.
3. Integrate into CI (optional) — fail build if critical issues (broken links, missing canonical, duplicate titles).
4. For dashboard, if feasible, generate static HTML report with noindex.

---

**End of monitoring report.**
