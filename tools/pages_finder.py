#!/usr/bin/env python3
"""Find My Brushes (recommendation engine), the thank-you page, and the
generated finder data file.

WHY THIS MODULE EXISTS
The catalog has 51 products and 28 of them cost exactly $5. Nothing on the
site helped a visitor decide, so the decision was left to them — which is
where most sessions died. This builds the decision for them from data that
already exists: real categories, real tags, real prices, real Payhip links.

Everything is static. The scoring runs in the visitor's browser against
js/finder-index.js (generated here, same delivery pattern as the existing
js/search-index.js), and a server-rendered fallback below the tool gives the
same recommendations as plain HTML so the page is useful and crawlable with
JavaScript disabled.

Nothing is invented: no popularity numbers, no ratings, no "X artists bought
this". The `priority` value in data/discovery.json is an editorial tie-breaker
and is never displayed or described as demand.
"""
import json
from core import *
from pages_main import page_head

FINDER_PAGE = "find-my-brushes.html"
THANKS_PAGE = "thank-you.html"
FINDER_JS = "js/finder-index.js"

# Fallback tier labels if discovery.json is missing its tier list.
TIER_FALLBACK = {"free": "Free", "entry": "Specialist pack", "bundle": "Bundle",
                 "flagship": "Master Library", "education": "Guide"}


# ── data projection ─────────────────────────────────────────────────────
def _compat(p):
    """Compatibility statement, derived from the product's own requirement
    text so we never claim support that is not in the data."""
    hay = " ".join((p.get("requirements") or []) + (p.get("technical") or [])
                   + [p.get("category", ""), p.get("short", "")]).lower()
    if "goodnotes" in hay or "notability" in hay:
        return "GoodNotes, Notability & compatible PDF note apps"
    if "canva" in hay:
        return "Canva (editable templates)"
    if "procreate" in hay or "ipad" in hay:
        return "Procreate on iPad (Procreate 5 or newer)"
    if p.get("category") in ("Other", "Guides & eBooks"):
        return "See the requirements on the product page"
    return "Procreate on iPad"


def _format(p):
    for t in (p.get("technical") or []):
        k, sep, v = t.partition(":")
        if sep and k.strip().lower() == "format":
            return v.strip()
    return "Instant digital download · lifetime access"


def finder_products():
    """Slim, public-safe projection of the catalog for the browser engine.
    Excludes anything the browser does not need (descriptions, SEO copy)."""
    out = {}
    for p in PRODUCTS:
        d = disc(p["slug"])
        im = p.get("images") or {}
        card = im.get("card") or ""
        out[p["slug"]] = {
            "slug": p["slug"],
            "name": p["name"],
            "short": p.get("short", ""),
            "assets": p.get("assets", ""),
            "price": p.get("price", 0),
            "priceText": p.get("priceText", ""),
            "free": bool(p.get("free")),
            "tier": d.get("tier", "entry"),
            "tierLabel": (TIERS.get(d.get("tier")) or {}).get("label") or TIER_FALLBACK.get(d.get("tier"), ""),
            "line": d.get("line", "procreate"),
            "craft": d.get("craft") or [],
            "improve": d.get("improve") or [],
            "level": d.get("level") or [],
            "style": d.get("style") or [],
            "stage": d.get("stage", ""),
            "priority": d.get("priority", 0),
            "aggregate": bool(d.get("aggregate")),
            "img": card if is_abs(card) else f"assets/products/{p['slug']}/{card}",
            "url": f"products/{p['slug']}/",
            "payhipUrl": p.get("payhipUrl", STORE_URL),
            "compat": _compat(p),
            "format": _format(p),
        }
    return out


def finder_payload():
    return {
        "version": DISCOVERY.get("version", 1),
        "questions": DISCOVERY.get("questions", []),
        "products": finder_products(),
        "flagship": DISCOVERY.get("flagship"),
        "education": DISCOVERY.get("education", {}),
        "animationNotice": DISCOVERY.get("animationNotice"),
    }


