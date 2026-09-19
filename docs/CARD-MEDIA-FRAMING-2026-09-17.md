# Product card framing — should cards show the full artwork?

**Date:** 2026-09-17 · **Branch:** `arena/01a0b15d-digikitpro` · **Files:** `css/style.css` (+ `tools/verify.py`)
**Follows:** PR #37 (article heroes uncropped: `.article-hero img` → `width:100%; height:auto; object-fit:contain`)

## The question

PR #37 uncropped the article hero because a fixed-height frame with
`object-fit:cover` sliced the product name out of covers that carry the name
*baked into the artwork*. Product cards were left alone, on the documented
grounds (comment above `.card-media`) that the uncropped version "rendered the
artwork small and shrunken", and that the square `cover` frame only "mildly"
crops 4:5 and 3:4 covers top/bottom. This is the measurement of that claim.

## What the artwork actually is

`cardW`/`cardH` in `data/products.json`, cross-checked against the real bytes of
all 173 `.webp` files in `assets/products/` (51 products). The `srcset` full-size
render shares the card's ratio for every product, so DPR never changes the crop.

| Artwork ratio | Products | What a 1:1 `cover` frame destroys |
|---|---|---|
| Landscape 3:2 / 4:3 / 16:9 | **41 of 51** | **24–44% of the width** — headlines cut mid-word |
| Portrait 0.56–0.81 (pack covers) | 9 | 19–44% of the height — brand lockup, feature-icon row, corner ribbon |
| Square 1:1 | 1 | nothing |

Mean area lost across the catalog: **30.3%**.

So the recorded rationale describes the wrong failure. The card problem is not a
mild top/bottom trim of portrait covers — it is a **hard side-crop of landscape
marketing banners**, on 4/5 of the catalog. `verify.py` output for the worst
cases, and the reason it matters: the banner text is the selling point.

| Product | Card art | Crop result under the old rule |
|---|---|---|
| `organic-watercolor-80-brushes` | 580×435 | title reads `80 WATERCOLO… BRUSHE… for PROCREA…` |
| `adhd-planner-2026` | 580×386 | header reads `al 2026 ADHD Balanced`, tags read `#Fully H` |
| `ultimate-fitness-planner` | 750×422 | loses both page-mockups that show what you buy |
| `master-library-2000-brushes` | 750×500 | `ARTIST'S PICK` ribbon arrives as `PICK` |
| `portrait-skin-brushes-procreate` | 750×946 | `DIGIKITPRO` lockup gone |
| `morocco-7-day-itinerary` | 750×1333 | 43.7% of height gone, bottom caption gone |

## Options measured, and why the shipped one won

