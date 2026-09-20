#!/usr/bin/env python3
"""
DigiKitPro — product-card frame measurement (4:3 pass, 2026-09-20).

    python3 tools/card_frame_measure.py                # 390 / 768 / 1024 / 1440
    python3 tools/card_frame_measure.py 320 390 768 1024 1440 1920

What it measures
----------------
Every `.card-media` product frame on the site, before (the old 1:1 square) and
after (the shipped 4:3 frame), at each viewport:

  frame      the media box: width from the grid rules, height from the frame's
             own `aspect-ratio`
  artwork    the box an `object-fit:contain` image actually paints into
             (scale = min(frame_w / R, frame_h), R = cardW / cardH of the real
             artwork in data/products.json)
  fill       artwork area ÷ frame area, as a percentage

Why this is computed rather than screenshotted
----------------------------------------------
This sandbox has no browser and cannot install one: every browser-binary CDN
(`cdn.playwright.dev`, `storage.googleapis.com`, `objects.githubusercontent.com`)
and the Debian apt mirror are unreachable, and Chromium's shared libraries
(`libnss3`, `libatk`, `libgbm`, `libxkbcommon`, `libcups`) are absent. So the
numbers below are derived from the shipped CSS box rules plus the intrinsic
artwork sizes — the same arithmetic Chromium's `object-fit: contain` performs
(exact ratio scaling, no approximation) over the same grid geometry
(`--wrap:1200px`, 20px wrap padding, `.grid` gaps, the `.cards`/`.cards-4`
column breakpoints, the card's 1px border).

Two things that are exact here and do not need a renderer:
  • fill % — the frame ratio is fixed at 4:3 at every width and the media is
    width-driven, so a cover's fill is min(4/3,R)/max(4/3,R): width-invariant.
  • the grid maths — column counts, gaps, wrap padding and the card border are
    plain arithmetic on integer px values.

The one judgement call is the scrollbar: headless Chromium on Linux reserves a
15px classic scrollbar on a page that overflows (the repo's earlier sweep
measured 1200 as "1185" for exactly this reason). Both variants are printed,
labelled `vw` (overlay scrollbars / mobile) and `-15` (classic scrollbar).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WRAP_MAX = 1200          # .wrap{max-width:var(--wrap)}
WRAP_PAD = 20            # .wrap{padding:0 20px}
CARD_BORDER = 1          # .card{border:1px solid var(--border)} — each side
FRAME_BEFORE = 1 / 1     # the old .card-media{aspect-ratio:1/1}
FRAME_AFTER = 4 / 3      # the shipped .card-media{aspect-ratio:4/3}
PORTRAIT_MAX = 0.95      # .card-media.portrait-cover threshold (cardW/cardH)
FILL_TARGET = 0.85       # "fills the frame" — the prototype's >=85% bar

# ── the grids that carry product cards ───────────────────────────────────
# (label, column rules [(min-width, cols)], gap px per range)
SURFACES = [
    ("catalog / category / season / guides / PDP related  (.grid.cards)",
     [(0, 1), (560, 2), (960, 3), (1280, 4)], 20.0),
    ("homepage #popular best sellers  (.grid.cards.cards-4)",
     [(0, 1), (560, 2), (1080, 4)], 22.4),
]
CARDS4_GAP_WIDE = 32.0   # .grid.cards-4{...gap:2rem} from 1080px


def layout_width(vw: int, scrollbar: bool) -> int:
    return vw - (15 if scrollbar else 0)


def content_width(vw: int, scrollbar: bool) -> int:
    return min(layout_width(vw, scrollbar), WRAP_MAX) - 2 * WRAP_PAD


def cols_for(rules: list[tuple[int, int]], vw: int) -> int:
    n = 1
    for min_w, c in sorted(rules):
        if vw >= min_w:
            n = c
    return n


def gap_for(label: str, vw: int) -> float:
    if label.startswith("homepage") and cols_for([(0, 1), (560, 2), (1080, 4)], vw) == 4:
        return CARDS4_GAP_WIDE
    return SURFACES[1][2] if label.startswith("homepage") else 20.0


def card_width(vw: int, scrollbar: bool, rules, gap: float) -> float:
    n = cols_for(rules, vw)
    return (content_width(vw, scrollbar) - (n - 1) * gap) / n


def media_width(vw: int, scrollbar: bool, rules, gap: float) -> float:
    return card_width(vw, scrollbar, rules, gap) - 2 * CARD_BORDER


def frame(vw: int, scrollbar: bool, rules, gap: float, ratio: float) -> tuple[float, float]:
    """(w, h) of the media frame for a given frame ratio."""
    w = media_width(vw, scrollbar, rules, gap)
    return w, w / ratio


def artwork(fw: float, fh: float, r: float) -> tuple[float, float]:
    """The painted box of an object-fit:contain image of ratio r — exactly what
    Chromium computes: uniform scale = min(fw/r, fh) (fh == fw/r_h, so the
    short edge decides)."""
    if fw / fh >= r:          # artwork is narrower than the frame -> height-bound
        ah = fh
        aw = fh * r
    else:                     # artwork is wider -> width-bound
        aw = fw
        ah = fw / r
    return aw, ah


def fill(fw: float, fh: float, r: float) -> float:
    aw, ah = artwork(fw, fh, r)
    return (aw * ah) / (fw * fh)


def load_products() -> list[dict]:
    out = []
    for p in json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8")):
        im = p.get("images") or {}
        w, h = im.get("cardW"), im.get("cardH")
        if not w or not h:
            continue
        out.append({"slug": p["slug"], "name": p["name"], "w": w, "h": h, "r": w / h})
    return out


def band(r: float) -> str:
    """The catalog's real artwork groups (cardW/cardH), named by ratio."""
    if r < PORTRAIT_MAX:
        return "portrait <0.95"
    if abs(r - 1) < 0.005:
        return "square 1:1"
    if abs(r - 1.5) < 0.01:
        return "landscape 3:2"
    if abs(r - 1.3335) < 0.005 or abs(r - 1.315) < 0.005 or abs(r - 1.429) < 0.005:
        return "landscape 4:3-ish"
    return "landscape 16:9"