# ── Python mirror of the browser scoring, for the no-JS/SEO fallback ────
def _score(rec, craft=None, improve=None, level=None, style=None):
    s = 0.0
    if craft and craft in (rec["craft"] or []): s += 40
    if improve and improve in (rec["improve"] or []): s += 30
    if style and style in (rec["style"] or []): s += 15
    if level and level in (rec["level"] or []): s += 10
    s += min(5, (rec["priority"] or 0) * 0.05)
    return s


def top_for_craft(craft_id, prods, n=3, tiers=("entry", "bundle")):
    # `aggregate` products (Master Library, Master Vault, Mega Bundle) match every
    # craft by definition, so including them here would make every single craft
    # block recommend the same three big bundles. They get their own flagship
    # band and the bundles page instead.
    #
    # NOTE: _score() cannot rank inside a single craft block. Every product here
    # already matches `craft_id`, so they all earn the same 40 craft points and the
    # only remaining differentiator is `priority` — a store-wide merchandising
    # number. That collapses each block into "global bestseller list filtered by
    # tag", which made Portraits and Illustration render byte-identical picks and
    # put Portrait Skin Brushes at the top of Concept Art. So rank on signals that
    # are actually about THIS craft, and leave priority as the final tiebreak only.
    out = []
    for slug, p in prods.items():
        if p.get("aggregate") or p["tier"] not in tiers:
            continue
        crafts = p["craft"] or []
        if craft_id not in crafts:
            continue
        s = 0.0
        # Built for this work first: the leading craft tag is the pack's primary.
        # This is the only signal in the data that is genuinely about THIS craft
        # rather than about the store as a whole.
        if crafts[0] == craft_id:
            s += 25.0
        # Store-wide priority as a light tiebreak, never the driver.
        s += min(5.0, (p["priority"] or 0) * 0.05)
        #
        # Two ideas were tried here and deliberately rejected on measured output:
        #
        # 1. A specificity bonus for narrowly-tagged packs. It sounds right, but in
        #    this catalog the narrowest tags belong disproportionately to seasonal
        #    and novelty items, so it promoted Halloween PNGs and Koi Fish Tattoo
        #    into Illustration and put a 10-brush hair pack above the 46-brush
        #    Portrait Mastery Kit. Narrow is not the same as better.
        #
        # 2. A penalty for packs already shown under another craft. It maximises
        #    variety (27 distinct products across 9 blocks) but it is a cosmetic
        #    goal, not a relevance one: it demoted the genuinely right answer to
        #    surface whatever was left over. Glitter brushes for Animation and
        #    Christmas brushes for Lettering are worse recommendations than an
        #    honest repeat. Variety is not worth a wrong pick.
        #
        # Where a craft has no primary-tagged packs at all (concept, animation,
        # lettering) this still falls back to priority order. That is a catalog
        # curation gap for the owner to close, not something ranking tricks should
        # paper over by inventing a primary craft a pack does not have.
        out.append((s, p))
    out.sort(key=lambda t: (-t[0], -(t[1]["priority"] or 0), t[1]["name"]))
    return [p for _, p in out[:n]]


def craft_fallback_section(depth, prods):
    """Server-rendered recommendations per craft. This is what a crawler
    indexes and what a no-JS visitor actually uses — real internal links to
    real product pages, not an empty shell waiting on a script."""
    questions = {q["id"]: q for q in DISCOVERY.get("questions", [])}
    craft_q = questions.get("craft") or {"options": []}
    blocks = ""
    for opt in craft_q["options"]:
        picks = top_for_craft(opt["id"], prods, n=3)
        if not picks:
            continue
        cards = "".join(
            f'''<li class="cb-item">
      <a href="{rel(depth, p['url'])}">
        <span class="cb-name">{esc(p['name'])}</span>
        <span class="cb-meta">{esc(p['assets'] or '')} · {esc('Free' if p['free'] else p['priceText'])}</span>
      </a>
    </li>''' for p in picks)
        blocks += f'''<div class="craft-block">
  <h3>{esc(opt['label'])}</h3>
  <p class="muted">{esc(opt.get('note',''))}</p>
  <ul class="cb-list">{cards}</ul>
</div>
'''
    return f'''<section class="section section-alt" id="browse-by-craft" aria-labelledby="bc-title">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow">No time for four questions?</p><h2 id="bc-title">Browse by what you create</h2></div>
      <a class="text-link" href="{rel(depth,'products.html')}">All {len(PRODUCTS)} products →</a>
    </div>
    <div class="grid craft-blocks">{blocks}</div>
  </div>
</section>
'''


