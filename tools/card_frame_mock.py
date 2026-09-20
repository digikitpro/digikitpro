#!/usr/bin/env python3
"""Before/after evidence for the product-card image container.

  A  the frame this mock was written against: one 4:3 box, object-fit:contain,
     artwork centred on the site mat — the read that came back as "the product
     images are tiny" (42-61% of the frame for a portrait cover).
  B  the shipped rule: each card's frame takes the rung of the 7-step ladder
     closest to its own cover's ratio and the image is object-fit:cover, so the
     artwork touches all four edges and the centred crop costs what it has to.

PIL composition of the real -card.webp artwork at the real catalog geometry.
B reproduces core.media_rung() exactly, so what is drawn here is what CSS does;
the sandbox has no browser, which is why the numbers are computed (see
card_frame_measure.py, whose section 5 prints the same ladder with crop costs).

    python3 tools/card_frame_mock.py shots/card-frame-edge-to-edge.png
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
CARD_W = 275            # (1160 content - 3*20 gap) / 4 at 1440px, 4-up .cards
BORDER = 1
MW = CARD_W - 2 * BORDER
GAP = 20
FRAME_NOW = 4 / 3       # the replaced frame: .card-media{aspect-ratio:4/3} + contain
PORTRAIT_MAX = 0.95     # the replaced .card-media.portrait-cover threshold
sys.path.insert(0, str(ROOT / "tools"))
from core import MEDIA_RUNGS, media_rung          # the shipped ladder, same source
RUNG_F = dict((n, f) for f, n, _css in MEDIA_RUNGS)
BODY = 150

BG, SURF, MAT, BORD, GOLD = (10, 10, 12), (20, 20, 23), (27, 27, 32), (41, 41, 47), (201, 168, 106)


def art(slug):
    d = ROOT / "assets" / "products" / slug
    f = sorted(x for x in os.listdir(d) if x.endswith("-card.webp"))[0]
    return Image.open(d / f).convert("RGB")


def media(img, mode):
    """Return the painted media box for one cover under a given framing rule."""
    w, h = img.size
    r = w / h
    if mode == "now":
        fh = round(MW / FRAME_NOW)
        box = Image.new("RGB", (MW, fh), MAT)
        if r < PORTRAIT_MAX:              # the ringed portrait-cover variant
            th, tw = fh, round(fh * r)
        else:                             # landscape: width fills, height follows
            tw, th = MW, round(MW / r)
        box.paste(img.resize((max(1, tw), max(1, th))), ((MW - tw) // 2, (fh - th) // 2))
        return box, tw * th
    rung = media_rung(w, h)               # shipped: cover, inside the cover's own rung
    fh = round(MW / RUNG_F[rung])
    scale = max(MW / w, fh / h)           # object-fit:cover
    sw, sh = w * scale, h * scale
    ox, oy = round((sw - MW) / 2), round((sh - fh) / 2)
    box = img.resize((round(sw), round(sh))).crop((ox, oy, ox + MW, oy + fh))
    return box, MW * fh


def img_size(slug):
    p = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    for q in p:
        if q["slug"] == slug:
            im = q.get("images") or {}
            return im.get("cardW") or 750, im.get("cardH") or 500
    return 750, 500


def row(mode):
    W = 4 * CARD_W + 3 * GAP + 40
    boxes = [media(art(s), mode) for s in SLUGS]
    H = max(b[0].height for b in boxes) + BODY + 6
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    x = 20
    for (slug, (box, area)) in zip(SLUGS, boxes):
        fh = box.height
        im.paste(box, (x, 0))
        dr.rectangle([x - BORDER, 0, x + MW + BORDER, H], outline=BORD, width=1)
        dr.rectangle([x, fh, x + MW, H], fill=SURF)
        dr.rectangle([x, fh, x + MW, fh + BODY], fill=SURF)
        dr.text((x + 9, fh + 12), slug.replace("-", " ")[:26], fill=(150, 146, 136))
        dr.text((x + 9, fh + 32), "Product title line for this kit", fill=(236, 232, 224))
        dr.text((x + 9, fh + 52), "$5.00", fill=GOLD)
        dr.text((x + 9, fh + BODY - 24),
                ("fill %d%%  ·  4:3 + contain" % (100 * area / (MW * fh))) if mode == "now"
                else ("rung media-%s  ·  cover" % media_rung(*img_size(slug))), fill=(120, 118, 110))
        x += CARD_W + GAP
    return im


SLUGS = ["portrait-skin-brushes-procreate", "anime-soft-style-studio-kit",
         "ultimate-portrait-mastery-bundle", "glitter-brushes-sparkle-shine-30"]

out = sys.argv[1] if len(sys.argv) > 1 else "shots/card-frame-mock.png"
a, b = row("now"), row("prop")
W, H = max(a.width, b.width), a.height + b.height + 86
canvas = Image.new("RGB", (W, H), (8, 8, 10))
dr = ImageDraw.Draw(canvas)
dr.text((20, 14), "A  BEFORE - one 4:3 frame for every card, contain (mat gutter around the artwork)", fill=(255, 255, 255))
canvas.paste(a, (0, 34))
y2 = 34 + a.height + 26
dr.text((20, y2 - 16), "B  SHIPPED - each frame takes the ladder rung closest to its own cover, cover-filled edge to edge", fill=(255, 255, 255))
canvas.paste(b, (0, y2))
Path(out).parent.mkdir(parents=True, exist_ok=True)
canvas.save(ROOT / out if not Path(out).is_absolute() else out)
print("wrote", out, canvas.size)
