# DigiKitPro — Metadata / Schema / Internal-Linking Gap Report (2026-09-19)

---

## 4.1 Meta Titles

**Current implementation:** `tools/core.py:head()` generates `<title>{esc(title)}</title>` from page-specific title passed by each builder. `seo_engine.py` generates `seoTitle` for products capped at 70 chars with `| DigiKitPro` suffix. Blog articles generate SEO title from frontmatter title + `| DigiKitPro`, trimmed to 65 chars with fallback logic (split at " (" or ":" or " for ").

**Baseline sample:**
- Homepage: `DigiKitPro | Procreate Brushes for iPad Artists | Instant Download` (from pages_main.py)
- Product: `Portrait Skin Brushes for Procreate: 19 Realistic Brushes | DigiKitPro` (68 chars, unique)
- Blog: `How to Paint Realistic Skin in Procreate: A Layered Workflow | DigiKitPro` (unique)
- Category: `Procreate Portrait Brushes | DigiKitPro` (unique)
- Guides: `Procreate Starter Kits for Beginners | DigiKitPro` (unique)

**Gaps:**
- No duplicate titles found (verified via audit script — 0 duplicate titles across all index.html).
- 4 orphaned blog drafts have titles that overlap with existing content roadmap but are not in sitemap — if published, need unique titles.
- Title length: house style allows 70 chars, slightly over generic 60, but consistent across catalog. Validate no title >70.
- Missing: No dynamic fallback rule documented for missing seoTitle — seo_engine fills gaps, but head() does not have fallback if title missing. Should define deterministic fallback: `name + category + | DigiKitPro` for products, `title + | DigiKitPro` for articles, with length validation.

**Recommendation:** Document fallback rules, add validation in verify.py to fail if title missing, duplicated, overlong (>70), or suspicious (e.g., contains "lorem", "test").

---

## 4.2 Meta Descriptions

**Current:** `seoDesc` for products capped at 165 chars, generated from first sentence + category benefit + price. Blog descriptions from frontmatter `description` (150-160 chars). All pages have `<meta name="description">`.

**Sample:**
- Product: `19 professional Procreate skin brushes for realistic pores, freckles, wrinkles and textured blending. Instant .brushset download for iPad, $5.00.` (unique)
- Blog: `Learn how to paint realistic skin in Procreate with a repeatable sequence for values, undertones, soft edges, texture, and restrained highlights.` (unique)

**Gaps:**
- No duplicate descriptions (0 duplicates found).
- No missing descriptions (all products have seoDesc via seo_engine).
- Length: 165 cap is slightly over 155-160, but matches existing. Should keep but document.
- Missing: No validation for overlong (>165) or suspicious (keyword list) descriptions.
- Orphaned drafts have descriptions but not in sitemap — if published, need to ensure unique.

**Recommendation:** Same as titles — add validation, fallback: for products, use `short` + assets + price; for articles, use first 150 chars of body; for categories, use category-specific benefit sentence.

---

## 4.3 Canonical URLs

**Current:** Every page has `<link rel="canonical" href="https://digikitpro.shop/...">` self-referential, absolute, https, no www, no index.html suffix, no params. Generated via `absurl()` helper.

**Sample:**
- Product: `https://digikitpro.shop/products/portrait-skin-brushes-procreate/`
- Blog: `https://digikitpro.shop/blog/how-to-create-realistic-skin-in-procreate/`
- Category: `https://digikitpro.shop/category/portrait/`

**Gaps:**
- No mismatched canonical vs file location (verify.py checks 0 mismatched).
- Search, thank-you, 404 have self-canonical but are noindex — correct, they canonicalize param variants to clean URL.
- No duplicate URL variants in sitemap (0 http, 0 github.io, 0 index.html).
- Missing: No canonical for paginated or filtered views (no pagination currently, JS filters use data attributes, not URLs — good).
- Risk: If GitHub Pages Enforce HTTPS off, http URLs serve same canonical https — Google reports "Alternate page with proper canonical tag" — expected, but should be fixed server-side.

**Recommendation:** Keep self-canonical, ensure all future pages follow same pattern. Document that search.html?q= and thank-you.html?lead= canonicalize to clean version.

---

## 4.4 Open Graph & Twitter/X

**Current:** All pages have OG and Twitter meta via `head()`:
- `og:type` = website, product, or article
- `og:site_name` = DigiKitPro
- `og:title` = same as SEO title
- `og:description` = same as meta description
- `og:url` = canonical
- `og:image` = product card or main image absolute URL, or og-cover.jpg fallback (1200x630)
- `og:image:width`, `og:image:height`, `og:image:alt`
- `og:locale` = en_US + alternates es_ES, fr_FR, de_DE, it_IT, pt_BR, nl_NL
- `og:see_also` = Pinterest profile
- `pinterest-rich-pin=true`
- `twitter:card` = summary_large_image
- `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`

