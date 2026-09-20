# DigiKitPro — Proposed SEO-Engine Architecture & Implementation Plan (Phase 1 Audit Deliverable)

**Date:** 2026-09-19  
**Status:** Awaiting approval (per brief section 4)  
**Branch:** arena/01a0bbfa-digikitpro

---

## 6.1 Goals (from brief)

- Build scalable, maintainable, template-driven SEO system — not mass-produced blog posts or speculative changes.
- Increase qualified organic traffic and convert relevant visitors (new digital artists, Procreate beginners, students, digital portrait artists).
- Improve visitor experience as well as search visibility.
- Preserve all existing URLs, redirects, canonical behavior, analytics, tracking, structured-commerce data, Pinterest catalog.
- Use reversible changes and maintain change log.

---

## 6.2 Current SEO Engine (Baseline)

**Existing components:**

1. **Config & Head Builder** (`tools/core.py`):
   - `SITE_URL`, `SITE_NAME`, `TAGLINE`, verification tokens, GA ID, Pinterest profile, SOCIAL, LANGUAGES, GEO_META.
   - `head(title, desc, canonical, depth, schemas, og_image, page_type, preload, ctx, robots)` — generates full head with title, desc, canonical, verification meta, theme-color, robots, googlebot, OG, Twitter, geo, locales, GA gtag, Pinterest Tag (dormant), preconnect/dns-prefetch, font preload, CSS, RSS, `window.DKP` context, JS includes, JSON-LD schemas.
   - `_GITHUB_KILL` JS guard for duplicate variants.
   - Schema builders: `schema_org()`, `schema_website()`, `schema_itemlist()`, `schema_breadcrumb()`, `schema_article()`, `schema_howto()`, `schema_faq()`.

2. **SEO Copy Engine** (`tools/seo_engine.py`):
   - Deterministic offline, no API.
   - Generates `keywords`, `tags`, `seoTitle` (70 chars), `seoDesc` (165 chars), `short` (155), `alt` (110) from verified product info.
   - Rules: hand-written copy never overwritten unless `auto:true` or missing/empty/boilerplate. Uses category seeds, name tokens, assets, description tokens, deduped, capped.
   - Called by `payhip_sync.py` for new products.

3. **Product Data** (`data/products.json`):
   - Single source of truth — 51 products, each with name, slug, category, price, assets, short, descriptionHtml, included, features, technical, requirements, perfectFor, bundleContents, faqs, tags, related, payhipUrl, images, seoTitle, seoDesc, featured, free, alt, keywords, spotPitch.

4. **Merchandising Model** (`data/discovery.json`):
   - Separate from products.json so sync never clobbers.
   - Tier, line, craft, improve, level, style, stage, priority, aggregate.

5. **Page Builders** (`pages_*.py`):
   - Template-driven, each builder calls `head()` + `header()` + content + `footer()` + `write()`.
   - Product pages: gallery, buy CTA, description, included, features, technical, requirements, perfectFor, bundleContents, FAQ, related products, newsletter, share buttons, pin buttons.
   - Blog: loads md frontmatter, renders markdown to HTML, extracts FAQ and HowTo steps, builds tools mentioned grid, related articles, share row, newsletter.

6. **Verification** (`tools/verify.py`):
   - 88 checks (currently 87 passing due to 2 broken links) — workflows, CNAME, SITE_URL, robots.txt, sitemap.xml/txt/images, github.io refs, canonicals, broken internal links, PDP Payhip URL, static pages existence, H1 count, finder removal, hero CTAs, homepage section order, ladder completeness, honesty checks, IndexNow, products.json/discovery.json unmodified, guides, partner, card framing, ebooks CTA uncrop.

**Gaps vs brief requirements:**

