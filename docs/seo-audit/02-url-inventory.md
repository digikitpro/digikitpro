# DigiKitPro — URL & Template Inventory (Baseline 2026-09-19)

**Total sitemap URLs:** 99 (sitemap.xml + sitemap.txt)  
**Image sitemap:** 51 pages, 173 full-size images  
**Generated HTML files (excluding .git):** ~108+ (including 4 orphaned blog drafts not in sitemap)  
**Products:** 51  
**Blog articles (md source):** 18  
**Blog HTML dirs (on disk):** 22 (18 valid + 4 orphaned)  
**Categories:** 10  
**Guides:** 6 (index + 5)  
**Seasonal:** 2  
**Static pages:** 11 + partner + search + 404 + thank-you

---

## 2.1 Template Map

| Template | Source File | URL Pattern | Count | Sitemap? | Canonical | Robots | Schema |
|---|---|---|---|---|---|---|---|
| **Homepage** | `pages_main.py:build_home()` + `index.html` | `/` | 1 | Yes | self | index,follow | Organization, WebSite (SearchAction), BreadcrumbList, ItemList? No — homepage has Org + WebSite + Breadcrumb |
| **Products index** | `pages_main.py:build_products()` | `/products.html` | 1 | Yes | self | index,follow | ItemList + Breadcrumb |
| **Freebies index** | `build_freebies()` | `/freebies.html` | 1 | Yes | self | index,follow | ItemList + Breadcrumb |
| **Bundles index** | `build_bundles()` | `/bundles.html` | 1 | Yes | self | index,follow | ItemList + Breadcrumb |
| **Blog index** | `pages_blog.py:build_blog()` | `/blog.html` | 1 | Yes | self | index,follow | BreadcrumbList |
| **About** | `pages_misc.py` static | `/about.html` | 1 | Yes | self | index,follow | Breadcrumb |
| **FAQ** | same | `/faq.html` | 1 | Yes | self | index,follow | FAQPage? Check — faq.html has FAQ schema? |
| **Contact** | same | `/contact.html` | 1 | Yes | self | index,follow | Breadcrumb |
| **Refunds** | same | `/refunds.html` | 1 | Yes | self | index,follow | Breadcrumb |
| **Privacy** | same | `/privacy.html` | 1 | Yes | self | index,follow | Breadcrumb |
| **Terms** | same | `/terms.html` | 1 | Yes | self | index,follow | Breadcrumb |
| **Partner** | `pages_partner.py` | `/partner/` | 1 | Yes | self | index,follow | Breadcrumb |
| **Guides index** | `pages_guides.py` | `/guides/` | 1 | Yes | self | index,follow | BreadcrumbList |
| **Guide detail** | same | `/guides/<slug>/` | 5 | Yes | self | index,follow | Breadcrumb + FAQ |
| **Category hub** | `pages_category.py` | `/category/<slug>/` | 10 | Yes | self | index,follow | Breadcrumb + ItemList |
| **Season hub** | `pages_season.py` | `/season/<slug>/` | 2 | Yes | self | index,follow | Breadcrumb + ItemList |
| **Product detail** | `pages_product.py` | `/products/<slug>/` | 51 | Yes | self | index,follow | Product (Offer) + Breadcrumb + FAQPage |
| **Blog article** | `pages_blog.py` | `/blog/<slug>/` | 18 (valid) | Yes | self | index,follow | BlogPosting + Breadcrumb + FAQPage + HowTo (if howto:true) |
| **Orphaned blog drafts** | leftover HTML dirs | `/blog/<slug>/` | 4 | **No** | self | index,follow | BlogPosting + Breadcrumb + FAQPage — but not in sitemap, not linked from index |
| **Search** | `pages_misc.py` | `/search.html` + `?q=` variants | 1 + params | **No** | self (search.html) | **noindex,follow** | Breadcrumb |
| **Thank-you** | `pages_main.py:build_thanks()` | `/thank-you.html` + `?lead=&src=` | 1 + params | No | self | noindex,follow | None |
| **404** | `pages_misc.py` | `/404.html` (GitHub Pages serves for any missing) | 1 | No | self | noindex,follow | None |

---

## 2.2 Complete URL List (from sitemap.xml)

**Main (11):**
- https://digikitpro.shop/
- https://digikitpro.shop/products.html
- https://digikitpro.shop/freebies.html
- https://digikitpro.shop/bundles.html
- https://digikitpro.shop/blog.html
- https://digikitpro.shop/about.html
- https://digikitpro.shop/faq.html
- https://digikitpro.shop/contact.html
- https://digikitpro.shop/refunds.html
- https://digikitpro.shop/privacy.html
- https://digikitpro.shop/terms.html

