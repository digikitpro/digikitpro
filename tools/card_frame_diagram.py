#!/usr/bin/env python3
"""
DigiKitPro — product-card frame diagram (4:3 pass, 2026-09-20).

    python3 tools/card_frame_diagram.py [viewport]

Writes shots/product-cards-frame-4x3-geometry-<viewport>.svg: a to-scale
diagram of the old 1:1 frame next to the shipped 4:3 frame for one
representative cover per artwork band, with the pixels object-fit:contain
actually paints drawn inside each frame. The geometry comes from
tools/card_frame_measure.py (grid rules from css/style.css, artwork ratios from
data/products.json), so the picture cannot drift from the numbers.

This is a geometry diagram, NOT a screenshot: this sandbox has no browser and
cannot install one (see the header of tools/card_frame_measure.py). It is a
scratch artifact — shots/ is gitignored on purpose.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import card_frame_measure as m  # noqa: E402

PAD, GAP, TOP = 18, 34, 66
SCALE = 0.30
HEIGHT = 246

# one representative cover per artwork band, with its real product name
PICKS = [
    ("landscape 3:2 — 34 covers", 1.5, "e.g. Master Library (750×500)"),
    ("landscape 4:3-ish — 6 covers", 4 / 3, "e.g. Organic Watercolor (580×435)"),
    ("landscape 16:9 — 1 cover", 750 / 422, "Ultimate Fitness Planner"),
    ("square 1:1 — 1 cover", 1.0, "Wellness Journal 2026"),
    ("portrait — 9 covers", 750 / 946, "e.g. Portrait Skin Brushes"),
    ("portrait 0.56 — the extreme", 750 / 1333, "Morocco 7-Day Itinerary"),
]


def art(r: float, fw: float, fh: float) -> tuple[float, float]:
    """object-fit:contain — the painted box, exactly as a browser computes it."""
    if fw / fh >= r:
        return fh * r, fh
    return fw, fw / r


def build(vw: int) -> str:
    rules = m.SURFACES[0][1]
    gap = 20.0
    fw_px, fh_px = m.frame(vw, False, rules, gap, m.FRAME_AFTER)
    bw_px, bh_px = m.frame(vw, False, rules, gap, m.FRAME_BEFORE)
    cols = m.cols_for(rules, vw)
    FW, FH = fw_px * SCALE, fh_px * SCALE
    BW, BH = bw_px * SCALE, bh_px * SCALE
    pair = BW + 10 + FW
    cell_w = pair + GAP
    W = PAD * 2 + cell_w * len(PICKS)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{HEIGHT}" '
        f'viewBox="0 0 {W:.0f} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#121216"/>',
        '<style>text{font:11px Manrope,-apple-system,Segoe UI,sans-serif;fill:#AAA7A0}'
        '.h{font:600 13.5px Georgia,serif;fill:#C9A86A}'
        '.s{font-size:9.5px;fill:#7d7a73}'
        '.lbl{font-size:10.5px;fill:#F5F2EB}</style>',
        f'<text x="{PAD}" y="24" class="h">Product-card frame geometry — measured, not rendered '
        f'({vw}px viewport, {cols}-up, media {fw_px:.0f}px wide)</text>',
        f'<text x="{PAD}" y="40" class="s">Each pair: old 1:1 square &#183; shipped 4:3 frame. '
        f'The gold rect inside a frame is the box object-fit:contain paints — nothing is ever cropped or stretched.</text>',
        f'<text x="{PAD}" y="54" class="s">portrait covers wear the ebook-style gold ring + shadow '
        f'(drawn with a bright edge) so a narrower cover reads as a framed book.</text>',
    ]
    y0 = TOP
    for i, (label, r, sub) in enumerate(PICKS):
        x = PAD + i * cell_w
        # ── old 1:1 ──
        aw, ah = art(r, BW, BH)
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{BW:.1f}" height="{BH:.1f}" '
                   f'fill="#1B1B20" stroke="#2b2b31"/>')
        out.append(f'<rect x="{x + (BW - aw) / 2:.1f}" y="{y0 + (BH - ah) / 2:.1f}" '
                   f'width="{aw:.1f}" height="{ah:.1f}" fill="#3A3324" stroke="#C9A86A" '
                   f'stroke-opacity=".5"/>')
        out.append(f'<text x="{x:.1f}" y="{y0 + max(BH, FH) + 14:.1f}" class="s">'
                   f'{aw * ah / (BW * BH) * 100:.0f}% of 1:1</text>')
        # ── shipped 4:3 ──
        x2 = x + BW + 10
        aw2, ah2 = art(r, FW, FH)
        out.append(f'<rect x="{x2:.1f}" y="{y0}" width="{FW:.1f}" height="{FH:.1f}" '
                   f'fill="#1B1B20" stroke="#2b2b31"/>')
        ring = ' rx="3"' if r < m.PORTRAIT_MAX else ''
        sw = ' stroke-width="1.8"' if r < m.PORTRAIT_MAX else ''
        out.append(f'<rect x="{x2 + (FW - aw2) / 2:.1f}" y="{y0 + (FH - ah2) / 2:.1f}" '
                   f'width="{aw2:.1f}" height="{ah2:.1f}" fill="#443A1F" stroke="#C9A86A" '
                   f'stroke-opacity=".92"{ring}{sw}/>')
        out.append(f'<text x="{x2:.1f}" y="{y0 + max(BH, FH) + 14:.1f}" class="s">'
                   f'{aw2 * ah2 / (FW * FH) * 100:.0f}% of 4:3</text>')
        out.append(f'<text x="{x:.1f}" y="{y0 + max(BH, FH) + 32:.1f}" class="lbl">{label}</text>')
        out.append(f'<text x="{x:.1f}" y="{y0 + max(BH, FH) + 45:.1f}" class="s">{sub}</text>')
    out.append(f'<text x="{PAD}" y="{HEIGHT - 9}" class="s">'
               f'frame {fw_px:.0f}&#215;{fh_px:.0f}px (was {bw_px:.0f}&#215;{bh_px:.0f}px) &#183; '
               f'a 3:2 banner paints the same pixels in both frames — the mat around it is what shrank &#183; '
               f'source: data/products.json cardW/cardH + css/style.css .card-media</text>')
    out.append('</svg>')
    return "\n".join(out)


def main(argv: list[str]) -> int:
    vw = int(argv[1]) if len(argv) > 1 else 1440
    dest = ROOT / "shots" / f"product-cards-frame-4x3-geometry-{vw}.svg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(vw), encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
