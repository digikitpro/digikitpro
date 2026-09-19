# Starter Guide & Masterclass — the CTA pills were being cut in half

**Date:** 2026-09-19 · **Files:** `css/style.css` (+ `tools/verify.py`, checks 83–86)
**Follows:** the 2026-09-17 card-media uncrop (PR #37 lineage) — same class of bug,
one layer down: not artwork cropped by a frame this time, but **buttons cropped by
their own card**.

**Two passes.** Round 1 (below, checks 83–84) stopped the cut in the geometry of
the day. Round 2 (at the end, checks 85–86) removes the clip that caused it in
the first place, and with it the whole class of bug.

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

(Round 2 revisits that first "wrong fix": it is wrong *bare*, and correct once
the mat and the gold bar carry their own corners. See below — #85 still fails
a bare `overflow:visible`.)

---

## Round 2 — the no-clip spec (checks 85–86)

Round 1 made the CTA fit; the clip was still the mechanism. Anything that ever
outgrew its row would be sliced at the card edge again — that is exactly how
the pills died the first time. Round 2 removes the mechanism.

**`.ebooks-grid .ebook-card` no longer crops: `overflow:visible;height:auto`.**
Nothing a card holds — CTA, label, badge, cover shadow, or anything added
later — can be cut by the card. Two decorations used to lean on that clip and
now round themselves:

| Leaned on the clip | Now |
|---|---|
| cover-dock mat (square corners, clipped by the card) | `border-radius:calc(var(--radius) - 1px) 0 0 calc(var(--radius) - 1px)` — the card's inner corner (14px − 1px border), left side only, since its right edge meets the body and not a corner |
| edu-deep gold top bar (3px absolute strip) | box is `height:calc(var(--radius) - 1px)`, only its top 3px are painted (`… top/100% 3px no-repeat`), `pointer-events:none` |

A 3px strip cannot carry a 13px radius — CSS scales a radius down when it
exceeds the box, so the strip spills past the card's rounded corner. A
corner-tall box with a 3px paint has the card's arc *exactly*: no clip, no
spill, and the bar is decoration only, so it can never eat a click.

**The two-up grid engages from 1080px, not 980px.** With no clip as a safety
net, two-up may only run where a card can hold its own CTA row. Columns below
are card − 2px of border − 220px cover − 1.2/1.5rem body padding; the price
and the pill need 208.0px on one line (48.9 + 14.4 gap + 144.7):

| Grid | Card | Pitch column | price + pill (208.0px) | Foot | Description |
|---|---|---|---|---|---|
| 980–1010px, old 980px rule | 458.0–473.0px | 192.8–207.8px | **did not fit** — price and pill on separate lines | 4 lines | 6 lines |
| 1011–1079px, old rule | 473.5–507.5px | 208.3–242.3px | fits with 0–34px slack | 3 lines | 5 lines |
| **1080px+, new two-up** | 508.0–518.0px | 242.8–252.8px | fits with 35–45px slack | 3 lines | 5 lines |
| **≤1079px, new one column** | up to 1040px | up to 773.8px | fits, and from 640px the link joins the same line | 2 lines (3 below 640px) | 5 → 2 lines |

So 1080px is the first width where the two-up card holds the row the design
asks for, and where the description keeps a 5-line measure instead of the
6-line squeeze at 192.8px. Below it one full-width card is the roomier layout
rather than a cramped pair.

Measured with round 1's method (fontTools 4.65.0, the site's own
`manrope-normal.woff2` / `playfairdisplay-normal.woff2` instanced at wght 600):
pill text 109.1px → 144.7px box, `$19.00` 48.9px, foot gap 14.4px. The table
reproduces exactly, including the arrows: Manrope carries neither U+2197 nor
U+2192, so `↗`/`→` come from the fallback font (≈0.74em — 10.9px in a link,
9.7px in a pill), which is why round 1's `111.7px` and `65.3px` re-derive
here to the decimal.

**Not touched:** typography, colours, spacing, markup, hover behaviour, the
round-1 caps and the narrow-phone stack, `object-fit:contain` on the covers,
and the rule that no `.ebook-foot` rule may position anything `absolute`.

## Guardrails, second pass

`tools/verify.py` is now **86 checks**. #85 ("ebooks cards crop nothing, by
construction") pins the card's `overflow:visible`/`height:auto`, the
contain-only cover, and both self-rounding decorations — so a bare
`overflow:visible`, the fix round 1 rejected, still fails the suite. #86
("the ebooks grid is one column until 1080px") pins the base `1fr` and the
single `@media(min-width:1080px)` two-up rule, and fails on any straggler
media rule that would widen the grid earlier. #83 was re-titled (assertions
unchanged) because the card no longer clips: the caps now guard the card's
*edge*, which is what keeps a label from spilling out of a card that has
stopped clipping.

All rebuilt pages changed only by the stylesheet cache-bust hash
(`?v=285a9123…` → `?v=0d5fc8f8…`; `tools/core.py` fingerprints the file).
