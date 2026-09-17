#!/usr/bin/env python3
"""Partner portal — /partner/ (one page, generated like every other page).

WHAT THIS IS
    The public front door of the DigiKitPro partner (affiliate) program:
    what the program is, how to get in, what partners may and may not say,
    and a ready-to-share kit of REAL product artwork, copy and links.

WHAT IT DELIBERATELY IS NOT
    A logged-in dashboard. Every order, download and message on this store
    runs through Payhip (STORE_URL in tools/core.py), and Payhip's own
    affiliate system is what tracks referrals, calculates each partner's
    share and pays it out. There is no DigiKitPro account, no session and no
    commission ledger here — so this page invents none, and shows no numbers
    it cannot keep true. Commission tracking lives in the partner's Payhip
    affiliate dashboard, and the page says exactly that.

    This also means the page is a genuine multi-page-site citizen: it is
    static HTML that works with JavaScript off, like every other URL here.

THE ONE CONFIG KNOB
    PARTNER_SIGNUP_URL (tools/core.py, or the repository variable of the same
    name that both workflows pass through). Payhip → Marketing → Affiliates
    hands out a single sign-up link; pasting it flips the primary CTA from
    "message us on Payhip" to the real application form. Left empty, the page
    states the program is invite-only and routes applicants to the store
    contact form — the only channel that reaches the owner, because
    EMAIL_ENDPOINT is unset and a form on this site would deliver nothing.

HONESTY RULES (the same ones tools/verify.py enforces site-wide)
    No fabricated commission rate, no earnings estimate, no partner count, no
    invented quotes, no "top affiliate" claims. The copy also avoids the bare
    word the honesty guard polices site-wide, so the rule cannot be tripped by
    a sentence that exists to state the rule. What the page does promise is
    verifiable: the catalog is real (read from data/products.json at build
    time, so a Payhip sync keeps every price and image true), delivery is
    instant, and refunds follow refunds.html.
"""
from core import *

PARTNER_DIR = "partner"
PARTNER_URL = f"/{PARTNER_DIR}/"

# ── The share kit ────────────────────────────────────────────────────────
# Explicit slug lists, same discipline as tools/pages_guides.py: chosen by
# hand from the real catalog, and the build FAILS LOUDLY if a slug disappears
# so a Payhip sync can never leave a silent hole on a page partners copy from.
#
# Free packs come first on purpose. A creator's audience converts on a $0
# download far more reliably than on a paid kit, and an honest program points
# partners at what actually works for them instead of at the biggest basket.
PARTNER_FREE_SLUGS = [
    "free-fine-liner-brushes-100",
    "free-color-vault-1200-swatches",
    "procreate-starter-guide-free-ebook",
]

PARTNER_PAID_SLUGS = [
    "portrait-skin-brushes-procreate",
    "brush-palette-bundle-160",
    "ultimate-portrait-mastery-bundle",
    "procreate-portrait-masterclass-ebook",
    "master-library-2000-brushes",
]

# Why each paid kit is in the share kit. Merchandising copy lives here (never
# in products.json, which tools/payhip_sync.py rewrites daily).
PARTNER_ANGLES = {
    "portrait-skin-brushes-procreate":
        "The lowest-friction paid kit: one specific complaint (flat, plastic-looking skin) and a $5 fix. Easiest thing to recommend honestly.",
    "brush-palette-bundle-160":
        "Two things every new library is missing — pattern brushes and colour — in one checkout. Reads as a sensible starter, not an upsell.",
    "ultimate-portrait-mastery-bundle":
        "For audiences already painting portraits: four kits wired into one line → skin → hair → finish workflow.",
    "procreate-portrait-masterclass-ebook":
        "A PDF method, not a brush pack. Right fit for tutorial and process audiences who want the workflow behind the tools.",
    "master-library-2000-brushes":
        "The flagship: one organised library in category folders instead of tool fatigue. Recommend it to people who already own brushes, not to beginners.",
}


def _kit_products(slugs):
    """Real product records for `slugs`, or a loud build failure.

    Same contract as the buyer guides: a renamed or removed product must break
    the build here rather than quietly drop out of a page partners copy links
    and prices from.
    """
    out = []
    for slug in slugs:
        p = BY_SLUG.get(slug)
        if not p:
            raise SystemExit(
                f"tools/pages_partner.py: '{slug}' is not in data/products.json. "
                "Fix the slug in PARTNER_FREE_SLUGS / PARTNER_PAID_SLUGS — a partner "
                "share kit with a hole in it is worse than no share kit.")
        out.append(p)
    return out


