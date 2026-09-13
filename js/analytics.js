/* ══════════════════════════════════════════════════════════════════════
   DigiKitPro — conversion event layer
   ---------------------------------------------------------------------
   WHY THIS EXISTS
   Before this file the site loaded GA4 with a bare `config` call and
   tracked nothing. The owner could not answer the only question that
   matters: which product pages get attention and which get buy-clicks.

   WHAT IT DOES
   1. Exposes `dkp.track(name, params)` — one entry point for every event.
   2. Forwards to GA4 (`gtag('event', …)`) when GA4 is present.
   3. Keeps a privacy-conscious first-party session summary in localStorage
      so there is measurable data even before GA4 is configured, and so a
      future serverless collector can be dropped in without touching HTML.
   4. Auto-binds the standard events by delegation (no per-page wiring):
      page views by type, outbound Payhip clicks, buy / free-download clicks,
      upgrade clicks, recommendation clicks, craft-card clicks, search,
      scroll depth, feedback.

   PRIVACY RULES (non-negotiable, mirrored in privacy.html)
   • No PII. No email addresses. No names. Nothing typed by a visitor is
     stored, except search-query LENGTH.
   • No new cookies are set by DigiKitPro. The local log is localStorage only.
   • `navigator.doNotTrack === "1"` → nothing is sent to GA4.
   • `window.DKP.analytics = false` → this whole module is inert.
   • No cross-site identifier, no fingerprinting, no ad platforms.

   DEBUG: open the console and run `dkp.report()` / `dkp.clear()`.
   ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var DKP = (window.DKP = window.DKP || {});
  if (DKP.analytics === false) return;

  var STORE_KEY = "dkp_session_v1";
  var OPTOUT_KEY = "dkp_analytics_optout";
  var DNT =
    navigator.doNotTrack === "1" ||
    window.doNotTrack === "1" ||
    navigator.msDoNotTrack === "1";

  /* ── opt-out ──────────────────────────────────────────────────────────
     Promised in privacy.html, so it has to actually work:
       • visiting any page with  #dkp-analytics=off  sets a permanent opt-out
       • visiting with          #dkp-analytics=on   clears it
       • the browser's Do Not Track flag is honoured as a full opt-out
     An opted-out visitor gets NO gtag forwarding and NO local counting. */
  function readOptOut() {
    try { return window.localStorage.getItem(OPTOUT_KEY) === "1"; } catch (e) { return false; }
  }
  function setOptOut(on) {
    try {
      if (on) window.localStorage.setItem(OPTOUT_KEY, "1");
      else window.localStorage.removeItem(OPTOUT_KEY);
    } catch (e) {}
  }
  (function () {
    var h = (location.hash || "").toLowerCase();
    if (h.indexOf("dkp-analytics=off") !== -1) setOptOut(true);
    else if (h.indexOf("dkp-analytics=on") !== -1) setOptOut(false);
  })();
  var OPTED_OUT = DNT || readOptOut();
  if (OPTED_OUT) {
    /* Inert, but still expose the API so nothing else on the page throws. */
    window.dkp = {
      track: function () { return false; },
      report: function () { return { opted_out: true, do_not_track: DNT, events: {} }; },
      clear: function () { return "nothing stored"; },
      contextOf: function () { return {}; }
    };
    return;
  }

  /* ── page context, injected by the generator as window.DKP.page ─────── */
  var PAGE = DKP.page || {};
  /* {type, slug, name, tier, price, category, free, line} */

  /* ── first-party session summary (counts only, no identifiers) ──────── */
  function readLog() {
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      var log = raw ? JSON.parse(raw) : null;
      if (!log || typeof log !== "object") return null;
      return log;
    } catch (e) {
      return null;
    }
  }
  function writeLog(log) {
    try {
      window.localStorage.setItem(STORE_KEY, JSON.stringify(log));
    } catch (e) {
      /* private mode / quota — analytics must never break the page */
    }
  }
  function newLog() {
    return { v: 1, started: Date.now(), events: {}, products: {}, last: null };
  }
  var LOG = readLog() || newLog();
  /* A "session" here is 30 minutes of inactivity, purely for local counting. */
  if (!LOG.started || Date.now() - (LOG.touched || LOG.started) > 1800000) {
    LOG = newLog();
  }

  function record(name, params) {
    params = params || {};
    LOG.touched = Date.now();
    LOG.events[name] = (LOG.events[name] || 0) + 1;
    LOG.last = name;
    var slug = params.product_id || params.slug;
    if (slug) {
      var p = LOG.products[slug] || (LOG.products[slug] = { v: 0, b: 0, u: 0 });
      if (name === "product_view") p.v++;
      if (name === "product_buy_click" || name === "free_download_click") p.b++;
      if (name === "upgrade_clicked") p.u++;
    }
    writeLog(LOG);
  }

  /* ── the single public entry point ──────────────────────────────────── */
  function track(name, params) {
    params = params || {};
    try {
      record(name, params);
      if (!DNT && typeof window.gtag === "function") {
        window.gtag("event", name, params);
      }
    } catch (e) {
      /* never let tracking break a sale */
    }
    return true;
  }

  /* ── helpers ────────────────────────────────────────────────────────── */
  function attrs(el) {
    /* Collect every data-dkp-* on an element into a params object. */
    var out = {};
    if (!el || !el.attributes) return out;
    for (var i = 0; i < el.attributes.length; i++) {
      var a = el.attributes[i];
      if (a.name.indexOf("data-dkp-") === 0 && a.name !== "data-dkp-event") {
        var key = a.name.slice(9).replace(/-([a-z])/g, function (m, c) {
          return c.toUpperCase();
        });
        out[key] = a.value;
      }
    }
    if (out.price) out.price = parseFloat(out.price) || undefined;
    return out;
  }

  /* Nearest element carrying product context (a card, a panel, a link). */
  function contextOf(el) {
    var node = el;
    while (node && node !== document.body) {
      if (node.getAttribute && node.getAttribute("data-dkp-slug")) return attrs(node);
      node = node.parentNode;
    }
    return {};
  }

  function isPayhip(href) {
    return /^https?:\/\/([^/]+\.)?payhip\.com\//i.test(href || "");
  }

  /* ── page-view classification ───────────────────────────────────────── */
  function pageEvent() {
    var t = PAGE.type;
    if (!t) {
      var path = location.pathname;
      if (/\/products\/[^/]+\/?$/.test(path)) t = "product";
      else if (/\/category\/[^/]+\/?$/.test(path)) t = "category";
      else if (/\/blog\/[^/]+\/?$/.test(path)) t = "article";
      else if (/find-my-brushes/.test(path)) t = "finder";
      else if (/thank-you/.test(path)) t = "thankyou";
      else if (/bundles/.test(path)) t = "bundles";
      else if (/freebies/.test(path)) t = "freebies";
      else if (/products\.html/.test(path)) t = "catalog";
      else if (/\/(index\.html)?$/.test(path)) t = "home";
      else t = "page";
    }
    var base = {
      page_type: t,
      page_path: location.pathname + location.search
    };
    if (PAGE.slug) {
      base.product_id = PAGE.slug;
      base.product_name = PAGE.name;
      base.tier = PAGE.tier;
      base.category = PAGE.category;
      base.price = PAGE.price;
    }
    switch (t) {
      case "home":
        track("homepage_view", base);
        break;
      case "product":
        track("product_view", base);
        if (PAGE.slug === "master-library-2000-brushes")
          track("master_library_view", base);
        if (PAGE.slug === "procreate-portrait-masterclass-ebook")
          track("masterclass_view", base);
        break;
      case "category":
        base.category = PAGE.category || PAGE.slug;
        track("category_view", base);
        break;
      case "bundles":
        track("bundle_view", base);
        break;
      default:
        track("page_view", base);
    }
  }

  /* ── click delegation: every money action on the site ───────────────── */
  document.addEventListener(
    "click",
    function (e) {
      var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;

      /* Explicit hook: <a data-dkp-event="name" data-dkp-foo="bar"> */
      var hookEl =
        e.target && e.target.closest ? e.target.closest("[data-dkp-event]") : null;
      if (hookEl) {
        var hp = attrs(hookEl);
        var name = hookEl.getAttribute("data-dkp-event");
        for (var k in PAGE) if (PAGE.hasOwnProperty(k) && !(k in hp)) hp["page_" + k] = PAGE[k];
        track(name, hp);
      }

      if (!a) return;
      var href = a.getAttribute("href") || "";

      /* Outbound to the store = the actual revenue action. */
      if (isPayhip(href)) {
        var ctx = attrs(a);
        if (!ctx.slug) ctx = contextOf(a);
        var params = {
          product_id: ctx.slug,
          product_name: ctx.name,
          price: ctx.price,
          tier: ctx.tier,
          location: ctx.loc || "unknown",
          outbound_url: href,
          page_type: PAGE.type || "page"
        };
        track("outbound_payhip_click", params);
        if (ctx.free === "1" || ctx.free === 1) {
          track("free_download_click", params);
        } else if (ctx.slug) {
          track("product_buy_click", params);
        }
      }
    },
    true
  );

  /* ── email signup: main.js dispatches this on a REAL provider response ─ */
  document.addEventListener("dkp:signup", function (e) {
    var d = (e && e.detail) || {};
    track("email_signup", {
      source: d.source || PAGE.type || "unknown",
      lead_magnet: d.lead || "",
      state: d.state || "ok"
    });
  });

  /* ── search (debounced; only the LENGTH is ever recorded) ───────────── */
  var searchTimer = null;
  function bindSearch(input) {
    if (!input || input.__dkpBound) return;
    input.__dkpBound = true;
    input.addEventListener("input", function () {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function () {
        var q = (input.value || "").trim();
        if (q.length >= 2) track("search_query", { term_length: q.length });
      }, 900);
    });
  }
  bindSearch(document.querySelector("[data-search-input]"));
  bindSearch(document.querySelector("[data-search-page-input]"));

  /* ── scroll depth on product pages (50% / 90%, once each) ───────────── */
  function bindScrollDepth() {
    if ((PAGE.type || "") !== "product") return;
    var fired = { 50: false, 90: false };
    var onScroll = function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      if (max <= 0) return;
      var pct = Math.round(((h.scrollTop || document.body.scrollTop) / max) * 100);
      [50, 90].forEach(function (mark) {
        if (!fired[mark] && pct >= mark) {
          fired[mark] = true;
          track("scroll_depth", {
            percent: mark,
            product_id: PAGE.slug,
            tier: PAGE.tier
          });
        }
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ── boot ───────────────────────────────────────────────────────────── */
  function boot() {
    pageEvent();
    bindScrollDepth();
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  /* ── public API ─────────────────────────────────────────────────────── */
  window.dkp = {
    track: track,
    /* Local first-party summary. Counts only — safe to read in the console. */
    report: function () {
      var out = JSON.parse(JSON.stringify(LOG));
      out.do_not_track = DNT;
      out.ga4_present = typeof window.gtag === "function";
      out.ga4_suppressed = DNT;
      return out;
    },
    clear: function () {
      LOG = newLog();
      writeLog(LOG);
      return "cleared";
    },
    contextOf: contextOf
  };
})();