# ── the finder page ─────────────────────────────────────────────────────
def finder_form(depth):
    questions = DISCOVERY.get("questions", [])
    steps = ""
    for q in questions:
        opts = ""
        for o in q["options"]:
            opts += f'''<label class="f-opt">
      <input type="radio" name="{esc(q['id'])}" value="{esc(o['id'])}">
      <span class="f-opt-label">{esc(o['label'])}</span>
      <span class="f-opt-note">{esc(o.get('note',''))}</span>
    </label>
'''
        steps += f'''<fieldset class="f-step" data-finder-step="{esc(q['id'])}">
    <legend><span class="f-num">{q.get('step','')}</span> {esc(q['question'])}</legend>
    <p class="f-hint muted">{esc(q.get('hint',''))}</p>
    <div class="f-opts">{opts}</div>
  </fieldset>
'''
    return f'''<form class="finder-form" data-finder-form method="get" action="{rel(depth, FINDER_PAGE)}">
  <div class="f-progress" role="progressbar" aria-label="Questions answered" aria-valuemin="0" aria-valuemax="{len(questions)}" aria-valuenow="0">
    <span class="f-progress-bar" data-finder-progress></span>
  </div>
  <div class="f-summary" data-finder-summary hidden></div>
  {steps}
  <div class="f-submit">
    <button class="btn btn-gold btn-lg" type="submit">Show my recommendation</button>
    <p class="muted f-submit-note">Four answers, no email required. Works on iPad and phone.</p>
  </div>
</form>
<div class="finder-results" data-finder-results hidden aria-live="polite"></div>'''


def build_finder():
    depth = 0
    prods = finder_products()

    faqs = [
        ("How does Find My Brushes decide what to recommend?",
         "It matches your four answers against what each pack is actually built for — the craft it serves, "
         "the problem it solves, the skill level it suits and the finish it produces — then ranks by relevance. "
         "Price is not part of the ranking, so the recommendation is never simply the most expensive item."),
        ("Do I need the Master Library?",
         "Not necessarily. If one specific thing is holding you back — skin texture, hair, line weight — a single "
         "specialist pack is the cheaper and faster answer. The Master Library makes sense when you work across "
         "several styles and would otherwise buy multiple packs separately."),
        ("Are these brushes really only for Procreate?",
         "The .brushset files require Procreate on an iPad. Every product page lists its own requirements and file "
         "formats. The catalog also carries a few items for other apps — digital planners, Canva "
         "templates and PNG packs — and each states its own requirements. Those are never recommended here as a brush solution, because this tool answers a brush question."),
        ("What if nothing matches what I make?",
         "The tool says so plainly instead of forcing a recommendation, and your answer is what tells the studio "
         "which pack to build next."),
    ]

    schemas = (schema_breadcrumb([("Home", "/"), ("Find My Brushes", "/" + FINDER_PAGE)])
               + schema_faq(faqs))

    faq_html = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary><div class="faq-body"><p>{esc(a)}</p></div></details>'
        for q, a in faqs)

    html_out = head(
        "Find My Brushes: Procreate Brush Finder | DigiKitPro",
        "Answer four questions and get the right Procreate brush pack for your work — portraits, anime, illustration, "
        "sketching, painting, lettering or animation. Ranked by relevance, never by price.",
        SITE_URL + "/" + FINDER_PAGE, depth, schemas=schemas,
        ctx=page_ctx("finder"))
    html_out += header(depth, active=FINDER_PAGE)
    html_out += f"""
<main id="main">
  {page_head(depth, "Product discovery", "Find My Brushes",
    "Fifty-one products is a lot to choose between. Answer four quick questions and we will point you at the pack that actually fits the work you make — and tell you honestly if we do not have one.",
    [("Find My Brushes", FINDER_PAGE)])}

  <section class="section finder-section">
    <div class="wrap" data-finder>
      {finder_form(depth)}
    </div>
  </section>

  {craft_fallback_section(depth, prods)}

  <section class="section">
    <div class="wrap narrow">
      <div class="sec-head"><div><p class="eyebrow">Straight answers</p><h2>How the finder works</h2></div></div>
      {faq_html}
    </div>
  </section>

  {newsletter(depth, source="finder", lead="brush-finder", uid="fb")}
</main>
"""
    html_out += footer(depth)
    write(FINDER_PAGE, html_out)

    # ── generated data file for the browser engine ──
    js = "window.DKP_FINDER=" + json.dumps(finder_payload(), ensure_ascii=False, separators=(",", ":")) + ";"
    write(FINDER_JS, js)
    return prods