**Gaps:**
- OG image dimensions: For product pages, og:image is card image (750w) but width/height declared as actual cardW/cardH? Check pages_product.py gallery_html: og_image passed as main image? Actually head() gets og_image param from builder — for product pages, gallery_html returns main image URL as og? Let's check: pages_product.py builds og_img as main image absolute URL, but card image used for pin? Need to verify — sample product og:image was main image? In sample we saw og:image? Actually earlier sample product page had og:image? We didn't check, but we saw og:title exists. Need to verify og:image width/height matches actual.
- Orphaned drafts: og:image uses card image (750w) but declares 1200x630 — mismatch (H-01).
- No `twitter:site` or `twitter:creator` — not needed unless Twitter profile exists.
- No `og:locale:alternate` for all languages? Currently 6 alternates, matches LANGUAGES.

**Recommendation:** Ensure og:image width/height always reflect actual file dimensions from products.json. Add validation.

---

## 4.5 H1/H2 Structure

**Current:** Every content page has exactly one H1 (verified by verify.py: "every content page has exactly one h1 — 0" failures). H2s used for sections.

**Sample:**
- Homepage H1: `Procreate Brushes for iPad Artists` (1 H1, verified)
- Product: H1 = product name
- Blog: H1 = article title
- Category: H1 = category name

**Gaps:**
- Product descriptionHtml contains H3s (demoted from H2) but may have empty H3s with <br/> (H-02).
- No automated H2/H3 hierarchy validation (e.g., H3 without parent H2).
- Blog markdown uses ## for H2, ### for FAQ questions — correct.

**Recommendation:** Clean empty headings, add hierarchy validation in verify.py.

---

## 4.6 Robots Directives

**Current:**
- Indexable pages: `<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">` + same for googlebot.
- Non-indexable: search.html, thank-you.html, 404.html = `noindex, follow` (both robots and googlebot agree — fixed in SEO-CANONICAL-FIX).
- robots.txt allows all, lists 3 sitemaps.

**Gaps:**
- No accidental noindex on important pages (verified).
- Search param variants correctly noindex via canonical + meta.
- No `noindex` on product, blog, category, guides — good.

**Recommendation:** Keep. Document robots fallback rule.

---

## 4.7 Breadcrumb Data

**Current:** Visible breadcrumbs via `crumbs()` helper + BreadcrumbList schema.

**Sample product breadcrumb:**
- Home (/) → Products (/products.html) → Category (/category/skin-texture/) → Product

**Sample blog breadcrumb:**
- Home → Blog → Article

**Gaps:**
- Some static pages (about, faq, etc.) may not have BreadcrumbList schema — need to verify pages_misc.py adds breadcrumb schema for all.
- Breadcrumb URLs are absolute via absurl() — correct.

**Recommendation:** Ensure BreadcrumbList schema on all indexable pages, not just product/blog/category.

---

## 4.8 Structured Data

**Current schemas per template (from core.py):**

- **Organization:** `@id: https://digikitpro.shop/#org`, name DigiKitPro, url, logo, sameAs (Pinterest, Instagram), contact? Check core.py schema_org() — includes? Need to verify.
- **WebSite:** name, url, potentialAction SearchAction with target `https://digikitpro.shop/search.html?q={search_term_string}`, inLanguage array.
- **BreadcrumbList:** itemListElement with position, name, item URL.
- **Product:** name, image (array of absolute URLs), description (plain text from short or descriptionHtml), brand DigiKitPro, url, contentLocation?, offers: price, priceCurrency USD, availability InStock, url (Payhip or product page). No aggregateRating, no review — correct (do not invent).
- **BlogPosting (Article):** headline, description, image (absolute), datePublished, dateModified, keywords (primary + secondary), author Organization, publisher @id org, mainEntityOfPage, inLanguage en, url.
- **FAQPage:** mainEntity array of Question/Answer — generated from product faqs[] or blog ## FAQ section.
- **HowTo:** name, description, step (HowToStep with position, name, text), totalTime (ISO8601), tool (HowToTool) — for articles flagged howto:true with ## Step sections.
- **ItemList:** For products index, freebies, bundles, categories — itemListElement with position, name, url.

**Gaps:**

