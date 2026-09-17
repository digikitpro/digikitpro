#!/usr/bin/env python3
"""
DigiKitPro — post-build verification suite.

Run after a successful `python3 tools/build.py`:

    python3 tools/verify.py

Expects: ALL 80 CHECKS PASSED.
(57 baseline + 5 from the 2026-09-14 homepage IA rework: section order,
ladder completeness x2, no fake-strikethrough pricing + 8 from the
2026-09-16 buyer-guides buildout: pages built, sitemap coverage x2, slug
integrity, no lifestyle leakage, comparison-table completeness, cross-link
mesh, footer links + 10 from the 2026-09-17 partner portal: page built,
canonical, sitemap coverage, share-kit slug integrity, live prices + Payhip
checkout links, site-wide footer link, no dead application CTA while the
sign-up variable is unset, no unpublished commission rate, the variable
reaching BOTH build workflows, and the CTA flipping when it is set.)

Lives in tools/ so it cannot be lost when a session closes. Fails the
process (exit 1) on the first-summary of any failure; never edits
data/products.json or data/discovery.json.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from html import escape as html_escape
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

HOST = "https://digikitpro.shop"
EXPECTED = 80

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))
    mark = "PASS" if ok else "FAIL"
    extra = f" — {detail}" if detail else ""
    print(f"  [{mark}] {name}{extra}")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def yaml_site_urls(rel: str) -> list[tuple[int, int, str]]:
    """(lineno, indent, line) for every SITE_URL: occurrence."""
    out = []
    for i, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"^\s*SITE_URL:", line):
            out.append((i, leading_spaces(line), line))
    return out


def yaml_env_indents(rel: str) -> list[int]:
    indents = []
    for line in (ROOT / rel).read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*env:\s*$", line):
            indents.append(leading_spaces(line))
    return indents


def git_clean(rel: str) -> bool:
    r = subprocess.run(
        ["git", "diff", "--quiet", "--", rel],
        cwd=ROOT, capture_output=True,
    )
    return r.returncode == 0


def git_tracked(rel: str) -> bool:
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", rel],
        cwd=ROOT, capture_output=True,
    )
    return r.returncode == 0


class HrefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.canonicals: list[str] = []
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and "href" in d:
            self.hrefs.append(d["href"])
        if tag == "link" and d.get("rel") == "canonical" and "href" in d:
            self.canonicals.append(d["href"])
        if tag == "h1":
            self.h1 += 1


def iter_html() -> list[Path]:
    skip_dirs = {".git", "tools", "data", "content", "docs", "scraped",
                 "shots", "uploads", ".cache", "__pycache__", ".github"}
    out: list[Path] = []
    for p in ROOT.rglob("*.html"):
        if any(part in skip_dirs for part in p.relative_to(ROOT).parts):
            continue
        out.append(p)
    return out


def is_verification_page(p: Path) -> bool:
    name = p.name.lower()
    return name.startswith("google") or name.startswith("yandex")


def resolve_href(page: Path, href: str) -> Path | None:
    raw = href.split("#", 1)[0].split("?", 1)[0].strip()
    if not raw:
        return None  # pure fragment
    if re.match(r"^(https?:|mailto:|javascript:|tel:|//)", raw, re.I):
        return None
    target = (page.parent / raw).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return target  # outside repo = broken
    if target.is_dir():
        index = target / "index.html"
        return index if index.exists() else target
    return target


def finder_combo_stats():
    from core import DISCOVERY, disc
    from pages_finder import finder_products

    questions = {q["id"]: q for q in DISCOVERY.get("questions", [])}
    crafts = [o["id"] for o in questions["craft"]["options"]]
    improves = [o["id"] for o in questions["improve"]["options"]]
    levels = [o["id"] for o in questions["level"]["options"]]
    styles = [o["id"] for o in questions["style"]["options"]]
    prods = finder_products()

    empty = aggregate = lifestyle = 0
    n = 0
    for craft in crafts:
        for improve in improves:
            for level in levels:
                for style in styles:
                    n += 1
                    scored = []
                    for slug, p in prods.items():
                        s = 0.0
                        if craft in (p.get("craft") or []):
                            s += 40
                        if improve in (p.get("improve") or []):
                            s += 30
                        if style in (p.get("style") or []):
                            s += 15
                        if level in (p.get("level") or []):
                            s += 10
                        s += min(5, (p.get("priority") or 0) * 0.05)
                        if p.get("aggregate") or s <= 0:
                            continue
                        scored.append((s, p.get("priority") or 0, p))
                    scored.sort(key=lambda t: (-t[0], -t[1]))
                    if not scored:
                        empty += 1
                        continue
                    buyable = [t for t in scored if t[2].get("tier") in ("entry", "bundle")]
                    primary = (buyable or scored)[0][2]
                    d = disc(primary["slug"])
                    if d.get("aggregate") or primary.get("aggregate"):
                        aggregate += 1
                    if d.get("line") == "lifestyle" or primary.get("line") == "lifestyle":
                        lifestyle += 1
    return n, empty, aggregate, lifestyle



def homepage_section_ids(html_text: str) -> list[str]:
    """Ordered ids of the homepage <main> sections — the information
    architecture itself. Cheap string scan (no parser, no new dependency):
    the page is machine-generated, so this is a stable read."""
    body = html_text.split('<main id="main">', 1)[-1].split("</main>", 1)[0]
    return re.findall(r"<section class=\"[^\"]*\" id=\"([a-z0-9-]+)\"", body)


def ladder_state() -> tuple[list[str], list[str]]:
    """(configured ladder slugs from discovery.json, slugs whose page exists)."""
    cfg = json.loads((ROOT / "data" / "discovery.json").read_text(encoding="utf-8"))
    rungs = (cfg.get("bundleLadder") or {}).get("rungs") or []
    want = [r.get("slug") for r in rungs if r.get("slug")]
    return want, [s for s in want if (ROOT / "products" / s / "index.html").is_file()]


DEAD_GOOGLE = re.compile(r"google\.com/ping\?sitemap=", re.I)
DEAD_BING = re.compile(r"bing\.com/ping", re.I)
DEAD_BING2 = re.compile(r"www\.bing\.com/webmaster/ping\.aspx", re.I)

# Fabrication patterns. Tuned to catch fake social proof without tripping
# on honest copy ("all sales are final", "sold through Payhip").
HONESTY = [
    ("testimonial claims", re.compile(r"\btestimonials?\b", re.I)),
    ("review-count claims", re.compile(r"\b\d[\d,]*\s*\+?\s*reviews?\b", re.I)),
    ("star ratings", re.compile(r"[★⭐]{2,}|rated\s+[1-5](?:\.\d)?\s*/\s*5|\b\d\s*out of\s*5\s*stars?\b", re.I)),
    ("customer-count claims", re.compile(r"\b\d[\d,]*\s*\+?\s*(happy\s+)?(customers|artists bought)\b", re.I)),
    ("scarcity / urgency", re.compile(r"\bonly\s+\d+\s+left\b|\blimited[- ]time offer\b|\bselling fast\b|\bact now\b|\bhurry,? (?:offer|ends|limited)\b", re.I)),
]


def source_blob() -> str:
    parts = []
    for rel in (
        ".github/workflows/deploy.yml",
        ".github/workflows/sync-payhip.yml",
        "tools/submit_index.py",
        "tools/pages_misc.py",
        "tools/build.py",
        "tools/core.py",
    ):
        parts.append(read(rel))
    return "\n".join(parts)


def esc_price(t: str) -> str:
    """Price text as it appears in generated HTML (nothing to escape today,
    but a currency symbol or an & must never break an equality check)."""
    return html_escape(str(t), quote=True)


def main() -> int:
    print("DigiKitPro verify — 80 checks\n")

    # ── 1–12 workflows ────────────────────────────────────────────────
    deploy = read(".github/workflows/deploy.yml")
    sync = read(".github/workflows/sync-payhip.yml")
    deploy_urls = yaml_site_urls(".github/workflows/deploy.yml")
    sync_urls = yaml_site_urls(".github/workflows/sync-payhip.yml")

    check("deploy.yml SITE_URL is https://digikitpro.shop",
          all("https://digikitpro.shop" in line and "github.io" not in line
              for _, _, line in deploy_urls) and len(deploy_urls) >= 1,
          f"{len(deploy_urls)} SITE_URL line(s)")

    check("deploy.yml SITE_URL indented 10 spaces",
          all(ind == 10 for _, ind, _ in deploy_urls),
          ", ".join(str(i) for _, i, _ in deploy_urls) or "none")

    env_indents = yaml_env_indents(".github/workflows/deploy.yml")
    check("deploy.yml env: indented 8 spaces",
          all(i == 8 for i in env_indents) and len(env_indents) >= 1,
          str(env_indents))

    check("deploy.yml permissions contents: write",
          re.search(r"^  contents: write\b", deploy, re.M) is not None)

    ping_at = deploy.find("tools/submit_index.py")
    deploy_pages_at = deploy.find("actions/deploy-pages")
    check("deploy.yml IndexNow step exists", ping_at != -1)
    check("deploy.yml IndexNow runs AFTER deploy-pages",
          ping_at != -1 and deploy_pages_at != -1 and ping_at > deploy_pages_at)

    # continue-on-error must sit on the ping step, not merely somewhere in the file.
    ping_block = deploy[deploy.find("Ping IndexNow"): ping_at] if ping_at != -1 else ""
    check("deploy.yml IndexNow has continue-on-error",
          "continue-on-error: true" in ping_block)

    check("deploy.yml IndexNow gated on INDEXNOW_KEY",
          "vars.INDEXNOW_KEY" in ping_block and "INDEXNOW_KEY" in ping_block)

    check("sync-payhip.yml build SITE_URL is https://digikitpro.shop",
          len(sync_urls) >= 1 and "https://digikitpro.shop" in sync_urls[0][2]
          and "github.io" not in sync_urls[0][2])

    check("sync-payhip.yml build SITE_URL indented 10",
          len(sync_urls) >= 1 and sync_urls[0][1] == 10,
          str(sync_urls[0][1]) if sync_urls else "missing")

    check("sync-payhip.yml ping SITE_URL is https://digikitpro.shop",
          len(sync_urls) >= 2 and "https://digikitpro.shop" in sync_urls[1][2]
          and "github.io" not in sync_urls[1][2])

    check("sync-payhip.yml ping SITE_URL indented 10",
          len(sync_urls) >= 2 and sync_urls[1][1] == 10,
          str(sync_urls[1][1]) if len(sync_urls) > 1 else "missing")

    # ── 13–17 domain ──────────────────────────────────────────────────
    all_wf_urls = deploy_urls + sync_urls
    check("no github.io in any workflow SITE_URL",
          all("github.io" not in line for _, _, line in all_wf_urls))

    cname = read("CNAME").strip()
    check("CNAME is digikitpro.shop", cname == "digikitpro.shop", cname)
    check("CNAME is tracked by git", git_tracked("CNAME"))

    core_src = read("tools/core.py")
    check("core.py default SITE_URL is https://digikitpro.shop",
          'os.environ.get("SITE_URL", "https://digikitpro.shop")' in core_src)

    robots = read("robots.txt") if exists("robots.txt") else ""
    check("robots.txt has no github.io", "github.io" not in robots)

    # ── 18–31 sitemaps ────────────────────────────────────────────────
    sitemap_lines = [ln.strip() for ln in robots.splitlines() if ln.lower().startswith("sitemap:")]
    check("robots.txt lists sitemap.xml",
          any(ln.endswith("/sitemap.xml") and HOST in ln for ln in sitemap_lines))
    check("robots.txt lists sitemap.txt",
          any(ln.endswith("/sitemap.txt") and HOST in ln for ln in sitemap_lines))
    check("robots.txt lists sitemap-images.xml",
          any(ln.endswith("/sitemap-images.xml") and HOST in ln for ln in sitemap_lines))
    check("robots.txt has exactly 3 Sitemap: lines",
          len(sitemap_lines) == 3, str(len(sitemap_lines)))

    sm_xml = read("sitemap.xml") if exists("sitemap.xml") else ""
    xml_locs = re.findall(r"<loc>([^<]+)</loc>", sm_xml)
    # sitemap.xml also contains image:loc; count only <url> page locs:
    page_locs = re.findall(r"<url>\s*<loc>([^<]+)</loc>", sm_xml)
    if not page_locs:
        # compact form: <url><loc>...</loc>
        page_locs = re.findall(r"<url><loc>([^<]+)</loc>", sm_xml)
    # 93 since the Find-My-Brushes page was removed per owner request
    # (tools/pages_finder.py build_all); +6 buyer-guide pages on 2026-09-16;
    # +1 partner portal (/partner/) on 2026-09-17.
    # The partner portal adds one URL, so both sitemaps moved 99 → 100.
    check("sitemap.xml has 100 page URLs",
          len(page_locs) == 100, str(len(page_locs)))
    check("sitemap.xml all locs on digikitpro.shop",
          bool(page_locs) and all(u.startswith(HOST) for u in page_locs)
          and not any("github.io" in u for u in page_locs))

    sm_txt = read("sitemap.txt") if exists("sitemap.txt") else ""
    txt_urls = [ln.strip() for ln in sm_txt.splitlines() if ln.strip()]
    check("sitemap.txt has 100 URLs", len(txt_urls) == 100, str(len(txt_urls)))
    check("sitemap.txt all on digikitpro.shop",
          bool(txt_urls) and all(u.startswith(HOST) for u in txt_urls)
          and not any("github.io" in u for u in txt_urls))

    check("sitemap-images.xml exists", exists("sitemap-images.xml"))
    img_xml = read("sitemap-images.xml") if exists("sitemap-images.xml") else ""
    img_urls = re.findall(r"<url>\s*<loc>([^<]+)</loc>", img_xml) or re.findall(
        r"<url><loc>([^<]+)</loc>", img_xml)
    img_locs = re.findall(r"<image:loc>([^<]+)</image:loc>", img_xml)
    check("sitemap-images.xml has 51 <url>", len(img_urls) == 51, str(len(img_urls)))
    check("sitemap-images.xml has 173 <image:loc>", len(img_locs) == 173, str(len(img_locs)))
    check("sitemap-images.xml all locs on digikitpro.shop",
          bool(img_urls) and bool(img_locs)
          and all(u.startswith(HOST) for u in img_urls + img_locs)
          and not any("github.io" in u for u in img_urls + img_locs))
    check("sitemap-images.xml has no -card. filenames",
          not any("-card." in u for u in img_locs),
          str(sum(1 for u in img_locs if "-card." in u)))
    check("sitemap-images.xml has no -thumb. filenames",
          not any("-thumb." in u for u in img_locs),
          str(sum(1 for u in img_locs if "-thumb." in u)))

    # ── 32–39 HTML quality ────────────────────────────────────────────
    html_files = iter_html()
    gio = 0
    bad_canon = 0
    broken = 0
    broken_samples: list[str] = []
    missing_payhip = 0
    h1_bad = 0
    for p in html_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        if "github.io" in text:
            gio += 1
        parser = HrefParser()
        try:
            parser.feed(text)
        except Exception:
            continue
        for c in parser.canonicals:
            if not c.startswith(HOST):
                bad_canon += 1
        if is_verification_page(p):
            continue
        if parser.h1 != 1:
            h1_bad += 1
        for href in parser.hrefs:
            target = resolve_href(p, href)
            if target is None:
                continue
            if not target.exists():
                broken += 1
                if len(broken_samples) < 5:
                    broken_samples.append(f"{p.relative_to(ROOT)} -> {href}")

    pdp_dir = ROOT / "products"
    pdp_missing = 0
    if pdp_dir.exists():
        for d in sorted(pdp_dir.iterdir()):
            idx = d / "index.html"
            if not idx.is_file():
                continue
            body = idx.read_text(encoding="utf-8", errors="replace")
            if "payhip.com" not in body:
                pdp_missing += 1

    check("0 github.io refs in generated HTML", gio == 0, str(gio))
    check("0 canonicals not on digikitpro.shop", bad_canon == 0, str(bad_canon))
    check("0 broken internal links", broken == 0,
          f"{broken}" + ("; " + "; ".join(broken_samples) if broken_samples else ""))
    check("0 PDPs missing a Payhip URL", pdp_missing == 0, str(pdp_missing))
    check("faq.html exists", exists("faq.html"))
    check("contact.html exists", exists("contact.html"))
    check("refunds.html exists", exists("refunds.html"))
    check("every content page has exactly one h1", h1_bad == 0, str(h1_bad))

    # ── 40–42 finder ──────────────────────────────────────────────────
    n_combos, n_empty, n_agg, n_life = finder_combo_stats()
    check("finder 1080 combos: 0 empty", n_combos == 1080 and n_empty == 0,
          f"{n_combos} combos, {n_empty} empty")
    check("finder 1080 combos: 0 aggregate primary", n_agg == 0, str(n_agg))
    check("finder 1080 combos: 0 lifestyle primary", n_life == 0, str(n_life))

    # ── 43–46 information architecture ────────────────────────────────
    home_html = read("index.html")
    ids = homepage_section_ids(home_html)
    IA = ["craft", "free", "ebooks", "results", "starting-points", "bundles", "master-library"]
    check("homepage section order matches the IA brief", ids[:len(IA)] == IA,
          ", ".join(ids) or "no sections found")
    # The page must close on free value and end with the one low-commitment CTA:
    # … master-library → (Why) → Articles → newsletter as the last <section>.
    check("homepage closes: master library → why → articles → email CTA",
          ids == IA + ["newsletter"], "final section: " + (ids[-1] if ids else "-"))

    products = {p["slug"]: p for p in json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))}
    want, kept = ladder_state()
    check("homepage ladder: every rung renders a card", len(kept) == len(want) and len(kept) >= 3,
          f"{len(kept)}/{len(want)} rung(s) rendered")
    check("homepage ladder: no bundle is missing a price or an asset line",
          all(p.get("priceText") and p.get("assets")
              for p in (products.get(s) or {} for s in kept) if p),
          "every rung needs priceText + assets from products.json")
    check("homepage: no 'was' / strikethrough pricing on the ladder",
          "was:" not in home_html.lower() and "<del>" not in home_html.lower(),
          "ladder prices are live store prices only")

    # ── 47–53 honesty + dead ping endpoints ───────────────────────────
    html_blob = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in html_files if not is_verification_page(p)
    )
    # Empty review slots (class "quote-slot") are deliberate placeholders,
    # not social-proof claims, and the owner fill-in instructions live in
    # HTML comments. Strip both so the fabrication guard keeps policing
    # published copy only — a real quote pasted outside a slot still trips it.
    html_blob = re.sub(r"<!--.*?-->", " ", html_blob, flags=re.S)
    html_blob = re.sub(r'<(?:figure|blockquote)\b[^>]*quote-slot[^>]*>.*?</(?:figure|blockquote)>',
                       " ", html_blob, flags=re.S)
    for label, pat in HONESTY:
        hits = pat.findall(html_blob)
        check(f"honesty: no {label}", len(hits) == 0,
              f"{len(hits)} hit(s)" + (f" e.g. {hits[0]!r}" if hits else ""))

    blob = source_blob() + "\n" + html_blob
    check("no google.com/ping?sitemap=", DEAD_GOOGLE.search(blob) is None)
    check("no bing.com/ping",
          DEAD_BING.search(blob) is None and DEAD_BING2.search(blob) is None)

    # ── 50–57 IndexNow script + data hygiene ──────────────────────────
    sub = read("tools/submit_index.py")
    check("submit_index.py uses SHA-256",
          "hashlib.sha256" in sub or "sha256" in sub)
    check("submit_index.py reads/writes data/indexnow-state.json",
          "indexnow-state.json" in sub)
    check("submit_index.py posts only to api.indexnow.org",
          "https://api.indexnow.org/indexnow" in sub
          and "google.com/ping" not in sub
          and "bing.com/ping" not in sub)

    env = os.environ.copy()
    env["INDEXNOW_KEY"] = ""
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "submit_index.py")],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=30,
    )
    check("submit_index.py returns 0 when INDEXNOW_KEY unset",
          r.returncode == 0, r.stderr.strip() or r.stdout.strip()[:120])
    dormant = "skipping" in (r.stdout + r.stderr).lower() or "dormant" in (r.stdout + r.stderr).lower()
    wrote_new = exists("data/indexnow-state.json") and not git_tracked("data/indexnow-state.json")
    wrote_dirty = exists("data/indexnow-state.json") and not git_clean("data/indexnow-state.json")
    check("submit_index.py does not write state without a key",
          dormant and not wrote_new and not wrote_dirty,
          (r.stdout or "").strip()[:80])

    check("products.json unmodified vs git", git_clean("data/products.json"))
    check("discovery.json unmodified vs git", git_clean("data/discovery.json"))
    # Look at the build step only — the file header also mentions tools/build.py.
    build_from = deploy.find("Build static site")
    build_to = deploy.find("configure-pages")
    build_step = deploy[build_from:build_to] if build_from != -1 and build_to > build_from else ""
    check("deploy.yml build env includes INDEXNOW_KEY",
          "INDEXNOW_KEY:" in build_step and "vars.INDEXNOW_KEY" in build_step
          and "python3 tools/build.py" in build_step)

    # ── 63–70 buyer guides (tools/pages_guides.py) ──────────────────────
    import pages_guides as pg

    guide_files = [f"guides/{g['slug']}/index.html" for g in pg.GUIDE_DEFS] + ["guides/index.html"]
    check("guides: all 6 guide pages built",
          all(exists(f) for f in guide_files),
          "; ".join(f for f in guide_files if not exists(f)) or "index + 5 guides")

    sm_want = [f"{HOST}/guides/"] + [f"{HOST}/guides/{g['slug']}/" for g in pg.GUIDE_DEFS]
    check("guides: all 6 URLs in sitemap.xml",
          all(u in page_locs for u in sm_want),
          "; ".join(u for u in sm_want if u not in page_locs) or "all present")
    check("guides: all 6 URLs in sitemap.txt",
          all(u in txt_urls for u in sm_want),
          "; ".join(u for u in sm_want if u not in txt_urls) or "all present")

    missing, lifestyle_hits = [], []
    for g in pg.GUIDE_DEFS:
        for grp in g.get("groups", []):
            for slug in grp.get("slugs", []):
                p = products.get(slug)
                if not p:
                    missing.append(f"{g['slug']}:{slug}")
                    continue
                d = pg.disc(slug)  # discovery entry (safe defaults when absent)
                if d.get("line") == "lifestyle" or d.get("stage") in ("planner", "travel", "templates"):
                    lifestyle_hits.append(slug)
    check("guides: every referenced product slug exists in products.json",
          not missing, "; ".join(missing) or f"{sum(len(gr['slugs']) for g in pg.GUIDE_DEFS for gr in g.get('groups', []))} refs")
    check("guides: no lifestyle / planner / template product on any guide grid",
          not lifestyle_hits, "; ".join(lifestyle_hits) or "brush context kept clean")

    comp_html = read("guides/procreate-bundles-compared/index.html") if exists("guides/procreate-bundles-compared/index.html") else ""
    real_bundles = [p for p in products.values() if p.get("category") == "Bundles"]
    check("guides: comparison table lists every real brush bundle",
          bool(real_bundles) and all(f"products/{p['slug']}/" in comp_html for p in real_bundles),
          f"{len(real_bundles)} bundles expected")

    mesh_ok = True
    for g in pg.GUIDE_DEFS:
        f = f"guides/{g['slug']}/index.html"
        if not exists(f):
            mesh_ok = False
            continue
        body = read(f)
        others = [x for x in pg.GUIDE_URLS if g["slug"] not in x]
        if not any(h in body for h in others):
            mesh_ok = False
    check("guides: every guide cross-links to at least one other guide", mesh_ok)

    check("guides: homepage footer links all 5 guides",
          all(f"guides/{g['slug']}/" in home_html for g in pg.GUIDE_DEFS),
          "; ".join(g["slug"] for g in pg.GUIDE_DEFS if f"guides/{g['slug']}/" not in home_html) or "all 5")

    # ── 71–80 partner portal (tools/pages_partner.py → /partner/) ───────
    # The portal is a marketing page, not a dashboard: Payhip's affiliate
    # system holds every tracked link and payout, so these checks police the
    # two things that could quietly rot — share-kit slugs that a Payhip sync
    # renamed, and copy that promises a number the store cannot keep.
    # Pin the variable OFF before importing, exactly as the INDEXNOW_KEY
    # checks do: the page's CTA depends on it, and this suite must be able to
    # verify the published artifact even when a developer's shell exports a
    # value the deployed site does not have.
    os.environ["PARTNER_SIGNUP_URL"] = ""
    import pages_partner as pp

    partner_file = f"{pp.PARTNER_DIR}/index.html"
    partner_html = read(partner_file) if exists(partner_file) else ""
    check("partner: /partner/index.html built", bool(partner_html), partner_file)

    partner_canon = f"{HOST}{pp.PARTNER_URL}"
    check("partner: URL in sitemap.xml and sitemap.txt",
          partner_canon in page_locs and partner_canon in txt_urls,
          f"xml={partner_canon in page_locs} txt={partner_canon in txt_urls}")
    check("partner: canonical is digikitpro.shop/partner/",
          f'<link rel="canonical" href="{partner_canon}">' in partner_html)

    kit_slugs = pp.PARTNER_FREE_SLUGS + pp.PARTNER_PAID_SLUGS
    check("partner: share kit lists 8 real catalog products",
          len(kit_slugs) == len(set(kit_slugs)) == 8
          and all(s in products for s in kit_slugs)
          and all(f"products/{s}/" in partner_html for s in kit_slugs),
          "; ".join(s for s in kit_slugs if s not in products) or "all 8 present")

    missing_payhip = [s for s in kit_slugs
                      if not (products.get(s) or {}).get("payhipUrl")
                      or (products[s]["payhipUrl"] not in partner_html)]
    check("partner: every share-kit entry carries its live price + Payhip URL",
          not missing_payhip
          and all(esc_price(products[s]["priceText"]) in partner_html
                  for s in kit_slugs if not products[s].get("free")),
          "; ".join(missing_payhip) or "prices + checkout links match products.json")

    foot_ok = [p for p in html_files
               if not is_verification_page(p) and 'partner/' in read(str(p.relative_to(ROOT)))]
    check("partner: linked from the footer of every generated page",
          len(foot_ok) == len([p for p in html_files if not is_verification_page(p)]),
          f"{len(foot_ok)} page(s) carry the footer link")

    # With no Payhip sign-up link configured the page must say the program is
    # invite-only and must NOT render an application CTA that leads nowhere.
    check("partner: no dead application CTA while PARTNER_SIGNUP_URL is unset",
          bool(pp.PARTNER_SIGNUP_URL)
          or ("Invite-only" in partner_html and "payhip.com/digikitpro" in partner_html
              and 'data-dkp-event="partner_apply_click"' in partner_html),
          "signup URL set" if pp.PARTNER_SIGNUP_URL else "invite-only copy + Payhip CTA")

    # Never print a commission rate or an earnings figure: it is agreed per
    # partner and paid by Payhip, so a number on this page could only be wrong.
    rate_hits = (re.findall(r"\b\d+(?:\.\d+)?\s*%\s*(?:commission|of (?:each|every) sale)", partner_html, re.I)
                 + re.findall(r"\b(?:commission|earn|paying)\s+(?:of\s+)?\d+(?:\.\d+)?\s*%", partner_html, re.I))
    check("partner: no unpublished commission rate or earnings claim",
          not rate_hits, str(rate_hits[:2]) if rate_hits else "0 rate/earnings figures")

    # The repository variable must reach BOTH builds, or a daily Payhip sync
    # would silently flip the page back to invite-only between deploys.
    sync_build_step = sync[sync.find("Rebuild static site"): sync.find("Commit auto-sync results")]
    check("both workflows pass PARTNER_SIGNUP_URL to tools/build.py",
          "PARTNER_SIGNUP_URL: ${{ vars.PARTNER_SIGNUP_URL }}" in build_step
          and "PARTNER_SIGNUP_URL: ${{ vars.PARTNER_SIGNUP_URL }}" in sync_build_step)

    # With the variable set, the CTA must really become the sign-up link and
    # the invite-only copy must go. Renders the page in-process, then rebuilds
    # it from the pinned (unset) environment so the artifact on disk always
    # matches the build a fresh checkout produces.
    # core must be reloaded first: pages_partner binds PARTNER_SIGNUP_URL with
    # `from core import *`, so reloading the page module alone would keep
    # reading the stale constant out of an already-imported core.
    import core as _core
    test_signup = "https://payhip.com/affiliates/verify-selftest"
    os.environ["PARTNER_SIGNUP_URL"] = test_signup
    importlib.reload(_core)
    importlib.reload(pp)
    pp.build_partner()
    open_html = read(partner_file)
    os.environ["PARTNER_SIGNUP_URL"] = ""
    importlib.reload(_core)
    importlib.reload(pp)
    pp.build_partner()
    restored_html = read(partner_file)   # re-read: partner_html above may predate a developer's local build
    check("partner: PARTNER_SIGNUP_URL switches the page to open applications",
          f'href="{test_signup}"' in open_html and "Apply to join" in open_html
          and "Invite-only" not in open_html
          and "Invite-only" in restored_html and test_signup not in restored_html,
          "application CTA + status copy follow the variable, and the artifact is rebuilt without it")

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = [(n, d) for n, ok, d in CHECKS if not ok]
    n = len(CHECKS)
    print()
    if failed or n != EXPECTED or passed != EXPECTED:
        print(f"FAILED: {passed}/{n} passed (expected {EXPECTED}).")
        for n_, d in failed:
            print(f"  - {n_}" + (f" ({d})" if d else ""))
        if n != EXPECTED:
            print(f"  - check count is {n}, not {EXPECTED}")
        return 1
    print(f"ALL {EXPECTED} CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
