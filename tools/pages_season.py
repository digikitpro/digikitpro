#!/usr/bin/env python3
"""Seasonal hub pages (Halloween, Christmas) for seasonal Procreate art searches.

These pages collect the relevant seasonal products that already exist in
data/products.json, plus companion effect brushes and helpful guides. All
product facts (counts, formats, compatibility) come straight from the product
data, so nothing is invented.
"""
from core import *
from pages_blog import load_articles

SEASON_DEFS = [
    {
        "slug": "halloween",
        "name": "Halloween",
        "seo_title": "Halloween Procreate Brushes & Spooky PNG Art Pack | DigiKitPro",
        "seo_desc": "Seasonal Halloween art assets for Procreate and iPad artists: a 300 DPI spooky pumpkin PNG illustration pack, plus glow, smoke and sparkle brushes for atmospheric autumn artwork.",
        "h1": "Halloween Procreate Brushes & Spooky Season Art",
        "eyebrow": "Seasonal collection",
        "intro": "Seasonal artwork runs on atmosphere: jack-o-lantern glow, rolling fog, moonlit silhouettes and a little glitter never hurt a pumpkin. This hub gathers the DigiKitPro assets that fit a Halloween workflow, starting with a ready-made spooky pumpkin illustration pack and the effect brushes that sell the mood.",
        "pack_label": "The Halloween pack",
        "pack_intro": "The centerpiece is a ready-to-use set of spooky pumpkin illustrations, delivered as high-resolution PNGs that drop into any design app as image layers.",
        "effects_label": "Brushes for mood and atmosphere",
        "effects_intro": "Pair the illustrations with smoke, glow and glitter brushes to build fog, candlelight and magical sparkle around your Halloween scenes.",
        "products_pack": ["halloween-pumpkin-bundle"],
        "products_effects": ["smoke-brushes-12", "glitter-brushes-sparkle-shine-30"],
        "guides": ["halloween-procreate-tutorial", "how-to-install-procreate-brushes", "best-procreate-brushes-for-beginners"],
        "ideas_title": "Ways to use the Halloween pack",
        "ideas": [
            "Import a PNG pumpkin illustration as a layer and paint glow, fog or sparkle behind it.",
            "Build party invitations, social posts or sticker sheets on a 300 DPI canvas.",
            "Combine pumpkins with smoke and glitter brushes for haunted, moonlit scenes.",
        ],
        "faq": [
            ("What is in the Halloween Spooky Pumpkin Bundle?",
             "The Halloween Spooky Pumpkin Bundle contains 20 pumpkin-themed PNG illustrations at 300 DPI. The artwork covers spooky scenes with witches, skulls, bats, ghosts, haunted houses, cauldrons and more."),
            ("Do I need Procreate to use the Halloween PNG pack?",
             "No. The Halloween pack ships as PNG image files, so you can import them into Procreate or any other app that accepts images, such as Canva, Photoshop or Affinity. The brush kits sold on DigiKitPro do require Procreate on iPad."),
            ("How are the Halloween files delivered?",
             "Checkout is handled by Payhip and the files are delivered as an instant digital download after payment. There is no shipping and no physical product. A download link is emailed to you and is also available from your Payhip account."),
            ("Can I use these assets in commercial Halloween designs?",
             "DigiKitPro digital products include a license for use in personal and commercial artwork under the terms on the Terms page. You may not resell, redistribute or share the image files themselves."),
        ],
    },
    {
        "slug": "christmas",
        "name": "Christmas",
        "seo_title": "Christmas Procreate Brushes, Stamps & Washi Tapes | DigiKitPro",
        "seo_desc": "Festive Procreate brush bundle for Christmas and holiday art: 173 Christmas stamps and brushes, 44 hand-drawn washi tapes, glitter papers, photo frames, chalkboards and more for iPad.",
        "h1": "Christmas Procreate Brushes & Holiday Art Bundle",
        "eyebrow": "Seasonal collection",
        "intro": "Holiday cards, gift tags, digital journal spreads and festive lettering all come together faster with dedicated seasonal stamps. This hub collects the DigiKitPro Christmas bundle alongside the sparkle and chalk brushes that pair well with winter artwork.",
        "pack_label": "The Christmas bundle",
        "pack_intro": "A large festive pack built for Procreate: Christmas stamps and brushes, hand-drawn washi tape brushes, glitter papers, frames and chalkboards, with an installation guide included.",
        "effects_label": "Brushes that pair with holiday art",
        "effects_intro": "Add shimmer with glitter brushes and a hand-lettered chalkboard look with free chalk brushes for cards, tags and seasonal layouts.",
        "products_pack": ["christmas-brushes-bundle"],
        "products_effects": ["glitter-brushes-sparkle-shine-30", "free-chalkboard-artists-toolkit"],
        "guides": ["christmas-procreate-tutorial", "how-to-install-procreate-brushes", "best-procreate-brushes-for-beginners"],
        "ideas_title": "Ways to use the Christmas bundle",
        "ideas": [
            "Stamp Christmas decor and florals, then layer colors and resize the shapes for cards and tags.",
            "Use the 44 washi tape brushes to tape down photos and notes in digital journal spreads.",
            "Try the glitter papers, photo frames and chalkboards for scrapbooking and social media designs.",
        ],
        "faq": [
            ("What is inside the Christmas Procreate Brushes Bundle?",
             "The Christmas bundle includes 173 Christmas stamps and brushes (decor, shapes, cookie-cutter shapes, embellishments, brushes and floral stamps), 44 hand-drawn Christmas washi tape brushes, and bonus items: 2 photo frames, 5 glitter papers, 4 Christmas photo frames in PNG and AI format, 5 chalkboards, an installation guide and brush-setting instructions."),
            ("What app do I need for the Christmas brush bundle?",
             "The brushes and stamps are made for Procreate on iPad, and the product notes recommend Procreate 5 or later. The bonus PNG and AI files can also be opened in other design apps that support those formats."),
            ("How do I install the Christmas brushes?",
             "Unzip the download, then send the .brushset file to your iPad (AirDrop on a Mac, or a file transfer service such as Dropbox on Windows). In the Files app, tap the .brushset file and choose to open it in Procreate; the brush pack installs automatically. The bundle includes a full installation guide."),
            ("What can I make with the Christmas bundle?",
             "The pack is versatile for scrapbooking, social media designs, chalk lettering, card making and digital journaling. Mix the stamps, brushes and washi tapes, change colors in separate layers, and adjust sizes for different layouts."),
        ],
    },
]