- Brief section 5 requires reusable, template-driven functionality for every indexable page with editable values for SEO title, meta description, canonical, OG title/desc/URL/image, Twitter, robots, breadcrumb, with deterministic fallback rules and validation. Currently exists for products via seo_engine, but not for blog, category, guides, static pages — those use hardcoded or frontmatter values without centralized fallback/validation.
- Brief section 6 Product SEO engine: exists, but needs to ensure visitor-facing H1, accurate image alt, Product + Breadcrumb structured data, relevant category/article/related-product links — partially exists, needs improvement for H1 (already product name) and alt (needs more descriptive).
- Brief section 7 Internal-linking engine: related products/articles exist but are manual, not contextual engine with relevance rules, max density, orphan detection, manual overrides.
- Brief section 10 Image SEO: exists (WebP, srcset, width/height, lazy), but alt improvements, filename rules, decorative handling, WebP/AVIF decision, CLS need documentation.
- Brief section 11 Structured data: exists, but Org + WebSite not on all pages, Product image array could include gallery, guides could benefit from more schema.
- Brief section 12 Technical SEO: sitemap, robots, canonical, HTTPS guard, 404, noindex, crawlability, pagination (none), indexability of search/filter/thin pages — mostly good, but HTTPS toggle needs manual fix.
- Brief section 13 Pinterest connection: feed exists, but no recommendations system for Pinterest title/desc/board/image concept per cluster.
- Brief section 14 Monitoring dashboard: does not exist — need lightweight internal report or exportable.
- Brief section 8 & 9 Topical architecture & articles: roadmap exists (20 articles), but only 18 published, 4 orphaned drafts, no opportunity record system with required fields.

---

## 6.3 Proposed SEO-Engine Architecture

### 6.3.1 Core Principles

- **Template-driven, not manual:** All SEO values generated via centralized engine with editable overrides.
- **Deterministic fallback:** Every indexable page type has fallback rules for missing/duplicated/overlong/suspicious values.
- **Validation:** Missing, duplicate, invalid metadata, alt, canonical, schema, broken links, orphan pages, thin content, cannibalization warnings.
- **Reversible & logged:** All changes via `tools/` generators, never manual HTML edits, change log in `docs/seo-audit/CHANGELOG.md`.
- **Preserve existing:** Product URLs, article URLs, category URLs, redirects, canonical behavior, analytics, tracking, structured-commerce data, Pinterest catalog must remain intact.
- **No fabrication:** Never create fake reviews, ratings, offers, prices, availability, statistics, credentials, search demand.
- **No keyword stuffing, doorway, hidden text, thin mass content.**

### 6.3.2 Components

#### A. SEO Metadata Engine (New: `tools/seo_metadata.py`)

**Purpose:** Centralized SEO metadata generation and validation for all indexable page types.