def _cover(p, depth):
    """(src, srcset, w, h) for a product cover — local file or Payhip remote."""
    im = p.get("images") or {}
    f = im.get("card") or im.get("main") or ""
    if not f:
        return "", "", 0, 0
    if is_abs(f):
        return f, "", im.get("cardW") or 0, im.get("cardH") or 0
    src = rel(depth, f"assets/products/{p['slug']}/{f}")
    return src, img_srcset(depth, p["slug"], im, "(max-width:640px) 92vw, 320px"), \
        im.get("cardW") or 750, im.get("cardH") or 750


def _share_card(p, depth, angle=None):
    """One row of the share kit: cover, the real copy, the real links.

    Every value is read from the product record — name, one-line summary,
    price, Payhip checkout URL — so a daily sync keeps the kit truthful
    without anyone editing this file. The artwork URL is absolute because a
    partner copies it into another site or a social post.
    """
    src, srcset, w, h = _cover(p, depth)
    art_abs = ""
    im = p.get("images") or {}
    art = im.get("main") or im.get("card") or ""
    if art:
        art_abs = art if is_abs(art) else absurl(f"assets/products/{p['slug']}/{art}")
    img_html = (f'<img src="{src}"{srcset} width="{w}" height="{h}" loading="lazy" '
                f'decoding="async" alt="{esc(p["name"])} cover">') if src else ""
    angle_html = f'<p class="pt-angle">{esc(angle)}</p>' if angle else ""
    free_note = ('<span class="pt-free">Free — $0, no card</span>' if p.get("free")
                 else f'<span class="pt-price">{esc(p["priceText"])}</span>')
    return f"""    <article class="pt-item">
      <div class="pt-thumb">{img_html}</div>
      <div class="pt-body">
        <h3>{esc(p['name'])}</h3>
        {free_note}
        <p class="pt-copy">{esc(p.get('short') or '')}</p>
        {angle_html}
        <dl class="pt-links">
          <div><dt>Product page</dt><dd><a href="{rel(depth, f"products/{p['slug']}/")}">{esc(absurl(f"products/{p['slug']}/"))}</a></dd></div>
          <div><dt>Checkout (Payhip)</dt><dd><a href="{esc(p.get('payhipUrl') or STORE_URL)}" target="_blank" rel="noopener">{esc(p.get('payhipUrl') or STORE_URL)} ↗</a></dd></div>
          <div><dt>Cover artwork</dt><dd><a href="{esc(art_abs)}" target="_blank" rel="noopener">{esc(art_abs)} ↗</a></dd></div>
        </dl>
      </div>
    </article>"""


def _steps(depth):
    """How a partner actually gets in and gets paid, on Payhip's rails.

    Step 1 branches on PARTNER_SIGNUP_URL so the page never offers a dead
    button: with no sign-up link configured it says the program is invite-only
    and points at the store contact form, which is the channel that reaches
    the owner.
    """
    if PARTNER_SIGNUP_URL:
        first = (f'Apply through the partner sign-up link below. It is the Payhip '
                 f'affiliate sign-up page for this store, so your application lands '
                 f'straight in the dashboard that will later pay you.')
    else:
        first = (f'Send a message through the <a href="{STORE_URL}" target="_blank" '
                 f'rel="noopener">Payhip store contact form ↗</a>. The program is '
                 f'invite-only for now, so there is no open application form to point '
                 f'you at — and this site runs no email endpoint of its own, so the '
                 f'store form is the one route that reliably reaches us.')
    items = [
        ("Apply", first +
         " Tell us where you post, who you post for, and which kit you would "
         "recommend first. That last answer matters more than follower counts."),
        ("Get approved and get your links",
         "Applications are read and answered by a person, not auto-approved. Once you are in, "
         "your Payhip affiliate dashboard holds a tracked link for each product you may promote, "
         "plus a profile link that sends visitors to the store home. Those links carry your "
         "affiliate key — that is the whole mechanism, and it is why only they get you credit."),
        ("Share it where your audience already is",
         "Use the artwork and copy in the share kit below, or write your own. A short honest "
         "note about what a kit fixed for you outperforms a pasted sales pitch, and it is the "
         "only kind of promotion the rules below allow."),
        ("Get paid by Payhip",
         "Payhip tracks the referral, calculates your share and pays it out on its own schedule "
         "and thresholds. Your earnings report lives in your Payhip affiliate dashboard. "
         "DigiKitPro never sees or holds your payout, so we cannot quote you a rate here — "
         "yours is confirmed in writing before you promote anything."),
    ]
    lis = "".join(
        f'<li><h3>{esc(t)}</h3><p>{b}</p></li>' for t, b in items)
    return f'<ol class="pt-steps">{lis}</ol>'


