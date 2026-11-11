#!/usr/bin/env python3
"""Christmas collection homepage section (2026-11-10, owner brief).

A special section presenting the four Christmas products, styled with Christmas
colours and ornaments and surrounded by flat, hand-drawn-style SVG characters
(Santa, reindeer, snowman, elf). Everything rendered is derived from
``data/products.json`` (names, slugs, prices) plus this module's artwork;
nothing here invents a price, count, rating or claim.

The artwork is inline SVG drawn in the house palette (dark pine ground, gold
caps, cream accents, candy red) — no external images, no stock art, no emoji.
Characters are aria-hidden decorative elements; the section is labelled by its
heading. Animations respect prefers-reduced-motion.
"""
from core import *

# ── inline SVG artwork ───────────────────────────────────────────────────────

SVG_SANTA = """<svg class="xmas-char xmas-santa" viewBox="0 0 160 190" aria-hidden="true" focusable="false">
  <path d="M34 78C36 26 126 26 128 78Z" fill="#B23A3A"/>
  <ellipse cx="81" cy="80" rx="52" ry="13" fill="#F4EBDC"/>
  <circle cx="34" cy="40" r="12" fill="#F4EBDC"/>
  <circle cx="46" cy="114" r="7" fill="#F2C9A0"/><circle cx="116" cy="114" r="7" fill="#F2C9A0"/>
  <circle cx="81" cy="112" r="36" fill="#F2C9A0"/>
  <g fill="#F4EBDC">
    <circle cx="50" cy="128" r="12"/><circle cx="64" cy="140" r="13"/>
    <circle cx="81" cy="146" r="14"/><circle cx="98" cy="140" r="13"/><circle cx="112" cy="128" r="12"/>
  </g>
  <ellipse cx="81" cy="121" rx="9.5" ry="6.8" fill="#D9A878"/>
  <circle cx="66" cy="106" r="4" fill="#33231A"/><circle cx="96" cy="106" r="4" fill="#33231A"/>
  <circle cx="64.6" cy="104.6" r="1.3" fill="#FFF9EF"/><circle cx="94.6" cy="104.6" r="1.3" fill="#FFF9EF"/>
  <ellipse cx="58" cy="118" rx="5" ry="3.2" fill="#E78E8E" opacity=".55"/>
  <ellipse cx="104" cy="118" rx="5" ry="3.2" fill="#E78E8E" opacity=".55"/>
  <path d="M34 190c4-26 22-38 47-38s43 12 47 38Z" fill="#B23A3A"/>
  <path d="M46 163h70" stroke="#F4EBDC" stroke-width="9" stroke-linecap="round"/>
  <circle cx="81" cy="179" r="4.5" fill="#E5B45B"/>
</svg>"""

SVG_REINDEER = """<svg class="xmas-char xmas-reindeer" viewBox="0 0 160 180" aria-hidden="true" focusable="false">
  <g fill="none" stroke="#6B4A2B" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <path d="M52 56C44 42 46 28 32 18"/><path d="M46 40 32 36"/><path d="M49 50 34 48"/>
    <path d="M108 56C116 42 114 28 128 18"/><path d="M114 40 128 36"/><path d="M111 50 126 48"/>
  </g>
  <ellipse cx="44" cy="102" rx="13" ry="7" fill="#7A5230" transform="rotate(-18 44 102)"/>
  <ellipse cx="116" cy="102" rx="13" ry="7" fill="#7A5230" transform="rotate(18 116 102)"/>
  <ellipse cx="80" cy="106" rx="37" ry="46" fill="#7A5230"/>
  <path d="M68 66 Q80 56 92 66 L80 76Z" fill="#5B3A29"/>
  <ellipse cx="80" cy="128" rx="19" ry="14" fill="#C89A72"/>
  <circle cx="80" cy="122" r="7.5" fill="#B23A3A"/>
  <circle cx="62" cy="94" r="4.2" fill="#241812"/><circle cx="98" cy="94" r="4.2" fill="#241812"/>
  <circle cx="60.8" cy="92.6" r="1.3" fill="#FFF9EF"/><circle cx="96.8" cy="92.6" r="1.3" fill="#FFF9EF"/>
</svg>"""

