#!/usr/bin/env python3
"""Dedicated category landing pages for Procreate search visibility."""
import os
from core import *
from pages_blog import load_articles

CATEGORY_DEFS = [
    {
        "slug": "portrait",
        "name": "Portrait Brushes",
        "category_key": "Portrait",
        "seo_title": "Procreate Portrait Brushes | DigiKitPro Studio",
        "seo_desc": "Hand-crafted Procreate portrait brushes for iPad artists. Sketch, blend, paint skin tones, and render expressive portrait artwork.",
        "h1": "Procreate Portrait Brushes",
        "eyebrow": "Portrait studio collection",
        "intro": "Painting portraits on the iPad requires brush tools that mimic the subtlety of physical media. DigiKitPro portrait brush sets are tuned for the Apple Pencil with realistic pressure response, so you can transition smoothly from preliminary layout sketches to luminous skin rendering and expressive facial features.",
        "guides": ["best-procreate-brushes-for-portraits", "how-to-create-realistic-skin-in-procreate", "procreate-portrait-workflow"]
    },
    {
        "slug": "skin-texture",
        "name": "Skin Texture Brushes",
        "category_key": "Skin Texture",
        "seo_title": "Procreate Skin Texture Brushes | DigiKitPro",
        "seo_desc": "Realistic Procreate skin texture brushes for pores, freckles, wrinkles, and blemishes. Hand-tested for lifelike portrait rendering on iPad.",
        "h1": "Procreate Skin Texture Brushes",
        "eyebrow": "Realistic portrait textures",
        "intro": "Smooth, flat colors make digital portraits look synthetic. These skin texture brushes add authentic pores, micro-textures, freckles, and delicate wrinkles without muddying your underlying color values. Built specifically to work with Procreate blending modes and Apple Pencil tilt.",
        "guides": ["how-to-create-realistic-skin-texture-in-procreate", "how-to-create-realistic-skin-in-procreate", "procreate-blending-brushes-guide"]
    },
    {
        "slug": "line-art",
        "name": "Line Art Brushes",
        "category_key": "Line Art",
        "seo_title": "Procreate Line Art Brushes | DigiKitPro Studio",
        "seo_desc": "Smooth, responsive Procreate inking and line art brushes. Clean taper, steady stroke control, and textured inks for iPad illustrators.",
        "h1": "Procreate Line Art Brushes",
        "eyebrow": "Inking and linework kits",
        "intro": "Confident lines require brushes with clean pressure tapers and predictable stroke stabilization. Our line art brush collection ranges from razor-sharp technical pens and studio inkers to free fine-liner pens and vintage marker pens suitable for comic illustration, concept sketching, and tattoo flash art.",
        "guides": ["best-procreate-brushes-for-line-art", "tattoo-design-in-procreate", "how-to-install-procreate-brushes"]
    },
    {
        "slug": "watercolor",
        "name": "Watercolor Brushes",
        "category_key": "Watercolor",
        "seo_title": "Procreate Watercolor Brushes | DigiKitPro",
        "seo_desc": "Realistic watercolor brushes for Procreate. Natural pigment bleeds, wet-on-wet pooling, paper grain, and organic edge granulation on iPad.",
        "h1": "Procreate Watercolor Brushes",
        "eyebrow": "Traditional watercolor simulation",
        "intro": "Real watercolor breathes: pigment pools along drying contours, colors feather into wet paper, and granulation settles into the paper tooth. DigiKitPro watercolor brush kits capture these organic characteristics for Procreate artists who want the feel of handmade watercolor sketches.",
        "guides": ["how-to-create-realistic-watercolor-in-procreate", "how-to-make-digital-art-look-traditional"]
    },
    {
        "slug": "anime",
        "name": "Anime & Manga Brushes",
        "category_key": "Anime",
        "seo_title": "Procreate Anime & Manga Brushes | DigiKitPro",
        "seo_desc": "Specialized Procreate anime and manga brushes: clean G-pen liners, soft shading blenders, glow passes, and character illustration tools.",
        "h1": "Procreate Anime & Manga Brushes",
        "eyebrow": "Anime illustration kits",
        "intro": "Modern anime illustration balances crisp line work with glowing ambient light and soft color gradients. These kits include character-focused inking pens, hair strand shaders, and luminous highlight brushes tuned for character art, light novel illustrations, and webtoon production.",
        "guides": ["best-procreate-brushes-for-anime", "how-to-paint-realistic-hair-in-procreate"]
    },
    {
        "slug": "hair",
        "name": "Hair & Hairstyle Brushes",
        "category_key": "Hair",
        "seo_title": "Procreate Hair Brushes & Stamps | DigiKitPro",
        "seo_desc": "Procreate hair brushes and hairstyle stamps for digital portraiture. Block volume, paint dynamic strands, and add flyaway details quickly.",
        "h1": "Procreate Hair Brushes & Stamps",
        "eyebrow": "Strand and volume kits",
        "intro": "Painting believable hair strand by strand can take hours and produce stiff, wire-like shapes. Our hair brushes and foundation stamps allow you to establish masses first, render light across flowing locks, and place individual highlights and wisps where they catch the eye.",
        "guides": ["how-to-paint-realistic-hair-in-procreate", "stamp-brushes-vs-painting-brushes"]
    },
    {
        "slug": "glitter-effects",
        "name": "Glitter & Effects Brushes",
        "category_key": "Glitter & Effects",
        "seo_title": "Procreate Glitter & FX Brushes | DigiKitPro",
        "seo_desc": "Sparkle, glitter, smoke, and texture brushes for Procreate. Add luminous light effects, atmospheric dust, and shimmer to digital artwork.",
        "h1": "Procreate Glitter & Effects Brushes",
        "eyebrow": "Visual effects and textures",
        "intro": "When a digital illustration needs magical atmosphere or surface shimmer, dedicated effect brushes save time. From metallic glitter and dust particles to smoke wisps and tie-dye patterns, these tools bring dimensional excitement to finished iPad drawings.",
        "guides": ["how-to-make-digital-art-look-traditional"]
    },
    {
        "slug": "figure-drawing",
        "name": "Figure Drawing & Pose Stamps",
        "category_key": "Figure Drawing",
        "seo_title": "Procreate Pose & Figure Drawing Brushes | DigiKitPro",
        "seo_desc": "Anatomical figure drawing stamps and dynamic pose brushes for Procreate. Speed up character layout, proportioning, and anatomy studies.",
        "h1": "Figure Drawing & Pose Stamps",
        "eyebrow": "Anatomy and character layout",
        "intro": "Constructing dynamic human figures requires solid anatomy and quick iteration. These pose stamps and figure drawing brushes provide clean anatomical guidelines for male and female characters, letting concept artists and illustrators block out proportions with accuracy.",
        "guides": ["stamp-brushes-vs-painting-brushes", "procreate-portrait-workflow"]
    },
    {
        "slug": "traditional",
        "name": "Traditional Media Brushes",
        "category_key": "Traditional",
        "seo_title": "Traditional Art Brushes for Procreate | DigiKitPro",
        "seo_desc": "Authentic charcoal, pastel, sketchbook pencil, and chalkboard brushes for Procreate. Natural paper textures and responsive pressure feel.",
        "h1": "Traditional Art Brushes for Procreate",
        "eyebrow": "Charcoal, pencil and paper textures",
        "intro": "Many digital paintings look too clean. Our traditional media collection brings back honest tooth, charcoal dust, velvety pastel smudges, and real paper texture to your iPad sketchbook, preserving the tactile charm of physical studio materials.",
        "guides": ["how-to-make-digital-art-look-traditional", "best-procreate-brushes-for-beginners"]
    },
    {
        "slug": "sketching",
        "name": "Sketching Brushes",
        "category_key": "Sketching",
        "seo_title": "Procreate Sketching Brushes | DigiKitPro Studio",
        "seo_desc": "Responsive sketching pencils and digital sketchbooks for Procreate. Natural tilt shading, graphite grain, and gesture drawing tools on iPad.",
        "h1": "Procreate Sketching Brushes",
        "eyebrow": "Graphite and gesture tools",
        "intro": "The initial sketch is where every creative concept begins. DigiKitPro sketching brushes respond accurately to Apple Pencil tilt and pressure, giving illustrators the organic drag and grain of graphite on paper for gesture studies, architectural layouts, and concept art.",
        "guides": ["best-procreate-brushes-for-beginners", "procreate-portrait-workflow"]
    }
]