**Supports per page:**
- SEO title (editable, fallback, length validation 60-70, uniqueness check)
- Meta description (editable, fallback, length 150-165, uniqueness)
- Canonical URL (deterministic from file path, always https://digikitpro.shop, self-consistent, no params)
- OG title, description, URL, image (with width/height from actual file)
- Twitter card, title, description, image
- Robots directives (index/follow vs noindex/follow with rules)
- Breadcrumb data (visible + schema)
- Validation: missing, duplicated, overlong, suspicious (e.g., contains "lorem", "test", "placeholder", keyword stuffing patterns)

**Fallback rules (deterministic, documented):**

- **Product:**
  - seoTitle: `products.json:seoTitle` if present and valid, else `name + ": " + assets + " | DigiKitPro"` trimmed to 70.
  - seoDesc: `seoDesc` if present, else `short` + price + " Instant download." trimmed to 165.
  - canonical: `https://digikitpro.shop/products/<slug>/`
  - og_image: main image absolute URL with width/height from images.fullW/fullH.
  - robots: `index, follow` unless product is comingSoon? Then noindex? Currently all index.
  - breadcrumb: Home → Products → Category → Product.

- **Blog article:**
  - seoTitle: frontmatter title + " | DigiKitPro" trimmed to 65 with split logic (existing).
  - seoDesc: frontmatter description, else first 150 chars of body plain text.
  - canonical: `https://digikitpro.shop/blog/<slug>/`
  - og_image: primary product card image or og-cover.jpg with actual dimensions.
  - robots: index,follow.
  - breadcrumb: Home → Blog → Article.

- **Category:**
  - seoTitle: `CATEGORY_SEO_TITLES[slug]` or `f"Procreate {Category} Brushes | DigiKitPro"`
  - seoDesc: category-specific benefit sentence + product count + "Instant download."
  - canonical: `https://digikitpro.shop/category/<slug>/`
  - og_image: first product in category main image or og-cover.
  - robots: index,follow.
  - breadcrumb: Home → Category.

- **Guides:**
  - seoTitle: from `pages_guides.py` GUIDE_DEFS seo_title.
  - seoDesc: from GUIDE_DEFS seo_desc.
  - canonical: `https://digikitpro.shop/guides/<slug>/` or `/guides/` for index.
  - og_image: og-cover or first product in guide.
  - robots: index,follow.
  - breadcrumb: Home → Buyer Guides → Guide.

- **Static (about, faq, etc.):**
  - seoTitle: hardcoded per page builder, but via engine with fallback `H1 + | DigiKitPro`.
  - seoDesc: hardcoded, fallback first paragraph.
  - canonical: `https://digikitpro.shop/<page>.html` or `/<page>/` for directory URLs.
  - robots: index,follow.

- **Search, thank-you, 404:**
  - robots: noindex,follow (already).
  - canonical: self, but noindex ensures param variants not indexed.
  - No OG? Currently has OG but could be minimal.

**Validation:**
- Missing: title, desc, canonical, og:image, breadcrumb.
- Duplicate: title, desc across site (check via dict).
- Overlong: title >70, desc >165, og:title >70, etc.
- Suspicious: contains "lorem", "placeholder", "test", repeated keyword >3 times, empty alt, etc.
- Report via `tools/verify.py` or new `tools/seo_report.py`.

#### B. Product SEO Engine (Enhanced: `tools/seo_engine.py` + `pages_product.py`)

**Already exists, enhance:**

- Ensure visitor-facing H1 = product name (already).
- Ensure accurate image alt: alt from products.json alt field, which should describe actual image content, not keyword list. Add rule: alt must describe image, not just product name + "preview". For new products, alt = `name + ": " + specific visual description` e.g., "close-up of pore texture brush stroke on cheek".
- Ensure Product + Breadcrumb structured data: Product schema with real values only, no fake reviews/ratings/offers. Image array includes all gallery full-size images (not just main). Offer uses real price, currency USD, availability InStock, url Payhip.
- Ensure relevant category, article, related-product links: category link from product category, related products from related[] or same category fallback, articles from blog frontmatter products[] reverse index (which articles mention this product).
- Related-product recommendations: existing related[] is manual, but could be enhanced with same-category + same-tier + same-craft logic from discovery.json, with manual override.
- Preserve product URLs exactly.

#### C. Internal-Linking Engine (New: `tools/internal_linking.py`)

**Purpose:** Contextual, limited internal links among products, articles, categories, helpful resources with descriptive anchor text, avoiding boilerplate repetition.

**Rules:**

- **Relevance mapping:**
  - Article topic → product category: e.g., realistic-skin tutorial → skin-texture category + portrait-skin-brushes product + portrait-mastery-kit bundle.
  - Line-art tutorial → line-art category + essential-line-art-sketch-kit + liner-marker-studio.
  - Beginner guide → freebies (free-fine-liner, free-color-vault) + Procreate Starter Guide ebook.
  - Portrait workflow → Ultimate Portrait Mastery Bundle when genuinely relevant (workflow covers line, skin, hair, glitter).
  - Define mapping in `data/internal_linking.json` or within `discovery.json` craft/improve fields.

- **Max link density:**
  - Per article body: max 3 contextual product links + 1 category link + product grid (3) + related articles (2-3) = max 7-8 internal links beyond nav/footer.
  - Per product page: related products (3) + category (1) + articles that mention product (up to 3) + breadcrumb = limited.
  - Avoid boilerplate repetition: same anchor text not repeated >2 times per page.

- **Orphan-page detection:**
  - Pages with <3 incoming internal links (excluding nav/footer) flagged as orphan candidates.
  - Seasonal hubs, guides, partner currently only linked from footer — need at least 1 contextual link from homepage or relevant article.

- **Manual overrides:**
  - Blog frontmatter `products[]` and `related[]` remain manual overrides.
  - Product `related[]` remains manual.
  - Guides `groups[].slugs` remain manual.
  - Engine suggests additional links but does not auto-insert without approval.

- **Anchor text:**
  - Use descriptive: product name or benefit phrase, not "click here", "this kit", "learn more".
  - For category: "Procreate skin texture brushes" not just "skin texture".

- **Implementation:**
  - New file `tools/internal_linking.py` with functions to generate suggestions and validate existing links.
  - Integration into `pages_blog.py` and `pages_product.py` to render contextual inline links where placeholder exists (e.g., `{{products}}` marker already exists in blog body for product grid, but could add inline links via markdown shortcodes).
  - Report via `tools/seo_report.py`.

#### D. Topical Architecture & Content Opportunities (New: `data/content_opportunities.json` + `tools/content_opportunities.py`)

**Purpose:** Build topical authority around Procreate digital art with clusters, prevent cannibalization, document opportunities.

**Clusters (from brief):**
- Procreate beginners: installation, layers, canvas size, DPI, shortcuts, brush basics.
- Portrait painting: portraits, realistic skin, hair, face shading, lighting, workflow.
- Procreate brushes: selection, skin texture, hair, line art, watercolor, texture.
- Student learning: exercises, practice ideas, portrait practice, digital-art workflows.

**Existing coverage (18 articles):**
- Brush buying guides: anime, beginners, line art, portraits
- Tutorials: realistic skin, skin texture, watercolor, hair, traditional look, blending, portrait workflow, tattoo, Christmas, Halloween
- Technical: install brushes, canvas size/DPI, stamp vs painting

**Opportunity record fields (per brief section 8):**
- Topic and primary keyword
- Search intent and target audience
- Related terms and common questions
- Existing competing coverage and content gap
- Relevant products and existing DigiKitPro pages
- Internal-link opportunities
- Pinterest angle
- Priority, rationale, estimated effort, risk

**Implementation:**
- Create `data/content_opportunities.json` with 20 opportunities from SEO-CONTENT-ROADMAP-2026.md, each with required fields.
- Before proposing/generating content, check existing pages to prevent cannibalization (via primary keyword and slug overlap check).
- Use current search results and first-party data where accessible — treat third-party volume as directional.
- Do not publish hundreds of pages or target same intent with multiple URLs.

#### E. Article Standards (Enforced via `pages_blog.py` + frontmatter validation)

**Each article must have:**
- One clear H1 (title) and logical H2/H3 hierarchy (## for H2, ### for H3)
- Accurate, useful, beginner-friendly instruction
- Practical examples and steps (not filler)
- Relevant images with accurate alt text (from product images or custom)
- Contextual internal links and product recommendations (via engine)
- Related articles (from frontmatter related[])
- FAQ content only where genuinely helps reader (## FAQ with ### questions)
- SEO title, meta description, canonical, Article schema (BlogPosting)
- Human-readable, non-repetitive, evidence-based where claims made, free of filler.

**Enforcement:**
- Frontmatter validation in `pages_blog.py:load_articles()` — require title, slug, description, date, primary_keyword, search_intent, target_audience.
- Markdown structure validation: exactly 0 H1 in body (title from frontmatter), at least 2 H2s, no empty headings.
- Image alt validation.
- Internal link validation (no broken links).
- FAQ extraction and schema only if FAQ section exists and visible.

#### F. Image SEO (Enhanced: `tools/core.py` + `pages_product.py` + `pages_blog.py`)

**Improvements without replacing artwork unnecessarily:**

- Descriptive filenames for new or safely renameable assets (e.g., `portrait-skin-brushes-procreate.webp` good, keep).
- Alt text describing actual image, not keyword list (enhance for new assets).
- Preserve meaningful empty alt for decorative images (none currently, but document).
- Add intrinsic dimensions and responsive behavior (already width/height + srcset + sizes).
- Use lazy loading below fold (already) and eager for hero.
- Use WebP/AVIF only where supported without harming quality or feeds (currently WebP only, Pinterest supports WebP, keep).
- Reduce layout shift and avoid large downloads (already width/height, card variants 750w, main 1400w, thumb).

**New validation:**
- Check for missing width/height, missing alt, alt too short, alt keyword stuffed.
- Check for oversized images (e.g., >2000w or >500KB) that could be optimized.
- Check for OG image dimensions matching actual file.

#### G. Structured Data (Enhanced: `tools/core.py`)

**Audit and implement valid Schema.org for applicable templates:**

- **Organization:** Present on all pages (currently only homepage? Need to add to all). Include name, url, logo, sameAs (Pinterest, Instagram).
- **WebSite:** Present on all pages with SearchAction.
- **BreadcrumbList:** Present on all indexable pages (currently product, blog, category, guides, but need to verify static pages).
- **Product:** Real values only, image array includes all gallery images, offers with real price, no fake reviews/ratings.
- **Article (BlogPosting):** Headline, description, image, datePublished, dateModified, keywords, author Org, publisher @id org, mainEntityOfPage, inLanguage, url.
- **FAQPage:** Only when visible page contains genuine, useful FAQs (product faqs[] or blog FAQ section).
- **HowTo:** Only for articles flagged howto:true with steps.
- **ItemList:** For products index, freebies, bundles, categories, guides index.

**Validation:**
- Syntax valid JSON-LD, required properties present, no unsupported claims, schema agrees with visible content.
- Use `tools/verify.py` to check schema types per template.

#### H. Technical SEO & Indexation (Enhanced: `tools/pages_misc.py` + `tools/core.py`)

**Verify and fix where approved:**

- XML sitemap validity and inclusion of canonical indexable URLs only (currently 99, excludes search, thank-you, 404 — correct).
- robots.txt correctness (currently allows all, lists 3 sitemaps — correct).
- Canonical URLs and duplicate URL control (self-canonical, JS guard for http/www/index.html/github.io, Netlify redirects).
- HTTPS and redirect behavior (requires Enforce HTTPS toggle — owner manual).
- 404 handling (404.html exists, noindex, custom content, includes header/footer).
- Accidental noindex (none).
- Crawlability of important pages (all important pages linked from nav/footer/homepage).
- Pagination and parameter handling (no pagination, search and thank-you param variants canonicalize and noindex — correct).
- Indexability of search, filter, thin pages (search noindex, filters JS not URL-based, thin pages? No thin pages observed).

**Do not change URLs for SEO convenience. If URL change ever proposed, provide migration plan with redirects and explicit approval.**

#### I. Pinterest Connection (Preserve + Recommendations)

**Do not modify or disrupt existing Pinterest catalog/feed.**

**For selected products and articles, generate recommendations (not automatic mass publishing) for:**

- Pinterest title and description (from seoTitle/seoDesc but tailored for Pinterest, e.g., more visual, save-worthy)
- Pin topic and target board (e.g., "Procreate portrait tutorials", "Procreate brushes for beginners")
- Destination URL (canonical)
- Image concept (e.g., before/after, step-by-step, palette swatches, close-up texture)
- Relationship to relevant search/content cluster (beginner, portrait, brushes, student)

**Implementation:**
- New file `data/pinterest_recommendations.json` with recommendations for top products and articles.
- Verify destination URLs, product identifiers, prices, catalog fields remain intact after any SEO changes.
- No auto-publishing — recommendations only.

#### J. Lightweight Monitoring Dashboard (New: `tools/seo_report.py` + optional `reports/`)

**If supported by current architecture, add lightweight internal report showing:**

- Missing, duplicate, invalid metadata (title, desc, canonical, og, twitter, robots)
- Missing canonical tags
- Missing or suspicious alt text
- Broken internal links
- Orphan pages
- Schema validation issues
- Thin-content candidates (e.g., <500 words, or low text-to-HTML ratio)
- Pages lacking contextual internal links
- Content opportunities and cannibalization warnings

**Implementation options:**

- **Option 1 (preferred for static site):** Exportable report — `tools/seo_report.py` generates JSON/CSV/Markdown in `reports/` or `docs/seo-audit/` with above metrics. No new dependencies, runs via `python3 tools/seo_report.py` after build. Could be included in CI.
- **Option 2 (if feasible):** Lightweight internal dashboard — e.g., `/tools/` or `/reports/` HTML page that reads `search-index.js` and product data and shows issues client-side, only visible if accessed directly (noindex). Avoid unnecessary dependencies, do not add if platform cannot support safely.

**Avoid unnecessary dependencies and do not add dashboard if platform cannot support safely; provide exportable report instead.**

---

## 6.4 Implementation Order (from brief section 15)

1. **Audit and baseline evidence** — Done in this Phase 1 (docs/seo-audit/01-06).
2. **Present findings, risks, assumptions, architecture for approval** — This document + issue register, etc., awaiting approval gate.
3. **Apply safe technical SEO fixes** — After approval:
   - Remove or convert orphaned blog drafts, fix broken links (C-01)
   - Fix OG image dimensions (H-01)
   - Clean empty headings in product descriptions (H-02)
   - Add BreadcrumbList + Organization + WebSite to all pages (M-06, L-05)
   - Ensure all img have width/height/alt validation
   - Verify HTTPS toggle (C-02) — owner manual
4. **Implement and test metadata/product SEO engine** — Build `seo_metadata.py` with fallback rules and validation, enhance `seo_engine.py` for alt improvements, integrate into page builders.
5. **Improve internal linking** — Build `internal_linking.py` with relevance rules, max density, orphan detection, manual overrides. Update blog and product templates to render contextual inline links.
6. **Implement and validate structured data** — Ensure Org+WebSite on all pages, Product image array includes gallery, guides have appropriate schema.
7. **Improve image SEO and performance** — Alt improvements, OG dimensions fix, validation for missing/suspicious alt, oversized images.
8. **Build content-cluster and opportunity system** — Create `content_opportunities.json` with 20 opportunities from roadmap, each with required fields, cannibalization check.
9. **Research and publish first approved high-priority articles** — Only a small number after opportunity research and approval, per article standards.
10. **Produce Pinterest recommendations without mass automation** — `pinterest_recommendations.json` for selected products/articles.
11. **Add lightweight monitoring/reporting** — `seo_report.py` exportable report, optional dashboard.

---

## 6.5 Testing and Acceptance Criteria (from brief section 16)

After implementation, run existing build, lint, test, deployment checks. Verify in staging or equivalent safe environment before production.

**Confirm that:**

- Homepage, representative product pages, categories, blog, articles render correctly.
- Mobile layouts remain usable.
- Existing product, article, category, Pinterest, and redirect URLs still work (no 404s introduced).
- Sitemap and robots.txt are valid.
- Canonicals are correct and self-consistent.
- Structured data is valid and matches visible content (via validator).
- Metadata is unique for representative page types (no duplicates).
- Product schema contains no fabricated properties (no fake reviews/ratings).
- Analytics, tracking, Pinterest catalog behavior remain intact (GA ID present, DKP context, feed fields).
- No new broken links, noindex mistakes, redirect chains, or material performance regressions introduced.
- Verify.py passes all checks (expected 88 or updated count).

**Record test URLs, results, screenshots or validation output where useful, and unresolved risks.**

---

## 6.6 Files, Templates, Settings to Change (Proposed)

**New files:**
- `tools/seo_metadata.py` — metadata engine with fallback rules and validation
- `tools/internal_linking.py` — internal linking engine with relevance rules
- `tools/seo_report.py` — monitoring report generator
- `tools/content_opportunities.py` — content opportunity management
- `data/content_opportunities.json` — 20 opportunities with required fields
- `data/pinterest_recommendations.json` — Pinterest recommendations
- `data/internal_linking.json` — relevance mapping (optional, could be in discovery.json)
- `docs/seo-audit/CHANGELOG.md` — change log for SEO engine
- `reports/` or `docs/seo-audit/reports/` — exportable reports

**Modified files (existing):**
- `tools/core.py` — head() to use seo_metadata engine, add Org+WebSite to all pages, fix OG dimensions, add breadcrumb schema to all pages
- `tools/seo_engine.py` — enhance alt generation, add validation
- `tools/pages_product.py` — use metadata engine, include gallery images in Product schema image array, render contextual article links
- `tools/pages_blog.py` — use metadata engine, validate frontmatter, render contextual product/category links inline
- `tools/pages_category.py` — use metadata engine
- `tools/pages_guides.py` — use metadata engine, add schema
- `tools/pages_misc.py` — use metadata engine, ensure sitemap includes only canonical indexable URLs, validate Pinterest feed
- `tools/pages_main.py` — use metadata engine
- `tools/verify.py` — add checks for metadata uniqueness, alt validation, schema presence, orphan detection, thin content
- `tools/build.py` — call new engines
- `data/products.json` — clean empty headings in descriptionHtml (if approved)
- `content/blog/*.md` — fix broken internal links, add contextual links (if approved)

**Preserved (no change):**
- All existing product URLs, article URLs, category URLs, redirects, canonical behavior, analytics, tracking, structured-commerce data, Pinterest catalog functionality — unless documented reason and approved.

---

## 6.7 Risks, Limitations, Unavailable Access

- **Risks:** See issue register and assumptions docs.
- **Limitations:** No Search Console, GA4 dashboard, server logs, Pinterest dashboard, Core Web Vitals field data — only site-side implementation.
- **Unavailable access:** GitHub Pages admin (Enforce HTTPS toggle), Payhip dashboard, domain DNS, Pinterest account — require owner.

---

## 6.8 Approval Gate (from brief section 4)

**Separate recommendations into:**

- **Safe fixes:** Low-risk, reversible, template-level improvements — e.g., remove orphaned drafts, fix broken links, OG dimensions, empty headings, add Org+WebSite schema, alt validation.
- **Review required:** Content, product copy, URL behavior, feed behavior, changes with conversion implications — e.g., content gap analysis, internal linking engine, FAQ expansion, alt improvements, Pinterest recommendations.
- **Blocked:** Changes requiring credentials, platform access, external approval, unavailable data — e.g., HTTPS toggle, Search Console Domain property, GA4 data review, Pinterest catalog validation.

**Proceed only with approved or clearly safe fixes.**

---

## 6.9 Next Steps

1. Owner reviews audit deliverables (01-06).
2. Owner approves safe fixes and provides decisions on orphaned drafts, content publishing scope, success metrics.
3. Owner performs manual steps: Enforce HTTPS toggle, Search Console Domain property + sitemap submission, Pinterest catalog validation.
4. Implement safe fixes in order, with change log, testing, and validation.
5. Implement metadata/product SEO engine, internal linking, structured data, image SEO, content clusters, Pinterest recommendations, monitoring — per implementation order, with approval at each stage.

---

**End of proposed architecture.**