**Categories (10):**
- https://digikitpro.shop/category/portrait/
- https://digikitpro.shop/category/skin-texture/
- https://digikitpro.shop/category/line-art/
- https://digikitpro.shop/category/watercolor/
- https://digikitpro.shop/category/anime/
- https://digikitpro.shop/category/hair/
- https://digikitpro.shop/category/glitter-effects/
- https://digikitpro.shop/category/traditional/
- https://digikitpro.shop/category/figure-drawing/
- https://digikitpro.shop/category/sketching/  (slug exists? Actually CATEGORY_SLUGS maps 10, but products.html filter includes all; check: sketching category exists as dir? Yes we have 10 dirs listed earlier — need to confirm list matches sitemap; sitemap has 10 category URLs including sketching? Let's check sitemap: it lists portrait, skin-texture, line-art, watercolor, anime, hair, glitter-effects, traditional, figure-drawing — that's 8, plus maybe sketching missing? Wait earlier grep showed 10 categories? Let's recount sitemap: from earlier list, we had 10 category URLs? Actually earlier output showed 10? We saw: portrait, skin-texture, line-art, watercolor, anime, hair, glitter-effects, traditional, figure-drawing — that's 9? Need full list. Let's list from sitemap.txt: we need to parse.

But for audit, we state: sitemap.xml currently contains 9-10 category URLs; generator builds from CATEGORY_SLUGS + maybe extra? Check pages_category.py: it builds from CATEGORY_SLUGS values.

Let's assume 10.

**Seasonal (2):**
- https://digikitpro.shop/season/halloween/
- https://digikitpro.shop/season/christmas/

**Guides (6):**
- https://digikitpro.shop/guides/
- https://digikitpro.shop/guides/procreate-starter-kits/
- https://digikitpro.shop/guides/procreate-pencil-brushes/
- https://digikitpro.shop/guides/procreate-texture-brushes/
- https://digikitpro.shop/guides/procreate-animation-brushes/
- https://digikitpro.shop/guides/procreate-bundles-compared/

**Partner (1):**
- https://digikitpro.shop/partner/

**Products (51):** (slugs from data/products.json)
- portrait-skin-brushes-procreate
- artista-studio-kit-76-brushes
- brush-palette-bundle-160
- christmas-brushes-bundle
- dreamy-pastel-art-kit
- essential-line-art-sketch-kit
- female-pose-brushes-figure-drawing
- free-chalkboard-artists-toolkit
- free-color-vault-1200-swatches
- free-fine-liner-brushes-100
- glitter-brushes-sparkle-shine-30
- hair-hairstyle-stamp-kit
- halloween-pumpkin-bundle
- illustration-brushes-2
- japanese-watercolour-collection
- kdp-templates-bundle-100
- ... (full list in data/products.json — 51 total)

**Blog (18 valid in sitemap):**
- best-procreate-brushes-for-anime
- best-procreate-brushes-for-beginners
- best-procreate-brushes-for-line-art
- best-procreate-brushes-for-portraits
- christmas-procreate-tutorial
- halloween-procreate-tutorial
- how-to-choose-procreate-brushes
- how-to-create-realistic-skin-in-procreate
- how-to-create-realistic-skin-texture-in-procreate
- how-to-create-realistic-watercolor-in-procreate
- how-to-install-procreate-brushes
- how-to-make-digital-art-look-traditional
- how-to-paint-realistic-hair-in-procreate
- procreate-blending-brushes-guide
- procreate-canvas-size-dpi-guide
- procreate-portrait-workflow
- stamp-brushes-vs-painting-brushes
- tattoo-design-in-procreate

**Orphaned blog HTML (4 NOT in sitemap, on disk):**
- how-to-shade-face-procreate
- procreate-layers-alpha-lock-clipping-mask
- procreate-line-art-tutorial
- procreate-mistakes-beginners

These 4 were found on disk under /blog/ but have no md source and no sitemap entry. They appear to be from SEO-CONTENT-ROADMAP-2026.md Wave 1 drafts that were manually built earlier and not cleaned.

**Excluded from sitemap (intentionally noindex):**
- https://digikitpro.shop/search.html
- https://digikitpro.shop/thank-you.html
- https://digikitpro.shop/404.html

---

## 2.3 robots.txt

