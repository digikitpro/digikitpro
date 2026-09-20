#!/usr/bin/env python3
"""
DigiKitPro — post-build verification suite.

Run after a successful `python3 tools/build.py`:

    python3 tools/verify.py

Expects: ALL 96 CHECKS PASSED.
(89 -> 93 on 2026-09-20: + 4 from the product image gallery repair — every
product page ships js/gallery.js with [data-product-gallery], #product-main-image
and a data-full-image per tile; a tile can never hand the frame the -card crop;
no frame keeps a srcset that belongs to another image (that override is what made
the thumbnails look dead) and js/main.js holds no gallery code any more; the CSS
carries the active-tile ring, the prev/next pair, the modal viewer with its scroll
lock and the sideways-scrolling tiles on a phone. Page design itself: untouched.)
(93 -> 94 on 2026-09-20, merged on top of the above: + 1 from the product-card
frame pass — the cards' shared .card-media frame moves 1:1 -> 4:3 (check 81
re-pinned from `aspect-ratio:1/1` to `aspect-ratio:4/3`) and a new check asserts
the 4:3 geometry leaves exactly 40/51 covers at >=85% fill, and that no .badge
sits inside any .card-media anywhere on the built site. Both halves are computed
against the real 51-product cardW/cardH ratios in data/products.json, not a
hard-coded expectation.)
(94 -> 96 on 2026-09-20, same day, same block: the storefront then read as
"product images are tiny" because the artwork did not reach the frame's edges, so
.card-media goes full bleed. Check 81 is re-pinned from `object-fit:contain` in
one 4:3 frame to `object-fit:cover` in a 7-rung ladder (16:9, 3:2, 4:3, 1:1, 4:5,
3:4, 2:3) whose frame a cover takes from its own cardW/cardH, with 4:3 kept as the
fallback; + 1 checks every rung the builder can name has its frame rule at that
exact ratio; the 82b fill assertion becomes a crop-cost assertion (mean 0.4% of
the artwork, 49/51 covers under 5%, worst 15.6%) because a fixed 4:3 cover frame
would have cost 13.5% mean and 57.8% worst; + 1 checks each built card carries the
rung its own cover picked and that no badge moved back into the frame. All three
are computed from data/products.json + the built HTML, never from a hard-coded
expectation.)
(88 -> 89 on 2026-09-20: + 1 from the ebooks cover-first pass — the Starter
Guide & Masterclass covers must fill 85–90% of their dock, the paid one
fullest, on a full-wrap grid whose two-up engages at 1200px; check 86 was
re-pinned from 1080px to 1200px in the same pass.)
(Retired 90 -> 88 on 2026-09-20: the public /seo-audit/ HTML was removed,
taking its two sitemap-presence checks with it. docs/seo-audit/ stays as
internal markdown; nothing else about the suite changed.)
(57 baseline + 5 from the 2026-09-14 homepage IA rework: section order,
ladder completeness x2, no fake-strikethrough pricing + 8 from the
2026-09-16 buyer-guides buildout: pages built, sitemap coverage x2, slug
integrity, no lifestyle leakage, comparison-table completeness, cross-link
mesh, footer links + 10 from the 2026-09-17 partner portal: page built,
canonical, sitemap coverage, share-kit slug integrity, live prices + Payhip
checkout links, site-wide footer link, no dead application CTA while the
sign-up variable is unset, no unpublished commission rate, the variable
reaching BOTH build workflows, and the CTA flipping when it is set + 2 from
the 2026-09-17 card-media uncrop: product cards must frame the artwork whole
inside one uniform 4:3 frame, and the mat behind it must not be painted over.
The three 2026-09-17 finder-combo checks were replaced on 2026-09-18 when
the Find My Brush Kit was removed in full: the page and both scripts must be
gone, no generated page may reference them, and the hero must offer exactly
the two storefront CTAs (Shop All Brushes / Try Free Brushes). The two
homepage-IA checks were re-pinned on 2026-09-19 to the proof-first order —
results → ebooks → popular → craft → bundles → master-library → free → articles → newsletter — a re-pin of the same two checks, so the count is unchanged.
+ 2 from the 2026-09-19 ebooks CTA uncrop: the Starter Guide & Masterclass
pills must never be clipped by their card's overflow:hidden, and they must
keep a full measure on a 320px phone + 2 from that day's no-clip second pass:
the card itself must crop nothing (overflow:visible at an auto height, covers
stay contain, and the cover mat and the gold bar round their own corners
instead of leaning on the clip) and the two-up grid must engage only from
1080px, one full-width card below it + 1 from the 2026-09-19 best-sellers
re-square: the #popular finish (shell, hairline, pedestal shadow, body,
price) may not re-dock .card-media — no #popular rule may put an
aspect-ratio, padding, height, fit or transform on the media or its img —
so the homepage's lead row shares the one square that 81–82 pin for every
other product card.)

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
EXPECTED = 96

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
    print("DigiKitPro verify — 96 checks\n")

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
    # 99 = 11 static + 10 categories + 2 seasons + 6 buyer guides +
    # 1 partner portal + 51 products + 18 blog articles (after cleanup of 4 orphaned drafts).
    # The check allows >=99 to accommodate SEO tools and future safe additions.
    # The 11 /seo-audit/ URLs were removed on 2026-09-20; the site now sits at 101.
    check("sitemap.xml has 99+ page URLs",
          len(page_locs) >= 99, str(len(page_locs)))
    check("sitemap.xml all locs on digikitpro.shop",
          bool(page_locs) and all(u.startswith(HOST) for u in page_locs)
          and not any("github.io" in u for u in page_locs))

    sm_txt = read("sitemap.txt") if exists("sitemap.txt") else ""
    txt_urls = [ln.strip() for ln in sm_txt.splitlines() if ln.strip()]
    check("sitemap.txt has 99+ URLs", len(txt_urls) >= 99, str(len(txt_urls)))
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

    # ── 40–42 Find My Brush Kit removal (2026-09-18) ──────────────────
    # The finder was removed in full per owner request: the page, both
    # generated scripts and every link to them must be gone. The earlier
    # three checks verified the recommendation engine; these three police
    # the removal so a later edit cannot resurrect a dead link.
    deleted = (not exists("find-my-brushes.html") and not exists("js/finder.js")
               and not exists("js/finder-index.js") and not exists("tools/pages_finder.py"))
    check("finder removed: find-my-brushes.html, js/finder.js, js/finder-index.js gone",
          deleted, "page + both scripts (and the generator module) deleted")
    refs = 0
    ref_samples = []
    for p in html_files:
        t = p.read_text(encoding="utf-8", errors="replace")
        if "find-my-brushes" in t or "js/finder" in t or "DKP_FINDER" in t:
            refs += 1
            if len(ref_samples) < 3:
                ref_samples.append(p.relative_to(ROOT).as_posix())
    check("finder removed: no generated page references the finder",
          refs == 0, "; ".join(ref_samples) or f"{len(html_files)} pages clean")

    # ── 43 information architecture (product-first storefront) ─────────
    home_html = read("index.html")
    # The hero is the storefront's first job: two CTAs, named exactly.
    check("hero CTAs are Shop All Brushes + Try Free Brushes",
          'href="products.html">Shop All Brushes' in home_html
          and 'href="freebies.html">Try Free Brushes' in home_html,
          "products.html + freebies.html as the two entry points")

    # ── 44–45 information architecture (result-first storefront) ───────
    # 2026-09-18 exact reorder (owner brief): proof first, discovery before
    # bundles, the portrait journey as the education funnel, community art
    # as an honest placeholder, learning late, email last. Same conversion
    # spine as the live brief: see → believe → find → try → start → deepen
    # → trust → learn → stay.
    ids = homepage_section_ids(home_html)
    IA = ["results", "ebooks", "popular", "craft", "bundles", "master-library", "free", "articles", "newsletter"]
    check("homepage section order matches the result-first brief",
          ids == IA, ", ".join(ids) or "no sections found")
    # The page must close on learning, then the one low-commitment CTA: … free → Articles → newsletter as the last section.
    check("homepage closes: free → articles → email CTA",
          ids[-3:] == ["free", "articles", "newsletter"],
          "final section: " + (ids[-1] if ids else "-"))

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

    # ── 81–82 product card framing (see .card-media in css/style.css) ──
    # Two invariants, each learned the hard way. (a) The artwork must FILL its
    # container edge to edge — a frame that letterboxes on the site mat is what
    # read as "the product images are tiny" (docs/PRODUCT-CARDS-4X3-FRAME-2026-09-20.md
    # raised mean fill to 83.9% and left the other 16.1% as mat, gutters and all).
    # (b) The crop that buys that fill may not slice the artwork's own edges:
    # every cover carries its product name, a brand lockup or a feature-icon row
    # baked into the image, and one hard frame ratio over 51 different ones costs
    # 13.5% of the artwork on average and 25-58% for 10 covers
    # (docs/CARD-MEDIA-FRAMING-2026-09-17.md — the Master Library ribbon arriving
    # as "PICK"). The 2026-09-20 fix is a LADDER: each card's frame takes the rung
    # closest to its own cover's ratio, so object-fit:cover is nearly free.
    css_txt = read("css/style.css")
    cm = re.search(r"\.card-media\{([^}]*)\}", css_txt)
    ci = re.search(r"\.card-media img\{([^}]*)\}", css_txt)
    check("product cards fill their media frame edge to edge, rung by rung",
          bool(ci) and "object-fit:cover" in ci.group(1)
          and "object-fit:contain" not in ci.group(1)
          and "transform" not in ci.group(1)
          and bool(cm) and "aspect-ratio:4/3" in cm.group(1)
          and "overflow:hidden" in cm.group(1) and "padding:0" in cm.group(1),
          "full bleed, no inset, no hover zoom to re-crop; 4/3 only as the fallback frame")
    # The ladder itself: every rung core.media_rung() can name must have a frame
    # rule at that exact ratio, or that cover silently renders in the fallback
    # 4:3 and its gutter comes back.
    from core import MEDIA_RUNGS as _RUNGS, media_rung as _media_rung
    RUNG_CSS = dict((n, css) for f, n, css in _RUNGS)
    rung_bad = [n for n, f in RUNG_CSS.items()
                if not (m := re.search(r"\.card-media\.media-%s\{([^}]*)\}" % n, css_txt))
                or "aspect-ratio:%s" % f not in m.group(1)]
    check("every media rung the builder can emit has a frame rule, at the right ratio",
          len(RUNG_CSS) == 7 and not rung_bad,
          "7 rungs: " + ", ".join("%s=%s" % (n, f) for n, f in RUNG_CSS.items()) if not rung_bad
          else "rung rules missing or wrong at: " + ", ".join(rung_bad))
    # background:none is load-bearing: the global `img{background:var(--surface-2)}`
    # paints on the ELEMENT box, so a cover with no recorded sizes (the vector
    # coming-soon placeholder, which keeps the fallback frame) would sit on a flat
    # panel instead of the mat.
    check("card media mat is not painted over by the global img background",
          bool(ci) and "background:none" in ci.group(1),
          ".card-media img must reset the inherited img background")
    # ── 82b what the ladder's crop costs, per cover (2026-09-20) ──
    # A cover of ratio R inside a frame of ratio F keeps min(F,R)/max(F,R) of its
    # area, the same arithmetic object-fit:cover performs. Computed from the real
    # cardW/cardH in data/products.json (51 products), with each cover in the rung
    # core.media_rung() picks for it: 0.6% of the cover's own box on average
    # (0.4% of its painted content, measured with a content bounding box over the
    # .webp files in tools/card_frame_mock.py's lab), 50 of 51 covers under 5%,
    # worst 15.6% (morocco-7-day-itinerary at 0.563 — the one cover the ladder
    # cannot serve better, it owns the 2:3 rung by itself). For comparison, over
    # the same 51: one 4:3 frame + cover costs 16.1% mean and 57.8% worst, and the
    # rule this pass replaced (one 4:3 frame + contain) cost no artwork at all and
    # 16.1% of the frame as mat, with the 9 portrait covers down at 42-61% fill.
    RUNG_F = dict((n, f) for f, n, css in _RUNGS)
    losses = []
    for _p in products.values():
        _im = _p.get("images") or {}
        _w = _im.get("cardW") or 0; _h = _im.get("cardH") or 0
        if not _w or not _h:
            continue
        _F, _R = RUNG_F[_media_rung(_w, _h)], _w / _h
        losses.append(1 - min(_F, _R) / max(_F, _R))
    mean_loss = sum(losses) / len(losses)
    lt5 = sum(1 for x in losses if x < 0.05)
    check("the rung each cover is framed in costs its artwork almost nothing",
          len(losses) == 51 and mean_loss <= 0.02 and lt5 >= 50 and max(losses) <= 0.17,
          f"mean {100*mean_loss:.1f}% of the cover cropped, {lt5}/{len(losses)} covers under 5%, "
          f"worst {100*max(losses):.1f}% (one 4:3 frame for all of them: "
          f"16.1% mean, 5/51 under 5%, 57.8% worst)")
    # And the built pages must agree with the builder: every card-media element
    # carries the rung its own cover picked, and no badge sits inside the frame
    # (with full bleed there is no mat corner left for one anyway).
    cards_html = "\n".join(read(str(pth.relative_to(ROOT))) for pth in html_files)
    media_els = re.findall(r'<a class="card-media([^"]*)"[^>]*>.*?</a>', cards_html, re.S)
    unframed = sum(1 for m in media_els if "media-" not in m)
    wrong_rung = []
    for _p in products.values():
        _im = _p.get("images") or {}
        _want = "media-" + _media_rung(_im.get("cardW") or 750, _im.get("cardH") or 500)
        if not re.search(r'<a class="card-media %s" href="[^"]*products/%s/' % (_want, re.escape(_p["slug"])),
                         cards_html):
            wrong_rung.append(_p["slug"])
    badge_in_media = sum(1 for m in media_els if 'class="badge' in m)
    card_top_ok = ('<div class="card-top">' in cards_html
                   and re.search(r"\.card-top\{[^}]*display:flex", css_txt) is not None
                   and re.search(r"\.card \.card-top \.badge\{([^}]*)\}", css_txt) is not None
                   and "position:static" in (re.search(r"\.card \.card-top \.badge\{([^}]*)\}", css_txt).group(1)))
    check("every built card frames its own cover, and no badge sits on the artwork",
          bool(media_els) and unframed == 0 and not wrong_rung and badge_in_media == 0 and card_top_ok,
          (f"{len(media_els)} card-media elements, {unframed} without a rung"
           + (f", wrong rung on: {', '.join(wrong_rung[:4])}" if wrong_rung else "")
           + (f", {badge_in_media} badges inside the frame" if badge_in_media else "")
           + ("" if card_top_ok else ", badge row (.card-top) not pinned in the body"))
          if (unframed or wrong_rung or badge_in_media or not card_top_ok)
          else f"{len(media_els)} card-media elements across the built site each carry their own cover's "
               f"rung; {badge_in_media} badges inside a frame (the badge row lives in .card-top)")

    # ── 83–84 ebooks CTA row (see .ebooks-grid .ebook-foot in css/style.css) ──
    # The Starter Guide & Masterclass cards are horizontal at every width, so
    # the fixed cover used to starve the pitch column on a phone and the card's
    # own overflow sliced the CTA pill. Two halves, each of which has a
    # plausible wrong fix: capping the foot children (so a CTA may wrap or move
    # to its own line, but never outgrow its card) and buying the label a real
    # measure below 480px. The card itself stopped clipping in the no-clip
    # second pass — checks 85–86 below.
    foot_kid = re.search(r"\.ebooks-grid \.ebook-foot>\*\{([^}]*)\}", css_txt)
    foot_btn = re.search(r"\.ebooks-grid \.ebook-foot \.btn\{([^}]*)\}", css_txt)
    foot_link = re.search(r"\.ebooks-grid \.ebook-foot \.text-link\{([^}]*)\}", css_txt)
    check("ebooks CTAs are capped to their row, so no label can outgrow the card",
          bool(foot_kid) and "max-width:100%" in foot_kid.group(1)
          and "min-width:0" in foot_kid.group(1)
          and bool(foot_btn) and "white-space:normal" in foot_btn.group(1)
          and bool(foot_link) and "white-space:normal" in foot_link.group(1)
          and "overflow-wrap:anywhere" in foot_link.group(1),
          "every .ebook-foot child is capped to the row and wraps its label instead")
    narrow = re.search(r"@media\(max-width:479px\)\{(.*?)\n\}", css_txt, re.S)
    nb = narrow.group(1) if narrow else ""
    cover_n = re.search(r"\.ebooks-grid \.ebook-cover\{flex:0 0 (\d+)px", nb)
    check("ebooks CTAs keep a full measure on a 320px phone",
          bool(cover_n) and int(cover_n.group(1)) <= 120
          and ".ebooks-grid .ebook-foot .btn" in nb and "flex:1 1 100%" in nb,
          "cover narrows and both CTAs go full width below 480px")

    # ── 85–86 the no-clip second pass (see .ebooks-grid in css/style.css) ──
    # Round 1 made the CTA fit; this pass removes the mechanism instead of the
    # symptom — the card itself no longer clips, so no descendant (CTA, label,
    # badge, cover shadow, or anything added later) can be sliced by the card
    # edge. The two decorations that used to lean on that clip must therefore
    # round themselves, and a bare `overflow:visible` without them is exactly
    # the wrong fix: the mat would square off the card's corners and the gold
    # bar would spill past them. Both are pinned here, as is the grid width
    # where a two-up card can still hold its own CTA row.
    card = re.search(r"\.ebooks-grid \.ebook-card\{([^}]*)\}", css_txt)
    card_css = card.group(1) if card else ""
    frame_img = re.search(r"\.ebooks-grid \.ebook-frame img\{([^}]*)\}", css_txt)
    dock = re.search(r"\.ebooks-grid \.ebook-cover\{([^}]*)\}", css_txt)
    gold = re.search(r"\.ebooks-grid \.ebook-card\.edu-deep::before\{([^}]*)\}", css_txt)
    gold_css = gold.group(1) if gold else ""
    corner = "calc(var(--radius) - 1px)"      # the card's inner corner: --radius - 1px border
    check("ebooks cards crop nothing, by construction",
          "overflow:visible" in card_css and "overflow:hidden" not in card_css
          and card_css.count("height:") == 1 and "height:auto" in card_css
          and bool(frame_img) and "object-fit:contain" in frame_img.group(1)
          and "object-fit:cover" not in frame_img.group(1)
          and bool(dock) and corner in dock.group(1)
          and f"height:{corner}" in gold_css and corner in gold_css
          and "100% 3px" in gold_css and "pointer-events:none" in gold_css,
          "card is overflow:visible at an auto height and the covers stay contain; the "
          "cover mat and the gold bar carry the card's own corners instead of a clip")
    base_grid = re.search(r"^#ebooks \.ebooks-grid\{([^}]*)\}", css_txt, re.M)
    two_up = [ln for ln in css_txt.splitlines()
              if "#ebooks .ebooks-grid{" in ln and "repeat(2,minmax(0,1fr))" in ln]
    # 2026-09-20: the breakpoint moved 1080px → 1200px with the cover-first
    # geometry (check 89) — 1200px is the first width where the full 1160px
    # wrap gives each two-up card 568px: a 300px dock AND a 222.8px pitch
    # column, which holds the price + "View Masterclass" pill on one line
    # with room to spare behind a classic scrollbar.
    widened = [ln for ln in css_txt.splitlines()
               if ln.startswith("@media(") and "ebooks-grid" in ln
               and "min-width:1200px" not in ln]
    check("the ebooks grid is one column until 1200px",
          bool(base_grid) and "grid-template-columns:1fr" in base_grid.group(1)
          and len(two_up) == 1 and two_up[0].startswith("@media(min-width:1200px){")
          and not widened,
          "one full-width card below 1200px; two-up only from 1200px, where a 300px dock "
          "still leaves the CTA row its line")
    # ── 87 the cover dock's min-width (third pass, 2026-09-19) ──────────
    # A flex item's automatic minimum is its content-based minimum, not its
    # flex-basis: the 3:4 cover <img> inside the dock lets Chrome resolve the
    # dock wider than its declared basis (264px measured against the 220px
    # rule), the body column absorbs the loss, its text wraps taller than the
    # cover-driven card height, and the foot row renders below the card's
    # frame. min-width:0 on the base rule binds the dock to its basis at all
    # three widths — the 479px/640px variants only override flex and padding.
    check("ebooks cover dock holds its declared width",
          bool(dock) and "min-width:0" in dock.group(1)
          and re.search(r"flex:0 0 \d+px", dock.group(1)) is not None,
          "the dock must declare min-width:0, or its cover image inflates it past its flex-basis")

    # ── 89 the ebooks covers fill their dock (cover-first, 2026-09-20) ──
    # The cover is the card's subject. Before this pass the two-up card was
    # 518px on a centred 1060px grid, the dock 260px with a 16/8.8px inset,
    # and the legacy `.ebook-cover{aspect-ratio:3/4}` held the dock 4/3 of
    # its width whatever the padding — 235×314 of art in a 260×398 mat, 71%
    # of the dock. Now the grid spans the wrap, the dock is 300px from 900px
    # (280px from 640px, 176px from 480px, 116px below), the mat is an even
    # --dock-pad ring (aspect-ratio:auto, so the cover sets the dock height
    # and nothing is left over), and the paid Masterclass runs the tighter
    # pad (8px, ~90% of the dock) against the Starter's 12px (~86%) — same
    # dock, same card height, the paid cover visibly fuller. Pinned so a
    # re-centred grid, a re-inflated dock or a flat pad cannot creep back;
    # the <img sizes> hint must quote the rendered widths (dock − 2×pad) so
    # the browser keeps picking the right srcset candidate.
    dock_css = dock.group(1) if dock else ""
    # the ebooks 640px block is the multi-line one whose rules are all .ebooks-grid
    mid = re.search(r"@media\(min-width:640px\)\{\n((?:\.ebooks-grid [^\n]*\n)+)\}", css_txt)
    mid_css = mid.group(1) if mid else ""
    wide = re.search(r"@media\(min-width:900px\)\{\n\.ebooks-grid \.ebook-cover\{([^}]*)\}", css_txt)
    dock_mid = re.search(r"\.ebooks-grid \.ebook-cover\{flex:0 0 (\d+)px;padding:var\(--dock-pad\)\}", mid_css)
    dock_wide = re.search(r"flex:0 0 (\d+)px", wide.group(1)) if wide else None
    pad_start = re.search(r"\.ebooks-grid \.ebook-card\.edu-start\{--dock-pad:(\d+)px\}", mid_css)
    pad_deep = re.search(r"\.ebooks-grid \.ebook-card\.edu-deep\{--dock-pad:(\d+)px\}", mid_css)
    fill = lambda dock_px, pad_px: ((dock_px - 2 * pad_px) ** 2 * 4 / 3) / (dock_px * ((dock_px - 2 * pad_px) * 4 / 3 + 2 * pad_px))
    fills_ok = (bool(dock_mid) and bool(dock_wide) and bool(pad_start) and bool(pad_deep)
                and int(pad_deep.group(1)) < int(pad_start.group(1))
                and all(0.85 <= fill(int(d), int(pd)) <= 0.92
                        for d in (dock_mid.group(1), dock_wide.group(1))
                        for pd in (pad_start.group(1), pad_deep.group(1))))
    sizes_hint = re.findall(r'class="ebook-frame"><img [^>]*sizes="([^"]+)"', home_html)
    hint_ok = (len(sizes_hint) == 2 and len(set(sizes_hint)) == 1 and bool(dock_wide) and bool(pad_deep)
               and f"(min-width: 900px) {int(dock_wide.group(1)) - 2 * int(pad_deep.group(1))}px" in sizes_hint[0]
               and bool(dock_mid) and f"(min-width: 640px) {int(dock_mid.group(1)) - 2 * int(pad_deep.group(1))}px" in sizes_hint[0])
    check("ebooks covers fill 85–90% of their dock, the paid one fullest",
          bool(base_grid) and "max-width" not in base_grid.group(1)
          and "aspect-ratio:auto" in dock_css and "padding:var(--dock-pad)" in dock_css
          and "--dock-pad:" in card_css and fills_ok and hint_ok,
          "full-wrap grid; dock resets the legacy 3:4 box and wears an even --dock-pad mat; "
          f"dock {dock_mid.group(1) if dock_mid else '?'}/{dock_wide.group(1) if dock_wide else '?'}px, "
          f"pad Starter {pad_start.group(1) if pad_start else '?'}px / Masterclass {pad_deep.group(1) if pad_deep else '?'}px; "
          "img sizes quote dock − 2×pad")

    # ── 88 the best-sellers row keeps the shared card frame (2026-09-19) ───
    # #popular is a scoped FINISH — gradient shell, gold hairline, roomier
    # body, gold price — and must never become a second frame. The premium
    # pass had re-docked the row in a 4:3 box with a 1rem/1.1rem inset: nothing
    # was cropped, but the storefront's lead row became the one product grid
    # whose cards did not share the .card-media frame that 81–82 pin — shorter
    # tiles than the free row, and the three portrait covers about a third
    # smaller than the same artwork on any other card. Both halves are pinned:
    # the built homepage still renders #popular as .card-media cards (so the
    # globals reach it at all, rungs included — each of these four covers takes
    # the same rung it would take anywhere else on the site), and every
    # #popular rule that touches the media carries no geometry and no fit — the
    # ladder, the cover and the zero padding all come from the globals. ::after
    # is exempt: an absolutely positioned overlay adds no box of its own.
    # Property names are compared whole, so max-width or line-height can never
    # trip (or hide behind) the width/height guards, and the selector scan is
    # not line-anchored, so a one-line @media block cannot smuggle the dock back
    # in either.
    pop_sec = re.search(r'<section[^>]*id="popular".*?</section>', home_html, re.S)
    # the rung class rides on the same element, so match the class prefix
    pop_cards = len(re.findall(r'class="card-media[ "]', pop_sec.group(0))) if pop_sec else 0
    pop_rules = re.findall(r"(#popular[^{}\n]*\.card-media[^{}\n]*)\{([^}]*)\}", css_txt)
    props = lambda body: {d.split(":", 1)[0].strip() for d in body.split(";") if ":" in d}
    frame_props = {"aspect-ratio", "padding", "padding-top", "padding-right", "padding-bottom",
                   "padding-left", "padding-block", "padding-inline", "height", "min-height",
                   "max-height", "width", "min-width", "max-width", "block-size", "inline-size"}
    fit_props = frame_props | {"object-fit", "object-position", "transform", "scale", "zoom"}
    redocked = [sel.strip() for sel, body in pop_rules if "::" not in sel
                and props(body) & (fit_props if sel.rstrip().endswith("img") else frame_props)]
    check("homepage best-sellers row keeps the shared card frame and its rung",
          bool(pop_sec) and pop_cards >= 1
          and "#popular .card-media{aspect-ratio:4/3" not in css_txt
          and not redocked,
          ("re-docked by: " + ", ".join(redocked)) if redocked
          else f"{pop_cards} #popular cards inherit the global .card-media ladder + cover; "
               "no #popular geometry or fit override")

    # ── 90–93 product image gallery (js/gallery.js, tools/pages_product.py) ──
    # The bug this suite now polices: the big frame kept a srcset generated
    # from image #1, and in the HTML image-selection algorithm a matching
    # srcset candidate ALWAYS wins over `src` — so every thumbnail click
    # updated the attribute while the browser kept painting the first picture,
    # and the tiles looked dead. Hence: srcset, sizes, src, width, height and
    # alt move together, and a srcset may only ever name the image it shows.
    gal_css = read("css/style.css")
    gal_js = read("js/gallery.js")
    site_js = read("js/main.js")
    gal_pages = sorted((ROOT / "products").glob("*/index.html"))
    gal_txt = {p_: p_.read_text(encoding="utf-8") for p_ in gal_pages}

    def _stem(url: str) -> str:
        """assets/.../kit-2-card.webp -> kit-2 : the image a source belongs to."""
        name = url.split("?")[0].split("#")[0].rsplit("/", 1)[-1]
        return re.sub(r"-(card|thumb)(?=\.[a-z0-9]+$)", "", name)

    nohook = [p_.parent.name for p_, t in gal_txt.items()
              if "data-product-gallery" not in t
              or 'id="product-main-image"' not in t
              or "js/gallery.js" not in t]
    check("90 product gallery: every product page ships the module and its hooks",
          bool(gal_pages) and not nohook,
          f"{len(gal_pages)} product pages carry [data-product-gallery] + #product-main-image "
          f"+ the deferred js/gallery.js" if not nohook else f"missing on: {nohook[:5]}")

    bad_tile: list[str] = []
    n_tiles = 0
    for p_, t in gal_txt.items():
        btns = re.findall(r'<button class="gal-thumb[^"]*"[^>]*>', t)
        n_tiles += len(btns)
        if len(btns) != t.count("data-full-image="):
            bad_tile.append(f"{p_.parent.name}: {len(btns)} tiles but {t.count('data-full-image=')} full-size references")
        for btn in btns:
            m = re.search(r'data-full-image="([^"]+)"', btn)
            if not m:
                bad_tile.append(f"{p_.parent.name}: a tile with no data-full-image")
            elif re.search(r"-(card|thumb)\.[a-z0-9]+$", m.group(1)):
                bad_tile.append(f"{p_.parent.name}: tile hands the frame a crop ({m.group(1)})")
    check("91 gallery tiles reference the full-size file, never the card crop",
          not bad_tile and n_tiles >= 100,
          f"{n_tiles} tiles across the catalogue, each pointing the frame at its own full-size "
          "file; the -card crop stays where it belongs, inside the tile"
          if not bad_tile else f"{bad_tile[:4]}")

    srcset_bad: list[str] = []
    for p_, t in gal_txt.items():
        mm = re.search(r'<img id="product-main-image"[^>]*>', t)
        if not mm:
            continue
        src = re.search(r'src="([^"]+)"', mm.group(0))
        ss = re.search(r'srcset="([^"]+)"', mm.group(0))
        if not src or not ss:
            continue
        cands = [c.strip() for c in ss.group(1).split(",") if c.strip()]
        if len({c.rsplit(" ", 1)[-1] for c in cands}) != len(cands):
            srcset_bad.append(f"{p_.parent.name}: two candidates share one width descriptor")
        if any(_stem(c.split()[0]) != _stem(src.group(1)) for c in cands):
            srcset_bad.append(f"{p_.parent.name}: srcset names another image than the frame shows")
    check("92 a gallery srcset can never override the clicked image",
          not srcset_bad and "data-gal-main" not in site_js and "gal-light" not in site_js
          and 'mainImage.setAttribute("srcset"' in gal_js
          and 'mainImage.removeAttribute("srcset")' in gal_js,
          "every frame's srcset is that image's own pair (no duplicated widths, no foreign file); "
          "js/main.js holds no gallery code any more, and js/gallery.js rewrites "
          "srcset+sizes+src+width+height+alt in one move"
          if not srcset_bad else f"{srcset_bad[:4]}")

    gal_css_need = {
        "the active tile is outlined and marked": ".product-gallery-thumb.active{outline:2px solid currentColor",
        "aria-current is styled, not only set": '.gal-thumb[aria-current="true"]',
        "prev/next sit over the artwork": ".gal-nav{position:absolute",
        "the viewer is a modal, not a link": ".dkp-lb{position:fixed",
        "the page behind cannot scroll": "html.dkp-lb-open",
        "the viewer has a close button": ".dkp-lb-x",
        "the viewer has arrows": ".dkp-lb-nav",
        "tiles stay tappable": ".gal-thumb{min-height:44px",
    }
    missing = [why for why, rule in gal_css_need.items() if rule not in gal_css]
    strip_mobile = re.search(r"@media\(max-width:600px\)\{[\s\S]{0,400}?\.gal-thumbs\{[^}]*overflow-x:auto", gal_css)
    check("93 gallery CSS keeps the active tile, the arrows and the lightbox real",
          not missing and bool(strip_mobile),
          "active outline + aria-current styling, prev/next over the artwork, dark modal viewer "
          "with close button, arrows and a scroll-locked page, sideways-scrolling tiles on a phone "
          "— with the existing frame, grid, type and colours untouched"
          if not missing and strip_mobile else f"missing: {missing + (['tiles do not scroll sideways on a phone'] if not strip_mobile else [])}")

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
