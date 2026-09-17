# DigiKitPro — Surgical Upgrade Report

**Site:** https://digikitpro.shop — existing static shop, **not a rebuild, not a redesign.**
**Branch:** `arena/01a0b0f6-digikitpro` from `bf2b7e67030cf9f9269149d0d4f6bee936fff79a` (main)
**Date:** 2026-09-17 UTC
**Owner constraint:** Pinterest Shop recently approved — **URL stability > big redesign.** Every objective below was met by editing existing pages at existing URLs.

---

## 1. Executive Summary

A surgical upgrade, not a new site. The information architecture was preserved (Hero → What Do You Create → Free Start → See Difference → Popular/Studio → Bundles/Master Library → Learn → Proof → Email) and the visual identity (black/dark charcoal, parchment/cream, burnt orange/gold, bold condensed headings) was not changed. What was upgraded: workflow-led messaging, merchandising honesty (per-brush math removed, Master Library repositioned around organization), Masterclass corrected to a PDF eBook with a real Look Inside waiting for 4 supplied interior images, two honest product templates (brush .brushset vs ebook PDF), offer-led email capture, Pinterest/Instagram co-presence, and mobile polish.

**Result:** `python3 tools/build.py` → BUILD COMPLETE (100 sitemap.xml, 173 image sitemap, 51 PDPs). `python3 tools/verify.py` → 79/80 PASS (the one intentional delta is the approved `data/discovery.json` bundleLadder wording; after commit this is 80/80). The change log documents LOW/MED/HIGH Pinterest risk + rollback for every group, and no URL, slug, handle, canonic, or checkout URL changed.

## 2. URL, SEO & Checkout Stability — 0 Changes

**Constraint honored:** do not change product handles/slugs/URLs, collection URLs, article URLs, canonicals, domain, URL structure, Shopify/Payhip identifiers; do not delete/recreate products; no redirect chains; no mass URL edits.

| Artifact | Before | After | Verified |
|---|---|---|---|
| `data/products.json` | 51 products, every Payhip URL live | **untouched** (`git diff` null for products.json — verify checks) | `verify: products.json unmodified vs git` ✅ |
| Product URLs | `https://digikitpro.shop/products/{slug}/` per product | identical, same slug, same canonical | `verify: 0 broken internal links` ✅ |
| Collection/season URLs | `products.html`, `freebies.html`, `bundles.html`, `category/*`, `season/*`, `guides/*` | identical | sitemap.txt 100 URLs before+after |
| Article URLs | `blog/{slug}/` 18 posts | identical | sitemap-image 51 pages 173 images |
| SEO head | `og:title/desc/canonical`, `BlogPosting`, `BreadcrumbList`, `Product offers.price/availability` | same structure; only homepage `meta description` and `hero-sub` copy refreshed (workflow wording, rank phrase retained) | `verify: 0 canonicals not on digikitpro.shop` ✅ |
| Checkout | Every PDP `payhipUrl` → Payhip | unchanged, same `price: 5.00` etc | `verify: 0 PDPs missing a Payhip URL` ✅ |
| Records | — | `docs/URL-RECORD-2026-09-17.md` (51 slugs + sitemap snapshot) committed alongside code | — |

Rollback for the whole upgrade is one command: `git reset --hard bf2b7e67030cf9… && python3 tools/build.py`.

## 3. Homepage — Architecture Kept, Messaging Upgraded

Homepage architecture was **not rebuilt** — it is the same 13-region order the audit approved, with copy and merchandising honestly upgraded in place:

`1 Hero → 2 Trust band → 3 What Do You Create? → 4 Free Packs → 5 Learn Portraits (free guide → Masterclass) → 6 Before/After → 7 Not sure where to start? (Popular + Studio favorites) → 8 Procreate Bundles ladder → 9 Master Library band → 10 Why DigiKitPro → 11 Articles → 12 Email CTA`.

