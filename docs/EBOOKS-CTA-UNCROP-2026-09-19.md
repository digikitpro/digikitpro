# Starter Guide & Masterclass — the CTA pills were being cut in half

**Date:** 2026-09-19 · **Files:** `css/style.css` (+ `tools/verify.py`, checks 83–84)
**Follows:** the 2026-09-17 card-media uncrop (PR #37 lineage) — same class of bug,
one layer down: not artwork cropped by a frame this time, but **buttons cropped by
their own card**.

## The report

"Starter Guide & Masterclass — buttons CTA buttons are cropped."

## What was actually happening

The `#ebooks` section renders two horizontal book-feature cards (`.ebook-card`).
Three rules combine:

1. `.ebooks-grid .ebook-card` is `flex-direction:row` at **every** width — the
   cards never stack, so the fixed 150px cover dock keeps claiming its slice
   down to the smallest phone.
2. `.ebooks-grid .ebook-foot` holds the price, the CTA pill (`.btn .btn-sm`)
   and a `.text-link` together in one `flex-wrap:wrap` row. The link is
   `white-space:nowrap` (base `.text-link`), the pill cannot shrink below its
   label, and no child had a `max-width` — so whenever the label was wider
   than the pitch column, the item just overflowed.
3. The card itself is `overflow:hidden` (rounded corners + the edu-deep gold
   top bar), so the overflow was **clipped flush at the card edge** — a
   half-pill, not a wrapped row. And `html,body{overflow-x:clip}` hid the
   evidence from the scrollbar too.

## The measurement

Glyph advances measured from the site's own fonts (`assets/fonts/manrope-normal.woff2`,
wght 600, instanced with fontTools) at the exact computed sizes — `.btn-sm`
13.12px, `.text-link` 14.72px, `.price` 16.32px — plus real padding/border,
per Chrome box sizing:

| Item | Text width | Box incl. padding |
|---|---|---|
| `.price` `$19.00` | 48.9px | 48.9px |
| btn `View Masterclass` | 109.1px | **144.7px** (137.1px ≤640px) |
| link `Buy on Payhip ↗` | 111.7px | **111.7px** |
| btn `Get Free ↗` | 65.3px | 100.9px (92.9px ≤640px) |
| link `View guide →` | 90.0px | **90.0px** |

Available pitch-column width (`viewport − cover − body padding`):

| Viewport | Cover | Column | `View Masterclass` | Outcome |
|---|---|---|---|---|
| 360px | 150px | **132.8px** | 137.1px | **clipped (−4.3px)** |
| 390px | 150px | 162.8px | 137.1px | fits, 25px spare |
| 320px | 150px | **92.8px** | 137.1px / link 111.7px | **both clipped** |
| ≥640px | 220px | 334.8px+ (single-col) · 192.8–252.8px (two-col ≥980px) | 144.7px | fits everywhere (two-col wraps to two lines) |

So the visible break is the Step 2 card at ≈360px CSS width and narrower —
exactly a standard phone. (Text-scale bumps or fallback fonts widen the
labels and pull the break up toward 390px.)

## The fix (`css/style.css`, ebooks block)

Two layers, so the class of bug is closed rather than this one instance:

- **No foot child can outgrow its row, anywhere.**
  `.ebook-foot>*{max-width:100%;min-width:0}`, the pill gets
  `flex:0 1 auto;white-space:normal`, the link
  `flex:0 1 auto;white-space:normal;overflow-wrap:anywhere`, the price stays
  `flex:0 0 auto`. A long label now wraps inside the pill instead of pushing
  it under the clip.
- **Below 480px the card stops starving the column.** The cover dock narrows
  to 116px, and both CTAs go `flex:1 1 100%` full-width, centred — a
  deliberate stack (price → gold CTA → link) that reads as design, not
  damage. Verified by simulation at every 1px-critical width 320–1920:
  no item, and no flex line, exceeds the column.

The cards' horizontal book layout, the mat, the gold frame and every hover
behaviour are untouched; nothing above 480px changed except the caps that
were no-ops there.

## Guardrails

`tools/verify.py` grew to **84 checks**: #83 pins the caps (no `.ebook-foot`
child may exceed the row; pill and link must be wrappable), #84 pins the
narrow-phone geometry (cover ≤120px, CTAs full width below 480px). Same
pattern as the 2026-09-17 card-media checks, so the two plausible wrong
"fixes" — `overflow:visible` on the card (unsquares the cover mat) and
leaving the 150px dock on small phones — both fail the suite.