1. **Per-card natural ratio** (what PR #37 did for heroes). Zero crop, and the
   homepage hero already does exactly this via `--hero-ar` in
   `tools/pages_main.py`. Rejected for cards on grid geometry: measured across
   all **94 product-card grids** on the site (378 rows at the 4-/3-/2-up
   breakpoints), a third of rows would mix media heights by **>1.75×** (worst
   **2.67×**, on `products.html`, where a 16:9 planner banner sits beside a
   0.56 itinerary). Only 47% of rows stay within 1.10×. A hero is one image in
   one column; a card grid cannot absorb a 2.7× height spread.
2. **Blurred copy of the artwork painted behind the image** (`--art` +
   `filter:blur()`). Best-looking letterbox fix, keeps the uniform frame, and
   prototyped — but a CSS `background-image` is **never lazy-loaded**, so it
   forces all 51 catalog artworks (2.70 MB of `*-card.webp`) to download at first paint, undoing
   the `loading="lazy"` on 47 of them in a build that otherwise cares a lot
   about LCP (`srcset`, `fetchpriority`, intrinsic width/height on every tag).
   Rejected: a prettier letterbox is not worth the storefront's worst LCP
   regression. Rejected in favour of option 3; revisit only with a tiny
   pre-blurred data-URI swatch (no request) or a load-time `--art` set in JS.
3. **Uniform 1:1 frame + `object-fit:contain`, leftover area treated as a deliberate
   mat** (shipped). `background:radial-gradient(gold sweep), var(--surface-2)`
   on the frame, `background:none` on the img, and the two hover zooms that used
   to scale the artwork by 5–6% removed (under `contain`, a zoom past 100% is
   just the crop arriving on mouseover).

Frame ratio 1:1 is also still the right *ratio*, not just the right frame:
it caps loss for a catalog spanning 0.56–1.78. A uniform 4:3 frame (the closest
"fix") zeroes the landscape crop but pushes portrait loss from 21% to 40% and
adds 20% of mat to the landscape cards; the flagship packs are the portrait
ones. Rejected.

## What the reader gains and loses

* 41 landscape banners: **identical width to before**, now with the complete
  composition. The "small and shrunken" critique does not apply to them — the
  original complaint was about portrait art contained inside a *3:2* frame with
  12px padding, which rendered at 53% of frame width. Nothing here does that.
* 9 portrait covers: ~79% of card width × 100% of frame height, versus 100% ×
  79% before — same artwork area, nothing sliced, brand lockup and feature row
  back.
* Cost: up to ⅓ of the frame height reads as mat on a 3:2 card, and the single
  worst case (`morocco-7-day-itinerary`, 0.56) renders at 56% width. If that one
  ever bothers the owner, the fix is a taller art render, not a CSS exception.

## Invariants now enforced

`tools/verify.py` 81–82 (count went 80 → 82): the `.card-media img` rule must
keep `object-fit:contain`, must not reintroduce `cover`, the frame must keep
`aspect-ratio:1/1`, and `.card-media img` must keep `background:none` — without
it the global `img{background:var(--surface-2)}` rule paints over the mat, since
a contained `<img>`'s box is the whole square. Both checks were confirmed to
fail against the old `cover` rule.

## Build + rollback

`python3 tools/build.py && python3 tools/verify.py` → `ALL 82 CHECKS PASSED`.
CSS-only change: `git diff` on the 102 HTML files is the `?v=` cache-buster line
and nothing else (0 content drift, verified by normalising `?v=` and diffing
every HTML file against `HEAD`). No data, no URL, no schema, no feed, no
`sitemap-images.xml` change — cards are still excluded from image sitemaps
because `-card.webp` files are downscales of the full render, not separate art.

Roll back: revert the `.card-media`, `.card-media img` and motion-block hunks in
`css/style.css`, rebuild. The artwork goes back to being cropped; nothing else
moves.

## Known same-defect surfaces, deliberately NOT changed here

Each frames product card art with `cover` and crops the way cards did. Left alone
to keep this reviewable as one visual decision; each is a 2-line fix using the
same mat pattern if the owner says go.

| Selector | Frame | Where | Loss under `cover` |
|---|---|---|---|
| `.dl-media` | 1:1 | freebies page cards | same as cards did: 24–44% |
| `.thanks-media` | 3:2 | thank-you page | **47%** of height on a 0.79 cover |
| `.pt-thumb` | 1:1 | partner share-kit thumbs | same as cards did |
| `.bundle-media`, `.finder-media`, `.ladder-media`, `.up-media` | varies | bundles, finder, homepage ladder, PDP upgrade | wide frames crop portrait covers hardest |

`.bs-media` (homepage best-seller panel) already uses `width:100%;height:auto` —
natural ratio, uncropped — which is the precedent that this treatment is
consistent with, not new invention.

## 2026-09-19 addendum — the best-sellers row rejoins the square

The 2026-09-18 premium pass on the homepage's **Best sellers** row (`#popular`,
the four lead kits, `.grid.cards-4`) re-docked its four cards in a **4:3 frame
with a 1rem/1.1rem inset** (`#popular .card-media{aspect-ratio:4/3;padding:1rem
1.1rem}` plus `aspect-ratio:auto` on the img), scoped after the global rules so
checks 81–82 kept passing. It cropped nothing — but it made the storefront's
lead row the one product grid on the site that did **not** share the square
above, and it re-introduced exactly the frame ratio this note rejected for the
catalog ("pushes portrait loss … the flagship packs are the portrait ones").
Three of the four best sellers are those portrait covers.

Computed from the shipped CSS (border-box, 16px root; 1200px wrap → 264px media
width at ≥1080px, 348px on a 390px phone):

| Cover | 4:3 + inset dock | Shared square | Δ |
|---|---|---|---|
| portrait 750×946 (×2) / 750×928 | 132×166 px desktop · 182×229 phone | 209×264 · 276×348 | **+59% / +52% linear**, ×2.5 / ×2.3 area |
| landscape 580×435 | 221×166 · 305×229 | 264×198 · 348×261 | +19% / +14% linear |
| media height (row height) | 198 · 261 | 264 · 348 | +66 px · +87 px — now equal to the free row |

So the portrait best sellers had been rendering at 63–66% of the size the same
artwork gets on every other card, in a tile shorter than its neighbours.

**Change (CSS only).** The `#popular .card-media{aspect-ratio:4/3;padding:…}`
rule is gone and `aspect-ratio:auto` is gone from `#popular .card-media img`;
the row now inherits the shared `.card-media` square + `contain` + zero padding
verbatim. Everything that was actually *premium* about the pass stays: the
gradient shell and gold border, the hairline `::after` overlay (absolutely
positioned — adds no box), the pedestal `drop-shadow` filter (never a
transform), the roomier body, the gold price.

**Invariant.** `tools/verify.py` **88** (count 87 → 88): the built homepage
must still render `#popular` as `.card-media` cards, and every `#popular` rule
whose selector reaches `.card-media` (the `::after` overlay excepted) may
declare no frame property — `aspect-ratio`, any `padding-*`, `width`/`height`
and their min/max/logical forms — and, on the img, no `object-fit`,
`object-position`, `transform`, `scale` or `zoom`. Property names are compared
whole. Confirmed to fail against the previous stylesheet, naming both offending
rules (`#popular .card-media`, `#popular .card-media img`).

**Build.** `python3 tools/build.py && python3 tools/verify.py` → `ALL 88 CHECKS
PASSED`; a second build leaves the tree clean; the 102 rebuilt HTML files differ
from `HEAD` only by the stylesheet cache-buster (`?v=e8d96474… → ?v=35fce012…`).
Roll back: restore the two `#popular` declarations and set `EXPECTED` back to 87.
