/* ══════════════════════════════════════════════════════════════════════
   DigiKitPro — "Find My Brushes" recommendation engine
   ---------------------------------------------------------------------
   Solves the #1 conversion problem on this store: 51 products, 28 of them
   priced at exactly $5, with no route from "I paint portraits and my skin
   looks plastic" to the right pack.

   HOW IT SCORES (relevance first, never price first)
     craft   match  +40     ← what the artist actually makes
     improve match  +30     ← the problem they are trying to fix
     style   match  +15     ← the finished look they want
     level   match  +10     ← beginner / intermediate / advanced
     editorial priority ≤+5 ← tie-breaker only (data/discovery.json)
   The most expensive product is NEVER the default answer. The Master
   Library is offered as a separate, clearly-labelled "want everything?"
   step, so the upgrade is a choice rather than a trick.

   DATA: window.DKP_FINDER, generated from data/products.json +
   data/discovery.json by tools/pages_finder.py. Nothing is fetched at
   runtime, so this works offline, on file://, and on GitHub Pages.

   ACCESSIBILITY / NO-JS: the questions are real radio inputs inside a real
   form, so they are keyboard-operable and screen-reader friendly. With
   JavaScript off the form still submits (query string) and the server-
   rendered "Browse by what you create" section below gives the same
   recommendations as plain HTML links.

   EVENTS: brush_finder_started, brush_finder_completed,
   recommendation_clicked, upgrade_clicked  (see js/analytics.js)
   ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var DATA = window.DKP_FINDER;
  var root = document.querySelector("[data-finder]");
  if (!DATA || !root) return;

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) {
    return Array.prototype.slice.call((c || document).querySelectorAll(s));
  };
  function rel(path) {
    if (/^(?:https?:)?\/\//i.test(path || "")) return path;
    return (window.__DKP_PREFIX || "") + path;
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function track(n, p) { if (window.dkp) window.dkp.track(n, p); }

  var QUESTIONS = DATA.questions || [];
  var PRODUCTS = DATA.products || {};
  var FLAGSHIP = DATA.flagship;
  var EDUCATION = DATA.education || {};
  var order = QUESTIONS.map(function (q) { return q.id; });
  var answers = { craft: null, improve: null, level: null, style: null };
  var started = false;
  var completedFor = null;   /* avoids re-firing on every re-render */

  /* ── scoring ────────────────────────────────────────────────────────── */
  function has(list, v) {
    return !!(list && list.length && v && list.indexOf(v) !== -1);
  }

  function score(p, a) {
    var s = 0;
    var hits = { craft: false, improve: false, style: false, level: false };
    if (has(p.craft, a.craft)) { s += 40; hits.craft = true; }
    if (has(p.improve, a.improve)) { s += 30; hits.improve = true; }
    if (has(p.style, a.style)) { s += 15; hits.style = true; }
    if (has(p.level, a.level)) { s += 10; hits.level = true; }
    s += Math.min(5, (p.priority || 0) * 0.05);
    return { total: Math.round(s * 10) / 10, hits: hits };
  }

  function candidates(a) {
    return Object.keys(PRODUCTS)
      .map(function (slug) {
        var p = PRODUCTS[slug];
        var r = score(p, a);
        return { p: p, score: r.total, hits: r.hits };
      })
      .filter(function (c) {
        return !c.p.aggregate && c.score > 0;
      })
      .sort(function (x, y) {
        return y.score - x.score || (y.p.priority || 0) - (x.p.priority || 0);
      });
  }

  function byTier(list, tiers) {
    return list.filter(function (c) { return tiers.indexOf(c.p.tier) !== -1; });
  }

  function labelFor(qid, val) {
    var q = QUESTIONS.filter(function (x) { return x.id === qid; })[0];
    if (!q) return val || "";
    var o = q.options.filter(function (x) { return x.id === val; })[0];
    return o ? o.label : val;
  }

  function whyText(c, a) {
    var bits = [];
    if (c.hits.craft) bits.push(labelFor("craft", a.craft).toLowerCase() + " work");
    if (c.hits.improve) bits.push("focused on " + labelFor("improve", a.improve).toLowerCase());
    var lead = "Based on your answers";
    if (bits.length) lead += " — " + bits.join(", ") + " —";
    var tail = [];
    if (c.p.assets) tail.push("it includes " + c.p.assets);
    if (c.p.stage && c.p.stage !== "library") tail.push("and sits at the " + c.p.stage + " stage of a real workflow");
    if (c.hits.style) tail.push("for the " + labelFor("style", a.style).toLowerCase() + " finish you described");
    return lead + " this is the strongest starting point: " +
      (tail.length ? tail.join(" ") : "it targets exactly what you selected") + ".";
  }

  /* ── rendering ──────────────────────────────────────────────────────── */
  function card(c, slot) {
    var p = c.p;
    var price = p.free ? "Free" : p.priceText;
    var cta = p.free ? "Get Free" : "Buy on Payhip";
    var href = p.free ? p.url : p.payhipUrl;
    var target = p.free ? "" : ' target="_blank" rel="noopener"';
    var why = c.hits ? '<p class="finder-why">' + esc(whyText(c, answers)) + "</p>" : "";
    return (
      '<article class="finder-card">' +
      '<a class="finder-media" href="' + esc(rel(p.url)) + '">' +
      (p.img ? '<img src="' + esc(rel(p.img)) + '" width="750" height="500" alt="' + esc(p.name) + '" loading="lazy" decoding="async">' : "") +
      '<span class="badge">' + esc(p.tierLabel || p.tier) + "</span></a>" +
      '<div class="finder-body">' +
      "<h3>" + esc(p.name) + "</h3>" +
      '<p class="finder-short">' + esc(p.short) + "</p>" +
      why +
      '<ul class="finder-specs">' +
      (p.assets ? "<li><span>Includes</span> " + esc(p.assets) + "</li>" : "") +
      "<li><span>Compatibility</span> " + esc(p.compat || "Procreate on iPad") + "</li>" +
      "<li><span>Delivery</span> " + esc(p.format || "Instant digital download, lifetime access") + "</li>" +
      "</ul>" +
      '<div class="finder-foot"><span class="price">' + esc(price) + "</span>" +
      '<a class="btn btn-gold btn-sm" href="' + esc(href) + '"' + target +
      ' data-dkp-event="recommendation_clicked" data-dkp-slot="' + esc(slot) + '"' +
      ' data-dkp-slug="' + esc(p.slug) + '" data-dkp-name="' + esc(p.name) + '"' +
      ' data-dkp-price="' + esc(p.price) + '" data-dkp-tier="' + esc(p.tier) + '"' +
      ' data-dkp-free="' + (p.free ? 1 : 0) + '" data-dkp-loc="finder-' + esc(slot) + '">' + cta + "</a>" +
      '<a class="text-link" href="' + esc(rel(p.url)) + '">Full details →</a></div>' +
      "</div></article>"
    );
  }

  function simpleCard(p, slot, heading) {
    if (!p) return "";
    var price = p.free ? "Free" : p.priceText;
    var cta = p.free ? "Get Free" : "Get it on Payhip";
    var href = p.free ? p.url : p.payhipUrl;
    var target = p.free ? "" : ' target="_blank" rel="noopener"';
    return (
      '<div class="finder-slot">' +
      (heading ? '<p class="finder-slot-label">' + esc(heading) + "</p>" : "") +
      '<article class="finder-card finder-card--slim">' +
      '<a class="finder-media" href="' + esc(rel(p.url)) + '">' +
      (p.img ? '<img src="' + esc(rel(p.img)) + '" width="750" height="500" alt="' + esc(p.name) + '" loading="lazy" decoding="async">' : "") +
      '</a><div class="finder-body"><h3>' + esc(p.name) + "</h3>" +
      '<p class="finder-short">' + esc(p.short) + "</p>" +
      (p.assets ? '<p class="finder-assets">' + esc(p.assets) + "</p>" : "") +
      '<div class="finder-foot"><span class="price">' + esc(price) + "</span>" +
      '<a class="btn btn-line btn-sm" href="' + esc(href) + '"' + target +
      ' data-dkp-event="recommendation_clicked" data-dkp-slot="' + esc(slot) + '"' +
      ' data-dkp-slug="' + esc(p.slug) + '" data-dkp-name="' + esc(p.name) + '"' +
      ' data-dkp-price="' + esc(p.price) + '" data-dkp-tier="' + esc(p.tier) + '"' +
      ' data-dkp-free="' + (p.free ? 1 : 0) + '" data-dkp-loc="finder-' + esc(slot) + '">' + cta + "</a>" +
      '<a class="text-link" href="' + esc(rel(p.url)) + '">Details →</a></div></div></article></div>'
    );
  }

  function flagshipBlock(primary) {
    var flagship = PRODUCTS[FLAGSHIP];
    if (!flagship || (primary && primary.p.slug === flagship.slug)) return "";
    var delta = (parseFloat(flagship.price) - parseFloat(primary ? primary.p.price : 0)).toFixed(2);
    return (
      '<div class="finder-slot finder-slot--flagship">' +
      '<p class="finder-slot-label">Want everything?</p>' +
      '<article class="finder-card finder-card--flag">' +
      '<a class="finder-media" href="' + esc(rel(flagship.url)) + '">' +
      (flagship.img ? '<img src="' + esc(rel(flagship.img)) + '" width="750" height="500" alt="' + esc(flagship.name) + '" loading="lazy" decoding="async">' : "") +
      '</a><div class="finder-body"><h3>' + esc(flagship.name) + "</h3>" +
      '<p class="finder-short">' + esc(flagship.short) + "</p>" +
      '<p class="finder-why">' + esc(flagship.assets || "2,000+ brushes") +
      " — every style in one organised library for " + esc(flagship.priceText) +
      ", instead of buying single packs one at a time" +
      (parseFloat(delta) > 0 && primary ? " (+$" + delta + " over the pick above)" : "") +
      ".</p>" +
      '<div class="finder-foot"><span class="price price-lg">' + esc(flagship.priceText) + "</span>" +
      '<a class="btn btn-gold" href="' + esc(flagship.payhipUrl) + '" target="_blank" rel="noopener"' +
      ' data-dkp-event="upgrade_clicked" data-dkp-from-product-id="' + esc(primary ? primary.p.slug : "") + '"' +
      ' data-dkp-to-product-id="' + esc(flagship.slug) + '" data-dkp-price-delta="' + esc(delta) + '"' +
      ' data-dkp-slug="' + esc(flagship.slug) + '" data-dkp-name="' + esc(flagship.name) + '"' +
      ' data-dkp-price="' + esc(flagship.price) + '" data-dkp-tier="flagship" data-dkp-free="0"' +
      ' data-dkp-loc="finder-flagship">Get the Master Library ↗</a>' +
      '<a class="text-link" href="' + esc(rel(flagship.url)) + '">See what is inside →</a>' +
      '<a class="text-link" href="' + esc(rel("bundles.html")) + '">Compare all libraries →</a></div></div></article></div>'
    );
  }

  var lastPrimary = null;
  function buildResult() {
    var list = candidates(answers);
    if (!list.length) { lastPrimary = null; return fallbackResult(); }

    var buyable = byTier(list, ["entry", "bundle"]);
    var primary = buyable[0] || list[0];
    var alternates = buyable.slice(1, 3);
    lastPrimary = primary;

    var freePick = null;
    if (answers.level === "beginner") {
      var frees = byTier(list, ["free"]);
      freePick = frees.length ? frees[0] : null;
    }

    var edu = null;
    var portraitIntent = answers.craft === "portraits" ||
      answers.improve === "skin" || answers.improve === "hair";
    if (portraitIntent) {
      edu = answers.level === "beginner" ? PRODUCTS[EDUCATION.free] : PRODUCTS[EDUCATION.paid];
    }

    var notice = answers.craft === "animation" ? DATA.animationNotice : null;

    var html = '<div class="finder-result">';
    html += '<p class="eyebrow">Your recommended starting point</p>';
    html += card(primary, "primary");

    if (notice) {
      html += '<div class="finder-notice"><h3>' + esc(notice.title) + "</h3><p>" +
        esc(notice.body) + '</p><p><a class="text-link" href="' + esc(rel(notice.cta.href)) + '">' +
        esc(notice.cta.label) + " →</a></p></div>";
    }

    if (alternates.length) {
      html += '<p class="finder-slot-label">Also a strong match</p><div class="finder-duo">';
      alternates.forEach(function (c, i) { html += card(c, "alternate" + (i + 1)); });
      html += "</div>";
    }

    if (freePick) html += simpleCard(freePick.p, "free", "Start free while you learn");

    html += flagshipBlock(primary);

    if (edu) html += simpleCard(edu, "education", "Learn the workflow behind it");

    html += '<div class="finder-restart"><button class="btn btn-line btn-sm" type="button" data-finder-restart>' +
      "Start over</button><a class=\"text-link\" href=\"" + esc(rel("products.html")) +
      '\">Browse the full catalog →</a></div>';
    html += "</div>";
    return html;
  }

  function fallbackResult() {
    var picks = [PRODUCTS[FLAGSHIP], PRODUCTS[EDUCATION.free]].filter(Boolean);
    return (
      '<div class="finder-result"><p class="eyebrow">No exact match yet</p>' +
      '<h2 class="finder-h">We do not have a pack for that exact combination — yet</h2>' +
      '<p class="muted">That answer is genuinely useful: it is what decides what gets built next. ' +
      "Meanwhile these cover most workflows.</p><div class=\"finder-duo\">" +
      picks.map(function (p) { return simpleCard(p, "fallback", ""); }).join("") +
      '</div><p><a class="text-link" href="' + esc(rel("freebies.html#newsletter")) +
      '\">Get new Procreate tool drops by email →</a></p></div>'
    );
  }

  /* ── wizard behaviour ───────────────────────────────────────────────── */
  var resultsBox = $("[data-finder-results]", root);
  var steps = $$("[data-finder-step]", root);
  var summary = $("[data-finder-summary]", root);
  var form = $("form[data-finder-form]", root);
  var submitBtn = form ? form.querySelector('[type="submit"]') : null;

  function currentStep() {
    for (var i = 0; i < order.length; i++) if (!answers[order[i]]) return i;
    return order.length;
  }

  function setAnswer(name, value) {
    if (!name || !value) return;
    if (order.indexOf(name) === -1) return;
    if (!started) { started = true; track("brush_finder_started", {}); }
    answers[name] = value;
    paint();
    syncHash();
    var next = $(".is-current", root);
    if (next && window.innerWidth < 900) {
      next.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  function paint() {
    var idx = currentStep();
    steps.forEach(function (s, i) {
      var qid = s.getAttribute("data-finder-step");
      s.hidden = i > idx;
      s.classList.toggle("is-current", i === idx);
      s.classList.toggle("is-done", i < idx);
      $$('input[type="radio"]', s).forEach(function (r) {
        var on = answers[qid] === r.value;
        if (r.checked !== on) r.checked = on;
        var lbl = r.closest(".f-opt");
        if (lbl) {
          lbl.classList.toggle("selected", on);
          lbl.setAttribute("aria-pressed", on ? "true" : "false");
        }
      });
    });
    if (summary) {
      var chips = order.filter(function (k) { return answers[k]; }).map(function (k) {
        return '<button class="finder-chip" type="button" data-edit="' + k + '" ' +
          'aria-label="Change answer: ' + esc(labelFor(k, answers[k])) + '">' +
          esc(labelFor(k, answers[k])) + " ✕</button>";
      }).join("");
      summary.innerHTML = chips;
      summary.hidden = !chips;
    }
    var bar = $("[data-finder-progress]", root);
    if (bar) {
      bar.style.width = Math.round((idx / order.length) * 100) + "%";
      var host = bar.parentNode;
      if (host) {
        host.setAttribute("aria-valuenow", String(idx));
        host.setAttribute("aria-valuetext", idx + " of " + order.length + " answered");
      }
    }
    if (submitBtn) {
      var complete = idx >= order.length;
      submitBtn.disabled = false; // keep enabled but change label for guidance
      submitBtn.textContent = complete ? "Show my recommendation" : "Answer " + (order.length - idx) + " more to see results";
      submitBtn.classList.toggle("btn-gold", complete);
      submitBtn.classList.toggle("btn-line", !complete);
    }
    if (resultsBox) {
      var complete = idx >= order.length;
      resultsBox.hidden = !complete;
      if (complete) {
        resultsBox.innerHTML = buildResult();
        var key = order.map(function (k) { return answers[k]; }).join("/");
        if (completedFor !== key) {
          completedFor = key;
          var list = candidates(answers);
          var shown = lastPrimary || { p: {}, score: 0 };
          track("brush_finder_completed", {
            craft: answers.craft, improve: answers.improve,
            level: answers.level, style: answers.style,
            recommended_id: shown.p.slug || "",
            recommended_tier: shown.p.tier || "",
            match_score: shown.score,
            result_count: list.length
          });
        }
        resultsBox.setAttribute("tabindex", "-1");
      } else {
        resultsBox.innerHTML = "";
        completedFor = null;
      }
    }
  }

  /* Real radio inputs → the `change` event is the accessible, keyboard- and
     screen-reader-safe hook. */
  if (form) {
    // Change bubbles from radio inputs
    form.addEventListener("change", function (e) {
      var r = e.target;
      if (!r || r.type !== "radio" || !r.name) return;
      setAnswer(r.name, r.value);
    });

    // Click on the whole .f-opt card ensures dynamic selection even if
    // the label's default behavior is prevented by other handlers.
    form.addEventListener("click", function (e) {
      var opt = e.target.closest ? e.target.closest(".f-opt") : null;
      if (!opt || !form.contains(opt)) return;
      var input = opt.querySelector('input[type="radio"]');
      if (!input) return;
      if (input.checked && answers[input.name] === input.value) return;
      // Manually set and fire logic
      input.checked = true;
      setAnswer(input.name, input.value);
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (window.FormData) {
        var data = new FormData(form);
        order.forEach(function (k) { var v = data.get(k); if (v) answers[k] = v; });
      }
      if (!started) { started = true; track("brush_finder_started", {}); }
      paint();
      syncHash();
      if (resultsBox && !resultsBox.hidden) {
        resultsBox.scrollIntoView({ behavior: "smooth", block: "start" });
        try { resultsBox.focus({ preventScroll: true }); } catch (err) { resultsBox.focus(); }
      } else {
        // Incomplete: scroll to next unanswered step
        var next = $(".is-current", root);
        if (next) next.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  }

  root.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var edit = t.closest("[data-edit]");
    if (edit) {
      answers[edit.getAttribute("data-edit")] = null;
      paint();
      syncHash();
      return;
    }
    if (t.closest("[data-finder-restart]")) {
      answers = { craft: null, improve: null, level: null, style: null };
      if (form) form.reset();
      paint();
      syncHash();
      root.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  /* ── shareable / deep-linkable answers ──────────────────────────────── */
  function syncHash() {
    var parts = order.map(function (k) { return answers[k] || ""; });
    if (parts.some(Boolean)) {
      var h = "#" + parts.join("/");
      if (location.hash !== h && window.history && history.replaceState) {
        history.replaceState(null, "", h);
      }
    }
  }

  function readState() {
    var found = false;
    if (window.URLSearchParams) {
      var qs = new URLSearchParams(location.search);
      order.forEach(function (k) {
        var v = qs.get(k);
        if (v && PRODUCTS) { answers[k] = v; found = true; }
      });
    }
    var raw = (location.hash || "").replace(/^#/, "");
    if (!raw) return found;
    var h = raw;

    // Handle craft=xxx or craft/xxx style from homepage
    // e.g. #craft=animation , #craft/animation , #animation , #craft=portraits
    if (h.indexOf("=") !== -1 || h.indexOf("/") === -1) {
      // Single craft shortcut: #animation or #craft=animation
      var single = h;
      if (single.indexOf("craft=") === 0) single = single.split("=")[1] || "";
      else if (single.indexOf("=") !== -1) {
        // could be craft=animation&improve=skin etc? handle &
        var params = {};
        single.split(/[&;]/).forEach(function (pair) {
          var kv = pair.split("=");
          if (kv.length === 2) params[kv[0]] = decodeURIComponent(kv[1] || "");
        });
        if (params.craft) { answers.craft = params.craft; found = true; }
        if (params.improve) { answers.improve = params.improve; found = true; }
        if (params.level) { answers.level = params.level; found = true; }
        if (params.style) { answers.style = params.style; found = true; }
        if (found) return found;
        // fallback: first token after = is craft
        var kv2 = h.split("=");
        if (kv2[0] === "craft" && kv2[1]) { answers.craft = kv2[1].split("&")[0].split("/")[0]; found = true; return found; }
      } else {
        // No =, check if it's a known craft id directly (#animation)
        var knownCrafts = (QUESTIONS[0] && QUESTIONS[0].options || []).map(function (o) { return o.id; });
        if (knownCrafts.indexOf(single) !== -1) {
          answers.craft = single;
          found = true;
          return found;
        }
      }
    }

    // Slash separated: craft/improve/level/style  or craft/animation
    var parts = h.split("/");
    if (parts.length === 2 && parts[0] === "craft") {
      var kv = parts[1].split("=");
      answers.craft = kv[1] || kv[0];
      found = true;
    } else if (parts.length >= 2 && parts[0].indexOf("=") === -1 && parts.length < order.length) {
      // Might be legacy #craft=animation stored as craft=animation split? already handled
      // Try to detect if first part is craft=xxx
      if (parts[0].indexOf("craft=") === 0) {
        answers.craft = parts[0].split("=")[1];
        found = true;
        // if there are more parts after, treat as improve/level/style
        if (parts[1]) { answers.improve = parts[1]; found = true; }
        if (parts[2]) { answers.level = parts[2]; found = true; }
        if (parts[3]) { answers.style = parts[3]; found = true; }
      }
    } else if (parts.length >= order.length) {
      order.forEach(function (k, i) { if (parts[i]) { answers[k] = parts[i]; found = true; } });
    } else if (parts.length === 1 && parts[0].indexOf("craft=") === 0) {
      answers.craft = parts[0].split("=")[1] || "";
      if (answers.craft) found = true;
    }
    return found;
  }

  if (readState()) started = true;
  paint();
})();