def _rules(depth):
    """What a partner may and may not say.

    The site's own fabrication rules (tools/verify.py: no testimonials, no
    review counts, no star ratings, no customer counts, no scarcity pressure)
    are simply extended to people promoting it. A partner who invents social
    proof damages buyers and the store, so this is a condition, not a preference.
    """
    allowed = [
        "Describe what is actually in the kit — the brush counts, file types and contents on the product page are real and safe to repeat.",
        "Show your own artwork made with the files, and say plainly that you are a partner and earn a share of sales through your link.",
        "Link the free packs. They are genuinely free, install the same way as paid kits, and they are the honest way for someone to test quality before spending.",
        "Quote the price shown on the product page, and the licence: finished artwork is the buyer's to use commercially; the brush files themselves may not be resold or redistributed.",
        "Answer questions from your own use. If you have not used a kit, say so rather than performing experience you do not have.",
    ]
    forbidden = [
        'Invented social proof: review counts, star ratings, sales totals, partner counts, or a quote from a customer who never said it. The site itself is not allowed to publish these — the build fails if any of them appear — and neither is anyone promoting it.',
        "Earnings promises to your audience (\"make $500 a month with these brushes\") or an income claim about the program that was not put in front of you in writing.",
        "Scarcity or urgency pressure that is not real — countdowns, \"price rises tonight\", \"last few copies\". Digital files do not run out.",
        "Spam: unsolicited DMs, comment-section link drops, or posting your link where you were not asked for it.",
        "Paid ads that bid on the DigiKitPro brand name, or any channel that makes a paid placement look like independent advice without disclosing it.",
        "Giving away the files, a discount code you invented, or a mirror of any download. Promote the store; do not redistribute the product.",
    ]
    a = "".join(f"<li>{esc(x)}</li>" for x in allowed)
    f_ = "".join(f"<li>{esc(x)}</li>" for x in forbidden)
    return f"""<div class="pt-rules">
      <div class="pt-rule-col pt-do">
        <h3>Do</h3>
        <ul>{a}</ul>
      </div>
      <div class="pt-rule-col pt-dont">
        <h3>Do not</h3>
        <ul>{f_}</ul>
      </div>
    </div>
    <p class="muted pt-rules-note">Breaking these ends the partnership. Full commercial terms sit in the
    <a href="{rel(depth, 'terms.html')}">Terms of Service</a>, and what you may promise buyers about refunds is in the
    <a href="{rel(depth, 'refunds.html')}">Refund Policy</a> — all sales are final once files are downloaded, and faulty files are always resolved.</p>"""


def _faqs():
    """FAQ copy in one place: rendered as the accordion and as FAQPage schema,
    so the structured data can never drift from what the page says."""
    signup_answer = (
        "Through Payhip, which already handles every order on this store. Its affiliate system "
        "issues your tracked links, attributes the sales you send and pays your share. DigiKitPro "
        "runs no separate partner accounts, no login and no commission ledger of its own.")
    if not PARTNER_SIGNUP_URL:
        signup_answer += (
            " The program is invite-only at the moment: message us through the Payhip store "
            "contact form and a person will answer.")
    return [
        ("How does the DigiKitPro partner program work?", signup_answer),
        ("What commission do partners earn?",
         "We do not publish a rate on this page, because a rate is set individually with each "
         "partner and Payhip is what actually calculates and pays it. Whatever is agreed is "
         "confirmed to you in writing before you promote anything, and your live figures are in "
         "your Payhip affiliate dashboard. What we will not do is print an estimate here that "
         "turns out to be wrong."),
        ("Where do I see my clicks, sales and payouts?",
         "In your Payhip affiliate dashboard, not on this site. This page is static HTML — it has "
         "no accounts and stores nothing about you, so there is nothing here to log into and "
         "nothing that can go out of date."),
        ("Do I need an audience to apply?",
         "No minimum, and follower counts are not the deciding factor. What matters is whether you "
         "actually use the tools and can tell a specific audience why a specific kit helps them. A "
         "small channel with real trust beats a large one pasting a sales pitch."),
        ("Do I have to buy the products first?",
         "No. The free packs install exactly like the paid kits, so you can judge the quality "
         "without spending anything — and they are the honest first thing to recommend to your "
         "own audience."),
        ("What am I allowed to say when I promote a kit?",
         "What is true. Describe the real contents, show your own artwork, state the price on the "
         "product page, and disclose that you are a partner. No invented reviews, ratings, sales "
         "totals or earnings promises, and no fake scarcity — the full list is above under the "
         "promotion rules."),
        ("Do I have to disclose the partnership?",
         "Yes, clearly and next to the link, before anyone taps it. It is required by advertising "
         "regulators in the US, UK and EU, and it is a condition of the program regardless of "
         "where you or your audience live."),
        ("Which links get me credit?",
         "Only the tracked links from your Payhip affiliate dashboard — they carry your affiliate "
         "key. A plain link to this website or to a product page does not attribute anything to "
         "you, so do not substitute one for the other."),
        ("Can I run paid ads to my links?",
         "Not on the DigiKitPro brand name. Other paid placement is worth a conversation first: "
         "tell us the channel and we will confirm in writing whether it is allowed, so nothing "
         "depends on a guess."),
        ("Who do I contact about a partner problem?",
         f"Message the Payhip store ({STORE_URL}), which is where every order and support request "
         "for this shop already goes. Include your affiliate details and what happened — that is "
         "the fastest route to a real answer."),
    ]