def build_categories():
    all_articles = {a["slug"]: a for a in load_articles()}
    
    for cdef in CATEGORY_DEFS:
        cslug = cdef["slug"]
        depth = 2
        
        # Filter matching products
        key = cdef["category_key"]
        cat_products = [p for p in PRODUCTS if p.get("category") == key]
        if not cat_products:
            # Fallback check for related products
            cat_products = [p for p in PRODUCTS if key.lower() in p.get("name", "").lower() or key.lower() in " ".join(p.get("tags", [])).lower()]
        
        # Related guides
        guides = [all_articles[s] for s in cdef.get("guides", []) if s in all_articles]
        guide_links = ""
        if guides:
            gcards = "".join(
                f'<a class="art-card art-card-sm" href="../../blog/{g["slug"]}/">'
                f'<div class="art-body"><span class="art-cat">{esc(g.get("category", "Guide"))}</span>'
                f'<h3>{esc(g["title"])}</h3>'
                f'<p class="muted">{esc(g.get("description", ""))}</p>'
                f'<span class="text-link">Read tutorial →</span></div></a>'
                for g in guides
            )
            guide_links = f"""<section class="section section-alt" aria-labelledby="cat-guides-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">Technique & Tutorials</p><h2 id="cat-guides-title">Related Procreate Guides</h2></div>
      <a class="text-link" href="../../blog.html">All articles →</a>
    </div>
    <div class="grid arts-grid">{gcards}</div>
  </div>
</section>"""

        # Other category pills
        other_cats = [c for c in CATEGORY_DEFS if c["slug"] != cslug]
        cat_pills = "".join(f'<a class="trend-pill" href="../{c["slug"]}/">{esc(c["name"])}</a>' for c in other_cats[:7])
        other_cats_html = f"""<div class="trend-pills-wrap" style="margin:2.5rem 0 0">
  <p class="trend-label">Explore other brush categories</p>
  <div class="trend-pills">{cat_pills}</div>
</div>"""

        canonical = absurl(f"category/{cslug}/")
        
        # Schemas
        schemas = schema_breadcrumb([
            ("Home", "/"),
            ("Products", "/products.html"),
            (cdef["name"], f"/category/{cslug}/")
        ])
        schemas += schema_itemlist(cat_products)

        # Products grid
        grid_html = product_grid(cat_products, depth, eager_first=2) if cat_products else '<p class="muted">Products coming soon.</p>'

        html_out = head(
            cdef["seo_title"],
            cdef["seo_desc"],
            canonical,
            depth,
            schemas=schemas
        )
        html_out += header(depth, active="products.html")
        html_out += f"""
<main id="main">
  <section class="page-head">
    <div class="wrap">
      {crumbs(depth, [("Products", "products.html"), (cdef["name"], f"category/{cslug}/")])}
      <p class="eyebrow">{esc(cdef["eyebrow"])}</p>
      <h1>{esc(cdef["h1"])}</h1>
      <p class="lead">{esc(cdef["intro"])}</p>
      {other_cats_html}
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">Kits & Tools</p><h2>Available Brush Packs ({len(cat_products)})</h2></div>
        <a class="text-link" href="../../products.html">All products →</a>
      </div>
      {grid_html}
    </div>
  </section>

  {guide_links}
  {newsletter(depth)}
</main>
"""
        html_out += footer(depth)
        
        out_dir = f"category/{cslug}"
        write(f"{out_dir}/index.html", html_out)

    print(f"Built {len(CATEGORY_DEFS)} dedicated category landing pages successfully.")
