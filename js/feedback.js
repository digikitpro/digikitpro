/* ══════════════════════════════════════════════════════════════════════
   DigiKitPro — "What stopped you from choosing a brush today?"
   ---------------------------------------------------------------------
   The cheapest qualitative signal available to this business. If the
   answers cluster on "Not sure which brush I need", the Brush Finder is
   the right investment. If they cluster on "Need more examples", product
   media is. Without this the owner is guessing.

   RULES THIS CODE ENFORCES
   • Never a modal. Never blocks a CTA. Never appears on the homepage.
   • Only on product pages and the catalog, only after real engagement
     (≥60% scrolled AND ≥25 seconds on page) and only if the visitor has
     NOT already clicked a buy link — people who are buying are left alone.
   • Once per visit; if dismissed, never shown again on that device.
   • One question, six answers, an "other" free-text box that is optional
     and never required.
   • Every answer produces something USEFUL for the visitor (a relevant
     next link), so it is help, not interrogation.
   • Sends a `feedback_reason` analytics event. Optionally POSTs to
     window.DKP.feedbackEndpoint — empty by default, so nothing is sent
     anywhere until the owner wires it up. No fake backend.
   ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var DKP = (window.DKP = window.DKP || {});
  if (DKP.analytics === false) return;

  /* Honours the same opt-out promised in privacy.html: a visitor who turned
     measurement off, or whose browser sends Do Not Track, is never prompted. */
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1") return;
  try { if (window.localStorage.getItem("dkp_analytics_optout") === "1") return; } catch (e) {}

  var PAGE = DKP.page || {};
  var ALLOWED = { product: 1, catalog: 1, bundles: 1, category: 1 };
  if (!ALLOWED[PAGE.type || ""]) return;

  var DISMISS_KEY = "dkp_fb_dismissed";
  var SHOWN_KEY = "dkp_fb_shown";

  function ls(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function sls(k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  function ss(k) { try { return window.sessionStorage.getItem(k); } catch (e) { return null; } }
  function sss(k, v) { try { window.sessionStorage.setItem(k, v); } catch (e) {} }

  if (ls(DISMISS_KEY) || ss(SHOWN_KEY)) return;

  var REASONS = [
    { id: "browsing",     label: "I was just browsing",              reply: "No problem. The free packs are genuinely free — no email required to look.", link: "freebies.html", linkLabel: "Browse the free brushes" },
    { id: "price",        label: "Too expensive",                    reply: "Fair. Start with the free collection, or compare bundles against single packs — the arithmetic is on the page.", link: "bundles.html", linkLabel: "Compare bundle value" },
    { id: "unsure",       label: "Not sure which brush I need",      reply: "Good question — the choosing guide walks through it honestly: what each kind of pack is for, and what is not worth buying.", link: "blog/how-to-choose-procreate-brushes/", linkLabel: "How to choose brushes" },
    { id: "examples",     label: "Need more examples of the results",reply: "Useful to know. The technique guides show the same brushes used on finished artwork.", link: "blog.html", linkLabel: "See the technique guides" },
    { id: "other-product",label: "Looking for something else",       reply: "Tell us what — that list decides what gets made next.", link: "about.html#contact", linkLabel: "Send a request" },
    { id: "other",        label: "Something else",                   reply: "Thanks for the honesty — it goes straight to the studio.", link: "about.html#contact", linkLabel: "Tell us more" }
  ];

  var bought = false;
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href*="payhip.com"]') : null;
    if (a) { bought = true; hide(true); }
  }, true);

  var sheet = null;
  var scrollOk = false;
  var timeOk = false;

  function rel(p) {
    if (/^(?:https?:)?\/\//i.test(p || "")) return p;
    return (window.__DKP_PREFIX || "") + p;
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function track(n, p) { if (window.dkp) window.dkp.track(n, p); }

  function maybeShow() {
    if (sheet || bought || ls(DISMISS_KEY) || ss(SHOWN_KEY)) return;
    if (!scrollOk || !timeOk) return;
    sss(SHOWN_KEY, "1");
    show();
  }

  window.addEventListener("scroll", function () {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    if (max <= 0) { scrollOk = true; }
    else if ((h.scrollTop || document.body.scrollTop) / max >= 0.6) { scrollOk = true; }
    maybeShow();
  }, { passive: true });

  setTimeout(function () { timeOk = true; maybeShow(); }, 25000);

  function hide(permanent) {
    if (!sheet) return;
    sheet.classList.remove("is-open");
    window.setTimeout(function () { if (sheet && sheet.parentNode) sheet.parentNode.removeChild(sheet); sheet = null; }, 220);
    if (permanent) sls(DISMISS_KEY, "1");
  }

  function show() {
    var opts = REASONS.map(function (r) {
      return '<button class="fb-opt" type="button" data-fb="' + r.id + '">' + esc(r.label) + "</button>";
    }).join("");

    sheet = document.createElement("aside");
    sheet.className = "fb-sheet";
    sheet.setAttribute("role", "complementary");
    sheet.setAttribute("aria-label", "Quick feedback");
    sheet.innerHTML =
      '<div class="fb-inner">' +
      '<button class="fb-close" type="button" aria-label="Dismiss feedback">✕</button>' +
      '<p class="fb-q">What stopped you from choosing a brush today?</p>' +
      '<p class="fb-note">One tap, nothing is required, and it decides what we improve next.</p>' +
      '<div class="fb-opts">' + opts + "</div>" +
      '<div class="fb-other" hidden>' +
      '<label class="sr-only" for="fb-other-input">Anything else? (optional)</label>' +
      '<input id="fb-other-input" type="text" maxlength="180" placeholder="Optional — what were you looking for?" autocomplete="off">' +
      '<button class="btn btn-gold btn-sm" type="button" data-fb-send>Send</button></div>' +
      '<div class="fb-thanks" hidden></div>' +
      "</div>";

    document.body.appendChild(sheet);
    requestAnimationFrame(function () { sheet.classList.add("is-open"); });

    sheet.querySelector(".fb-close").addEventListener("click", function () { hide(true); });

    sheet.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-fb]") : null;
      if (b) return choose(b.getAttribute("data-fb"));
      if (e.target.closest && e.target.closest("[data-fb-send]")) {
        var input = sheet.querySelector("#fb-other-input");
        return submit("other", (input && input.value || "").trim().slice(0, 180));
      }
    });
  }

  function choose(id) {
    if (id === "other" || id === "other-product") {
      var box = sheet.querySelector(".fb-other");
      sheet.querySelector(".fb-opts").hidden = true;
      box.hidden = false;
      box.querySelector("input").focus();
      pending = id;
      return;
    }
    submit(id, "");
  }

  var pending = null;

  function submit(id, note) {
    var r = REASONS.filter(function (x) { return x.id === (pending || id); })[0] || REASONS[0];
    track("feedback_reason", {
      reason: r.id,
      note_length: note ? note.length : 0,
      page_type: PAGE.type,
      product_id: PAGE.slug || "",
      tier: PAGE.tier || ""
    });

    /* Optional owner-configured collector. Empty by default = nothing sent. */
    var endpoint = (DKP.feedbackEndpoint || "").trim();
    if (endpoint && window.fetch) {
      try {
        window.fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            reason: r.id,
            note: note || undefined,
            page_type: PAGE.type || "",
            product_id: PAGE.slug || "",
            ts: new Date().toISOString()
          })
        }).catch(function () {});
      } catch (e) {}
    }

    var thanks = sheet.querySelector(".fb-thanks");
    thanks.innerHTML =
      "<p>" + esc(r.reply) + "</p>" +
      '<p><a class="btn btn-gold btn-sm" href="' + esc(rel(r.link)) + '">' + esc(r.linkLabel) + " →</a></p>";
    sheet.querySelector(".fb-opts").hidden = true;
    var other = sheet.querySelector(".fb-other");
    if (other) other.hidden = true;
    sheet.querySelector(".fb-q").hidden = true;
    sheet.querySelector(".fb-note").hidden = true;
    thanks.hidden = false;

    sls(DISMISS_KEY, "1"); /* answered → never ask again on this device */
    window.setTimeout(function () { hide(false); }, 12000);
  }
})();
