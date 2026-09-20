# Starter Guide & Masterclass — the covers now fill their dock

**Date:** 2026-09-20 · **Files:** `css/style.css` (ebooks block), `tools/pages_main.py`
(the `<img sizes>` hint), `tools/verify.py` (check 86 re-pinned, check 89 added),
plus the cache-bust hash on every built page.
**Follows:** the 2026-09-19 CTA uncrop (`EBOOKS-CTA-UNCROP-2026-09-19.md`) — the
geometry that pass pinned (a card that crops nothing, a dock that holds its
declared width, a CTA row that always gets its line) is kept whole.

## The brief

Make the cover substantially larger — about 85–90% of the available image
area — with less empty mat around it, at the original 3:4 proportions (no
crop, no stretch), without touching the text column, with the Masterclass
cover visibly dominant (it is the paid product), and with both cards the same
height and alignment.

## What was actually happening

Measured headless (Chromium, the site's own fonts) at 1440px, two-up:

| | dock | art | art ÷ dock area |
|---|---|---|---|
| both cards | 260 × 398.5 | 235.2 × 313.6 | **71%** |

Three things held the cover small:

1. **The grid was a centred 1060px block** inside a 1160px wrap, so two-up
   cards were 518px. After the 2px border, the 1.2/1.5rem body padding and
   the 212.8px pitch column that the price + "View Masterclass" pill needs
   (208px on one line), the dock could not grow past 260px.
2. **The dock inset was 16 / 8.8 / 16 / 16px**, so a 260px dock showed 235px
   of art.
3. **The legacy `.ebook-cover{aspect-ratio:3/4}`** (the old stacked-card rule,
   never reset for the homepage dock) held the dock 4/3 of its width whatever
   the padding — so even a p-padded cover sat in a 4p/3 gap above and below —
   and in two-up the 398.5px body-driven card added a further 42px of mat top
   and bottom.

## The fix (`css/style.css`, ebooks block)

- **The grid spans the wrap.** `#ebooks .ebooks-grid` drops its `max-width:1060px`
  and centring; the cards now sit flush with the section heading and with the
  Best Sellers grid below. Two-up engages at **1200px** (was 1120px; check 86
  still said 1080px — the stale pin is fixed too): the first width where each
  card is 568px, which is a **300px dock plus a 222.8px pitch column — 10px
  more column than before**, so the price + pill keep their line with 7px to
  spare even behind a 15px classic scrollbar (layout 1185px → column 215.3px).
- **An even mat: `padding:var(--dock-pad)`.** The dock resets `aspect-ratio:auto`
  so the cover sets the dock height and nothing is left over. Per card:
  `.edu-deep{--dock-pad:8px}` (Masterclass) and `.edu-start{--dock-pad:12px}`
  (Starter) from 640px; 8px at 480–639px; 6px below 480px.
- **Dock widths per range:** 116px (<480, unchanged — the CTAs need the
  measure), 176px (480–639, was 156), 280px (640–899, was 260), **300px (900+,
  was 260)**.
- **The paid cover is the dominant one:** the tighter mat plus a brighter gold
  ring and a soft gold halo on `.edu-deep .ebook-frame`, deepening on hover.
- **Cover flag** moves to `calc(var(--dock-pad) + 6px)` so it sits just inside
  the cover's corner (the mat is too narrow to hold it now).

`tools/pages_main.py`: the ebooks `<img sizes>` now quotes the rendered widths
(`(min-width: 900px) 284px, (min-width: 640px) 264px, (min-width: 480px) 160px,
104px`) so the browser keeps picking the right `srcset` candidate.

## The measurement (after)

DOM-geometry sweep, headless Chromium, 320–1920px:

| Viewport | Layout | Card | Dock | Masterclass art (fill) | Starter art (fill) | Pitch column | Foot |
|---|---|---|---|---|---|---|---|
| 1200–1920 | two-up | 568 × 396.7 (both) | 300 × 394.7 | 284 × 378.7 (**90.8%**) | 276 × 368 (**85.8%**) | 222.8px | price + pill on one line |
| 1185 (1200 − scrollbar) | two-up | 560.5 × 400.5 | 300 × 398.5 | 284 × 378.7 (90.0%) | 276 × 368 (85.0%) | 215.3px | one line |
| 900–1199 | one column | up to 1159 wide | 300 × 394.7 | 90.8% | 86.4% | 505–804px | one line |
| 640–899 | one column | 600–859 wide | 280 × 368 | 264 × 352 (90.2%) | 256 × 341.3 (85.4%) | 274.8px+ | one line |
| 480–639 | one column, body-driven | | 176 × 233–334 | 160 × 213 (58–83%) | same | 226.8px+ | holds |
| 320–479 | one column, body-driven | | 116 × 307–570 | 104 × 139 | same | unchanged | full-width stack (unchanged) |

Card height in two-up is now set by the Masterclass cover — 396.7px against
the old body-driven 400.5px — and is the same for both cards (one grid row).
No `.ebook-foot` child overflows its row at any width; the foot sits inside
the card everywhere.

Below 640px the cards stay horizontal (the 2026-09-19 decision), so the cover
can only fill the width of its strip (90%), not the body-driven height; the
strip is 176px on small tablets and 116px on phones. A stacked phone card
(cover above the pitch) is the next step if the phone cover should grow too.

## Guardrails

`tools/verify.py` is now **89 checks**. #86 is re-pinned to 1200px. #89
("ebooks covers fill 85–90% of their dock, the paid one fullest") asserts the
full-wrap grid, the `aspect-ratio:auto` + `padding:var(--dock-pad)` dock, both
dock widths, both pads (with the Masterclass strictly tighter), that every
dock × pad pair computes to 85–92% fill by the cover-driven formula, and that
the `<img sizes>` hint quotes dock − 2 × pad. Mutation-tested: re-centring the
grid, a flat pad, a 260px dock, the legacy 3:4 box, a 20px pad and a 1120px
two-up each fail exactly one check.

**Not touched:** typography, copy, colours, the CTA row's caps and the
narrow-phone stack, `object-fit:contain`, the no-clip card, the gold top bar,
the dock's `min-width:0` + explicit basis pair.