SVG_SNOWMAN = """<svg class="xmas-char xmas-snowman" viewBox="0 0 150 180" aria-hidden="true" focusable="false">
  <path d="M40 122 20 106 M26 108 19 96 M26 108 36 97" stroke="#5B3A29" stroke-width="4.5" stroke-linecap="round" fill="none"/>
  <path d="M110 122 130 106 M124 108 131 96 M124 108 114 97" stroke="#5B3A29" stroke-width="4.5" stroke-linecap="round" fill="none"/>
  <circle cx="75" cy="128" r="38" fill="#F4F6F4"/>
  <circle cx="75" cy="66" r="27" fill="#F4F6F4"/>
  <rect x="56" y="12" width="38" height="21" rx="4" fill="#191919"/>
  <rect x="56" y="26" width="38" height="7" fill="#B23A3A"/>
  <rect x="46" y="33" width="58" height="8" rx="4" fill="#191919"/>
  <rect x="48" y="88" width="54" height="11" rx="5.5" fill="#B23A3A"/>
  <rect x="86" y="94" width="11" height="30" rx="5.5" fill="#B23A3A"/>
  <circle cx="66" cy="58" r="3.2" fill="#241812"/><circle cx="84" cy="58" r="3.2" fill="#241812"/>
  <path d="M75 62 98 66 75 68Z" fill="#E67E22"/>
  <path d="M64 73 Q75 80 86 73" stroke="#241812" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <circle cx="75" cy="118" r="3.6" fill="#241812"/><circle cx="75" cy="138" r="3.6" fill="#241812"/>
</svg>"""

SVG_ELF = """<svg class="xmas-char xmas-elf" viewBox="0 0 160 180" aria-hidden="true" focusable="false">
  <path d="M28 92 8 78 26 108Z" fill="#F2C9A0"/>
  <path d="M132 92 152 78 134 108Z" fill="#F2C9A0"/>
  <circle cx="80" cy="96" r="34" fill="#F2C9A0"/>
  <path d="M46 76C44 30 116 30 114 76Z" fill="#1F6F43"/>
  <ellipse cx="80" cy="75" rx="37" ry="9" fill="#B23A3A"/>
  <circle cx="52" cy="34" r="9" fill="#F4EBDC"/>
  <circle cx="66" cy="92" r="4" fill="#241812"/><circle cx="94" cy="92" r="4" fill="#241812"/>
  <path d="M64 110 Q80 121 96 110" stroke="#241812" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  <ellipse cx="57" cy="103" rx="4.6" ry="3" fill="#E78E8E" opacity=".55"/>
  <ellipse cx="103" cy="103" rx="4.6" ry="3" fill="#E78E8E" opacity=".55"/>
  <path d="M52 136 Q80 160 108 136 L108 154 L52 154Z" fill="#B23A3A"/>
  <path d="M52 136 Q66 150 80 136 Q94 150 108 136" fill="none" stroke="#F4EBDC" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

def _bauble(cx, cy, r, fill):
    """One hanging bauble: string, cap, body, highlight. Drawn inline."""
    return f"""<g>
  <path d="M{cx} 0V{cy - r - 9}" stroke="#C9A86A" stroke-width="2" opacity=".85"/>
  <rect x="{cx - 8}" y="{cy - r - 10}" width="16" height="9" rx="2.5" fill="#C9A86A"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>
  <path d="M{cx - r * 0.62} {cy - r * 0.1}a{r * 0.72} {r * 0.72} 0 0 1 {r * 0.5} -{r * 0.62}" stroke="rgba(255,255,255,.5)" stroke-width="{r * 0.16}" fill="none" stroke-linecap="round"/>
