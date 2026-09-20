#!/usr/bin/env python3
"""SEO audit pages — browsable HTML version of docs/seo-audit/ for digikitpro.shop/seo-audit/"""

import os
import re
import glob
from core import *
# md_to_html and parse_md live in pages_blog.py (not core)
try:
    from pages_blog import md_to_html, parse_md
except Exception:
    # Fallback minimal implementations if pages_blog not available during import
    def parse_md(path):
        txt = open(path, encoding="utf-8").read()
        # Simple frontmatter extraction
        if txt.startswith("---"):
            parts = txt.split("---", 2)
            if len(parts) >= 3:
                return {}, parts[2]
        return {}, txt
    def md_to_html(body, depth=2):
        # Very minimal: use core's markdown? Fallback to plain
        return "<pre>" + esc(body[:5000]) + "</pre>"

AUDIT_SRC_DIR = os.path.join(ROOT, "docs/seo-audit")
AUDIT_OUT_DIR = "seo-audit"
AUDIT_URL_PREFIX = "/seo-audit/"

# Order for index page — executive summary first, then numbered
ORDER = [
    "00-executive-summary",
    "01-platform-and-safeguards",
    "02-url-inventory",
    "03-issue-register",
    "04-metadata-schema-linking-gaps",
    "05-assumptions-and-manual-review",
    "06-proposed-architecture",
    "07-monitoring-report",
    "08-approval-gate",
    "CHANGELOG",
]

def _slug_from_filename(fname):
    # docs/seo-audit/00-executive-summary.md -> 00-executive-summary
    base = os.path.splitext(os.path.basename(fname))[0]
    return base.lower().replace("_", "-")

def _title_from_body(body, fallback_slug):
    # Try first H1
    m = re.search(r'^#\s+(.+)$', body, re.M)
    if m:
        return m.group(1).strip()
    # Fallback from slug
    return fallback_slug.replace("-", " ").title()

def _desc_from_body(body, max_len=160):
    # Strip markdown, take first paragraph after H1
    txt = re.sub(r'(?is)<(script|style).*?</\1>', ' ', body)
    # Remove markdown headings, links, etc roughly
    txt = re.sub(r'^#+\s+.*$', '', txt, flags=re.M)
    txt = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', txt)  # [label](url) -> label
    txt = txt.replace("**", "").replace("__", "")
    txt = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', txt)
    txt = re.sub(r'^\s*[-*]\s+', '', txt, flags=re.M)
    txt = re.sub(r'\s+', ' ', txt).strip()
    # First sentence or first 160 chars
    if not txt:
        return "DigiKitPro SEO audit documentation."
    # Take up to first period
    m = re.match(r'(.+?[.!?])(\s|$)', txt)
    first = m.group(1) if m else txt
    if len(first) > max_len:
        cut = first[:max_len-1]
        if " " in cut:
            cut = cut[:cut.rindex(" ")]
        return cut.rstrip(" ,;:.") + "…"
    return first

def load_audit_docs():
    """Return list of dicts: slug, src_path, title, desc, body, html_body"""
    files = glob.glob(os.path.join(AUDIT_SRC_DIR, "*.md"))
    # Sort by ORDER then alphabetical
    def sort_key(p):
        slug = _slug_from_filename(p)
        try:
            idx = ORDER.index(slug)
        except ValueError:
            # CHANGELOG and others not in ORDER list? Use len
            idx = 999
        return (idx, slug)
    files.sort(key=sort_key)
    docs = []
    for fp in files:
        raw = open(fp, encoding="utf-8").read()
        # Use core.parse_md if frontmatter present, else raw is body
        try:
            fm, body = parse_md(fp)
            # parse_md returns fm dict and body
            if not body.strip():
                body = raw
        except Exception:
            fm = {}
            body = raw
        slug = _slug_from_filename(fp)
        title = fm.get("title") or _title_from_body(body, slug)
        desc = fm.get("description") or _desc_from_body(body)
        # Convert markdown to HTML — docs will be rendered at depth 2 (seo-audit/<slug>/index.html)
        # so relative links like /products/ become ../../products/
        html_body = md_to_html(body, depth=2)
        docs.append({
            "slug": slug,
            "src": fp,
            "title": title,
            "desc": desc,
            "body": body,
            "html_body": html_body,
            "fm": fm,
        })
    return docs