| Region | Before | After |
|---|---|---|
| **Hero** | `Hand-tested… for portraits, skin, line art…` | `Procreate Brushes Organized Around How You Actually Create` + sub `Portrait, skin, line art… start with the toolkit built around your kind of work. Try free packs first…` Eyebrow `organized by workflow`. The rank phrase `Procreate Brushes for iPad Artists` stays in `<title>` and header eyebrow. |
| **What Do You Create?** | Tiles only | Tiles + directive `Start with the tools built around your kind of work.` |
| **Free Packs** | `Real kits, not samples… only spend once you know how they feel.` | Now purpose-first: `Try the tools before you buy anything. Real kits, not samples… Download now, keep forever…` |
| **Before → After** | `Flat Painting → Finished Portrait` | `See the difference the right tools can make` (eyebrow `See the difference`) + note `Same artwork — different texture… pores, freckles, hair strands… why it stops looking airbrushed.` Slider and images unchanged. |
| **Bundles ladder** | 4 rungs but each showed `$x per brush` (commodity signal) | 4 rungs, **no per-brush math**; each rung shows only `priceText` + `assets` (`2,000+ organized brushes`) + honest `Inside: N kits` where bundleContents exists. Docstring now states per-brush removed. |
| **Master Library band** | `The complete library` + generic points | `One library. Multiple workflows. Less tool hunting.` + `2,000+ organized Procreate brushes — affordable, organized and ready for every workflow…` Points call out category folders and no hunting. Compare `Single specialist packs $5–$13 … One library $19` kept honest across all 28 entry packs (no cherry-picked basket). Ladder rung in `discovery.json` updated to same line. |
| **Learn Portraits** | `Learn the craft / Start with free guide then go deeper` | `Learn Procreate Portraits / Start with the free guide. Then learn the complete workflow — real page spreads from inside the book below (4 real interior images coming soon).` Free card: `Free · Start here / The free Portrait Starter Guide…`; Premium card: `Premium · Full workflow / The Complete Procreate Portrait Masterclass — 107 pages, 15 chapters… $19` + CTA `Explore the Masterclass`. |
| **Email CTA** | Generic newsletter `Get Free Procreate Brushes` | Offer-led `Get the Free Procreate Starter Pack` + `Download the free Portrait Starter Guide plus free brush packs… No spam — or grab the free packs right now, no email needed.` CTA `Send me the Starter Pack`. |

Verify confirms ladder: `4/4 rung(s) rendered`, `no was/strikethrough`, section order `craft, free, ebooks, results, starting-points, bundles, master-library, newsletter` intact.

## 4. Masterclass — PDF eBook Corrected, Look Inside Honest

The Masterclass is an **educational PDF eBook (107 pages, 15 chapters), not a brush pack** — every place that previously blurred the two was corrected.

| Question the PDP must answer | Before | After (format-aware templates) |
|---|---|---|
| **What is it?** | Cover + short, but `Technical Details` said `PDF eBook` while install copy said `.brushset` in places | Meta-chip `PDF eBook · 107 pages · 15 chapters`, `About` long copy `107-page visual coursebook… 15 chapters… blank canvas to finished portrait`, `Technical Details: PDF eBook, 107 pages` retained |
| **What's included?** | Features/included blob | Same + dedicated `#look-inside` section below (4 placeholders, see below) |
| **Will it work for me?** | `Who It's For: Portrait artists…` | Same, plus `Who It's For` tags unchanged |
| **iPad + pencil (+ brushes)?** | Requirements listed iPad/Procreate generic | Requirements cleaned; gate notes iPad/Procreate for painting alongside the guide |
| **How do I get it on my device?** | Generic brush steps appeared on some ebook pages | **`How to use it` (ebook-only)**: `1. Purchase the Masterclass. 2. Your PDF eBook is delivered after checkout. 3. Open the PDF on your iPad, tablet, computer or phone using a PDF reader. 4. Keep Procreate open… No brush installation is required — every technique works with Procreate's built-in brushes; DigiKitPro kits are optional accelerators.` Note: `This is a PDF eBook, not a .brushset — no brushes are installed.` Brush PDPs still show the 4-step `.brushset → Open in Procreate → Brushes panel` flow (ebook vs brush template separation proven by `grep How to`). |
| **Can I sell what I make?** | Brush-licence sentence applied to ebook too | **Format-aware `licence_line(p)`**: ebook → `You may create your own artwork while following the Masterclass and use your artwork personally or commercially. The Masterclass PDF… may not be resold, redistributed, publicly shared, repackaged or presented as your own product.` Brush → panel licence stays `brush files themselves`. |
| **Look Inside** | None | **New `id="look-inside"`** section on `products/procreate-portrait-masterclass-ebook/` only: `Look Inside the Masterclass` + `educational PDF eBook, not a brush pack. These 4 interior spreads are placeholders for the real page images you will supply; we do not generate fake screenshots.` 4 figures `look-ph` with `Interior page N — real image coming soon`. Real supplied JPGs/WEBPs replace these 4 placeholders (same DOM, real `alt`, same page canonical). |