- **Organization + WebSite not on all pages:** Homepage has Org + WebSite, but product pages have Product + Breadcrumb + FAQ — missing Org + WebSite? Check sample product page schemas: we found 3 schemas: Product, Breadcrumb, FAQ — no Org/WebSite. Should add Org + WebSite to all pages for consistency and to provide publisher @id reference.
- **Product image array:** Should be absolute URLs, currently uses main image only? Check core.py schema_product() — image field uses `asset_abs()` for main + gallery? Need to verify.
- **Offer price:** Uses float price from products.json, formatted as 2 decimals — correct.
- **FAQPage only when visible FAQs:** Product pages have visible FAQ section? Check product page template — does it render faqs[] as visible HTML? Yes, product page has FAQ section if faqs exist. Blog FAQ section is visible as ## FAQ with ### questions — matches schema.
- **HowTo validation:** HowTo steps extracted from ## Step headings — need to ensure visible steps match schema.
- **No Article schema on guides?** Guides are buyer guides, not blog — they have Breadcrumb + FAQ, but could benefit from Article or Buyer's Guide schema? Currently they use Breadcrumb only? Check guides/index.html sample — we saw only BreadcrumbList schema in head. Should add Article or ItemList?
- **Image sitemap vs schema:** Product schema image should match sitemap-images.xml image — currently both use main image, but sitemap has 173 images (all gallery), schema may have only main — could add all gallery images to schema image array for richer results.

**Recommendation:**
- Add Organization + WebSite schemas to all indexable pages (not just homepage).
- Ensure Product schema image array includes all gallery images (full-size, not card/thumb).
- Validate FAQPage only when visible FAQ present (currently does).
- Ensure HowTo totalTime is valid ISO8601 (PT90M etc.).
- Add BreadcrumbList to all pages.

---

## 4.9 Internal Linking

**Current:**
- **Navigation:** Header + footer + mobile nav provide site-wide links to main sections.
- **Homepage:** Links to 4 popular products, 2 ebooks, bundle ladder (4 bundles), master library, free products, 3 guides, articles.
- **Product pages:** Related products (3), category link, breadcrumb, footer.
- **Blog:** Tools mentioned (product grid from frontmatter products[]), related articles (from frontmatter related[]), breadcrumb, share buttons.
- **Category:** Product grid (all products in category), breadcrumb.
- **Guides:** Product grids per group (from hardcoded slugs), cross-links to other guides, breadcrumb, FAQ internal anchors? Guides have comparison table linking to products.
- **Seasonal:** Product grid for seasonal products.
- **Footer:** Links to all categories, guides, articles, legal, partner.

**Gaps:**
- **Orphan-page detection:** No automated detection — seasonal hubs only linked from footer and maybe homepage? Actually homepage does not link to seasonal hubs directly, only footer. Could be considered low internal link equity.
- **Contextual linking:** Brief requires contextual, limited internal links among products, articles, categories, helpful resources with descriptive anchor text, avoiding boilerplate repetition. Current related links are somewhat boilerplate (related[] from products.json, related[] from blog frontmatter) — not fully contextual within body copy.
- **Examples from brief:**
  - Realistic-skin tutorials → skin-texture brushes: Currently blog `how-to-create-realistic-skin-in-procreate` links to portrait-skin-brushes-procreate and portrait-mastery-kit via "Tools mentioned" grid, not within body copy. Could add contextual inline links.
  - Line-art tutorials → liner brushes: `best-procreate-brushes-for-line-art` links to free-fine-liner, essential-line-art-sketch-kit, liner-marker-studio — via product grid, not inline.
  - Beginner guides → free Starter Guide: Some beginner articles link to free packs via product grid, but not always inline.
  - Portrait workflow → Ultimate Portrait Mastery Bundle: `procreate-portrait-workflow` links to portrait-mastery-kit, starter-guide, portrait-skin-brushes — but not explicitly Ultimate bundle? Check frontmatter products[] includes? It includes portrait-mastery-kit, starter-guide, portrait-skin-brushes, ultimate bundle? Need to verify.
- **Anchor text:** Product card titles are product names — descriptive. Category links are category names — good. But body copy internal links use generic? Check blog markdown: e.g., `[Portrait Skin Brushes](/products/portrait-skin-brushes-procreate/)` — anchor text is product name, good.
- **Max link density:** No rule defined, no validation.
- **Orphan pages:** 4 orphaned drafts have no incoming links from sitemap pages (since not in sitemap), but they are linked from each other? Actually procreate-mistakes-beginners links to non-existent articles, so broken.
- **Manual overrides:** No system for manual overrides yet.

**Recommendation:**
- Implement internal-linking engine with rules:
  - Relevance: Map article topics to product categories (e.g., skin texture article → skin-texture category + portrait-skin-brushes product).
  - Max density: e.g., max 3 contextual product links per article body + 1 category link + product grid (3) = total 7, avoid boilerplate repetition.
  - Orphan detection: Weekly report of pages with <3 incoming internal links (excluding nav/footer).
  - Manual overrides: Frontmatter `products[]` and `related[]` remain manual overrides, but engine can suggest additional contextual links.
  - Anchor text: Use descriptive, not "click here" or "this kit" — use product name or benefit phrase.