def main(argv: list[str]) -> int:
    views = [int(a) for a in argv[1:]] or [390, 768, 1024, 1440]
    products = load_products()
    n = len(products)

    print(f"DigiKitPro product-card frame measurement — {n} products, "
          f"viewports {', '.join(str(v) for v in views)}\n")

    # ── 1. frame geometry per viewport ───────────────────────────────────
    print("1. FRAME GEOMETRY (shipped 4:3 frame)\n")
    for label, rules, _gap in SURFACES:
        print(f"  {label}")
        print(f"    {'vw':>6} {'cols':>5} {'card':>8} {'frame w×h':>16} "
              f"{'3:2 art':>14} {'portrait 0.793 art':>20}")
        for vw in views:
            for sb, tag in ((False, ""), (True, " -15")):
                if sb and vw < 560:
                    continue
                g = gap_for(label, vw)
                cw = card_width(vw, sb, rules, g)
                fw, fh = frame(vw, sb, rules, g, FRAME_AFTER)
                a32 = artwork(fw, fh, 1.5)
                apo = artwork(fw, fh, 750 / 946)
                print(f"    {str(vw) + tag:>6} {cols_for(rules, vw):>5} {cw:>8.1f} "
                      f"{fw:>7.1f}×{fh:<8.1f} {a32[0]:>6.1f}×{a32[1]:<7.1f} "
                      f"{apo[0]:>8.1f}×{apo[1]:<10.1f}")
        print()

    # ── 2. fill by artwork band, before vs after ─────────────────────────
    bands: dict[str, list[dict]] = {}
    for p in products:
        bands.setdefault(band(p["r"]), []).append(p)

    print("2. FILL BY ARTWORK BAND (fill % is width-invariant: the frame ratio is "
          "fixed and the media is width-driven)\n")
    print(f"  {'band':<20} {'n':>3} {'before 1:1':>12} {'after 4:3':>12} {'Δ':>8}   products")
    for b in ("landscape 3:2", "landscape 4:3-ish", "landscape 16:9",
              "square 1:1", "portrait <0.95"):
        rows = bands.get(b) or []
        if not rows:
            continue
        before = sum(fill(1, 1, p["r"]) for p in rows) / len(rows)
        after = sum(fill(FRAME_AFTER, 1, p["r"]) for p in rows) / len(rows)
        delta = (after - before) * 100
        sample = ", ".join(p["slug"] for p in rows[:2]) + ("…" if len(rows) > 2 else "")
        print(f"  {b:<20} {len(rows):>3} {before * 100:>11.1f}% {after * 100:>11.1f}% "
              f"{delta:>+7.1f}%   {sample}")
    print()

    # ── 3. the headline count ────────────────────────────────────────────
    before85 = sum(1 for p in products if fill(1, 1, p["r"]) >= FILL_TARGET)
    after85 = sum(1 for p in products if fill(FRAME_AFTER, 1, p["r"]) >= FILL_TARGET)
    mean_before = sum(fill(1, 1, p["r"]) for p in products) / n
    mean_after = sum(fill(FRAME_AFTER, 1, p["r"]) for p in products) / n
    print("3. COVERS AT >=85% FILL\n")
    print(f"  before 1:1 square : {before85}/{n}   mean fill {mean_before * 100:.1f}%")
    print(f"  after  4:3 frame  : {after85}/{n}   mean fill {mean_after * 100:.1f}%   "
          f"({after85 - before85:+d} covers)\n")

    portraits = [p for p in products if p["r"] < PORTRAIT_MAX]
    print(f"  the {len(portraits)} portrait covers (ratio < {PORTRAIT_MAX}) — ringed, "
          f"not counted as failures:")
    for p in sorted(portraits, key=lambda x: x["r"]):
        print(f"    {p['slug']:<42} {p['w']}×{p['h']}  r={p['r']:.3f}  "
              f"fill {fill(FRAME_AFTER, 1, p['r']) * 100:>4.1f}%  "
              f"(was {fill(1, 1, p['r']) * 100:>4.1f}% in the square)")
    print()

    # ── 4. absolute sizes at each viewport ───────────────────────────────
    print("4. RENDERED ARTWORK PX (catalog grid, 3:2 landscape vs portrait 0.793)\n")
    rules = SURFACES[0][1]
    print(f"  {'layout':>8} {'cols':>5} {'frame':>14} {'3:2 artwork':>16} "
          f"{'portrait artwork':>18}")
    for vw in views:
        for sb, tag in ((False, "vw"), (True, "-15")):
            if sb and vw < 560:
                continue
            g = gap_for(SURFACES[0][0], vw)
            fw, fh = frame(vw, sb, rules, g, FRAME_AFTER)
            fb, fhb = frame(vw, sb, rules, g, FRAME_BEFORE)
            a32 = artwork(fw, fh, 1.5)
            apo = artwork(fw, fh, 750 / 946)
            b32 = artwork(fb, fhb, 1.5)
            print(f"  {str(vw) + ' ' + tag:>8} {cols_for(rules, vw):>5} "
                  f"{fw:>6.1f}×{fh:<7.1f} {a32[0]:>7.1f}×{a32[1]:<8.1f} "
                  f"{apo[0]:>8.1f}×{apo[1]:<9.1f}    (1:1 was {b32[0]:.1f}×{b32[1]:.1f})")
    print()
    print("   Note: a contained 3:2 banner is width-bound in the 4:3 frame, so it "
          "paints the\n   frame's full width; a portrait cover is height-bound, so it "
          "paints the frame's\n   full height and wears the ring at its own width.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