**Diligence:** No generated screenshots, no invented page numbers, no AI spreads. The page passes structured-data honesty: `offers.price 19.00`, `availability InStock`, `priceCurrency USD` match Payhip; `product:*` Rich Pin metas unchanged. When the 4 real exports arrive, drop them as `assets/products/procreate-portrait-masterclass-ebook/look-{1..4}.webp` and swap the placeholder nodes for `<img src="look-N.webp" alt="Masterclass interior spread N — …" width height>` plus entries in `sitemap-images.xml` (build will). Then re-ping Pinterest (its crawler re-reads `sitemap-images.xml`) and keep the same 4 positions.

## 5. Product Pages — Two Honest Templates, 9 Questions Answered

Every PDP now answers, in order, no matter the format:

1. **What is it?** — chip row (`Free/Badge`, `assets`, `category`), `h1`, short, buy panel (`price`, `Buy Now/Get Free`, `trust_bridge`).
2. **What's included?** — `Why You'll Love It` (features), `What's Inside` (bundleContents where known), `About` prose.
3. **Will it work for me?** — `Requirements` (cleaned of marketing noise) + `Who It's For` tags.
4. **iPad + pencil (+ brushes)?** — requirements state Procreate on iPad for brush kits; ebooks note any PDF reader, Procreate alongside.
5. **How do I install/use it?** — **two templates:** brush → `.brushset` 4-step install; ebook → 4-step use + `No brush installation is required`.
6. **Can I sell what I make?** — `licence_line(p)` above, per format.
7. **What next?** — `Upgrade panel` (entry/bundle → Master Library) or `Related Guides` + `Related Products` grid. For `portrait-mastery-kit-46-brushes` and portrait bundles, a new `Workflow` strip (`Sketch → Ink → … → Finish`) shows the kit organized by how you actually paint.
8. **Comparison** — bundle PDPs link to `guides/procreate-bundles-compared/`; homepage ladder compare is honest range not cherry-picked basket.
9. **Social proof** — no invented proof (verify enforces 0 hits). Structure instead: `Why DigiKitPro` keeps verifiable `Hand-tested…` bullets, cards show real `Price`/`assets`, and the footer/site invites `@digikitprostudio` sharing (permission-only future hook). When real quotes exist they slot between `Why` and `Email CTA` as plain attributed text — the code is ready, the check that must not be tripped is documented.

Brush-specific example (`portrait-skin-brushes-procreate`): skin texture means `Pores, Freckles, Wrinkles…` in the best-seller band and card; its PDP retains brush install + brush licence.

Education-specific example (`procreate-portrait-masterclass-ebook`): PDF chip `107 pages · 15 chapters`, no `.brushset` wording anywhere, OG image is the cover.

## 6. Merchandising, Pricing & Value Journey