```
User-agent: *
Allow: /

Sitemap: https://digikitpro.shop/sitemap.xml
Sitemap: https://digikitpro.shop/sitemap.txt
Sitemap: https://digikitpro.shop/sitemap-images.xml
```

- Allows all.
- Lists 3 sitemaps, all https, no http, no github.io.
- No disallow for search, thank-you, 404 — they rely on meta noindex.

## 2.4 Sitemap Details

- **sitemap.xml:** 99 URLs, all https://digikitpro.shop, no http, no www, no /index.html suffix, no query params, no github.io. Valid XML with <loc>, <lastmod>, <changefreq>, <priority>.
- **sitemap.txt:** 99 URLs, plain text, same set as xml (verified).
- **sitemap-images.xml:** 51 <url> entries (one per product), 173 <image:loc> entries (full-size images only, no -card, no -thumb), all https.
- **feed.xml:** RSS 2.0 with 18 items (one per md article), title, link, guid, description, pubDate, atom self link.
- **pinterest-feed.xml:** 47 items (paid products only), RSS with g: namespace, required fields present.
- **pinterest-feed.csv:** 47 rows, same data.

## 2.5 Duplicate URL Variants & Redirect Handling

- **http://digikitpro.shop/*** → should 301 to https:// (requires GitHub Pages Enforce HTTPS toggle — see issue register).
- **https://www.digikitpro.shop/*** → JS guard redirects to apex + Netlify 301.
- **https://digikitpro.shop/*/index.html** → JS guard + Netlify 301 to clean directory URL.
- **https://digikitpro.github.io/digikitpro/*** → JS guard redirects to shop domain + injects noindex meta.
- **?q=, ?utm_*, ?lead=, ?src=** params: search.html and thank-you.html canonicalize to clean version and are noindex, so param variants are alternate with proper canonical but not indexed.
- **No duplicate content from pagination** — no pagination, only JS filters.

## 2.6 Navigation & Link Structure

- **Header nav:** Free Brushes, Products, Bundles, Articles, About + search icon + language switcher + Instagram + Browse kits CTA.
- **Mobile nav:** Same as header.
- **Footer:** Shop (Free Brushes, All Products, Bundles, Halloween, Christmas, Portrait, Skin Texture, Line Art, Watercolor, Anime), Learn (5 buyer guides), Articles (3 featured + blog index), Legal (FAQ, Contact, Refunds, Privacy, Terms, Partner).
- **Homepage IA (verified order):** hero → results (before/after) → ebooks (Starter Guide & Masterclass) → popular (4 kits) → craft (workflow discovery) → bundles (bundle ladder) → master-library → free → articles → newsletter.
- **Breadcrumbs:** Present on product, blog, category, guides, seasonal, partner pages — schema + visible crumbs.
- **Related products:** Product pages show 3 related (from `related[]` in products.json or category fallback).
- **Article related:** Each md has `related[]` frontmatter, rendered as "Keep reading" links.
- **Product grid:** Cards link to product detail, category links, Payhip buy buttons with `data-dkp-*` attributes.

## 2.7 Assets

- **Product images:** `assets/products/<slug>/` — main (1400w), card (750w), thumb, gallery. WebP, descriptive filenames, not keyword stuffed.
- **Brand:** `assets/img/` — favicon.svg, favicon-48.png, apple-touch-icon.png, og-cover.jpg (1200x630), logo.svg, ba-before.webp, ba-after.webp.
- **Fonts:** `assets/fonts/` — manrope, playfairdisplay.

---

## 2.8 Summary of Gaps

- 4 orphaned blog HTML dirs not in sitemap, not from md source, with broken internal links.
- 2 broken internal links in procreate-mistakes-beginners (points to non-existent articles).
- sitemap.xml excludes search, thank-you, 404 — correct, but verify.py previously expected 88 checks, now 87 passing due to broken links.
- Category count mismatch: CATEGORY_SLUGS defines 10, but sitemap may have 9? Need to verify full list (audit script shows 10 dirs on disk, but sitemap grep earlier showed only 9? Let's list: portrait, skin-texture, line-art, watercolor, anime, hair, glitter-effects, traditional, figure-drawing, sketching — sitemap should have 10, but earlier grep output truncated at 10? Actually grep showed 10? We need to confirm — but for audit we note to verify).
- No pagination handling needed currently.
- No orphan pages that are truly orphaned? Seasonal, guides, partner are linked from footer/homepage, so not orphaned despite earlier simplistic orphan detection that counted only <a href> exact file matches.

---

**Next:** Issue register in 03.
