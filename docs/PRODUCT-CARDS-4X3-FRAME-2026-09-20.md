# Product cards frame the artwork whole — the frame moves 1:1 → 4:3

> **Superseded on one point the same day:** the 4:3 *single* ratio and its
> `object-fit:contain` are replaced by a full-bleed 7-rung ladder (each cover gets the
> frame that costs its own artwork least). The no-blind-crop contract this note protects
> is kept whole, and its numbers are the baseline the replacement measures against.
> See `docs/PRODUCT-CARDS-EDGE-TO-EDGE-2026-09-20.md`.

**Date:** 2026-09-20 · **Files:** `css/style.css` (`.card-media` block, `.card-top`),
`tools/core.py` (`product_card`), `tools/verify.py` (check 81 re-pinned, + check 82b
fill/badge),
`tools/card_frame_measure.py` + `tools/card_frame_diagram.py` (new, measurement),
plus the cache-bust hash on every built page.
**Follows:** `docs/CARD-MEDIA-FRAMING-2026-09-17.md` (the uncrop that made
`object-fit:contain` non-negotiable) and its 2026-09-19 addendum (the #popular row
rejoining the shared frame). **Supersedes:** that note's *frame ratio* choice only —
its no-crop contract is kept whole and is what this pass is built on.

## The brief

41 of the site's 51 card artworks are landscape marketing banners, and a square
frame is the one ratio that suits them least: a 3:2 banner can only fill 66.7% of
a 1:1 frame, so two thirds of the storefront sat inside a 1.6:1 letterbox of mat.
Move the frame to **4:3** so the landscape covers fill ~90% of it, keep
`object-fit:contain` (never crop, never stretch), keep every card's text, price
and CTA byte-identical, keep one height per row, move the corner badge off the
artwork, and give the 9 portrait covers (ratio < 0.95) the ebook-style ring +
shadow. Re-pin the verify check and record the measurement.

## What was actually happening

Measured over the real catalog (`images.cardW`/`cardH` in `data/products.json`,
51 products) against the shipped 1:1 frame — the fill a browser's
`object-fit:contain` produces is `min(1,R)/max(1,R)`:

| Artwork band | Covers | Fill in the 1:1 frame |
|---|---|---|
| landscape 3:2 (1.499–1.503) | **34** | 66.7% |
| landscape 4:3-ish (1.315–1.429) | 6 | 70.0–75.9% |
| landscape 16:9 (1.778) | 1 | 56.3% |
| square (1.000) | 1 | 100% |
| portrait (<0.95) | 9 | 56.3–80.9% |

**1 of 51 covers reached 85% fill. Mean fill 69.7%.** The landscape banners were
already rendering at their full column width, so what made the storefront read as
"small artwork" was never the artwork — it was the mat the square frame parked
above and below every banner (at 1440px: a 273×273 frame around a 273×182 banner,
91px of mat).

## The fix

**1 · The frame ratio (`css/style.css`).** `.card-media` and `.card-media img`
move from `aspect-ratio:1/1` to `aspect-ratio:4/3`. Nothing else about the frame
changes: still one uniform ratio for every card on the site, still
`object-fit:contain` with no crop and no transform, still the same mat
(`background:var(--mat)`), still the same zero padding, so row heights stay
uniform and CLS stays zero.

**2 · The 9 portrait covers** (`.card-media.portrait-cover`, emitted by
`product_card` when `cardW/cardH < 0.95`) hug their own ratio at the frame's full
height (`width:auto;height:100%`) and wear the ebook-style treatment —
`border-radius:6px` plus a gold ring and pedestal shadow
(`0 0 0 1px rgba(201,168,106,.45)` + `0 16px 34px -14px rgba(0,0,0,.72)`,
deepening on hover), the same visual language as the eBook dock. `overflow:visible`
on the media lets that shadow fall into the body's top padding like a book resting
on the card; the card's own `overflow:hidden` still holds the card's corners. In
the `#popular` row the row's pedestal `drop-shadow` filter is switched off for
these covers so the gold ring stays the only edge (rest and hover).

**3 · The corner badge leaves the artwork.** A contained image always reaches the
frame's own corners, so there is no in-frame corner with mat enough to hold a
badge without covering art. The badge is out of `.card-media` entirely and now
lives in a `.card-top` row in the card body, right-aligned beside the category
(`display:flex;justify-content:space-between;flex-wrap:wrap`,
`margin-left:auto` keeps it right even if a very narrow body wraps it).
`position:static` overrides the global `.badge` absolute rule. It cannot overlap
the artwork, the category or the title at any width, and it adds no geometry to
the media.

## The measurement (after)