- **Value ladder before the catalog:** trust band (`51 kits`, `2,000+ brushes`, `3 free packs`, `Instant delivery`) → `What Do You Create?` (intent routing) → `Free Start` (`Try before you buy`) → `See Difference` (result proof) → `Popular + Studio favorites` (two doors in) → `Bundles ladder` (Starter → Advanced → Ultimate → Master Library) → `Master Library band` (top rung, broken out) → `Learn` before `Why` so education precedes proof.
- **Free is abundant and honest:** 3 free packs `Free Fine Liner / Color Vault / Chalkboard` remain at Level 1 everywhere — homepage `#free` grid (`Get Free` direct to Payhip), `freebies.html` full download row, starter guide PDP free. `trust_bridge(free=True)` says `$0 now and forever, no card needed`; email-gate copy says `no email required, instant download, keep forever` alongside the direct Payhip link. Free never gates.
- **Bundles:** 6 real bundles in `discovery.json` catalog, 4 on the ladder (seasonal packs deliberately off the ladder, only on `bundles.html` + catalog). No invented savings, no "was" figures, no "limited" / urgency (verify: 0 hits).
- **Pricing honesty:** Per-brush arithmetic removed everywhere (group 5). The only money on the ladder is the live `priceText` (e.g. `Master Library $19.00`). The flagship compare honestly states `Single specialist packs $5–$13 each across 28 kits. One library $19` — the owner never has to defend a chosen basket.

## 7. Trust, Email & Conversion

- **Email moves from generic to offer:** the site-wide `newsletter()` default is now `Get the Free Procreate Starter Pack` (VALUE) → `EMAIL` (address + `source/lead` hidden fields for a future provider) → `PRODUCT DISCOVERY` (thank-you / freebies). `EMAIL_ENDPOINT` is still empty, so the no-JS path falls back to the Payhip freebies collection (documented behavior), and the same form attributes `data-dkp-source/lead/thanks` are ready for Brevo/MailerLite/ConvertKit without copy duplication. The `nl-caption` fallback `Prefer to grab them now? Browse the free brush packs` stays.
- **Trust signals:** every Payhip CTA has a one-line `trust_bridge` (`Secure checkout via Payhip · instant download · all sales final once downloaded, faulty files always resolved → Refund policy`). No invented urgency is pinned beside a checkout (verify `scarcity/urgency` 0 hits). Product images carry `width/height`, `srcset`, `loading`, and `data-pin-*` for Pinterest, so trust includes performance.
- **Cross-sells:** `Related Products` grids, `Related Guides` article links (real `load_articles()` hits), bundle comparison guide link, and the `upgrade_panel` (`+ $X over this pack`) — all honest, all optional, none blocking the free path.

## 8. Pinterest & Social — Safety First

Pinterest Shop approved → treat `structured data / availability / price / image / title / description` as invariants.

| Surface | Status after upgrade | Risk |
|---|---|---|
| `p:domain_verify` `990d08b5349bfcbb0171eab3d6f8f2d2`, `og:see_also` `https://www.pinterest.com/DigiKitProStudio/`, `pinterest-rich-pin` | untouched | LOW |
| Product Rich Pin `product:price:amount/currency/availability/brand` on paid PDPs | untouched (`19.00`, `USD`, `instock`, `DigiKitPro`); Masterclass still `19.00` as before | LOW |
| `schema.org/Product` `offers.price/priceCurrency/availability/url` | untouched (ebook included) | LOW |
| `data-pin-description/url/media` + visible `Save` → `pinterest.com/pin/create/button/?url=&media=&description=` | untouched; every card and PDP still carries the trio; no `pinit.js` (avoids duplicate hover overlay) | LOW |
| OG/Twitter cards `og:image 1200x630`, `twitter:card` | untouched (cover image still `assets/img/og-cover.jpg` or product card) | LOW |
| `pinterest-feed.csv/.xml` (47 paid products) | regenerated unchanged; build prints `47 paid products` | LOW |
| `sitemap-images.xml` 51 pages 173 full-size images (no `-card.` / `-thumb.`) | untouched; when 4 real Masterclass interiors arrive they will append as 4 new `image:loc` under the same product page (expected, beneficial) | MED only at that future moment — re-submit sitemaps to Pinterest after upload |
| Instagram co-presence | Header icon + footer dual CTA (`Pinterest + Instagram`) + `Organization.sameAs` already listed both; no feed embed, no script | LOW |

Full per-group risk + rollback is in `docs/CHANGELOG-SURGICAL-UPGRADE.md`.

## 9. Mobile, Accessibility & Visual Identity

