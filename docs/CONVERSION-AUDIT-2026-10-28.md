# DigiKitPro: conversion audit and implementation plan

**Review date:** 28 October 2026<br>
**Status:** Changes are in the working branch and have been tested locally. They have **not been deployed to digikitpro.shop**. No live order, free download completion, email delivery, GA4 report, Search Console account, or Payhip administrator setting was tested.

## 1. Executive assessment

There is not enough evidence to say *why* free visitors rarely buy. We do not have visitor counts, traffic sources, device mix, free-download completions, checkout starts, paid orders, refunds, acquisition cost, or customer feedback. Price sensitivity, low-intent traffic, poor product fit, missing proof, and checkout friction are hypotheses, not findings.

The review did identify several concrete problems worth fixing before experimenting with growth:

1. **Search input can execute as HTML.** The public `js/main.js` inserts the `q` parameter into a no-results message as HTML. A harmless marker executed when this was reproduced locally in Chromium. The local fix renders the query as text. Treat deployment of this security fix as urgent; the local test does not show that the live site has been exploited.
2. **A Payhip click can open two tabs.** The public script calls `window.open(..., 'noopener')` and treats a null return as a blocked popup, then redirects the original tab. With the original code, a local Chromium test produced two Payhip tabs from one click. Native links replace that handler in the branch; the corrected behavior was tested with Payhip stubbed.
3. **Mobile navigation was clipped.** The original 390px product-page screenshot showed the header's browse button cut off and the menu beyond the viewport. The responsive header was repaired locally and tested down to 320px.
4. **The free-to-paid handoff and email expectations were unclear.** Free resources link directly to Payhip; the repository has no configured newsletter endpoint, while the old thank-you page asserted a signup. The branch removes the unconfigured forms and false confirmation, preserves the free links, and offers optional, relevant next steps. We cannot inspect whether the Payhip account has separately configured redirects or email automations.
5. **Actual purchase measurement is unavailable to this review.** The website's Payhip clicks are not completed checkouts. The local event improvements make some actions observable, but only a verified Payhip/GA setup and order data can establish purchases and attribution.

**Commercial interpretation:** the fixes remove verified UX/security problems and improve product selection. Their effect on paid conversion, search visibility, or revenue is unknown until measured after deployment.

## 2. Evidence and boundaries

