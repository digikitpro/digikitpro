# Product cards go full bleed — the frame becomes a 7-rung ladder

**Date:** 2026-09-20 · **Files:** `css/style.css` (the `.card-media` block, the
`#popular` row), `tools/core.py` (`media_rung()` + `product_card`),
`tools/verify.py` (check 81 re-pinned, 82b turned into a crop-cost assertion,
+2 new checks, `EXPECTED` 94 → 96), `tools/card_frame_measure.py` (new section 5),
`tools/card_frame_mock.py` (new, before/after evidence), plus the cache-bust hash
on every built page.
**Follows:** `docs/PRODUCT-CARDS-4X3-FRAME-2026-09-20.md` (the same day's 1:1 → 4:3
move) and `docs/CARD-MEDIA-FRAMING-2026-09-17.md` (the uncrop). **Supersedes:** the
*fit and the single ratio* both notes pin — `object-fit:contain` inside one fixed
4:3 frame. The no-blind-crop contract they were written to protect is kept, and is
the reason this pass is a ladder rather than a straight `cover`.

## The brief

> "product images are tiny i want them to be edge-edge in side image container card"

The complaint is geometrically exact. A card's `.card-media` frame was one uniform
4:3 box with the artwork inside it at `object-fit:contain`, so every cover floated
on the site mat:

| Cover | Painted in the 4:3 frame @1440 | Frame | What the shopper sees |
|---|---|---|---|
| 3:2 landscape banner (34 of 51) | 273 × 182.0 | 273 × 204.8 | 11.1% of the frame is dark mat, in two bands |
| 16:9 planner banner (1) | 273 × 153.6 | 273 × 204.8 | 25% mat |
| 1:1 (1) | 204.8 × 204.8 | 273 × 204.8 | 25% mat, left and right |
| 0.793 portrait cover (2) | **162.3 × 204.8** | 273 × 204.8 | **41% of the frame is mat**, a gutter down each side |
| 0.563 portrait (Morocco itinerary) | **115.3 × 204.8** | 273 × 204.8 | **58% mat** |

The 2026-09-20 morning pass had already lifted mean fill to 83.9% by shortening the
frame; the 16.1% that was left is what this brief is about. Nothing in the artwork
was small — the *frames* were bigger than their art.

## The first answer, and why it was not shipped

The instruction reads as `object-fit:cover`, and that was tried on the numbers
first. A cover of ratio `R` in a frame of ratio `F` keeps `min(F,R)/max(F,R)` of
its area, so **one** frame ratio charged to **51 different** ratios costs, over the
real `cardW`/`cardH` in `data/products.json`:

* mean **16.1%** of the cover's box cropped (13.5% of its painted content, measured
  with a content bounding box over the `.webp` files);
* **5 of 51** covers would stay under 5% loss, and 10 land at 25–58%;
* the 10 worst are precisely the ones that must not be cut — `morocco-7-day-itinerary`
  (57.8%), both ebook covers (43.1–43.8%), `mindfulness-system-planner` (42.1%), the four
  portrait brush packs and the portrait bundle (34.8–38.2%), `wellness-journal-2026`
  (25%) and the 16:9 planner (25%). Every one of them carries its product name, a
  ribbon or a feature-icon row baked into the artwork's own edge: a centred crop
  takes the title and the icon row together. This is the exact failure
  `docs/CARD-MEDIA-FRAMING-2026-09-17.md` was written after — the Master Library
  ribbon arriving as "PICK".

Full bleed is therefore kept, and the fixed ratio is what goes.

## The fix — a ladder, chosen per cover

**1 · The frame (`tools/core.py`).** `media_rung(w, h)` snaps a cover to the rung
of a 7-step ladder whose ratio costs it least (ties to the wider rung, which keeps
rows shorter): **16:9, 3:2, 4:3, 1:1, 4:5, 3:4, 2:3**. `product_card` prints it as
one extra class — `class="card-media media-4x5"` — and nothing else about the card
changes: same markup, same `width`/`height` attributes, same `srcset`/`sizes`, same
`.card-top` badge row, same lazy loading.

**2 · The CSS (`css/style.css`).** The media img becomes `object-fit:cover` with
`object-position:center`, and seven one-property rules give each rung its
`aspect-ratio`. `.card-media` itself keeps `aspect-ratio:4/3` as the fallback for a
cover with no recorded sizes (the vector coming-soon placeholder). The `portrait-cover`
ring, its `overflow:visible` and its `#popular` filter carve-outs are deleted with the
mat they were drawn on: an edge-to-edge cover has no bare frame left to justify a ring.
The hover zoom stays out of the file on purpose — with `cover`, a 6% zoom is 6% of the
artwork's edge cropped, i.e. the old bug deferred to mouseover.