def build_audit():
    docs = load_audit_docs()
    if not docs:
        print("No audit docs found in docs/seo-audit/")
        return []

    # Build index page
    # Create cards for each doc
    cards = ""
    for d in docs:
        # Use slug as URL: seo-audit/<slug>/
        url = f"{AUDIT_OUT_DIR}/{d['slug']}/"
        # Truncate desc
        desc = d['desc'][:160]
        cards += f"""<a class="art-card" href="{d['slug']}/">
      <div class="art-body"><span class="art-cat">SEO Audit</span>
      <h2>{esc(d['title'])}</h2>
      <p class="muted">{esc(desc)}</p>
      <span class="text-link">Read report →</span></div>
    </a>"""

    # Index page schemas
    index_schemas = schema_breadcrumb([("Home", "/"), ("SEO Audit", "/seo-audit/")])
    index_title = "DigiKitPro SEO Audit — Baseline 2026-09-19"
    index_desc = "Complete SEO baseline audit for DigiKitPro: platform, URL inventory, issue register, metadata gaps, assumptions, proposed architecture, monitoring report and approval gate."

    html_out = head(
        index_title,
        index_desc,
        SITE_URL + "/seo-audit/",
        1,
        schemas=index_schemas,
        ctx=page_ctx("audit_index"),
        # Make audit indexable but low priority — it's useful documentation, not doorway
        robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    )
    html_out += header(1)
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(1, [("SEO Audit","seo-audit/")])}
    <p class="eyebrow">Internal documentation</p>
    <h1>DigiKitPro SEO Audit</h1>
    <p class="lead">Baseline audit from 2026-09-19 — platform, URL inventory, prioritized issues, metadata/schema gaps, assumptions, proposed SEO-engine architecture, monitoring report and approval gate. This is the same documentation from <code>docs/seo-audit/</code> rendered as browsable HTML on digikitpro.shop.</p>
    <p class="muted">No production code was changed during Phase 1 — only documentation. This section exists so you can view the audit directly on your domain: <code>https://digikitpro.shop/seo-audit/</code></p>
  </div></section>
  <section class="section"><div class="wrap">
    <div class="grid arts-grid">{cards}</div>
    <div class="prose" style="margin-top:3rem">
      <h2>How to use this audit</h2>
      <ol>
        <li><strong>Start with 00-executive-summary</strong> — high-level findings and approval gate.</li>
        <li><strong>Check 03-issue-register</strong> — prioritized issues with severity, evidence, fix, effort, risk.</li>
        <li><strong>Review 08-approval-gate</strong> — safe fixes vs review required vs blocked, and decision needed on 4 orphaned blog drafts.</li>
        <li><strong>Approve</strong> — safe fixes can proceed, review required needs owner input, blocked needs manual steps (Enforce HTTPS, Search Console Domain property).</li>
      </ol>
      <h3>Live URLs</h3>
      <ul>
        <li>Index: <code>/seo-audit/</code> → <a href="{absurl('seo-audit/')}">{absurl('seo-audit/')}</a></li>
        <li>Each report: <code>/seo-audit/&lt;slug&gt;/</code> e.g. <code>/seo-audit/00-executive-summary/</code></li>
      </ul>
      <p class="muted">These pages are generated from <code>docs/seo-audit/*.md</code> via <code>tools/pages_audit.py</code> and included in sitemap with low priority (0.3). They are intentionally not linked from main navigation to avoid clutter, but accessible via direct URL and this index.</p>
    </div>
  </div></section>
  {newsletter(1)}
</main>
{footer(1)}
"""
    write(f"{AUDIT_OUT_DIR}/index.html", html_out)

    # Build individual pages
    built_urls = [f"/seo-audit/"]
    for d in docs:
        slug = d['slug']
        depth = 2  # seo-audit/slug/index.html -> depth 2
        # Breadcrumb: Home -> SEO Audit -> This report
        schemas = schema_breadcrumb([
            ("Home", "/"),
            ("SEO Audit", "/seo-audit/"),
            (d['title'], f"/seo-audit/{slug}/")
        ])
        # Use doc title + site name
        seo_title = f"{d['title']} | DigiKitPro SEO Audit"
        # Trim if too long
        if len(seo_title) > 70:
            seo_title = f"{d['title'][:50]}… | DigiKitPro"
        canonical = absurl(f"seo-audit/{slug}/")
        html_out = head(
            seo_title,
            d['desc'],
            canonical,
            depth,
            schemas=schemas,
            page_type="article",
            ctx=page_ctx("audit_doc", slug=slug, name=d['title']),
            robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
        )
        html_out += header(depth)
        # Add a small audit nav
        audit_nav = "".join(
            f'<a class="text-link" href="../{other["slug"]}/" style="margin-right:1rem">{esc(other["title"])}</a>'
            for other in docs if other["slug"] != slug
        )
        html_out += f"""
<main id="main">
  <article class="article wrap">
    {crumbs(depth, [("SEO Audit","seo-audit/"), (d['title'], f"seo-audit/{slug}/")])}
    <header class="article-head">
      <span class="art-cat">SEO Audit · {esc(slug)}</span>
      <h1>{esc(d['title'])}</h1>
      <p class="article-meta">Source: <code>docs/seo-audit/{esc(slug)}.md</code> · Generated {BUILD_DATE}</p>
    </header>
    <div class="prose article-body">{d['html_body']}</div>
    <nav class="article-related" aria-label="Other audit reports"><p class="eyebrow">Other reports</p><div class="rel-arts" style="display:flex;flex-wrap:wrap;gap:0.5rem">{audit_nav}</div></nav>
    <nav class="article-nav" aria-label="Audit navigation"><a class="btn btn-line" href="../../seo-audit/">← All audit reports</a><a class="btn btn-gold" href="../../">Back to homepage</a></nav>
  </article>
  {newsletter(depth)}
</main>
{footer(depth)}
"""
        write(f"{AUDIT_OUT_DIR}/{slug}/index.html", html_out)
        built_urls.append(f"/seo-audit/{slug}/")

    print(f"Built SEO audit pages: {len(docs)} docs + index -> {AUDIT_OUT_DIR}/ (URLs: {', '.join(built_urls[:3])}...)")
    return built_urls

if __name__ == "__main__":
    build_audit()