def _faq_schema(defs):
    return [{"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q,
                             "acceptedAnswer": {"@type": "Answer", "text": a}}
                            for q, a in defs["faq"]]}]


def build_seasons():
    all_articles = {a["slug"]: a for a in load_articles()}

    for sdef in SEASON_DEFS:
        slug = sdef["slug"]
        depth = 2

        pack_products = [BY_SLUG[s] for s in sdef["products_pack"] if s in BY_SLUG]
        effect_products = [BY_SLUG[s] for s in sdef["products_effects"] if s in BY_SLUG]
        guides = [all_articles[s] for s in sdef.get("guides", []) if s in all_articles]

        other = [s for s in SEASON_DEFS if s["slug"] != slug]
        pills = "".join(f'<a class="trend-pill" href="../{o["slug"]}/">{esc(o["name"])} art</a>' for o in other)
        pills += '<a class="trend-pill" href="../../bundles.html">All bundles</a>'
        pills += '<a class="trend-pill" href="../../freebies.html">Free brushes</a>'
        season_pills = f"""<div class="trend-pills-wrap" style="margin:2.5rem 0 0">
  <p class="trend-label">More seasonal art &amp; tools</p>
  <div class="trend-pills">{pills}</div>
</div>"""

        # Ideas list
        ideas_html = "".join(f"<li>{esc(i)}</li>" for i in sdef["ideas"])
        ideas_block = f"""<section class="section section-alt" aria-labelledby="season-ideas-title">
  <div class="wrap narrow prose">
    <p class="eyebrow">Seasonal workflow</p>
    <h2 id="season-ideas-title">{esc(sdef["ideas_title"])}</h2>
    <ul>{ideas_html}</ul>
  </div>
</section>"""

        # Guides
        guide_links = ""
        if guides:
            gcards = "".join(
                f'<a class="art-card art-card-sm" href="../../blog/{g["slug"]}/">'
                f'<div class="art-body"><span class="art-cat">{esc(g.get("category", "Guide"))}</span>'
                f'<h3>{esc(g["title"])}</h3>'
                f'<p class="muted">{esc(g.get("description", ""))}</p>'
                f'<span class="text-link">Read tutorial &rarr;</span></div></a>'
                for g in guides
            )
            guide_links = f"""<section class="section" aria-labelledby="season-guides-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">Technique &amp; Tutorials</p><h2 id="season-guides-title">Guides to help you use these packs</h2></div>
      <a class="text-link" href="../../blog.html">All articles &rarr;</a>
    </div>
    <div class="grid arts-grid">{gcards}</div>
  </div>
</section>"""

        # Visible FAQ (also emitted as FAQPage structured data for answer engines)
        faq_items = "".join(
            f"<div class=\"faq-item\"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>"
            for q, a in sdef["faq"]
        )
        faq_block = f"""<section class="section section-alt" aria-labelledby="season-faq-title">
  <div class="wrap narrow prose">
    <p class="eyebrow">Questions, answered</p>
    <h2 id="season-faq-title">{esc(sdef['name'])} pack FAQ</h2>
    {faq_items}
  </div>
</section>"""

        canonical = absurl(f"season/{slug}/")
        schemas = schema_breadcrumb([
            ("Home", "/"),
            (sdef["name"] + " art", f"/season/{slug}/"),
        ])
        schemas += schema_itemlist(pack_products + effect_products)
        schemas += _faq_schema(sdef)

        pack_grid = product_grid(pack_products, depth, eager_first=1) if pack_products else ""
        effects_grid = product_grid(effect_products, depth) if effect_products else ""

        html_out = head(
            sdef["seo_title"],
            sdef["seo_desc"],
            canonical,
            depth,
            schemas=schemas,
        )
        html_out += header(depth, active="products.html")
        html_out += f"""
<main id="main">
  <section class="page-head">
    <div class="wrap">
      {crumbs(depth, [(sdef["name"] + " art", f"season/{slug}/")])}
      <p class="eyebrow">{esc(sdef["eyebrow"])}</p>
      <h1>{esc(sdef["h1"])}</h1>
      <p class="lead">{esc(sdef["intro"])}</p>
      {season_pills}
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Seasonal pack</p><h2>{esc(sdef["pack_label"])}</h2></div>
      </div>
      <p class="muted" style="max-width:62ch;margin-top:-1rem">{esc(sdef["pack_intro"])}</p>
      {pack_grid}
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Companion tools</p><h2>{esc(sdef["effects_label"])}</h2></div>
        <a class="text-link" href="../../products.html">All products &rarr;</a>
      </div>
      <p class="muted" style="max-width:62ch;margin-top:-1rem">{esc(sdef["effects_intro"])}</p>
      {effects_grid}
    </div>
  </section>

  {ideas_block}
  {guide_links}
  {faq_block}
  {newsletter(depth)}
</main>
{footer(depth)}"""

        write(f"season/{slug}/index.html", html_out)

    print(f"Built {len(SEASON_DEFS)} seasonal hub pages successfully.")