# ── the thank-you page ──────────────────────────────────────────────────
def build_thanks():
    """Post-signup page. Two jobs, in this order:
    1. DELIVER. Every free file is linked directly, so the promise is kept on
       the page even if the confirmation email is delayed or lands in spam.
    2. LADDER. One starter offer, then the flagship. Never more than one ask
       per level — a thank-you page that sells five things sells nothing.
    """
    depth = 0
    freebies = [p for p in PRODUCTS if p.get("free") and not p.get("comingSoon")]
    freebies.sort(key=lambda p: -(disc(p["slug"]).get("priority") or 0))

    cards = ""
    for p in freebies:
        im = p.get("images") or {}
        card = im.get("card") or ""
        cards += f'''<article class="thanks-card" data-thanks-slug="{esc(p['slug'])}">
  <a class="thanks-media" href="{rel(depth, 'products/' + p['slug'] + '/')}">
    <img src="{asset_file(depth, p['slug'], card)}"{img_srcset(depth, p['slug'], im, "(min-width: 1100px) 320px, 92vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(p.get('alt') or p['name'])}" loading="lazy" decoding="async">
  </a>
  <div class="thanks-body">
    <span class="badge badge-free">Free</span>
    <h2>{esc(p['name'])}</h2>
    <p class="muted">{esc(p.get('assets') or '')}</p>
    <a class="btn btn-gold btn-sm" href="{p['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(p, 'thanks')}>Get Free ↗</a>
  </div>
</article>'''

    # ONE starter offer: the highest-priority paid specialist pack.
    entries = [p for p in PRODUCTS
               if not p.get("free") and tier_of(p) == "entry" and line_of(p) == "procreate"]
    entries.sort(key=lambda p: -(disc(p["slug"]).get("priority") or 0))
    starter = entries[0] if entries else None
    starter_html = ""
    if starter:
        im = starter.get("images") or {}
        starter_html = f'''<section class="section section-alt" aria-labelledby="starter-title">
  <div class="wrap starter-inner">
    <div class="starter-media">
      <a href="{rel(depth, 'products/' + starter['slug'] + '/')}">
        <img src="{asset_file(depth, starter['slug'], im.get('card',''))}"{img_srcset(depth, starter['slug'], im, "(min-width: 960px) 340px, 92vw")} width="{im.get('cardW') or 750}" height="{im.get('cardH') or 500}" alt="{esc(starter.get('alt') or starter['name'])}" loading="lazy" decoding="async">
      </a>
    </div>
    <div class="starter-body">
      <p class="eyebrow">Your next step</p>
      <h2 id="starter-title">{esc(starter['name'])}</h2>
      <p class="muted">{esc(starter.get('short',''))}</p>
      <ul class="tick-list check">
        <li>{esc(starter.get('assets') or 'Complete specialist set')}</li>
        <li>{esc(_compat(starter))}</li>
        <li>Instant download, lifetime access</li>
      </ul>
      <div class="starter-cta">
        <span class="price price-lg">{esc(starter['priceText'])}</span>
        <a class="btn btn-gold" href="{starter['payhipUrl']}" target="_blank" rel="noopener" {buy_attrs(starter, 'thanks-starter')}>Buy Now ↗</a>
        <a class="text-link" href="{rel(depth, 'products/' + starter['slug'] + '/')}">See what is inside →</a>
      </div>
      <p class="muted starter-note">Not yet? No pressure at all — the free packs above are yours to keep, and the
        <a href="{rel(depth, 'products.html')}">full catalog</a> is waiting when you are ready.</p>
    </div>
  </div>
</section>'''

    html_out = head(
        "Thank You — Your Free Procreate Downloads | DigiKitPro",
        "Your free Procreate brushes are ready to download right now, plus the recommended next step for your workflow.",
        SITE_URL + "/" + THANKS_PAGE, depth,
        schemas=schema_breadcrumb([("Home", "/"), ("Thank you", "/" + THANKS_PAGE)]),
        ctx=page_ctx("thankyou"))
    # Thank-you pages should be reachable but not compete for ranking.
    html_out = html_out.replace(
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        '<meta name="robots" content="noindex, follow">', 1)
    html_out += header(depth)
    html_out += f"""
<main id="main">
  <section class="page-head thanks-head"><div class="wrap">
    <p class="eyebrow">You are on the list</p>
    <h1 data-thanks-title>Your free Procreate downloads are ready</h1>
    <p class="lead" data-thanks-lead>Grab them right here — no need to wait for an email. Every file below is free,
      delivered instantly by Payhip, and yours to keep.</p>
    <p class="muted thanks-mail" data-thanks-mail>We have also sent a confirmation to your inbox. If it does not appear
      in a few minutes, check spam, or just use the links below.</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="grid thanks-grid">{cards}</div>
  </div></section>

  {starter_html}

  {flagship_band(depth)}

  <section class="section"><div class="wrap narrow">
    <div class="sec-head"><div><p class="eyebrow">While you are here</p><h2>Learn the workflow</h2></div></div>
    <p class="muted">Brushes are half of it. These guides show the same tools used on finished artwork, step by step.</p>
    <ul class="thanks-links">
      <li><a href="{rel(depth,'blog/procreate-portrait-workflow/')}">The complete Procreate portrait workflow →</a></li>
      <li><a href="{rel(depth,'blog/how-to-install-procreate-brushes/')}">How to install .brushset files on iPad →</a></li>
      <li><a href="{rel(depth,'blog/how-to-choose-procreate-brushes/')}">How to choose brushes without regretting it →</a></li>
    </ul>
  </div></section>
</main>
"""
    html_out += footer(depth)

    # Tiny inline script: the only page-specific JS on the site. It reads the
    # ?lead= parameter set by the signup form and puts the promised pack first,
    # so the page matches what the visitor actually asked for.
    html_out = html_out.replace("</body>", """<script>
(function(){
  try{
    var lead=new URLSearchParams(location.search).get('lead');
    if(!lead)return;
    var card=document.querySelector('[data-thanks-slug="'+CSS.escape(lead)+'"]');
    if(card&&card.parentNode)card.parentNode.insertBefore(card,card.parentNode.firstChild);
    var t=document.querySelector('[data-thanks-title]');
    var name=card?card.querySelector('h2'):null;
    if(t&&name)t.textContent='Your download is ready: '+name.textContent;
    var m=document.querySelector('[data-thanks-mail]');
    if(m)m.hidden=true;
  }catch(e){}
})();
</script>
</body>""", 1)
    write(THANKS_PAGE, html_out)


def build_all():
    # Find My Brushes removed per owner request - keep only thank-you page
    # build_finder()
    build_thanks()