| Observation | Evidence and confidence | Local action / remaining uncertainty |
|---|---|---|
| Search query reflected into `innerHTML` | Public [site script](https://digikitpro.shop/js/main.js) and one safe local Chromium reproduction using `/search.html?q=…`. | Escaped as text in `js/main.js`; regression-tested. No live exploitation or production fix verified. |
| Double outbound navigation | Public script has the `window.open`/fallback logic; baseline source reproduced two tabs in local Chromium at 390×844 with Payhip stubbed. | Removed interception; seven paid/free links each opened one stubbed Payhip tab and kept the original page. Live checkout remains untested. |
| Header controls outside a narrow viewport | Baseline local product screenshot at 390px; clipped by page overflow. | Removed duplicate mobile header links, retained them in the menu/footer, and tested menu and layout at 320–1440px. |
| No working site newsletter provider | `EMAIL_ENDPOINT` is empty in the checked-out source; the old page nevertheless described a signup/confirmation. | Default build has resource links instead of an unconfigured form. No ESP, consent record, unsubscribe, or delivery has been implemented. |
| Free resources lack an explicit, relevant next purchase choice | Original free product pages linked to Payhip but had no resource-specific comparison. This establishes a design gap, not its effect on sales. | Four comparisons and practice exercises added; free assets remain useful without purchasing. Follow-up is visitor-initiated, not automatic. |
| Product choices were hard to differentiate | Baseline priority pages had generic/repeated sales copy and generic upgrades. The [Portrait Mastery](https://digikitpro.shop/products/portrait-mastery-kit-46-brushes/), [Skin](https://digikitpro.shop/products/portrait-skin-brushes-procreate/) and [Artista](https://digikitpro.shop/products/artista-studio-kit-76-brushes/) pages and corresponding Payhip listings were inspected. | Specific positioning, FAQs, installation details and alternatives added. The three observed listing prices matched the catalog at review time: $8, $5 and $5 respectively. No price was changed. |
| Artwork provenance and sales rank not established | The original homepage connected illustrative before/after art to product tools and used bestseller language; no source files or sales ranking were available to verify these claims. | Illustration is labelled as illustrative; the unverified bestseller badge is displayed as “Featured.” Product-cover images remain existing catalog artwork, not newly invented proof. |
| Inherited trust and delivery claims need account-side verification | The original About/FAQ pages described a newsletter that the repository does not configure, certain payment methods and an exact delivery mechanism; other inherited copy promises instant delivery or lifetime access. | Selected high-traffic copy is more cautious. The existing Terms and other catalog descriptions have **not** been comprehensively revised and need owner/legal review; delivery was not tested. |
| Some accessibility issues were detected in a local automated sample | An initial axe-core run on five 390px pages identified low-contrast small text, non-distinct inline links and mismatches between visible and accessible labels. | Colors, link styling and labels were corrected. The same automated sample reports zero violations; this is not a full accessibility audit. |
| Search technical basics exist, but performance is unknown | The live [robots.txt](https://digikitpro.shop/robots.txt) and [sitemap](https://digikitpro.shop/sitemap.xml) were accessible. Local verification checks canonicals, internal links and structured data. | The sitemap no longer declares every page modified on every build; FAQ schema duplication was removed. This does **not** establish indexing, ranking, clicks or Core Web Vitals. |
| Catalog synchronization may drift | All 51 existing local catalog records are manually owned (`auto` is false/absent); the existing sync updates live facts only on auto-owned records. | No price, ID, Payhip URL, availability flag, product name or image filename was changed. Compare manual records with Payhip regularly; no mismatch beyond the selected listings was established. |

### What was and was not checked

- Inspected the public homepage, free-resource page, thank-you page, priority product pages, selected Payhip listings, robots/sitemaps, source templates, event layer and workflows.
- Compared all 51 catalog records to `git show HEAD:data/products.json`: product count, identity, price, currency, free flag, availability flag, Payhip destinations and image filenames were unchanged. This is a **local baseline comparison**, not a reconciliation of all 51 against the live store.
- Existing customer records, orders, payment settings and pricing were not accessed or modified. No campaign or promotion was launched.
- No customer interviews, heatmaps, representative accessibility audit, field performance test, real checkout, iPad import, delivery test, or search-account data were available. A local mocked browser test cannot certify those outcomes.

## 3. Priorities

| Priority | Action | Why / how to verify | Status |
|---|---|---|---|
| **P0** | Review and deploy the search injection fix; re-test a harmless encoded query in production. | Prevent query text from becoming executable HTML. Check the deployed versioned `main.js` and normal search results. | Fixed and regression-tested locally; not deployed. |
| **P0** | Deploy the native outbound-link and mobile-header fixes. | Reproduce the single-tab flow and reachable menu on a real phone and desktop, then test actual Payhip separately. | Local tests passed with Payhip stubbed. |
| **P0** | Decide an appropriate analytics consent approach for operating jurisdictions; verify GA enhanced measurement and Payhip cookie behavior. | DNT/GPC/opt-out are not necessarily sufficient consent. Inspect actual network requests, search terms, referrers and vendor settings with counsel as needed. | Account/legal access needed. `DKP_ANALYTICS=false` is available as a build kill switch. |
| **P1** | Measure real paid orders and check cross-domain continuity. | Use Payhip order reports as financial source of truth; validate GA4 purchase events and deduplication before reporting attributed sales. | Requires owner access and an approved test. |
| **P1** | Deploy the four relevant, optional free-to-paid comparisons and improved priority pages. | Compare recommendation engagement and downstream paid-product interest by resource; do not call a click a sale. | Built and locally tested. |
| **P1** | Review inherited Terms and catalog promises before release. | Terms still describe instant delivery; some other catalog listings still contain lifetime/access or performance claims that were not verified. Resolve contradictions with actual policy and legal review; do not silently change customer rights. | Owner review required. |
| **P1** | Verify checkout, receipt, file download, import and support on actual devices. | Cover the free guide, each paid priority kit and at least one other file type. A private/sandbox test or any test coupon requires owner approval. | Not done. |
| **P2** | Add verifiable product demonstrations and preview images. | Confirm rights and the exact brushes used; compare with existing Payhip galleries. Ask customers for permission before using their work or quotes. | No new proof or reviews invented. |
| **P2** | Reconcile catalog facts and inspect Search Console/field performance. | Review prices, contents, compatibility, internal links, indexing, search queries, and real mobile performance. | Account/device access needed. |

## 4. Implemented funnel and page copy

### Homepage

The branch retains the black-and-gold brand and uses the existing product cover as the hero image. The first message is **“Procreate Brushes for iPad Artists”** with “Shop All Brushes” and “Try Free Brushes.” Featured paid kits now precede the illustration and free resources; they are not described as proven bestsellers. The before/after is explicitly illustrative. The hero is visible on first paint; its entrance animation, looping float, decorative parallax, slider autoplay and unsolicited sticky sales bar are disabled.

The featured row leads to Portrait Mastery, Portrait Skin, Artista and Essential Line Art. This is merchandising, not evidence that these are the highest-selling products. The free guide and free tools remain easily accessible.

### Free-resource journey

A visitor can use the free product on its own. Each page has its original direct Payhip link plus a visible, optional **“After downloading: see your practice plan”** link and an in-page exercise/comparison. `thank-you.html?lead=<slug>` displays the selected suggestion; an unknown slug or JavaScript-disabled browser sees all four. The URL can be opened at any time, so it is not a conversion confirmation.

| Free resource | Practice prompt | Relevant separate paid option | Why it is relevant, not a forced upgrade |
|---|---|---|---|
| Portrait Starter Guide (PDF) | Make a small head study using three value groups; add texture after the shapes read. | Portrait Mastery, 46 brushes + four paper textures, **$8** | The guide teaches concepts; the paid kit organizes tools for a portrait workflow. Built-in brushes are enough to follow the guide. |
| Free Fine Liner, 100 brushes + 13 paper textures | Draw one object with two line weights and group the shadows. | Artista Studio, 76 brushes, **$5** | Artista adds broader sketch, shading, graphite, traditional-media and effects categories. Some linework overlaps; neither pack is a prerequisite. |
| Free Chalkboard toolkit | Letter a short word on a dark canvas; lift small areas with the eraser. | Professional Charcoal Studio, **$5** | A different traditional-media texture option, not a claim that chalk is incomplete. |
| Free Color Vault, 40 palettes / 1,200+ swatches | Use three colors from one palette in a small illustration. | Brush & Color Palette Bundle, 160 pattern brushes + 12 palettes, **$5** | The free item is a color resource, not a brushset or trial. The paid bundle combines pattern tools and other palettes. |

Prices and contents above are from the local catalog, which must be reconciled with Payhip before launch; no discount or price change is proposed here.

**Important delivery warning:** do not automatically redirect customers away from their Payhip completion page merely to show this funnel. Payhip says a checkout redirect replaces the immediate digital-download page, requiring the buyer to find the email link instead. Protect access to the purchased files first; consider any product-specific redirect only with explicit owner approval and a tested recovery path. [1](https://help.payhip.com/article/97-checkout-redirect)

### Priority product positioning

| Product | Implemented lead / fit | Buyer-facing distinctions |
|---|---|---|
| **Portrait Mastery 46** | “Sketch, blend and finish portraits with 46 Procreate brushes organized by task, plus four paper textures.” | Wider sketch-to-finish portrait workflow, $8. Lists sketch, ink, blend, hair, detail, texture and finish groups; a tool kit, not a course. The FAQ distinguishes it from the separate Skin set and explains the listed contents of the Ultimate Portrait bundle. |
| **Portrait Skin 19** | “Add pores, freckles and natural-looking texture to portraits with 19 Procreate brushes, including textured blenders and detail tools.” | Focused on skin details and blending, $5. Points to the broader 46-brush kit and notes the Skin kit is listed in the Ultimate Portrait bundle so visitors can check for overlap. |
| **Artista 76** | “A versatile 76-brush Procreate studio for sketching, linework, shading, graphite, markers and texture—organized into eight groups.” | Broad studio use, $5; contrasts it with the portrait-focused kit and acknowledges overlap with the free liner set. |

The pages now surface contents, iPad/Procreate requirements, ZIP sizes from the catalog (91 MB, 77 MB and 66 MB respectively), installation guidance, FAQs, comparison links and existing preview art. These are catalog/listing facts, not evidence of a tested file or artistic result. Four local images exist for each priority product; the viewed Payhip listings showed more. Audit rights, accuracy and performance before transferring additional imagery.

**Next evidence to collect:** a short, genuine screen recording of the actual kit; a close-up of each relevant brush with the brush name; installation on a real iPad; and optional customer work with explicit permission. Do not present illustrative art, reviews, results, rankings or compatibility claims as verified proof without provenance.

## 5. Technical, checkout and privacy change log

- `tools/core.py`, `tools/pages_main.py`, `tools/pages_product.py`, `tools/pages_misc.py`, `data/products.json`, `data/free-journeys.json`: product-first homepage, four journeys, safer delivery/consent copy, format-specific installation, product FAQs/comparisons, and one FAQ schema block per product. Forty-six identical generic delivery answers were softened; FAQ/About no longer promise an unconfigured newsletter or guaranteed payment methods. Prices and legal refund terms were not changed. The existing Terms and other inherited product copy still require owner verification.
- `js/main.js`: native external links and search-query escaping; future provider responses no longer imply a confirmed subscription. `tools/qa_form.py` is now an offline state check and does not send an email.
- `css/style.css`, `js/motion.js`, `js/translate.js`: responsive header/product grid, immediate hero visibility, non-autoplay before/after and no unsolicited sticky bar; improved small-text contrast, inline-link distinction and language/share control labels. The mobile navigation has a no-JavaScript fallback.
- `js/analytics.js`, `tools/core.py`, `tools/pages_misc.py`: front-end event fields and privacy disclosure, early GA/local-count suppression for DNT, GPC and site opt-out, no production Google tag on preview hosts, query-free configured page URL, and limited campaign labels. Site opt-out does not automatically erase old cookies or control Payhip's independent processing.
- `.github/workflows/deploy.yml` and `sync-payhip.yml`: both honor the optional repository variable `DKP_ANALYTICS=false`. Current default remains enabled; setting the variable and running a build is an owner decision.
- `tools/pages_misc.py`: removed unverified build-date `lastmod` values and automatically changing “last updated” policy dates. Google says `lastmod` should reflect significant changes and can be omitted when unreliable; Google ignores sitemap `priority` and `changefreq`. [2](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- Product image preloads now use the same relative URL as the gallery image, so local previews do not fetch the live domain. Main, analytics, motion and translation script URLs carry content hashes after a rebuild, reducing stale-script risk. HTML/CDN cache behavior still needs checking after deployment.
- `tools/payhip_sync.py`, `tools/seo_engine.py`, `tools/pages_season.py`, `tools/pages_partner.py`: selected default copy no longer adds blanket claims about instant delivery or access duration. This does not change any existing Payhip listing or payment setting.

### Checkout test checklist — requires authorization and access

1. With an owner-approved private test/sandbox method, follow a free resource and one paid kit from the site to Payhip on iPhone/Android and desktop. Record each screen, total price, currency, tax, any email requirement, wallet/payment options, back-navigation and failure handling. Do not publish a coupon or change prices without approval.
2. Complete the authorized test; verify the order in Payhip, whether the completion page offers the file, the email/receipt, download and re-download, and a help request. Handle test orders and refunds according to the owner's bookkeeping policy.
3. Open the ZIP on an actual iPad, import `.brushset` and `.swatches` files separately, and open the guide PDF. Verify contents, app/version compatibility and missing-file recovery; the local web tests did none of this.
4. Reconcile the refund, support, access-duration and commercial-use statements with actual store policy and applicable law. Do not assume a platform default proves this account's configuration.

## 6. Measurement and attribution specification

### Event inventory in the local build

| Event | Meaning | Key fields | Do **not** interpret as |
|---|---|---|---|
| `product_view` | A catalog product page rendered with analytics allowed | `product_id`, `price`, `free`, `page_path` | An engaged shopper or completed order |
| `free_download_click` | A visitor clicked a free Payhip link | `product_id`, numeric `price` (0), `location` | A completed free download or marketing consent |
| `free_next_step_click` | The optional practice-plan link was clicked | `source_product_id`, `surface` | A completed download |
| `free_next_step_view` | The optional follow-up page was viewed | `source_product_id` only when the slug matches a rendered resource | A signup or download confirmation |
| `premium_product_click` | A paid recommendation link was clicked | `source_product_id`, `product_id`, `surface` | Checkout or purchase |
| `kit_comparison_click` | A comparison alternative was clicked | `source_product_id`, `product_id` | Purchase |
| `product_buy_click` / `outbound_payhip_click` | A paid buy link / any Payhip link was clicked | `product_id` when available, `price`, `location`, `outbound_url` | A Payhip checkout start, successful payment or revenue |
| `email_signup_request` | A configured provider returned a response to a future form request | `source`, `lead_magnet`, `state` | Confirmed opt-in, unsubscribe functionality or delivered email |

These events were tested in the browser's local data layer with the Google tag **stubbed**. Browser `localStorage` counts (`dkp.report()`) are not a shared dashboard. The tag itself, GA4 ingestion, DebugView, Google enhanced measurement, consent behavior across Payhip and purchase event configuration were not tested. Avoid adding the GA enhanced-measurement outbound click count to the custom outbound count as if they were different people.

### Owner-only account setup after consent review

1. Inspect the site's GA4 property and Payhip before changing anything. Payhip documents entering a GA4 measurement ID in **Account → Settings → Advanced Settings → Google Analytics**, and says it sends a purchase event after completed checkout; whether this particular account is configured or whether free checkouts affect reports must be verified. [1](https://help.payhip.com/article/93-google-analytics)
2. If approved and legally appropriate, use the same intended data stream on both domains and configure `digikitpro.shop` and `payhip.com` in GA4 **Admin → Data streams → Web → Configure tag settings → Configure your domains**. Google describes verifying the `_gl` linker parameter on the destination. Payhip redirects, a shared platform domain, browser privacy and consent can still prevent continuity; test rather than assume. [1](https://support.google.com/analytics/answer/10071811?hl=en)
3. Register needed event-scoped custom dimensions such as `product_id`, `source_product_id`, `surface` and `location`; check available GA4 dimension limits and future data collection. Use DebugView/Tag Assistant with an authorized test and compare event parameters to Payhip's order and transaction ID. Do not create a second purchase event for the same transaction.
4. GA's page-location config omits arbitrary query strings. The site forwards `utm_source`, `utm_medium` and `utm_campaign` as campaign fields only when all three match a limited ASCII format; `utm_content` and `utm_id` are optional. This is locally tested configuration, **not verified attribution**. Use non-personal campaign labels: format checks cannot detect all names or sensitive data. `utm_term` and paid click-ID attribution have not been validated; Google documents the campaign configuration fields. [1](https://developers.google.com/analytics/devguides/collection/ga4/reference/config)
5. Review GA4 enhanced measurement, especially site-search query capture and referrer/URL data, as well as vendor cookies. The custom event code records search length, not the query, but that alone does not prove Google or Payhip cannot collect query text. Test DNT/GPC, the explicit opt-out link, rejection/withdrawal of consent where required, and a repeat visit on each domain.

### Dashboard definitions

Use the same date range, timezone, attribution model and unit (users, sessions or orders) for each comparison. Label missing values as unavailable; avoid joining records on email or adding personal data to URLs.

| Metric | Numerator / denominator or calculation | Source and caveat |
|---|---|---|
| Traffic mix | Sessions and users by source/medium, landing page, device and country | GA4 after consent and UTM validation. Blockers and consent reduce coverage. |
| Free-resource interest | Unique users or sessions with `free_download_click`, separately by free `product_id` | GA4; a click is not a fulfilled download. |
| Recommendation engagement | Unique users who click `premium_product_click` for a free source / unique users viewing that source page, same time window | GA4 exploration; ensure the denominator and numerator use the same user scope. Does not show that the free file was obtained. |
| Product-page buy intent | Sessions with `product_buy_click` for a paid product / sessions with `product_view` for that same product | GA4 session-scoped exploration/export; the event is not a checkout start. |
| Checkout and paid-order rates | Actual checkout starts and completed **paid** orders, by product and period | Payhip analytics/order export. Payhip's conversion metrics include free and paid products, so separate them where the account allows and validate each denominator. [3](https://help.payhip.com/article/108-conversion-rate) |
| Paid revenue and refunds | Paid order value, discounts/tax treatment, refunds and fees as defined by the owner | Payhip and payment-processor reports; GA is directional, not the accounting ledger. |
| Free-to-paid cohort | After validated identity/attribution: opted-in/measurable users with a free-resource click followed by a verified paid order in 7 and 30 days / users with that free-resource click | Requires cross-domain continuity and reconciled orders. Otherwise report “unavailable,” not a fabricated conversion rate. |
| Search opportunity | Search clicks, impressions, queries, indexed pages and mobile field performance | Search Console and field performance reports; no account access was available. |
| Email | Confirmed opt-ins, sends, bounces, unsubscribes, complaints, clicks and verified orders by consented cohort | ESP and Payhip only after integration. Opens are an unreliable proxy due to privacy features. |

For a **narrow** GA4 funnel, create a closed, user-scoped exploration per free resource: `free_download_click` for that source → `premium_product_click` with the same source and mapped paid product → `product_view` for that paid product → `product_buy_click` for it. Add a verified paid purchase step only after event/transaction validation. This excludes users who buy by another path and cannot prove file delivery; it is not the overall free-to-paid rate.

## 7. 30-day growth and learning plan

All publishing, outreach, provider setup, experiments and campaigns below are proposals requiring owner approval. No budget, traffic, conversion lift or sample size is assumed.

| Window | Actions | Decision / output |
|---|---|---|
| **Days 1–3** | Review this patch, prioritize the search/security fix, deploy through the normal release process, and check mobile, search and one-tab outbound behavior on production. Decide whether to disable analytics until the consent review is complete. | Release checklist, rollback point and evidence of actual deployed files. |
| **Days 4–7** | Gain read-only GA4/Search Console and Payhip reporting access. Audit consent, tag configuration, channel and product data. Run an approved checkout/file/support test. | Baseline dashboard with explicit unknowns; documented checkout failures if any. |
| **Days 8–14** | Reconcile the 51 manual catalog records against Payhip. Produce authentic brush samples for the three priority kits and a short practical guide; add only verified previews. Review Search Console queries and internally link the most relevant tutorial to each kit. | A documented content/proof backlog; no claim of improved SEO yet. |
| **Days 15–21** | Choose **one** low-risk experiment, e.g. whether the guide page's portrait-workflow comparison improves paid-kit engagement. Predefine primary metric, audience, duration, randomization, guardrails and minimum detectable effect using actual baseline traffic. Preserve the free download and price in both variants. | Approved experiment plan, or defer if traffic is insufficient. |
| **Days 22–30** | Inspect quality and completeness of events/orders; review the experiment only if it has enough data. Draft, but do not send, the consent-based email sequence. Prepare 2–3 authentic tutorial/social concepts with destination links and non-personal UTMs for approval. | A decision memo: ship, iterate, continue collecting, or stop. No causal claim from a simple before/after comparison. |

**Guardrails:** free-download link availability, actual file access, mobile navigation, page errors, refund/support requests, and measured paid orders. Do not use revenue-per-click as a substitute for completed paid orders. Avoid choosing a winner from a handful of clicks or running several simultaneous changes and calling their combined movement an experiment result.

## 8. Proposed five-email sequence — not configured or sent

**Entry rule:** only after a person has explicitly opted in to DigiKitPro product news/art tips and any required confirmation is complete. A free-download email, purchase receipt or checkbox unrelated to marketing is not consent. Store the opt-in text/version, time, source and confirmation; honor withdrawal and suppression immediately. Configure sender identity, physical/contact details and a working unsubscribe in the provider; review relevant laws for recipients' jurisdictions. The UK's ICO illustrates the distinction between receipt consent and direct-marketing consent. [2](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/direct-marketing-guidance/plan-direct-marketing/)

Timing below is relative to **confirmed opt-in**, not a download. Each draft includes a footer placeholder that must be replaced by the ESP's tested unsubscribe URL. Adapt the exercise to the resource the subscriber actually chose, without claiming their download completed. Stop the sequence on unsubscribe; suppress or adapt offers after a verified purchase only if that integration is consent-appropriate and tested.

### Email 1 — Day 0: welcome and a useful starting point
**Subject:** A simple portrait practice to start with<br>
**Preheader:** One small study, three values, no special brushes required.

Hi,

Thanks for choosing to receive DigiKitPro art tips. For your next short practice, sketch a head using just three value groups: light, midtone and shadow. Keep the shapes simple before adding detail.

If a guide would help, the free Portrait Starter Guide walks through a portrait workflow. Procreate's built-in brushes are enough to follow along.

**CTA:** [Explore the free guide](https://digikitpro.shop/products/procreate-starter-guide-free-ebook/)

— DigiKitPro<br>
You opted in to product news and art tips. [Unsubscribe: ESP link]

### Email 2 — Day 2: a practical brush exercise
**Subject:** Make texture work for the portrait<br>
**Preheader:** Try a separate layer and build slowly.

Hi,

Once your light and shadow shapes read clearly, add a separate layer and try a small amount of texture around the cheeks or forehead. Reduce the layer's opacity if it distracts from the larger forms.

You can do this with tools you already own. If you are comparing a dedicated workflow kit, Portrait Mastery groups 46 brushes by sketch, ink, blend, hair, detail, texture and finish, with four paper textures.

**CTA:** [See what is in Portrait Mastery](https://digikitpro.shop/products/portrait-mastery-kit-46-brushes/)

— DigiKitPro<br>
You opted in to product news and art tips. [Unsubscribe: ESP link]

### Email 3 — Day 4: choose the right kit
**Subject:** Skin details, portraits or a broader studio?<br>
**Preheader:** Three different toolkits, three different starting points.

Hi,

A larger brush count is not automatically the best fit. Choose according to the work you want to make:

- **Portrait Skin:** 19 brushes focused on skin texture and blending.
- **Portrait Mastery:** 46 brushes for a wider portrait workflow, plus four paper textures.
- **Artista Studio:** 76 brushes across sketching, linework, shading and traditional-media styles.

Each is a separate product. Check the contents and requirements before choosing; keep using the free resources if they already meet your needs.

**CTA:** [Compare the brush kits](https://digikitpro.shop/products.html)

— DigiKitPro<br>
You opted in to product news and art tips. [Unsubscribe: ESP link]

### Email 4 — Day 7: installation help
**Subject:** A quick Procreate import checklist<br>
**Preheader:** Find the file type before you tap it.

Hi,

If you are adding brushes to Procreate, first locate the downloaded file in the iPad Files app. If it is a ZIP, tap it to extract the contents. Then tap the `.brushset` file to import it into Procreate. Palettes use a `.swatches` file; the free guide is a PDF and does not install as a brush.

If anything fails, keep the file and order details and contact the store for help.

**CTA:** [Read the installation guide](https://digikitpro.shop/blog/how-to-install-procreate-brushes/)

— DigiKitPro<br>
You opted in to product news and art tips. [Unsubscribe: ESP link]

### Email 5 — Day 10: answer the decision question
**Subject:** What would you like to practise next?<br>
**Preheader:** Start with the tools that match the work you enjoy.

Hi,

If you are deciding what to practise next, start with the job rather than the biggest collection. Looking for a full portrait workflow? Explore Portrait Mastery. Mainly adding skin detail to an existing painting? Explore Portrait Skin. Prefer drawing and mixed traditional textures? Artista may be a better place to look.

Every product page lists its contents, price and requirements. There is no need to buy another kit if your current tools are working for you.

**CTA:** [Browse the available kits](https://digikitpro.shop/products.html)

— DigiKitPro<br>
You opted in to product news and art tips. [Unsubscribe: ESP link]

## 9. Local QA and release checklist

Latest local results:

- `python3 tools/build.py`: completed; generated pages, feeds, sitemap and search index.
- `python3 tools/verify.py`: **114/114** checks passed, including internal links, product schema, 51 product records, free journeys, no blanket sitemap lastmod, and current script fingerprints.
- `node tools/qa_gallery.mjs`: **134 passed, 0 failed** (jsdom).
- `tools/qa_conversion.mjs`: **73 passed, 0 failed** in local Chromium; includes responsive header, gallery keyboard behavior, seven stubbed Payhip links, four journeys, no-JS fallback, safe search, basic event payloads, campaign config and analytics opt-outs. Payhip and Google requests were stubbed/blocked.
- `tools/qa_accessibility.mjs`: axe-core reported **zero automated WCAG 2.0/2.1 A/AA violations on five sampled pages at 390px**, and checked language-button labels for seven synthetic cookie values. Google Translate itself was blocked and not tested. Comprehensive keyboard, screen-reader and zoom testing, all other pages, and a full manual audit remain outstanding.
- `python3 tools/qa_form.py`: default build contains no unconfigured signup form; no email sent. A `DKP_ANALYTICS=false` source-level check confirmed no GA bootstrap is emitted.
- `python3 tools/qa_assets.py`: **2,760 local image, script, stylesheet and icon references across 104 HTML files, zero missing**. This checks HTML references only, not CSS background URLs, remote asset availability or visual fidelity.

To repeat the browser regression, install `playwright-core` locally and supply an installed Chromium binary as described in `tools/qa_conversion.mjs`; serve the generated site locally first. Do not use a live store for the stubbed regression.

**Release:** review the working-tree diff, rebuild, run the checks, merge/deploy through the owner's normal approved workflow, verify the production JavaScript/cache and pages, then perform the separately authorized real Payhip tests. Do not interpret local QA as proof of live purchases, delivery, consent compliance, SEO results, or increased conversion.