Frame geometry, shipped 4:3 frame, catalogue grid (`.grid.cards`) — media width
from the Wrap (1200px max, 20px padding), `.grid` gaps and the card's 1px border:

| Viewport | Layout | Cols | Card | Frame | 3:2 artwork | Portrait 0.793 artwork |
|---|---|---|---|---|---|---|
| 390 | 390 | 1 | 350.0 | 348.0 × 261.0 | 348.0 × 232.0 | 206.9 × 261.0 |
| 768 | 768 | 2 | 354.0 | 352.0 × 264.0 | 352.0 × 234.7 | 209.3 × 264.0 |
| 768 | 753 (−15 scrollbar) | 2 | 346.5 | 344.5 × 258.4 | 344.5 × 229.7 | 204.8 × 258.4 |
| 1024 | 1024 | 3 | 314.7 | 312.7 × 234.5 | 312.7 × 208.4 | 185.9 × 234.5 |
| 1024 | 1009 | 3 | 309.7 | 307.7 × 230.8 | 307.7 × 205.1 | 182.9 × 230.8 |
| 1440 | 1440 | 4 | 275.0 | 273.0 × 204.8 | 273.0 × 182.0 | 162.3 × 204.8 |

The homepage best-sellers row (`.grid.cards.cards-4`) is 2-up at 768 and **still
2-up at 1024** (that grid goes 4-up at 1080), so its cards are 480.8 wide there —
frame 478.8 × 359.1. At 1440 it is 4-up: card 266.0, frame 264.0 × 198.0.

Fill, before → after (fill % is width-invariant: the frame ratio is fixed and the
media is width-driven, so one number holds at every viewport):

| Artwork band | Covers | 1:1 (before) | 4:3 (after) | Δ |
|---|---|---|---|---|
| landscape 3:2 | 34 | 66.7% | **88.9%** | +22.2 |
| landscape 4:3-ish | 6 | 70.0–75.9% | **93.3–100%** | +24.3 |
| landscape 16:9 | 1 | 56.3% | 75.0% | +18.8 |
| square 1:1 | 1 | 100% | 75.0% | −25.0 |
| portrait <0.95 | 9 | 56.3–80.9% | 42.2–60.7% | −19.0 |

**40/51 covers now reach 85% fill (was 1/51). Mean fill 69.7% → 83.9%** — the
prototype figure this pass was briefed against, reproduced exactly.

Two honest consequences, both intended:

* **The landscape banners' pixels do not change.** A 3:2 banner is width-bound in
  both frames, so it paints 273×182 at 1440 either way. What changed is the frame
  above and below it (273 tall → 204.8), i.e. the mat. The card got shorter, the
  banner did not get smaller — which is precisely the "fills ~90% of the frame"
  the brief asked for. The one 16:9 planner (1.778) is the only landscape that
  still leaves real mat (75%); it is 1 of 51 and would need a re-render, not a CSS
  exception.
* **The 9 portrait covers render ~25% smaller linearly** (273 → 204.8 tall at
  1440; 44% less area), because a portrait cover is height-bound and the frame is
  now shorter. That is the accepted cost of the trade, and it is why those nine
  get the ebook-style ring: at 42–61% fill a bare contained cover reads as a
  shrunken thumbnail, and a ringed one reads as a framed book. If the owner later
  wants them bigger, the fix is a taller art render for those 9 products (or a
  dedicated portrait row), **not** a second frame ratio on the cards — the
  uniformity is what keeps every row one height.

Portrait covers in detail (the exact nine named in the brief):

| Product | Artwork | Ratio | 4:3 fill | 1:1 fill |
|---|---|---|---|---|
| `morocco-7-day-itinerary` | 750×1333 | 0.563 | 42.2% | 56.3% |
| `procreate-starter-guide-free-ebook` | 750×1000 | 0.750 | 56.2% | 75.0% |
| `procreate-portrait-masterclass-ebook` | 750×1000 | 0.750 | 56.2% | 75.0% |
| `mindfulness-system-planner` | 750×971 | 0.772 | 57.9% | 77.2% |
| `portrait-skin-brushes-procreate` | 750×946 | 0.793 | 59.5% | 79.3% |
| `essential-line-art-sketch-kit` | 750×946 | 0.793 | 59.5% | 79.3% |
| `artista-studio-kit-76-brushes` | 750×928 | 0.808 | 60.6% | 80.8% |
| `portrait-mastery-kit-46-brushes` | 750×928 | 0.808 | 60.6% | 80.8% |
| `ultimate-portrait-mastery-bundle` | 750×927 | 0.809 | 60.7% | 80.9% |

## How this was measured — and its one limit