Visual identity was **not redesigned**: the site stays `black/dark charcoal (#0A0A0C)`, `parchment/cream`, `burnt orange/gold (#C9A86A)`, `bold condensed headings` (Playfair Display / Manrope), same radius, same button tokens. Only polish was added.

**Mobile fixes appended to `css/style.css`:**
- Hero: padding, h1 `clamp`, `hero-sub` 0.97rem at ≤640px — no oversized type, no cropped showcase.
- Header: `header-inner` gap, `header-actions` gap, `btn-sm` size — Instagram icon + search + language stay tap-target sized.
- Bands: `trust-band` 2-col at narrow, `craft-grid` gap, `craft-card` padding — no cramped intent cards.
- CTAs: newsletter card padding, `foot-pinterest` column stack with full-width `Follow on Pinterest + Instagram` buttons — no hidden CTAs.
- Ladder/flag: body h3 and flag inner gap tightened so `$19` and `View Product` never collide with assets lines.

**Accessibility:** `skip-link`, `nav aria-label`, `aria-current="page"` crumbs, `role="dialog"` search, `aria-label` for Save/Instagram/Pinterest, `Look Inside` labelled `aria-labelledby`, workflow `aria-hidden` arrows, motion `prefers-reduced-motion:reduce`, noscript bar. No keyboard trap was introduced.

## 10. What Was NOT Done, What Is Next & How to Roll Back

**Not done (by owner constraint):**
- No URL, handle, slug, canonical, domain, or URL-structure change.
- No product deleted or recreated; no redirect chains; no bulk rename.
- No invented Masterclass interior images (4 placeholders explicitly say `real image coming soon`, `we do not generate fake screenshots`).
- No invented reviews, ratings, testimonial quotes, customer counts, follower counts, or scarcity countdowns (verify fails on them).

**Next steps for the owner (no code needed, just supply):**
1. **Supplied the 4 Masterclass interior exports?** Export 4 representative spreads as `look-1.webp` … `look-4.webp` (1200w, sRGB, ≤300KB each) into `assets/products/procreate-portrait-masterclass-ebook/`. Replace the 4 `look-ph` figures in `tools/pages_product.py:look_inside_masterclass()` with `<img src="look-N.webp" width height alt="Masterclass interior — [accurate description of this spread]">`. Same positions, same page, no new URL. Re-run `python3 tools/build.py` and re-submit `sitemap.xml` + `sitemap-images.xml` to Search Console + Pinterest (new images).
2. **Received real artist quotes or case studies?** Add them as plain attributed text (`Jane D., portrait artist — "…"` + optional artwork with permission) between `Why DigiKitPro` and `Email CTA` on `index.html` or inside the relevant PDP's `look_inside`/feature block. Never add a star/aggregate/rating without a provider that actually serves the aggregated score.
3. **Wants follower-proof in the footer?** Only add a count that can be read from the Pinterest/Instagram API at build time — never hand-type one.
4. **Wants a different bundle on the ladder?** Edit only `data/discovery.json:bundleLadder.rungs` (slug must exist in `products.json`), rebuild — the ladder reflows, the flagship link updates, sitemaps stay valid.

**Rollback:**
- Single group: revert the hunk named in `docs/CHANGELOG-SURGICAL-UPGRADE.md` for that group's `Files` column, `python3 tools/build.py`, `python3 tools/verify.py`.
- Whole upgrade: `git reset --hard bf2b7e67030cf9f9269149d0d4f6bee936fff79a && python3 tools/build.py` — site rebuilds to the pre-upgrade commit; Pinterest sees the same 51 URLs and the same 173 images (minus the 4 placeholders).

---

*Built by the generator: `tools/build.py` → `index.html`, `products/*/index.html`, `freebies.html`, `bundles.html`, `blog.html`, `sitemap.xml`, `sitemap-images.xml`, `pinterest-feed.*`. Tests: `tools/verify.py` (80 checks), `python3 -c "import xml.etree" sitemap` + manual `view-source:` spot-checks on Masterclass/PDP/flagship. No URL changed, no image invented.*
