#!/usr/bin/env python3
"""Blog: markdown -> article pages + index."""
import re, os, glob
from core import *

def parse_md(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta, body = m.group(1), m.group(2)
    fm = {}
    for line in meta.strip().split("\n"):
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        fm[k.strip()] = v
    return fm, body

def inline(t, depth=2):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\_(.+?)\_(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((\/[^)]+)\)", lambda m: f'<a href="{rel(depth, m.group(2))}">{m.group(1)}</a>', t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', t)
    return t

def md_to_html(body, depth=2):
    lines = body.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("{{products}}"):
            out.append("__PRODUCTS__"); i += 1; continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:], depth)}</h3>"); i += 1; continue
        if ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:], depth)}</h2>"); i += 1; continue
        if ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(lines[i][2:]); i += 1
            out.append(f"<blockquote>{inline(' '.join(buf), depth)}</blockquote>"); continue
        if re.match(r"^- ", ln):
            buf = []
            while i < len(lines) and re.match(r"^- ", lines[i]):
                buf.append(f"<li>{inline(lines[i][2:], depth)}</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        if re.match(r"^\d+\. ", ln):
            buf = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                clean = re.sub(r"^\d+\. ", "", lines[i])
                buf.append(f"<li>{inline(clean, depth)}</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>"); continue
        buf = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{2,3} |[-≥] |\d+\. |> |\{\{)", lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(buf), depth)}</p>")
    return "\n".join(out)

_ARTICLES = None
def load_articles():
    global _ARTICLES
    if _ARTICLES is not None: return _ARTICLES
    arts = []
    for path in glob.glob(os.path.join(ROOT, "content/blog/*.md")):
        fm, body = parse_md(path)
        fm["body"] = body
        # hero image: the primary linked product's artwork
        prods = [s for s in (fm.get("products") or []) if s in BY_SLUG]
        if prods:
            im = BY_SLUG[prods[0]]["images"] or {}
            card_url, main_url = im.get("card",""), im.get("main","")
            fm["_pslug"], fm["_im"] = prods[0], im
            fm["image"] = card_url if is_abs(card_url) else f"assets/products/{prods[0]}/{card_url}"
            fm["imgW"], fm["imgH"] = im.get("cardW") or 750, im.get("cardH") or 500
            fm["hero"] = main_url if is_abs(main_url) else f"assets/products/{prods[0]}/{main_url}"
            fm["heroW"], fm["heroH"] = im.get("fullW") or 1200, im.get("fullH") or 800
        else: # every article card MUST have a thumbnail → branded fallback
            fm["image"] = "assets/img/og-cover.jpg"
            fm["imgW"], fm["imgH"] = 1200, 630
        arts.append(fm)
    arts.sort(key=lambda a: a.get("date", ""), reverse=True)
    _ARTICLES = arts
    return arts

def tools_mention(fm, depth=2):
    prods = [BY_SLUG[s] for s in fm.get("products", []) if s in BY_SLUG]
    if not prods: return ""
    return f"""<aside class="article-products" aria-labelledby="ap-title">
    <p class="eyebrow">Tools mentioned in this guide</p>
    <h2 id="ap-title">Get the brushes</h2>
    {product_grid(prods, depth, classes="grid cards cards-sm")}
    </aside>"""

def build_blog():
    arts = load_articles()
    # index
    cards = ""
    for a in arts:
        ss = img_srcset(0, a.get("_pslug", ""), a.get("_im") or {}, "(min-width: 1100px) 370px, (min-width: 700px) 45vw, 92vw")
        img = (f'<img class="art-img" src="{a["image"]}"{ss} width="{a.get("imgW",750)}" height="{a.get("imgH",500)}" alt="{esc(a["title"])}" loading="lazy" decoding="async">') if a.get("image") else ""
        cards += f"""<a class="art-card" href="blog/{a['slug']}/">{img}
      <div class="art-body"><span class="art-cat">{esc(a.get('category','Guide'))}</span>
      <h2>{esc(a['title'])}</h2>
      <p class="muted">{esc(a['description'])}</p>
      <span class="text-link">Read article →</span></div>
    </a>"""
    html_out = head("Procreate Tutorials & Digital Art Guides, DigiKitPro Blog",
        "Technique-first guides for iPad artists: realistic skin, hair, watercolor, line art and how to choose the right Procreate brushes.",
        SITE_URL + "/blog.html", 0, schemas=schema_breadcrumb([("Home","/"),("Blog","/blog.html")]))
    html_out += header(0, active="blog.html")
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(0, [("Articles","blog.html")])}
    <p class="eyebrow">Learn the craft</p>
    <h1>Procreate Tutorials & Brush Guides</h1>
    <p class="lead">Original, technique-first articles for iPad artists, every guide tested against real artwork, every recommendation a tool we make and use.</p>
  </div></section>
  <section class="section"><div class="wrap"><div class="grid arts-grid">{cards}</div></div></section>
  {newsletter(0)}