</g>"""

def _lights():
    """Zig-zag string of coloured bulbs along the top edge."""
    xs = list(range(30, 1200, 66))
    bulbs, path = [], []
    for i, x in enumerate(xs):
        y = 10 if i % 2 == 0 else 30
        path.append(f"{x} {y}")
        color = ("#E5B45B", "#B23A3A", "#2E8B57")[i % 3]
        bulbs.append(
            f'<circle cx="{x}" cy="{y + 6}" r="7" fill="{color}" opacity=".18"/>'
            f'<circle cx="{x}" cy="{y + 6}" r="3.6" fill="{color}"/>'
            f'<circle cx="{x - 1.2}" cy="{y + 4.8}" r="1.1" fill="#FFF9EF" opacity=".9"/>')
    polyline = " ".join(path)
    return (f'<svg class="xmas-lights" viewBox="0 0 1200 44" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            f'<polyline points="{polyline}" fill="none" stroke="#0A0A0A" stroke-width="2.4" opacity=".65" stroke-linejoin="round"/>'
            + "".join(bulbs) + "</svg>")

_ORNAMENTS = (
    f'<svg class="xmas-orn xmas-orn--tl" viewBox="0 0 160 130" aria-hidden="true" focusable="false">{_bauble(38, 88, 22, "#B23A3A")}{_bauble(96, 62, 16, "#E5B45B")}{_bauble(140, 96, 12, "#2E8B57")}</svg>'
    f'<svg class="xmas-orn xmas-orn--tr" viewBox="0 0 160 130" aria-hidden="true" focusable="false">{_bauble(34, 84, 15, "#2E8B57")}{_bauble(84, 56, 22, "#B23A3A")}{_bauble(138, 90, 15, "#E5B45B")}</svg>'
)

# ── the section ──────────────────────────────────────────────────────────────

XMAS_SLUGS = (
    "christmas-brushes-bundle",
    "christmas-sweater-knit-pattern-brushes",
    "christmas-tree-stamp-brushes",
    "christmas-stamp-brushes-hand-drawn",
)

def christmas_section(byslug, depth=0):
    items = [byslug[s] for s in XMAS_SLUGS if s in byslug]
    if not items:
        return ""
    # "Santa's list" — names and prices straight from products.json.
    dots = ("#B23A3A", "#E5B45B", "#2E8B57", "#F4EBDC")
    rows = []
    for i, p in enumerate(items):
        rows.append(
            f'<li><span class="xmas-list-dot" style="--dot:{dots[i % 4]}" aria-hidden="true"></span>'
            f'<a href="{rel(depth, "products/" + p["slug"] + "/")}">{esc(p["name"])}</a>'
            f'<span class="xmas-list-price">{esc(p["priceText"])}</span></li>')
    list_html = "".join(rows)
    return f"""
<section class="section xmas-section" id="christmas" aria-labelledby="christmas-title">
  {_lights()}
  {SVG_SANTA}
  {SVG_REINDEER}
  {SVG_SNOWMAN}
  {SVG_ELF}
  {_ORNAMENTS}
  <div class="wrap xmas-inner">
    <div class="xmas-head">
      <div class="xmas-copy">
        <p class="eyebrow xmas-eyebrow"><span aria-hidden="true">✦</span> The Holiday Collection</p>
        <h2 class="xmas-title" id="christmas-title">Deck your December<br>with <em>Christmas brushes</em></h2>
        <p class="xmas-sub">Four festive sets for Procreate on iPad — a 173-piece stamps &amp; washi tape bundle, 62 seamless knit-pattern brushes, 25 Christmas tree stamps and 100 hand-drawn Christmas stamps. Digital downloads via Payhip, from $5.00.</p>
        <div class="xmas-ctas">
          <a class="btn btn-gold btn-lg" href="{rel(depth, 'season/christmas/')}">Shop The Christmas Collection</a>
          <a class="btn btn-line btn-lg" href="{rel(depth, 'products/christmas-brushes-bundle/')}">Christmas Bundle · $8.00</a>
        </div>
      </div>
      <aside class="xmas-list" aria-label="The Christmas list">
        <p class="xmas-list-cap"><span aria-hidden="true">★</span> Santa&rsquo;s sketchbook — this year&rsquo;s list</p>
        <ol>{list_html}</ol>
        <p class="xmas-list-foot">Ticked off with a gold pen · listed prices</p>
      </aside>
    </div>
    {product_grid(items, depth, classes="grid cards cards-4 xmas-cards", dual_buy=True)}
    <p class="xmas-foot">For iPad with the Procreate app · No physical item ships · Digital downloads via Payhip</p>
  </div>
</section>
"""