This pass could not run a browser. Every browser-binary source is unreachable from
the sandbox — `cdn.playwright.dev`, `storage.googleapis.com`,
`objects.githubusercontent.com` and `deb.debian.org` all refuse the connection —
and Chromium's shared libraries (`libnss3`, `libatk-1.0`, `libgbm`, `libxkbcommon`,
`libcups`) are not installed, with no package source to get them from. So the
numbers above come from `tools/card_frame_measure.py`, which applies the shipped
CSS box rules (Wrap 1200/20px, `.grid` gaps, the `.cards` and `.cards-4` column
breakpoints, the card's 1px border, the frame's own `aspect-ratio`) to the real
artwork ratios in `data/products.json` using the same arithmetic a browser's
`object-fit:contain` performs.

That arithmetic is exact for the question asked — `contain` is uniform ratio
scaling, with no text metrics or font loading involved, and the grid maths is
integer arithmetic on the declared rules. Two caveats are recorded rather than
hidden: the scrollbar (headless Chromium on Linux reserves 15px on an overflowing
page, so both variants are printed) and the fact that this is a derivation from
the CSS, not a rendering of it.

**To re-confirm in a real browser** (any machine with network):

```bash
python3 -m pip install playwright && python3 -m playwright install chromium
```

then load `index.html`, `products.html` and a `category/` page at 390/768/1024/1440
and read `document.querySelector('.card-media').getBoundingClientRect()` (expect
the frame numbers above, ±1.5% for the scrollbar variant) and each card's `img`
intrinsic ratio against its painted box. Every expectation in this note is in the
tables above; `shots/product-cards-frame-4x3-geometry-1440.svg`
(`tools/card_frame_diagram.py`) draws the geometry to scale from the same source.

## Guardrails

`tools/verify.py` is now **90 checks**:

* **#81 re-pinned** — "product cards frame the artwork whole, in a uniform 4:3
  frame": `.card-media img` must keep `object-fit:contain` and must not
  reintroduce `cover`; the frame must be `aspect-ratio:4/3`.
* **#82b new** — "4:3 product cards leave 40/51 covers at >=85% fill (landscapes
  whole, portraits ringed)": recomputes fill for all 51 real artwork ratios and
  asserts exactly 40 reach 85%; in the same check, no `.badge` may appear inside
  any `.card-media` element across all built pages (409 cards scanned) and the
  badge must be pinned by `.card .card-top .badge{position:static}`.
* #82 (mat not painted over) and #88 (`#popular` may not re-dock the media) both
  still pass unchanged against the 4:3 frame.

Mutation-tested: restoring `aspect-ratio:1/1` fails #81; a `1/1` frame fails #82b
on the 40/51 count; putting the badge back inside the media fails #82b's badge
half; `object-fit:cover` fails #81.

## Build, drift and rollback

`python3 tools/build.py && python3 tools/verify.py` → **ALL 90 CHECKS PASSED**; a
second and third build leave the working tree byte-identical (idempotent).

104 HTML files changed. The drift was proved to be structural only: after
normalising the `?v=` cache-buster, **every one of the 104 files has exactly the
same words as `HEAD`** (multiset comparison of all visible text, scripts and
styles stripped) — 51 files differ only in the *order* of words, because the badge
label ("Best Seller", "Free", "Bundle") moved from the media into the card body's
first row. No copy, price or CTA text changed anywhere on the site.

Roll back: restore `aspect-ratio:1/1` in the two `.card-media` rules, delete the
`.card-media.portrait-cover*` and `.card-top` blocks, revert the badge to its
in-media position in `product_card`, set `EXPECTED = 89` and rebuild. The artwork
goes back to a square frame; nothing else moves.

## Deliberately not changed

* **The Pinterest Save button** (`.pin-btn`) still sits over the media's top-right
  corner. It is a control, not a badge, and it is the artwork's own pinnable
  surface — moving it into the body would cut the button off from the image it
  pins. It is hover-revealed on pointer devices and always-on for touch, exactly
  as it shipped. Worth a second look if the owner wants *nothing* over artwork.
* **`.dl-media`, `.thanks-media`, `.pt-thumb`, `.gal-thumb`, `.craft-art`,
  `.ladder-media`, `.journey-media`, `.bundle-media`** — other 1:1 product frames
  on other surfaces (freebies, thank-you, partner, PDP thumbs, homepage strips).
  Out of scope for this pass, which was scoped to `.card-media`; each is a
  one-line ratio change if the owner wants the same treatment site-wide.
* **`#popular` geometry, card typography, prices, CTAs, hover lifts, the reveal
  motion, `loading`/`srcset`/`fetchpriority` hints.** The frame ratio is the only
  geometry that moved.