</main>
{footer(0)}"""
    write("blog.html", html_out)

    # articles
    for a in arts:
        depth = 2
        body_html = md_to_html(a["body"].strip(), depth)
        marker = "__PRODUCTS__"
        tools = tools_mention(a, depth)
        if marker in body_html:
            body_html = body_html.replace(f"<p>{marker}</p>", tools).replace(marker, tools)
        else:
            body_html += tools
        related = [x for x in (a.get("related") or [])]
        rel_arts = [x for x in arts if x["slug"] in related]
        rel_html = ""
        if rel_arts:
            rel_html = """<nav class="article-related" aria-label="Related articles"><p class="eyebrow">Keep reading</p><div class="rel-arts">""" + "".join(
                f'<a class="text-link" href="../{r["slug"]}/">{esc(r["title"])}</a>' for r in rel_arts) + "</div></nav>"
        schemas = schema_article(a) + schema_breadcrumb([("Home","/"),("Blog","/blog.html"),(a["title"], f"/blog/{a['slug']}/")])
        hero_ss = img_srcset(depth, a.get("_pslug",""), a.get("_im") or {}, "(min-width: 860px) 760px, 94vw")
        og_img = (asset_abs(a["products"][0], BY_SLUG[a["products"][0]]["images"]["card"])
                  if a.get("products") and a["products"][0] in BY_SLUG else None)
        raw_title = a['title']
        if len(f"{raw_title} | {SITE_NAME}") > 65:
            t = raw_title
            if " (" in t:
                t = t.split(" (")[0].strip()
            if ":" in t:
                t = t.split(":")[0].strip()
            if len(f"{t} | {SITE_NAME}") > 65 and " for " in t:
                t = t.split(" for ")[0].strip()
            seo_t = f"{t} | {SITE_NAME}" if len(f"{t} | {SITE_NAME}") <= 65 else f"{raw_title[:45]}... | {SITE_NAME}"
        else:
            seo_t = f"{raw_title} | {SITE_NAME}"
        html_out = head(seo_t, a["description"], absurl(f"blog/{a['slug']}/"), depth,
                        schemas=schemas, page_type="article", og_image=og_img)
        html_out += header(depth, active="blog.html")
        html_out += f"""
<main id="main">
  <article class="article wrap">
    {crumbs(depth, [("Articles","blog.html"),(a["title"], f"blog/{a['slug']}/")])}
    <header class="article-head">
      <span class="art-cat">{esc(a.get('category','Guide'))}</span>
      <h1>{esc(a['title'])}</h1>
      <p class="article-meta">By the {SITE_NAME} studio · <time datetime="{a['date']}">{a['date']}</time></p>
    </header>
    {f'<figure class="article-hero"><img src="{a["hero"] if is_abs(a["hero"]) else rel(depth, a["hero"])}"{hero_ss} width="{a.get("heroW",1200)}" height="{a.get("heroH",800)}" alt="{esc(a["title"])}" fetchpriority="high" decoding="async"><figcaption>Artwork shown: {esc(BY_SLUG[a["products"][0]]["name"]) if a.get("products") else SITE_NAME}</figcaption></figure>' if a.get('hero') else ''}
    <div class="prose article-body">{body_html}</div>
    {rel_html}
    <nav class="article-nav" aria-label="More articles"><a class="btn btn-line" href="../../blog.html">← All articles</a><a class="btn btn-gold" href="../../products.html">Browse brushes</a></nav>
  </article>
  {newsletter(depth)}
</main>
{footer(depth)}"""
        write(f"blog/{a['slug']}/index.html", html_out)