**3 · Rows.** Rungs are shared, not per-card, so the grid keeps rhythm: 35 of the 51
covers sit on 3:2, 5 on 4:3, 5 on 4:5, 3 on 3:4, one each on 16:9, 1:1 and 2:3. A row
that mixes bands still keeps **one card height** — `align-items:stretch` is the grid
default and `.card-foot{margin-top:auto}` pins price and CTA to the bottom, so the
difference is absorbed by the text block, not by ragged cards.

## The measurement (after)

Frame geometry at 1440 (catalog grid `.grid.cards`: wrap 1200 − 40 padding, 4-up,
20px gaps, the card's 1px border → media 273 wide):

| Rung | Covers | Frame @1440 | Worst crop in the rung | Painted area vs the 4:3 mat frame |
|---|---|---|---|---|
| 16/9 | 1 | 273 × 153.6 | 0.0% | 1.00× (band gone) |
| 3/2 | 35 | 273 × 182.0 | 4.8% | 1.00× (band gone) |
| 4/3 | 5 | 273 × 204.8 | 1.4% | 1.00× |
| 1/1 | 1 | 273 × 273.0 | 0.0% | **1.78×** |
| 4/5 | 5 | 273 × 341.3 | 1.1% | **2.80×** |
| 3/4 | 3 | 273 × 364.0 | 2.9% | **3.16×** |
| 2/3 | 1 | 273 × 409.5 | 15.6% | **4.73×** |

* Mean crop **16.1% → 0.6%** of the cover's box (13.5% → 0.4% of painted content).
* Covers losing under 5%: **5 of 51 → 50 of 51.**
* Fill is 100% everywhere by construction: no mat gutter on any product card on the
  site, at any viewport, for any of the 409 built `.card-media` elements.
* The nine portrait covers are the ones that answer the brief: linearly ~1.7× bigger
  (162.3 × 204.8 → 273 × 341.3) while showing 99% of their own artwork.
* The 3:2 landscapes keep the exact pixels they had — they were already width-bound —
  so what changes for them is the removal of two 5.6% mat bands, and the card is
  22.8px shorter at 1440. The frame got tighter; the artwork did not get smaller.

Reproduce both passes with `python3 tools/card_frame_measure.py` (sections 1–4 are the
replaced frames, section 5 the shipped ladder) and see the result composed from the
real `-card.webp` files with `python3 tools/card_frame_mock.py shots/card-frame-edge-to-edge.png`
(A = 4:3 + contain, B = rung + cover). This sandbox has no browser and cannot install
one, so the numbers are the same arithmetic Chromium runs, derived from the shipped CSS
box rules and the intrinsic artwork sizes — the reasoning `card_frame_measure.py`
documents, unchanged.

## What is pinned

`tools/verify.py`, all computed from `data/products.json` and the built HTML — never a
hard-coded expectation:

1. **81** — `.card-media img` must be `object-fit:cover` and never `contain`; the
   frame keeps `overflow:hidden` and `padding:0`, and carries no `transform` (no
   hover re-crop).
2. **new** — all seven rungs `media_rung()` can name have a frame rule at that exact
   ratio. A rung the builder can emit and the CSS does not define would silently fall
   back to 4:3 and bring the gutter back for that cover.
3. the mat must not be painted over (`background:none` on the img) — still load-bearing
   for the placeholder cover on the fallback frame.
4. **82b** — the crop the ladder chooses costs the artwork ≤2% on average, ≥50 of 51
   covers under 5%, and nothing over 17%.
5. **new** — every built `.card-media` carries the rung its own cover picked (409 of
   409), and no badge sits inside a frame.
6. **88** — the `#popular` row still takes the shared frame and its rung: a scoped
   finish, never a second frame.

## What this deliberately does not fix

`morocco-7-day-itinerary` (750 × 1333, ratio 0.563) is the one cover full bleed
cannot serve: its own 2:3 rung still costs 15.6% of the artwork, because a 1:1.78
tall image inside the widest portrait frame the site uses must lose something. Two
ways to make it whole, both owner calls and neither a CSS exception:

* re-render that card at **2:3** (750 × 1125) — a rung-identical, lossless frame;
* or give it and any future portrait artwork its own row (`classes="grid cards"` with
  a portrait-aware subset), where a single frame ratio can be 2:3 outright.

Same note as the 16:9 planner in the 4:3 pass: an outlier ratio is an asset problem,
not a reason to fork the frame.