---

## 4.10 Product Feed & Pinterest

**Current:** pinterest-feed.xml and .csv with 47 paid products, fields as per Pinterest catalog spec.

**Gaps:**
- Feed includes only paid products (free excluded) — correct per generator (paid only for catalog).
- Price, availability, brand, condition, google_product_category, product_type, item_group_id present.
- Destination URLs are canonical https — good.
- Image_link is main image WebP — Pinterest supports WebP? Yes, but could also provide JPEG fallback? WebP is supported by Pinterest.
- No `g:additional_image_link` — could add gallery images as additional images.
- No `g:custom_label_*` for grouping.
- Feed does not include lifestyle products? Actually includes all paid products regardless of line? Check — discovery.json line lifestyle includes planners, but those are paid and in feed? Sample feed includes planners? Let's check feed for planner — e.g., adhd-planner? That is paid but line lifestyle — is it in feed? Need to verify. The feed generator in pages_misc.py includes all paid products, not filtering by line — so lifestyle products are in feed, which may not be ideal for Pinterest audience (Procreate brushes focus). Could filter to procreate line only for Pinterest catalog? But brief says do not disrupt existing catalog — keep as is, document.
- No validation of feed against Pinterest spec (e.g., price format "5.00 USD" correct, availability "in stock" correct).

**Recommendation:** Keep feed as is, add validation step in verify.py to check required fields present and URLs reachable. For future, consider adding additional_image_link.

---

## 4.11 Image SEO

**Current:**
- Filenames: descriptive, e.g., `portrait-skin-brushes-procreate.webp`, `...-card.webp`, `...-thumb.webp` — good, not keyword stuffed.
- Alt text: descriptive, e.g., "Portrait Skin Brushes for Procreate, product preview artwork" — accurate, not keyword list. Gallery thumbs add "thumbnail" or "preview N thumbnail" — acceptable.
- Dimensions: width/height attributes present on all img tags (verified sample: 0 missing).
- Responsive: srcset with 750w and 1400w variants, sizes attribute `(min-width: 1100px) 350px, ...` — good.
- Format: WebP primary, no JPEG fallback — modern, but consider <picture> for older browsers only if without harming feeds.
- Lazy loading: below-fold images lazy, hero eager with fetchpriority high — good.
- Layout shift: width/height + contain/mat prevents CLS — verified card media framing check passes.
- Decorative images: ba-before/ba-after have meaningful alt, not empty — correct (they are content). No decorative images with empty alt? Need to check — e.g., icons are SVG with aria-hidden true — good.

**Gaps:**
- Alt text for some gallery images is generic "preview N" — could be more descriptive (e.g., "close-up of pore texture brush stroke").
- No explicit `decoding="async"` on all images? Actually sample shows decoding async on all — good.
- No WebP/AVIF with fallback — low risk.
- No intrinsic dimensions for og-cover fallback? og-cover.jpg is 1200x630, but card images 750w have different aspect ratios — OG width/height mismatch noted earlier.

**Recommendation:**
- Improve alt text for new assets to describe actual image content.
- Preserve empty alt for truly decorative images (none currently, but document rule).
- Add validation for alt missing, alt too short (<5 chars), alt keyword stuffed (e.g., contains "Procreate brushes" repeated >2 times).
- Ensure all new images have width/height and srcset.

---

## 4.12 Summary of Gaps

| Area | Status | Gap |
|---|---|---|
| Titles | Good, unique, 0 duplicates | Need fallback rule doc + validation for >70 chars |
| Descriptions | Good, unique, 0 duplicates | Need fallback + validation |
| Canonical | Good, self-consistent, 0 mismatched | Need to ensure Enforce HTTPS toggle on |
| OG/Twitter | Present, but dimension mismatch for orphaned drafts | Fix og:image dimensions to match actual file |
| H1/H2 | 1 H1 per page, verified | Clean empty H3s in product descriptions |
| Robots | Correct index/noindex | None |
| Breadcrumbs | Present, but not on all static pages? | Add BreadcrumbList to all indexable pages |
| Structured data | Product, Breadcrumb, FAQ, BlogPosting, HowTo, ItemList present, but Org/WebSite missing on some pages | Add Org+WebSite to all pages, include all gallery images in Product image array |
| Internal linking | Related products, related articles, nav/footer present, but not fully contextual inline | Implement contextual linking engine with relevance rules, max density, orphan detection |
| Pinterest feed | Valid, 47 products, required fields present | Add additional_image_link, validate feed |
| Image SEO | Good, WebP, srcset, width/height, alt descriptive | Improve alt for gallery, validate alt, ensure OG dimensions correct |

---

**Next:** Assumptions and manual review in 05.