def build_partner():
    """Generate partner/index.html (depth 1: links back to the root are ../)."""
    depth = 1
    free_kit = _kit_products(PARTNER_FREE_SLUGS)
    paid_kit = _kit_products(PARTNER_PAID_SLUGS)

    if PARTNER_SIGNUP_URL:
        cta_href, cta_label, cta_ext = PARTNER_SIGNUP_URL, "Apply to join ↗", ' target="_blank" rel="noopener"'
        status = ('<p class="pt-status"><span class="pt-dot pt-dot-open"></span>'
                  'Applications are open — apply through the Payhip partner sign-up page.</p>')
    else:
        cta_href, cta_label, cta_ext = STORE_URL, "Message us on Payhip ↗", ' target="_blank" rel="noopener"'
        status = ('<p class="pt-status"><span class="pt-dot pt-dot-invite"></span>'
                  'Invite-only for now — message the store and a person replies. No open '
                  'application form exists yet, so this page will not pretend one does.</p>')

    faqs = _faqs()
    faq_items = "".join(
        f'<details class="faq-q"><summary>{esc(q)}</summary>'
        f'<div class="faq-body"><p>{esc(a)}</p></div></details>' for q, a in faqs)
    schemas = (schema_breadcrumb([("Home", "/"), ("Partner Program", PARTNER_URL)])
               + schema_faq(faqs))

    free_cards = "\n".join(_share_card(p, depth) for p in free_kit)
    paid_cards = "\n".join(_share_card(p, depth, PARTNER_ANGLES.get(p["slug"])) for p in paid_kit)

    html_out = head("Partner Program — Promote DigiKitPro Procreate Brushes",
        "The DigiKitPro partner program: promote real Procreate brush kits, get tracked links through Payhip's affiliate system, and use our ready-made share kit of artwork, copy and links. Read the honest rules first.",
        absurl(PARTNER_DIR + "/"), depth, schemas=schemas,
        ctx=page_ctx("partner"))
    html_out += header(depth)
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(depth, [("Partner Program", PARTNER_DIR + "/")])}
    <p class="eyebrow">Partner program</p>
    <h1>Promote brushes you can <em>actually stand behind</em></h1>
    <p class="lead">DigiKitPro is a catalog of Procreate brush kits, sold as instant digital downloads
    through Payhip. Partners recommend the kits that fit their audience, share tracked links, and are
    paid by Payhip for the sales they send. No invented social proof, no earnings theatre — the rules
    below are the same ones this site holds itself to.</p>
    {status}
    <div class="pt-cta-row">
      <a class="btn btn-gold btn-lg" href="{esc(cta_href)}"{cta_ext} data-dkp-event="partner_apply_click">{cta_label}</a>
      <a class="btn btn-line btn-lg" href="{rel(depth, 'freebies.html')}">Try the free kits first</a>
    </div>
    <p class="muted pt-cta-note">Prefer to look first? Browse the <a href="{rel(depth, 'products.html')}">full catalog</a>
    or the <a href="{rel(depth, 'bundles.html')}">bundles</a> — every price and brush count on this page is read
    from the live product data at build time.</p>
  </div></section>

  <section class="section" id="how"><div class="wrap">
    <p class="eyebrow">How it works</p>
    <h2>Four steps, all on Payhip's rails</h2>
    <p class="lead-sm muted">Payhip already takes every payment, delivers every file and answers every
    order message for this store. The partner program runs on its affiliate system for the same reason:
    one place that holds the truth about a sale.</p>
    {_steps(depth)}
  </div></section>

  <section class="section section-alt" id="share-kit"><div class="wrap">
    <p class="eyebrow">Share kit</p>
    <h2>What to post, already written down</h2>
    <p class="lead-sm muted">Real covers, real one-line copy, real links — pulled from the catalog when
    the page is built, so a price change in Payhip reaches this page on the next deploy. Copy the text,
    save the artwork, and replace the plain links with your own tracked ones once you are approved.</p>

    <h3 class="pt-sub">Start with the free kits</h3>
    <p class="muted pt-sub-note">$0, no card, and they install exactly like the paid sets. This is how
    someone tests the quality before trusting you with a purchase — so it is the first thing worth sharing.</p>
    <div class="pt-kit">
{free_cards}
    </div>

    <h3 class="pt-sub">Then the kits worth recommending</h3>
    <p class="muted pt-sub-note">Chosen for audiences that already paint: one $5 specialist fix, one
    sensible starter bundle, one deep portrait workflow, one method eBook, one flagship library. Each
    note says who it is genuinely for — and who it is not.</p>
    <div class="pt-kit">
{paid_cards}
    </div>

    <div class="pt-assets">
      <h3 class="pt-sub">More to link, if you want it</h3>
      <div class="trend-pills">
        <a class="trend-pill" href="{rel(depth, 'freebies.html')}">All free brush packs</a>
        <a class="trend-pill" href="{rel(depth, 'bundles.html')}">Bundles compared</a>
        <a class="trend-pill" href="{rel(depth, 'guides/procreate-bundles-compared/')}">Which bundle should I buy?</a>
        <a class="trend-pill" href="{rel(depth, 'guides/procreate-starter-kits/')}">Starter kits guide</a>
        <a class="trend-pill" href="{rel(depth, 'category/portrait/')}">Portrait brushes</a>
        <a class="trend-pill" href="{rel(depth, 'category/skin-texture/')}">Skin texture</a>
        <a class="trend-pill" href="{rel(depth, 'blog/how-to-install-procreate-brushes/')}">How to install a .brushset</a>
        <a class="trend-pill" href="{rel(depth, 'products.html')}">Full catalog</a>
      </div>
      <p class="muted">Tutorials and guides are the easiest honest entry point: they answer a question
      someone already has, and the kit sits in the answer. Browse the
      <a href="{rel(depth, 'blog.html')}">article library</a> and the
      <a href="{rel(depth, 'guides/')}">buyer guides</a>.</p>
    </div>
  </div></section>

  <section class="section" id="rules"><div class="wrap">
    <p class="eyebrow">Promotion rules</p>
    <h2>What you may say, and what ends the partnership</h2>
    <p class="lead-sm muted">This site is not allowed to publish fake reviews, invented ratings,
    customer counts or pressure tactics — a build check fails the deploy if any of it appears. Partners
    promote under the same rule.</p>
    {_rules(depth)}
  </div></section>

  <section class="section section-alt" id="faq"><div class="wrap narrow">
    <p class="eyebrow">Questions</p>
    <h2>Partner FAQ</h2>
    <div class="faq-list">{faq_items}</div>
    <div class="prose">
      <h2>Ready to apply?</h2>
      <p>{'Use the sign-up link at the top of this page.' if PARTNER_SIGNUP_URL else 'The program is invite-only right now, so there is no form to fill in — message the store instead.'}
      Either way, tell us where you post, who reads or watches it, and which kit you would recommend
      first. Applications are read by a person and answered honestly, including when the answer is no.</p>
      <p><a class="btn btn-gold" href="{esc(cta_href)}"{cta_ext}>{cta_label}</a></p>
      <p class="muted">Anything about an order, a download or a file that will not open goes to the
      <a href="{rel(depth, 'contact.html')}">contact page</a> or the
      <a href="{STORE_URL}" target="_blank" rel="noopener">Payhip store ↗</a>.</p>
    </div>
  </div></section>
  {newsletter(depth, heading="Free brush drops for your audience",
              sub="New free packs and kit releases, sent when they go live — useful when you want something honest to share before you are a partner.",
              source="partner", lead="partner-program", uid="ptnl",
              cta="Send me new releases", eyebrow="Stay in the loop")}
</main>
{footer(depth)}"""
    write(f"{PARTNER_DIR}/index.html", html_out)
    print(f"Built partner portal: /{PARTNER_DIR}/ "
          f"({len(free_kit)} free + {len(paid_kit)} paid share-kit entries, "
          f"{'applications open' if PARTNER_SIGNUP_URL else 'invite-only — PARTNER_SIGNUP_URL not set'})")
